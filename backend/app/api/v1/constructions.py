"""
装修决策Agent - 施工进度管理API（PRD V2.6.1 对齐 V15.3）
6大阶段 S00-S05、流程互锁、阶段时间校准、提醒联动
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

from datetime import date as date_type
from app.core.database import get_db
from app.core.security import get_user_id
from app.core.config import settings
from app.models import Construction, UserSetting
from app.schemas import (
    StartDateRequest, UpdateStageStatusRequest, CalibrateStageRequest,
    ConstructionResponse, ApiResponse
)

router = APIRouter(prefix="/constructions", tags=["施工进度"])
logger = logging.getLogger(__name__)

STAGE_ORDER = getattr(settings, "STAGE_ORDER", None) or ["S00", "S01", "S02", "S03", "S04", "S05"]
STAGE_DURATION = getattr(settings, "STAGE_DURATION", None) or {}

# 旧阶段键到 S00-S05 的映射
STAGE_KEY_TO_S = {
    "material": "S00", "plumbing": "S01", "carpentry": "S02",
    "woodwork": "S03", "painting": "S04", "installation": "S05",
    "flooring": "S02", "soft_furnishing": "S05",
}


def normalize_stage_key(stage: str) -> str:
    if stage in STAGE_ORDER:
        return stage
    return STAGE_KEY_TO_S.get(stage, stage)


def _stage_passed(stages: Dict, key: str) -> bool:
    """检查阶段是否已通过"""
    s = stages.get(key) or {}
    # 处理JSON字符串格式
    if isinstance(s, str):
        import json
        try:
            s = json.loads(s)
        except:
            s = {}
    st = s.get("status") if isinstance(s, dict) else "pending"
    if not st:
        st = "pending"
    # S00阶段：checked表示已通过
    if key == "S00":
        return st == "checked"
    # 其他阶段：passed或completed表示已通过
    return st in ("passed", "completed")


def _serialize_stages_with_lock(stages: Dict) -> Dict[str, Dict[str, Any]]:
    """序列化阶段数据并添加locked状态"""
    # 处理JSON字符串格式
    if isinstance(stages, str):
        import json
        try:
            stages = json.loads(stages)
        except:
            stages = {}
    if not isinstance(stages, dict):
        stages = {}
    
    out = {}
    for i, key in enumerate(STAGE_ORDER):
        raw = stages.get(key) or {}
        # 处理字典中的字符串值
        if isinstance(raw, str):
            import json
            try:
                raw = json.loads(raw)
            except:
                raw = {}
        if not isinstance(raw, dict):
            raw = {}
        
        # 计算locked状态：检查前置阶段是否通过
        prev_passed = True
        if i > 0:
            prev_key = STAGE_ORDER[i - 1]
            prev_passed = _stage_passed(stages, prev_key)
        locked = not prev_passed

        # 如果阶段数据为空，至少返回基本信息
        if not raw:
            item = {
                "status": "pending",
                "sequence": i + 1,
                "stage_key": key,
                "locked": locked
            }
        else:
            item = dict(raw)
            for k, v in list(item.items()):
                if isinstance(v, datetime):
                    item[k] = v.isoformat() if v else None
            # 确保 status 字段存在，如果缺失则设为 pending（避免前端映射错误）
            if "status" not in item or not item.get("status"):
                item["status"] = "pending"
            item["locked"] = locked
            item["stage_key"] = key
        
        out[key] = item
    return out


def _stages_to_json_serializable(stages: Dict[str, Any]) -> Dict[str, Any]:
    """将 stages 中的 datetime 转为 ISO 字符串，便于写入 JSON 列"""
    out = {}
    for k, v in stages.items():
        item = dict(v)
        for key in ("start_date", "end_date"):
            if key in item and item[key] is not None:
                val = item[key]
                if hasattr(val, "isoformat"):
                    item[key] = val.isoformat()
        out[k] = item
    return out


def calculate_construction_schedule(start_date: datetime, custom_durations: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """V2.6.2优化：支持自定义阶段周期"""
    stages = {}
    current_date = start_date
    # 使用自定义周期，如果没有则使用默认周期
    durations = custom_durations or {}
    for stage in STAGE_ORDER:
        duration = durations.get(stage) or STAGE_DURATION.get(stage, 7)
        if isinstance(current_date, datetime):
            end_date = current_date + timedelta(days=duration - 1)
        else:
            end_date = current_date + timedelta(days=duration - 1)
        stages[stage] = {
            "status": "pending",
            "start_date": current_date,
            "end_date": end_date,
            "duration": duration,
            "sequence": STAGE_ORDER.index(stage) + 1,
        }
        current_date = end_date + timedelta(days=1)
    estimated_end_date = current_date - timedelta(days=1)
    return {"stages": stages, "estimated_end_date": estimated_end_date}


def calculate_progress(stages: Dict) -> int:
    total = sum((s.get("duration") or 0) for s in stages.values())
    if total == 0:
        return 0
    done = 0
    for s in stages.values():
        st = s.get("status") or "pending"
        d = s.get("duration") or 0
        if st in ("checked", "passed", "completed"):
            done += d
        elif st in ("in_progress", "need_rectify", "pending_recheck"):
            done += d * 0.5
    return min(100, int((done / total) * 100))


@router.get("/schedule", response_model=ConstructionResponse)
async def get_construction_schedule(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取施工进度计划（含阶段互锁 locked、日期序列化）。未设置开工日期时返回 200 空数据，便于前端展示「设置开工日期」而不报错。"""
    try:
        result = await db.execute(select(Construction).where(Construction.user_id == user_id))
        construction = result.scalar_one_or_none()
        if not construction:
            return ConstructionResponse(
                id=0,
                start_date=None,
                estimated_end_date=None,
                progress_percentage=0,
                is_delayed=False,
                delay_days=0,
                stages={},
                notes=None,
            )

        is_delayed = False
        delay_days = 0
        if construction.start_date and construction.estimated_end_date:
            today = datetime.now().date()
            end = construction.estimated_end_date.date() if hasattr(construction.estimated_end_date, "date") else construction.estimated_end_date
            if today > end:
                is_delayed = True
                delay_days = (today - end).days

        stages_raw = construction.stages or {}
        # 处理JSON字符串格式（PostgreSQL JSON字段可能返回字符串）
        if isinstance(stages_raw, str):
            import json
            try:
                stages_raw = json.loads(stages_raw)
            except Exception as e:
                logger.warning(f"解析stages JSON字符串失败: {e}")
                stages_raw = {}
        if not isinstance(stages_raw, dict):
            stages_raw = {}
        
        # 如果stages为空，从start_date初始化所有阶段（仅在首次查询时）
        # 注意：不要在这里重新初始化，因为可能会覆盖已更新的状态
        # 如果stages为空，说明数据有问题，应该记录错误而不是重新初始化
        if not stages_raw and construction.start_date:
            logger.warning(f"查询进度计划时stages为空，但start_date存在: {construction.start_date}，这不应该发生")
            # 不重新初始化，避免覆盖已更新的状态
            # 只在确实需要时才初始化（例如首次设置开工日期后立即查询）
        
        # 调试日志：记录查询时的原始数据
        s00_raw = stages_raw.get('S00', {})
        s01_raw = stages_raw.get('S01', {})
        logger.debug(f"查询进度计划，stages keys: {list(stages_raw.keys())}, S00状态: {s00_raw.get('status') if isinstance(s00_raw, dict) else 'N/A'}, S01存在: {'S01' in stages_raw}, S01数据: {s01_raw}")
        
        stages_serialized = _serialize_stages_with_lock(stages_raw)
        
        # 调试：确保返回的数据包含所有阶段
        s00_serialized = stages_serialized.get('S00', {})
        s01_serialized = stages_serialized.get('S01', {})
        logger.debug(f"返回进度计划，stages keys: {list(stages_serialized.keys())}, S00状态: {s00_serialized.get('status')}, S01存在: {'S01' in stages_serialized}, S01锁定: {s01_serialized.get('locked') if isinstance(s01_serialized, dict) else 'N/A'}")

        return ConstructionResponse(
            id=construction.id,
            start_date=construction.start_date,
            estimated_end_date=construction.estimated_end_date,
            actual_end_date=construction.actual_end_date,
            progress_percentage=construction.progress_percentage or 0,
            is_delayed=is_delayed,
            delay_days=delay_days,
            stages=stages_serialized,
            notes=construction.notes
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取施工进度失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取进度失败")


@router.post("/start-date")
async def set_start_date(
    request: StartDateRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """设置开工日期（FR-011）；未设置则所有阶段卡片置灰"""
    try:
        if request.start_date < datetime.now().date():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="开工日期不能早于今天")

        # 转为 datetime 供 DB 与计算使用（前端传 YYYY-MM-DD，Pydantic 解析为 date）
        start_dt = datetime.combine(request.start_date, datetime.min.time())

        result = await db.execute(select(Construction).where(Construction.user_id == user_id))
        construction = result.scalar_one_or_none()
        if not construction:
            construction = Construction(user_id=user_id)
            db.add(construction)
            await db.flush()

        construction.start_date = start_dt
        # V2.6.2优化：支持自定义阶段周期
        custom_durations = getattr(request, "custom_durations", None)
        schedule = calculate_construction_schedule(start_dt, custom_durations)
        construction.stages = _stages_to_json_serializable(schedule["stages"])
        construction.estimated_end_date = schedule["estimated_end_date"]
        construction.progress_percentage = 0
        construction.is_delayed = False
        construction.delay_days = 0
        await db.commit()
        await db.refresh(construction)

        return ApiResponse(
            code=0,
            msg="进度计划更新成功",
            data={
                "id": construction.id,
                "start_date": construction.start_date.isoformat(),
                "estimated_end_date": construction.estimated_end_date.isoformat() if construction.estimated_end_date else None,
                "stages": _serialize_stages_with_lock(construction.stages or {})
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"设置开工日期失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="设置失败")


@router.put("/stage-status")
async def update_stage_status(
    request: UpdateStageStatusRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新阶段状态（FR-013 流程互锁：前置未通过则 409）"""
    try:
        result = await db.execute(select(Construction).where(Construction.user_id == user_id))
        construction = result.scalar_one_or_none()
        if not construction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未设置开工日期")

        stage_key = normalize_stage_key(request.stage)
        # 确保stages是字典格式，处理JSON存储的情况
        # 重要：创建独立的字典副本，避免直接修改数据库对象的引用
        stages_raw = construction.stages or {}
        if isinstance(stages_raw, str):
            import json
            try:
                stages_raw = json.loads(stages_raw)
            except:
                stages_raw = {}
        if not isinstance(stages_raw, dict):
            stages_raw = {}
        
        # 创建深拷贝，确保修改不会影响原始对象
        import copy
        stages = copy.deepcopy(stages_raw)
        
        # 如果stages为空，从start_date初始化所有阶段（确保有基础数据）
        if not stages and construction.start_date:
            schedule = calculate_construction_schedule(construction.start_date)
            stages = schedule["stages"]
            logger.info(f"stages为空，从start_date初始化所有阶段: {list(stages.keys())}")

        if stage_key not in STAGE_ORDER:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"阶段 {request.stage} 不存在")

        idx = STAGE_ORDER.index(stage_key)
        # 流程互锁：检查前置阶段是否通过
        if idx > 0:
            prev_key = STAGE_ORDER[idx - 1]
            if not _stage_passed(stages, prev_key):
                prev_name = {"S00": "材料进场核对", "S01": "隐蔽工程", "S02": "泥瓦工", "S03": "木工", "S04": "油漆", "S05": "安装收尾"}.get(prev_key, prev_key)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"请先完成{prev_name}验收/核对"
                )

        # 如果阶段不存在，初始化阶段数据
        if stage_key not in stages or not stages[stage_key]:
            # 如果stages为空，从start_date初始化所有阶段
            if not stages and construction.start_date:
                schedule = calculate_construction_schedule(construction.start_date)
                stages = schedule["stages"]
                logger.info(f"stages为空，从start_date初始化所有阶段: {list(stages.keys())}")
            else:
                # 从已有阶段获取基础信息，或使用默认值
                base_stage = stages.get(STAGE_ORDER[0], {}) if stages else {}
                start_date = base_stage.get("start_date")
                if isinstance(start_date, str):
                    try:
                        start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                    except:
                        start_date = construction.start_date or datetime.now()
                elif not start_date:
                    start_date = construction.start_date or datetime.now()
                
                duration = STAGE_DURATION.get(stage_key, 7)
                end_date = start_date + timedelta(days=duration - 1) if isinstance(start_date, datetime) else datetime.now() + timedelta(days=duration - 1)
                
                stages[stage_key] = {
                    "status": "pending",
                    "sequence": idx + 1,
                    "start_date": start_date.isoformat() if isinstance(start_date, datetime) else str(start_date),
                    "end_date": end_date.isoformat() if isinstance(end_date, datetime) else str(end_date),
                    "duration": duration
                }
        
        # 确保阶段数据存在
        if stage_key not in stages:
            logger.error(f"阶段{stage_key}初始化失败")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"阶段{stage_key}初始化失败")
        
        # 更新阶段状态
        # 确保阶段字典存在且是可修改的
        if stage_key not in stages:
            logger.error(f"阶段{stage_key}不存在于stages中，这不应该发生")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"阶段{stage_key}数据异常")
        
        # 确保阶段数据是字典类型
        if not isinstance(stages[stage_key], dict):
            logger.warning(f"阶段{stage_key}数据不是字典类型，重新初始化")
            stages[stage_key] = {}
        
        # 记录更新前的状态
        old_status = stages[stage_key].get("status", "N/A")
        logger.info(f"更新阶段{stage_key}状态: {old_status} -> {request.status}, 更新前stages[{stage_key}]: {stages[stage_key]}")
        
        stages[stage_key]["status"] = request.status
        
        # 验证状态是否已更新
        if stages[stage_key].get("status") != request.status:
            logger.error(f"状态更新失败！期望: {request.status}, 实际: {stages[stage_key].get('status')}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="状态更新失败")
        
        logger.info(f"更新阶段{stage_key}状态为: {request.status}, 当前stages: {list(stages.keys())}, S00状态: {stages.get('S00', {}).get('status', 'N/A')}, S01存在: {'S01' in stages}, stages[{stage_key}]完整数据: {stages[stage_key]}")

        # 如果当前阶段完成，自动创建下一个阶段（如果不存在）
        if request.status in ("checked", "passed", "completed"):
            if idx < len(STAGE_ORDER) - 1:
                next_key = STAGE_ORDER[idx + 1]
                # 检查下一个阶段是否存在，如果不存在或为空则创建
                next_stage = stages.get(next_key)
                if not next_stage or not isinstance(next_stage, dict) or not next_stage.get("start_date"):
                    duration = STAGE_DURATION.get(next_key, 7)
                    cur = stages[stage_key]
                    end = cur.get("end_date")
                    
                    # 如果当前阶段没有end_date，从start_date计算
                    if not end:
                        start = cur.get("start_date")
                        if isinstance(start, str):
                            try:
                                start = datetime.fromisoformat(start.replace("Z", "+00:00"))
                            except:
                                start = construction.start_date or datetime.now()
                        elif not isinstance(start, datetime):
                            start = construction.start_date or datetime.now()
                        cur_duration = cur.get("duration", STAGE_DURATION.get(stage_key, 7))
                        end = start + timedelta(days=cur_duration - 1) if isinstance(start, datetime) else datetime.now()
                        # 更新当前阶段的end_date
                        cur["end_date"] = end.isoformat() if isinstance(end, datetime) else str(end)
                        cur["duration"] = cur_duration
                    
                    # 解析end_date
                    if isinstance(end, str):
                        try:
                            end = datetime.fromisoformat(end.replace("Z", "+00:00"))
                        except Exception:
                            end = datetime.now()
                    elif not isinstance(end, datetime):
                        end = datetime.now()
                    
                    # 计算下一个阶段的开始和结束时间
                    next_start = end + timedelta(days=1) if isinstance(end, datetime) else datetime.now() + timedelta(days=1)
                    next_end = next_start + timedelta(days=duration - 1)
                    
                    # 创建下一个阶段数据
                    stages[next_key] = {
                        "status": "pending",
                        "start_date": next_start.isoformat() if isinstance(next_start, datetime) else str(next_start),
                        "end_date": next_end.isoformat() if isinstance(next_end, datetime) else str(next_end),
                        "duration": duration,
                        "sequence": idx + 2,
                    }
                    
                    logger.info(f"自动创建下一阶段: {next_key}, 开始时间: {next_start}, 结束时间: {next_end}, stages keys: {list(stages.keys())}, S01数据: {stages.get('S01', {})}")
                
                # 更新预计结束日期
                last_key = STAGE_ORDER[-1]
                last_stage = stages.get(last_key, {})
                last_end_date = last_stage.get("end_date")
                if last_end_date:
                    if isinstance(last_end_date, str):
                        try:
                            last_end_date = datetime.fromisoformat(last_end_date.replace("Z", "+00:00"))
                        except:
                            last_end_date = None
                    if isinstance(last_end_date, datetime):
                        construction.estimated_end_date = last_end_date

        # 序列化stages为JSON格式存储
        stages_serialized = _stages_to_json_serializable(stages)
        
        # 验证序列化后的数据包含状态（在保存前验证）
        logger.info(f"准备保存阶段状态: {stage_key} -> {request.status}, 序列化后的stages keys: {list(stages_serialized.keys())}, S00状态: {stages_serialized.get('S00', {}).get('status') if 'S00' in stages_serialized else 'N/A'}, S01存在: {'S01' in stages_serialized}, S01数据: {stages_serialized.get('S01', {})}")
        
        # 确保序列化后的数据包含所有必要的字段
        if stage_key in stages_serialized:
            if stages_serialized[stage_key].get("status") != request.status:
                logger.error(f"序列化后状态不匹配！期望: {request.status}, 实际: {stages_serialized[stage_key].get('status')}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="状态序列化失败")
        
        construction.stages = stages_serialized
        construction.progress_percentage = calculate_progress(stages)
        all_done = all(_stage_passed(stages, k) for k in STAGE_ORDER)
        if all_done and not construction.actual_end_date:
            construction.actual_end_date = datetime.now()

        await db.commit()
        await db.refresh(construction)
        
        # 验证保存的数据（从数据库重新读取）
        saved_stages = construction.stages or {}
        if isinstance(saved_stages, str):
            import json
            try:
                saved_stages = json.loads(saved_stages)
            except:
                saved_stages = {}
        
        saved_s00_status = saved_stages.get('S00', {}).get('status') if isinstance(saved_stages, dict) and 'S00' in saved_stages else 'N/A'
        saved_s01_exists = isinstance(saved_stages, dict) and 'S01' in saved_stages
        saved_s01_data = saved_stages.get('S01', {}) if saved_s01_exists else {}
        
        logger.info(f"阶段状态更新完成: {stage_key} -> {request.status}, saved keys: {list(saved_stages.keys()) if isinstance(saved_stages, dict) else 'not dict'}, saved S00状态: {saved_s00_status}, S01存在: {saved_s01_exists}, S01数据: {saved_s01_data}")

        # 使用已保存的数据构建响应（避免重复刷新）
        stages_for_response = saved_stages if isinstance(saved_stages, dict) else {}
        
        # 验证响应数据
        response_stages = _serialize_stages_with_lock(stages_for_response)
        response_s00_status = response_stages.get('S00', {}).get('status', 'N/A')
        response_s01_locked = response_stages.get('S01', {}).get('locked', True)
        response_s01_exists = 'S01' in response_stages
        
        logger.info(f"返回响应数据: S00状态={response_s00_status}, S01存在={response_s01_exists}, S01锁定={response_s01_locked}")
        
        return ApiResponse(
            code=0,
            msg="更新成功",
            data={
                "progress_percentage": construction.progress_percentage,
                "stages": response_stages
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新阶段状态失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新失败")


@router.put("/stage-calibrate")
async def calibrate_stage_time(
    request: CalibrateStageRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """阶段时间校准（FR-015）；校准时间需晚于开工日期"""
    try:
        result = await db.execute(select(Construction).where(Construction.user_id == user_id))
        construction = result.scalar_one_or_none()
        if not construction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未设置开工日期")

        stage_key = normalize_stage_key(request.stage)
        if stage_key not in STAGE_ORDER:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效阶段")

        start_date = construction.start_date
        if not start_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未设置开工日期")
        start_date_val = start_date.date() if hasattr(start_date, "date") else start_date

        stages = construction.stages or {}
        if stage_key not in stages:
            stages[stage_key] = {"status": "pending", "sequence": STAGE_ORDER.index(stage_key) + 1}

        if request.manual_start_date:
            d = request.manual_start_date.date() if hasattr(request.manual_start_date, "date") else request.manual_start_date
            if d < start_date_val:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="校准时间需晚于开工日期，请重新选择")
            stages[stage_key]["start_date"] = request.manual_start_date
        if request.manual_acceptance_date:
            d = request.manual_acceptance_date.date() if hasattr(request.manual_acceptance_date, "date") else request.manual_acceptance_date
            if d < start_date_val:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="校准时间需晚于开工日期，请重新选择")
            stages[stage_key]["acceptance_date"] = request.manual_acceptance_date

        construction.stages = stages
        await db.commit()
        await db.refresh(construction)
        return ApiResponse(code=0, msg="时间校准成功，提醒同步更新", data={"stages": _serialize_stages_with_lock(construction.stages or {})})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"校准失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="校准失败")


@router.get("/reminder-schedule")
async def get_reminder_schedule(
    date: str = Query(..., description="YYYY-MM-DD，查询该日应触达的提醒"),
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取提醒计划（FR-029/FR-030）：供定时 worker 或前端查询「某日应发送的施工/验收提醒」。
    返回当前用户在该日应收到的阶段开始提醒、验收提醒列表。
    """
    try:
        try:
            query_date = date_type.fromisoformat(date)
        except ValueError:
            raise HTTPException(status_code=400, detail="date 格式为 YYYY-MM-DD")
        result = await db.execute(select(Construction).where(Construction.user_id == user_id))
        construction = result.scalar_one_or_none()
        if not construction or not construction.stages:
            return ApiResponse(code=0, msg="success", data={"list": []})
        settings_result = await db.execute(select(UserSetting).where(UserSetting.user_id == user_id))
        user_setting = settings_result.scalar_one_or_none()
        n_days = (user_setting.reminder_days_before or 3) if user_setting else 3
        if user_setting and not user_setting.notify_progress:
            n_days = 0
        reminders = []
        stages = construction.stages or {}
        for stage_key in STAGE_ORDER:
            s = stages.get(stage_key)
            if not s:
                continue
            start_d = s.get("start_date")
            end_d = s.get("end_date")
            if start_d:
                if hasattr(start_d, "date"):
                    start_d = start_d.date()
                elif isinstance(start_d, str):
                    start_d = date_type.fromisoformat(start_d[:10])
                else:
                    continue
                target = query_date + timedelta(days=n_days)
                if start_d == target and (not user_setting or user_setting.notify_progress):
                    reminders.append({
                        "stage": stage_key,
                        "event_type": "stage_start",
                        "planned_date": str(start_d),
                        "reminder_days_before": n_days,
                    })
            if end_d and (not user_setting or user_setting.notify_acceptance):
                if hasattr(end_d, "date"):
                    end_d = end_d.date()
                elif isinstance(end_d, str):
                    end_d = date_type.fromisoformat(end_d[:10])
                else:
                    continue
                target = query_date + timedelta(days=n_days)
                if end_d == target:
                    reminders.append({
                        "stage": stage_key,
                        "event_type": "stage_acceptance",
                        "planned_date": str(end_d),
                        "reminder_days_before": n_days,
                    })
        return ApiResponse(code=0, msg="success", data={"list": reminders, "date": date})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取提醒计划失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取失败")


@router.delete("/schedule")
async def reset_schedule(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """重置施工进度"""
    try:
        result = await db.execute(select(Construction).where(Construction.user_id == user_id))
        construction = result.scalar_one_or_none()
        if construction:
            await db.delete(construction)
            await db.commit()
        return ApiResponse(code=0, msg="重置成功", data=None)
    except Exception as e:
        logger.error(f"重置失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="重置失败")

"""
装修决策Agent - 施工进度管理API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

from app.core.database import get_db
from app.core.config import settings
from app.models import Construction, User
from app.schemas import (
    StartDateRequest, UpdateStageStatusRequest, ConstructionResponse, ApiResponse
)

router = APIRouter(prefix="/constructions", tags=["施工进度"])
logger = logging.getLogger(__name__)


def calculate_construction_schedule(start_date: datetime) -> Dict[str, Dict]:
    """
    计算施工进度计划

    Args:
        start_date: 开工日期

    Returns:
        阶段信息字典
    """
    stages = {}
    current_date = start_date

    stage_order = [
        "plumbing",      # 水电 10天
        "carpentry",     # 泥木 20天
        "painting",      # 油漆 10天
        "flooring",      # 地板 5天
        "soft_furnishing"  # 软装 6天
    ]

    stage_duration = settings.STAGE_DURATION

    for stage in stage_order:
        duration = stage_duration.get(stage, 0)
        end_date = current_date + timedelta(days=duration - 1)

        stages[stage] = {
            "status": "pending",
            "start_date": current_date,
            "end_date": end_date,
            "duration": duration,
            "sequence": stage_order.index(stage) + 1
        }

        current_date = end_date + timedelta(days=1)

    estimated_end_date = current_date - timedelta(days=1)

    return {
        "stages": stages,
        "estimated_end_date": estimated_end_date
    }


def calculate_progress(stages: Dict) -> int:
    """
    计算整体进度百分比

    Args:
        stages: 阶段信息字典

    Returns:
        进度百分比（0-100）
    """
    total_duration = sum(s.get("duration", 0) for s in stages.values())
    completed_duration = 0

    for stage in stages.values():
        if stage.get("status") == "completed":
            completed_duration += stage.get("duration", 0)
        elif stage.get("status") == "in_progress":
            # 进行中的阶段按50%计算
            completed_duration += stage.get("duration", 0) * 0.5

    if total_duration == 0:
        return 0

    progress = int((completed_duration / total_duration) * 100)
    return min(progress, 100)


@router.get("/schedule", response_model=ConstructionResponse)
async def get_construction_schedule(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取施工进度计划

    Args:
        user_id: 用户ID
        db: 数据库会话

    Returns:
        施工进度信息
    """
    try:
        result = await db.execute(
            select(Construction)
            .where(Construction.user_id == user_id)
        )
        construction = result.scalar_one_or_none()

        if not construction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未设置开工日期"
            )

        # 计算延期天数
        is_delayed = False
        delay_days = 0

        if construction.start_date:
            today = datetime.now().date()
            if construction.estimated_end_date:
                if today > construction.estimated_end_date.date():
                    is_delayed = True
                    delay_days = (today - construction.estimated_end_date.date()).days

        return ConstructionResponse(
            id=construction.id,
            start_date=construction.start_date,
            estimated_end_date=construction.estimated_end_date,
            actual_end_date=construction.actual_end_date,
            progress_percentage=construction.progress_percentage,
            is_delayed=is_delayed,
            delay_days=delay_days,
            stages=construction.stages or {},
            notes=construction.notes
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取施工进度失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取进度失败"
        )


@router.post("/start-date")
async def set_start_date(
    user_id: int,
    request: StartDateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    设置开工日期

    Args:
        user_id: 用户ID
        request: 开工日期请求
        db: 数据库会话

    Returns:
        设置结果
    """
    try:
        # 验证日期（不能早于今天）
        if request.start_date.date() < datetime.now().date():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开工日期不能早于今天"
            )

        # 查找或创建施工进度记录
        result = await db.execute(
            select(Construction)
            .where(Construction.user_id == user_id)
        )
        construction = result.scalar_one_or_none()

        if not construction:
            # 创建新记录
            construction = Construction(user_id=user_id)
            db.add(construction)
            await db.flush()

        # 更新开工日期
        construction.start_date = request.start_date

        # 计算进度计划
        schedule = calculate_construction_schedule(request.start_date)
        construction.stages = schedule["stages"]
        construction.estimated_end_date = schedule["estimated_end_date"]
        construction.progress_percentage = 0
        construction.is_delayed = False
        construction.delay_days = 0

        await db.commit()
        await db.refresh(construction)

        logger.info(f"设置开工日期: {user_id}, 日期: {request.start_date}")

        return ApiResponse(
            code=0,
            msg="设置成功",
            data={
                "id": construction.id,
                "start_date": construction.start_date.isoformat(),
                "estimated_end_date": construction.estimated_end_date.isoformat(),
                "stages": construction.stages
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"设置开工日期失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="设置失败"
        )


@router.put("/stage-status")
async def update_stage_status(
    user_id: int,
    request: UpdateStageStatusRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    更新施工阶段状态

    Args:
        user_id: 用户ID
        request: 状态更新请求
        db: 数据库会话

    Returns:
        更新结果
    """
    try:
        # 查找施工进度记录
        result = await db.execute(
            select(Construction)
            .where(Construction.user_id == user_id)
        )
        construction = result.scalar_one_or_none()

        if not construction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未设置开工日期"
            )

        stages = construction.stages or {}
        stage_key = request.stage.value

        if stage_key not in stages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"阶段 {stage_key} 不存在"
            )

        # 更新阶段状态
        stages[stage_key]["status"] = request.status.value

        # 如果设置为已完成，需要重新计算后续阶段的时间
        if request.status.value == "completed":
            # 找到下一个阶段，调整其开始时间
            stage_order = ["plumbing", "carpentry", "painting", "flooring", "soft_furnishing"]
            current_index = stage_order.index(stage_key)

            if current_index < len(stage_order) - 1:
                next_stage_key = stage_order[current_index + 1]
                current_stage = stages[stage_key]
                next_start_date = current_stage["end_date"] + timedelta(days=1)

                # 重新计算后续所有阶段
                for i in range(current_index + 1, len(stage_order)):
                    next_key = stage_order[i]
                    next_stage = stages[next_key]
                    duration = settings.STAGE_DURATION.get(next_key, 0)
                    next_stage["start_date"] = next_start_date
                    next_stage["end_date"] = next_start_date + timedelta(days=duration - 1)
                    next_start_date = next_stage["end_date"] + timedelta(days=1)

                # 更新预计完工日期
                last_stage_key = stage_order[-1]
                construction.estimated_end_date = stages[last_stage_key]["end_date"]

        # 重新计算整体进度
        construction.stages = stages
        construction.progress_percentage = calculate_progress(stages)

        # 检查是否全部完成
        all_completed = all(
            s.get("status") == "completed"
            for s in stages.values()
        )
        if all_completed and not construction.actual_end_date:
            construction.actual_end_date = datetime.now()

        await db.commit()
        await db.refresh(construction)

        logger.info(f"更新阶段状态: {user_id}, 阶段: {stage_key}, 状态: {request.status.value}")

        return ApiResponse(
            code=0,
            msg="更新成功",
            data={
                "progress_percentage": construction.progress_percentage,
                "estimated_end_date": construction.estimated_end_date.isoformat(),
                "stages": construction.stages
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新阶段状态失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败"
        )


@router.delete("/schedule")
async def reset_schedule(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    重置施工进度（删除记录）

    Args:
        user_id: 用户ID
        db: 数据库会话

    Returns:
        重置结果
    """
    try:
        result = await db.execute(
            select(Construction)
            .where(Construction.user_id == user_id)
        )
        construction = result.scalar_one_or_none()

        if construction:
            await db.delete(construction)
            await db.commit()
            logger.info(f"重置施工进度: {user_id}")

        return ApiResponse(
            code=0,
            msg="重置成功",
            data=None
        )

    except Exception as e:
        logger.error(f"重置施工进度失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="重置失败"
        )

"""
装修决策Agent - 验收分析API (P30)
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from typing import List, Optional

from app.core.database import get_db, AsyncSessionLocal
from sqlalchemy.orm.attributes import flag_modified
from app.core.security import get_user_id, _resolve_user_id
from app.core.config import settings
from app.models import AcceptanceAnalysis
from app.services import ocr_service, risk_analyzer_service
from app.api.v1.quotes import upload_file_to_oss
from app.services.oss_service import oss_service
from app.core.config import settings
from app.schemas import ApiResponse
from app.services.message_service import create_message

router = APIRouter(prefix="/acceptance", tags=["验收分析"])
import logging
logger = logging.getLogger(__name__)

STAGES = ["S01", "S02", "S03", "S04", "S05"]
STAGES_LEGACY = ["plumbing", "carpentry", "painting", "flooring", "soft_furnishing", "woodwork", "installation", "material"]


class AnalyzeRequest(BaseModel):
    stage: str
    file_urls: List[str]


class RecheckRequest(BaseModel):
    rectified_photo_urls: List[str] = Field(default_factory=list, max_length=5)


class MarkPassedRequest(BaseModel):
    """用户主动标记为已通过（仅限rectify_exhausted状态，低/中风险）"""
    confirm_photo_urls: Optional[List[str]] = Field(None, description="说明照片（至少1张）")
    confirm_note: str = Field(..., min_length=20, max_length=500, description="说明文字（≥20字）")


@router.post("/upload-photo")
async def upload_acceptance_photo(
    request: Request,
    file: UploadFile = File(...),
    access_token: Optional[str] = Form(None),
    user_id_form: Optional[str] = Form(None),
):
    """上传单张验收照片。微信 uploadFile 可能不传 header/query，支持从 formData 读取 access_token、user_id"""
    user_id = _resolve_user_id(request, form_token=access_token, form_user_id=user_id_form)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    try:
        if file.size and file.size > (settings.MAX_UPLOAD_SIZE or 10 * 1024 * 1024):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件过大")
        ext = (file.filename or "").split(".")[-1].lower() if file.filename else "jpg"
        if ext not in (settings.ALLOWED_FILE_TYPES or ["pdf", "jpg", "jpeg", "png"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持图片格式")
        # 上传到OSS（统一使用OSS服务，验收照片使用照片bucket，生命周期1年）
        object_key = upload_file_to_oss(file, "acceptance", user_id, is_photo=True)
        # 返回 file_url（签名 URL）供前端直接展示；object_key 供 analyze 使用
        file_url = oss_service.sign_url_for_key(object_key, expires=86400)  # 24h 内可展示
        return ApiResponse(code=0, msg="success", data={"object_key": object_key, "file_url": file_url})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传验收照片失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="上传失败")


@router.post("/analyze")
async def analyze_acceptance(
    request: AnalyzeRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """根据已上传的照片URL进行验收分析（前端先调用 upload-photo 上传获取URL）"""
    try:
        if request.stage not in STAGES and request.stage not in STAGES_LEGACY:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的阶段")
        file_urls = [u for u in (request.file_urls or []) if u][:9]
        if not file_urls:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请上传1-9张照片")

        from app.services.oss_service import oss_service
        ocr_texts = []
        for url_or_key in file_urls:
            try:
                # 支持 object_key 或旧版公网 URL：object_key 需先换为临时签名 URL
                fetch_url = oss_service.sign_url_for_key(url_or_key, expires=3600) if not url_or_key.startswith("http") else url_or_key
                ocr_result = await ocr_service.recognize_general_text(fetch_url)
                text = ocr_result.get("text", "") if ocr_result else ""
                ocr_texts.append(text)
            except Exception:
                ocr_texts.append("")

        analysis_result = await risk_analyzer_service.analyze_acceptance(request.stage, ocr_texts)
        issues = analysis_result.get("issues", [])
        suggestions = analysis_result.get("suggestions", [])
        severity = analysis_result.get("severity", "pass")
        summary = analysis_result.get("summary", "")
        result_status = "passed" if severity == "pass" else "need_rectify"

        record = AcceptanceAnalysis(
            user_id=user_id,
            stage=request.stage,
            file_urls=file_urls,
            result_json=analysis_result,
            issues=issues,
            suggestions=suggestions,
            severity=severity,
            status="completed",
            result_status=result_status
        )
        db.add(record)
        await db.flush()
        await create_message(
            db, user_id,
            category="acceptance",
            title="验收报告已生成",
            content=summary or f"阶段{request.stage}验收分析完成",
            summary=summary,
            link_url=f"/pages/acceptance/index?id={record.id}",
        )
        await db.commit()
        await db.refresh(record)

        return ApiResponse(
            code=0,
            msg="success",
            data={
                "id": record.id,
                "stage": record.stage,
                "file_urls": file_urls,
                "issues": issues,
                "suggestions": suggestions,
                "severity": severity,
                "summary": summary,
                "created_at": record.created_at.isoformat() if record.created_at else None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验收分析失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="分析失败")


@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取验收分析结果"""
    try:
        result = await db.execute(
            select(AcceptanceAnalysis).where(
                AcceptanceAnalysis.id == analysis_id,
                AcceptanceAnalysis.user_id == user_id
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在")
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "id": record.id,
                "stage": record.stage,
                "file_urls": record.file_urls or [],
                "issues": record.issues or [],
                "suggestions": record.suggestions or [],
                "severity": record.severity,
                "result_status": getattr(record, "result_status", None) or "completed",
                "result_json": record.result_json,
                "recheck_count": getattr(record, "recheck_count", 0),
                "rectified_photo_urls": getattr(record, "rectified_photo_urls", None),
                "created_at": record.created_at.isoformat() if record.created_at else None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取验收分析失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取失败")


@router.post("/{analysis_id}/mark-rectify")
async def mark_acceptance_rectify(
    analysis_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """标记整改（FR-025）：阶段状态更新为待整改"""
    try:
        result = await db.execute(
            select(AcceptanceAnalysis).where(
                AcceptanceAnalysis.id == analysis_id,
                AcceptanceAnalysis.user_id == user_id
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")
        record.result_status = "need_rectify"
        await db.commit()
        return ApiResponse(code=0, msg="success", data={"result_status": "need_rectify"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记整改失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败")


# 阶段 key 到 Construction 后端 S00-S05 的映射
_ACCEPTANCE_STAGE_TO_S = {"material": "S00", "plumbing": "S01", "carpentry": "S02", "woodwork": "S03", "painting": "S04", "installation": "S05", "flooring": "S02", "soft_furnishing": "S05"}
for _s in ["S00", "S01", "S02", "S03", "S04", "S05"]:
    _ACCEPTANCE_STAGE_TO_S[_s] = _s


async def _run_recheck_analysis(analysis_id: int, rectified_urls: list):
    """后台任务：对整改照片进行 AI 复检分析，更新验收记录；复检3次后仍不合格则自动置阶段为 rectify_exhausted 以允许进入下一阶段"""
    from app.services.oss_service import oss_service
    from app.models import Construction
    import copy
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(AcceptanceAnalysis).where(AcceptanceAnalysis.id == analysis_id)
            )
            record = result.scalar_one_or_none()
            if not record or not rectified_urls:
                return
            stage = record.stage or "plumbing"
            ocr_texts = []
            for url_or_key in rectified_urls[:5]:
                try:
                    fetch_url = oss_service.sign_url_for_key(url_or_key, expires=3600) if not (url_or_key or "").startswith("http") else url_or_key
                    ocr_result = await ocr_service.recognize_general_text(fetch_url)
                    text = ocr_result.get("text", "") if ocr_result else ""
                    ocr_texts.append(text)
                except Exception:
                    ocr_texts.append("")
            analysis_result = await risk_analyzer_service.analyze_acceptance(stage, ocr_texts)
            issues = analysis_result.get("issues", [])
            suggestions = analysis_result.get("suggestions", [])
            severity = analysis_result.get("severity", "pass")
            result_status = "passed" if severity == "pass" else "need_rectify"
            record.result_json = analysis_result
            record.issues = issues
            record.suggestions = suggestions
            record.severity = severity
            record.result_status = result_status
            await db.commit()
            await db.refresh(record)
            recheck_count = getattr(record, "recheck_count", 0) or 0
            if recheck_count >= RECHECK_MAX_COUNT and result_status == "need_rectify":
                stage_s = _ACCEPTANCE_STAGE_TO_S.get(stage, stage) if stage else "S01"
                const_res = await db.execute(select(Construction).where(Construction.user_id == record.user_id))
                construction = const_res.scalar_one_or_none()
                if construction and construction.stages:
                    stages_raw = construction.stages if isinstance(construction.stages, dict) else {}
                    if isinstance(construction.stages, str):
                        import json
                        try:
                            stages_raw = json.loads(construction.stages)
                        except Exception:
                            stages_raw = {}
                    stages = copy.deepcopy(stages_raw)
                    if stage_s in stages and isinstance(stages[stage_s], dict):
                        stages[stage_s]["status"] = "rectify_exhausted"
                        construction.stages = stages
                        flag_modified(construction, "stages")
                        await db.commit()
                        logger.info(f"复检次数已用完且未通过: analysis_id={analysis_id}, 阶段{stage_s}置为rectify_exhausted")
            logger.info(f"复检分析完成: analysis_id={analysis_id}, result_status={result_status}")
    except Exception as e:
        logger.error(f"复检分析失败: analysis_id={analysis_id}, err={e}", exc_info=True)


RECHECK_MAX_COUNT = 3

@router.post("/{analysis_id}/request-recheck")
async def request_recheck(
    analysis_id: int,
    body: RecheckRequest,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """申请复检（FR-025）：上传整改后照片，触发待复检状态，后台自动进行 AI 复检分析；最多3次，超限拒绝"""
    from datetime import datetime
    try:
        result = await db.execute(
            select(AcceptanceAnalysis).where(
                AcceptanceAnalysis.id == analysis_id,
                AcceptanceAnalysis.user_id == user_id
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")
        current_count = getattr(record, "recheck_count", 0) or 0
        if current_count >= RECHECK_MAX_COUNT:
            raise HTTPException(status_code=400, detail=f"复检次数已达上限（最多{RECHECK_MAX_COUNT}次），可进入下一阶段或咨询AI监理")
        record.result_status = "pending_recheck"
        record.recheck_count = getattr(record, "recheck_count", 0) + 1
        rectified_urls = []
        if body.rectified_photo_urls:
            rectified_urls = body.rectified_photo_urls[:5]
            record.rectified_photo_urls = rectified_urls
            record.rectified_at = datetime.now()
        await db.commit()
        await db.refresh(record)
        if rectified_urls:
            background_tasks.add_task(_run_recheck_analysis, analysis_id, rectified_urls)
        return ApiResponse(code=0, msg="success", data={"result_status": "pending_recheck", "recheck_count": record.recheck_count})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"申请复检失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败")


@router.post("/{analysis_id}/mark-passed")
async def mark_acceptance_passed(
    analysis_id: int,
    body: MarkPassedRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """用户主动标记为已通过（仅限rectify_exhausted状态，低/中风险问题）"""
    from app.models import Construction
    import copy
    try:
        # 1. 获取验收记录
        result = await db.execute(
            select(AcceptanceAnalysis).where(
                AcceptanceAnalysis.id == analysis_id,
                AcceptanceAnalysis.user_id == user_id
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        # 2. 检查风险等级：仅允许低/中风险
        severity = record.severity or ""
        if severity == "high":
            raise HTTPException(
                status_code=400,
                detail="高风险问题必须通过申诉流程，无法直接标记为已通过"
            )
        if severity not in ("low", "mid", "warning", "pass"):
            raise HTTPException(
                status_code=400,
                detail="当前状态不允许标记为已通过"
            )
        
        # 3. 检查Construction阶段状态：必须是rectify_exhausted
        stage = record.stage or "plumbing"
        stage_s = _ACCEPTANCE_STAGE_TO_S.get(stage, stage) if stage else "S01"
        const_res = await db.execute(
            select(Construction).where(Construction.user_id == user_id)
        )
        construction = const_res.scalar_one_or_none()
        if not construction:
            raise HTTPException(status_code=404, detail="施工记录不存在")
        
        stages_raw = construction.stages if isinstance(construction.stages, dict) else {}
        if isinstance(construction.stages, str):
            import json
            try:
                stages_raw = json.loads(construction.stages)
            except Exception:
                stages_raw = {}
        
        stage_info = stages_raw.get(stage_s) or {}
        if isinstance(stage_info, str):
            import json
            try:
                stage_info = json.loads(stage_info)
            except Exception:
                stage_info = {}
        
        current_status = stage_info.get("status") if isinstance(stage_info, dict) else ""
        if current_status != "rectify_exhausted":
            raise HTTPException(
                status_code=400,
                detail="仅当复检次数已用完且未通过时，可主动标记为已通过"
            )
        
        # 4. 验证必填项
        if not body.confirm_note or len(body.confirm_note.strip()) < 20:
            raise HTTPException(status_code=400, detail="说明文字至少20字")
        
        confirm_photos = body.confirm_photo_urls or []
        if len(confirm_photos) < 1:
            raise HTTPException(status_code=400, detail="请上传至少1张说明照片")
        
        # 5. 更新验收记录
        record.result_status = "passed"
        record.severity = "pass"  # 标记为通过
        # 保存用户确认信息到result_json
        if not record.result_json:
            record.result_json = {}
        if isinstance(record.result_json, dict):
            record.result_json["user_confirmed"] = True
            record.result_json["confirm_note"] = body.confirm_note
            record.result_json["confirm_photo_urls"] = confirm_photos
            record.result_json["confirmed_at"] = datetime.now().isoformat()
        
        # 6. 更新Construction阶段状态
        stages = copy.deepcopy(stages_raw)
        if stage_s in stages and isinstance(stages[stage_s], dict):
            stages[stage_s]["status"] = "passed"
            stages[stage_s]["user_confirmed"] = True
            construction.stages = stages
            flag_modified(construction, "stages")
        
        await db.commit()
        await db.refresh(record)
        
        logger.info(f"用户主动标记为已通过: analysis_id={analysis_id}, stage={stage_s}, severity={severity}")
        
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "result_status": "passed",
                "stage_status": "passed",
                "message": "已标记为已通过，可进入下一阶段"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记为已通过失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败")


@router.get("")
async def list_analyses(
    user_id: int = Depends(get_user_id),
    stage: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """获取验收分析列表"""
    try:
        offset = (page - 1) * page_size
        stmt = select(AcceptanceAnalysis).where(
            AcceptanceAnalysis.user_id == user_id,
            AcceptanceAnalysis.deleted_at.is_(None),
        )
        if stage:
            stmt = stmt.where(AcceptanceAnalysis.stage == stage)
        stmt = stmt.order_by(AcceptanceAnalysis.created_at.desc()).limit(page_size).offset(offset)
        result = await db.execute(stmt)
        records = result.scalars().all()
        count_stmt = select(func.count(AcceptanceAnalysis.id)).where(
            AcceptanceAnalysis.user_id == user_id,
            AcceptanceAnalysis.deleted_at.is_(None)
        )
        if stage:
            count_stmt = count_stmt.where(AcceptanceAnalysis.stage == stage)
        total = (await db.execute(count_stmt)).scalar() or 0

        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": [
                    {
                        "id": r.id,
                        "stage": r.stage,
                        "severity": r.severity,
                        "result_status": getattr(r, "result_status", None) or "completed",
                        "created_at": r.created_at.isoformat() if r.created_at else None
                    }
                    for r in records
                ],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        )
    except Exception as e:
        logger.error(f"获取验收分析列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取失败")

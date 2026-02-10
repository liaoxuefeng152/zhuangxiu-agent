"""
装修决策Agent - 验收分析API (P30)
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_user_id
from app.core.config import settings
from app.models import AcceptanceAnalysis
from app.services import ocr_service, risk_analyzer_service
from app.api.v1.quotes import upload_file_to_oss
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


@router.post("/upload-photo")
async def upload_acceptance_photo(
    user_id: int = Depends(get_user_id),
    file: UploadFile = File(...)
):
    """上传单张验收照片，返回URL供 analyze 使用"""
    try:
        if file.size and file.size > (settings.MAX_UPLOAD_SIZE or 10 * 1024 * 1024):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件过大")
        ext = (file.filename or "").split(".")[-1].lower() if file.filename else "jpg"
        if ext not in (settings.ALLOWED_FILE_TYPES or ["pdf", "jpg", "jpeg", "png"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持图片格式")
        url = upload_file_to_oss(file, "acceptance")
        return ApiResponse(code=0, msg="success", data={"file_url": url})
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

        ocr_texts = []
        for url in file_urls:
            try:
                ocr_result = await ocr_service.recognize_general_text(url)
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


@router.post("/{analysis_id}/request-recheck")
async def request_recheck(
    analysis_id: int,
    body: RecheckRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """申请复检（FR-025）：上传整改后照片，触发待复检状态"""
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
        record.result_status = "pending_recheck"
        record.recheck_count = getattr(record, "recheck_count", 0) + 1
        if body.rectified_photo_urls:
            record.rectified_photo_urls = body.rectified_photo_urls[:5]
            record.rectified_at = datetime.now()
        await db.commit()
        await db.refresh(record)
        return ApiResponse(code=0, msg="success", data={"result_status": "pending_recheck", "recheck_count": record.recheck_count})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"申请复检失败: {e}", exc_info=True)
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

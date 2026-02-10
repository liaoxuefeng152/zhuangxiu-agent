"""
装修决策Agent - 验收申诉 (P30 FR-026) 与特殊申请 (P09 FR-016)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import AcceptanceAppeal, AcceptanceAnalysis, SpecialApplication
from app.schemas import ApiResponse

router = APIRouter(prefix="/appeals", tags=["验收申诉与特殊申请"])
logger = logging.getLogger(__name__)


class AppealCreateRequest(BaseModel):
    reason: str = Field(..., min_length=1)
    images: List[str] = Field(default_factory=list, max_length=3)


class SpecialApplicationRequest(BaseModel):
    application_type: str = Field(..., description="exemption | dispute_appeal")
    stage: Optional[str] = None
    content: str = Field(..., min_length=10)
    images: List[str] = Field(default_factory=list, max_length=3)


@router.post("/acceptance/{analysis_id}")
async def create_acceptance_appeal(
    analysis_id: int,
    request: AppealCreateRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """提交验收申诉（FR-026）"""
    try:
        result = await db.execute(
            select(AcceptanceAnalysis).where(
                AcceptanceAnalysis.id == analysis_id,
                AcceptanceAnalysis.user_id == user_id
            )
        )
        analysis = result.scalar_one_or_none()
        if not analysis:
            raise HTTPException(status_code=404, detail="验收记录不存在")

        appeal = AcceptanceAppeal(
            user_id=user_id,
            acceptance_analysis_id=analysis_id,
            stage=analysis.stage or "",
            reason=request.reason,
            images=request.images or None,
            status="pending"
        )
        db.add(appeal)
        await db.commit()
        await db.refresh(appeal)
        return ApiResponse(
            code=0,
            msg="申诉已提交，1-2个工作日审核",
            data={"id": appeal.id, "status": appeal.status}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提交申诉失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="网络异常，请重试")


@router.get("/acceptance")
async def list_acceptance_appeals(
    user_id: int = Depends(get_user_id),
    analysis_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """申诉列表"""
    try:
        stmt = select(AcceptanceAppeal).where(AcceptanceAppeal.user_id == user_id)
        if analysis_id:
            stmt = stmt.where(AcceptanceAppeal.acceptance_analysis_id == analysis_id)
        stmt = stmt.order_by(AcceptanceAppeal.created_at.desc()).limit(page_size).offset((page - 1) * page_size)
        result = await db.execute(stmt)
        rows = result.scalars().all()
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": [
                    {
                        "id": r.id,
                        "acceptance_analysis_id": r.acceptance_analysis_id,
                        "stage": r.stage,
                        "reason": r.reason,
                        "status": r.status,
                        "created_at": r.created_at.isoformat() if r.created_at else None
                    }
                    for r in rows
                ],
                "page": page,
                "page_size": page_size
            }
        )
    except Exception as e:
        logger.error(f"获取申诉列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取失败")


@router.post("/special")
async def create_special_application(
    request: SpecialApplicationRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """特殊申请（FR-016）：自主装修豁免 / 核对验收争议申诉"""
    try:
        if request.application_type not in ("exemption", "dispute_appeal"):
            raise HTTPException(status_code=400, detail="application_type 为 exemption 或 dispute_appeal")

        app = SpecialApplication(
            user_id=user_id,
            application_type=request.application_type,
            stage=request.stage,
            content=request.content,
            images=request.images or None,
            status="pending"
        )
        db.add(app)
        await db.commit()
        await db.refresh(app)
        return ApiResponse(
            code=0,
            msg="申请已提交，1-2个工作日审核",
            data={"id": app.id, "status": app.status}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提交特殊申请失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="网络异常，请稍后重试")


@router.get("/special")
async def list_special_applications(
    user_id: int = Depends(get_user_id),
    application_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """特殊申请列表"""
    try:
        stmt = select(SpecialApplication).where(SpecialApplication.user_id == user_id)
        if application_type:
            stmt = stmt.where(SpecialApplication.application_type == application_type)
        stmt = stmt.order_by(SpecialApplication.created_at.desc()).limit(page_size).offset((page - 1) * page_size)
        result = await db.execute(stmt)
        rows = result.scalars().all()
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": [
                    {
                        "id": r.id,
                        "application_type": r.application_type,
                        "stage": r.stage,
                        "content": r.content[:50] + "..." if r.content and len(r.content) > 50 else r.content,
                        "status": r.status,
                        "created_at": r.created_at.isoformat() if r.created_at else None
                    }
                    for r in rows
                ],
                "page": page,
                "page_size": page_size
            }
        )
    except Exception as e:
        logger.error(f"获取特殊申请列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取失败")

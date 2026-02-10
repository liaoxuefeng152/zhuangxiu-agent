"""
装修决策Agent - 数据管理API (P20/P21 批量删除、回收站、恢复)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import User, ConstructionPhoto, AcceptanceAnalysis
from app.schemas import ApiResponse

router = APIRouter(prefix="/users/data", tags=["数据管理"])
logger = logging.getLogger(__name__)

RECYCLE_DAYS = 7


class DataDeleteRequest(BaseModel):
    type: str  # photo, acceptance
    ids: List[int]


class DataRestoreRequest(BaseModel):
    type: str
    id: int


@router.post("/delete")
async def soft_delete_data(
    request: DataDeleteRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """软删除施工照片或验收记录（移入回收站）"""
    try:
        now = datetime.now()
        if request.type == "photo":
            await db.execute(
                update(ConstructionPhoto).where(
                    ConstructionPhoto.id.in_(request.ids),
                    ConstructionPhoto.user_id == user_id,
                ).values(deleted_at=now)
            )
        elif request.type == "acceptance":
            await db.execute(
                update(AcceptanceAnalysis).where(
                    AcceptanceAnalysis.id.in_(request.ids),
                    AcceptanceAnalysis.user_id == user_id,
                ).values(deleted_at=now)
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="type 仅支持 photo, acceptance")
        await db.commit()
        return ApiResponse(code=0, msg="已移入回收站", data={"count": len(request.ids)})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="操作失败")


@router.get("/recycle")
async def list_recycle(
    user_id: int = Depends(get_user_id),
    type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """回收站列表（仅会员7天内可恢复）"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_member:
            return ApiResponse(code=0, msg="success", data={"list": [], "member_only": True})
        cutoff = datetime.now() - timedelta(days=RECYCLE_DAYS)
        items = []
        if type in (None, "photo"):
            rows = await db.execute(
                select(ConstructionPhoto).where(
                    ConstructionPhoto.user_id == user_id,
                    ConstructionPhoto.deleted_at.isnot(None),
                    ConstructionPhoto.deleted_at >= cutoff,
                ).order_by(ConstructionPhoto.deleted_at.desc())
            )
            for r in rows.scalars().all():
                items.append({
                    "type": "photo",
                    "id": r.id,
                    "stage": r.stage,
                    "file_url": r.file_url,
                    "deleted_at": r.deleted_at.isoformat() if r.deleted_at else None,
                })
        if type in (None, "acceptance"):
            rows = await db.execute(
                select(AcceptanceAnalysis).where(
                    AcceptanceAnalysis.user_id == user_id,
                    AcceptanceAnalysis.deleted_at.isnot(None),
                    AcceptanceAnalysis.deleted_at >= cutoff,
                ).order_by(AcceptanceAnalysis.deleted_at.desc())
            )
            for r in rows.scalars().all():
                items.append({
                    "type": "acceptance",
                    "id": r.id,
                    "stage": r.stage,
                    "deleted_at": r.deleted_at.isoformat() if r.deleted_at else None,
                })
        return ApiResponse(code=0, msg="success", data={"list": items})
    except Exception as e:
        logger.error(f"获取回收站失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取失败")


@router.post("/restore")
async def restore_data(
    request: DataRestoreRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """从回收站恢复（仅会员，且删除在7天内）"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_member:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅会员支持数据恢复")
        cutoff = datetime.now() - timedelta(days=RECYCLE_DAYS)
        if request.type == "photo":
            row = await db.execute(
                select(ConstructionPhoto).where(
                    ConstructionPhoto.id == request.id,
                    ConstructionPhoto.user_id == user_id,
                    ConstructionPhoto.deleted_at.isnot(None),
                    ConstructionPhoto.deleted_at >= cutoff,
                )
            )
            obj = row.scalar_one_or_none()
            if not obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在或已过期")
            obj.deleted_at = None
        elif request.type == "acceptance":
            row = await db.execute(
                select(AcceptanceAnalysis).where(
                    AcceptanceAnalysis.id == request.id,
                    AcceptanceAnalysis.user_id == user_id,
                    AcceptanceAnalysis.deleted_at.isnot(None),
                    AcceptanceAnalysis.deleted_at >= cutoff,
                )
            )
            obj = row.scalar_one_or_none()
            if not obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在或已过期")
            obj.deleted_at = None
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="type 仅支持 photo, acceptance")
        await db.commit()
        return ApiResponse(code=0, msg="已恢复", data=None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"恢复失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="操作失败")

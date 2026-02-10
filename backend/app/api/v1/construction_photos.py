"""
装修决策Agent - 施工照片API (P15/P17/P29)
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_user_id
from app.core.config import settings
from app.models import ConstructionPhoto
from app.schemas import ApiResponse
from app.api.v1.quotes import upload_file_to_oss

router = APIRouter(prefix="/construction-photos", tags=["施工照片"])
import logging
logger = logging.getLogger(__name__)

STAGES = getattr(settings, "STAGE_ORDER", None) or ["material", "plumbing", "carpentry", "woodwork", "painting", "installation"]


@router.post("/upload")
async def upload_photo(
    stage: str = Query(..., description="material|plumbing|carpentry|woodwork|painting|installation"),
    user_id: int = Depends(get_user_id),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """上传施工照片"""
    try:
        if stage not in STAGES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的阶段")
        if file.size and file.size > (settings.MAX_UPLOAD_SIZE or 10 * 1024 * 1024):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件过大")
        ext = (file.filename or "").split(".")[-1].lower() if file.filename else "jpg"
        if ext not in (settings.ALLOWED_FILE_TYPES or ["pdf", "jpg", "jpeg", "png"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持图片格式")

        file_url = upload_file_to_oss(file, "construction")
        photo = ConstructionPhoto(
            user_id=user_id,
            stage=stage,
            file_url=file_url,
            file_name=file.filename or "photo",
            is_read=False
        )
        db.add(photo)
        await db.commit()
        await db.refresh(photo)
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "id": photo.id,
                "stage": photo.stage,
                "file_url": photo.file_url,
                "file_name": photo.file_name,
                "created_at": photo.created_at.isoformat() if photo.created_at else None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传施工照片失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="上传失败")


@router.get("")
async def list_photos(
    stage: Optional[str] = Query(None),
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取施工照片列表，按阶段分组"""
    try:
        stmt = select(ConstructionPhoto).where(
            ConstructionPhoto.user_id == user_id,
            ConstructionPhoto.deleted_at.is_(None),
        )
        if stage:
            stmt = stmt.where(ConstructionPhoto.stage == stage)
        stmt = stmt.order_by(ConstructionPhoto.created_at.desc())
        result = await db.execute(stmt)
        photos = result.scalars().all()

        by_stage = {}
        for p in photos:
            if p.stage not in by_stage:
                by_stage[p.stage] = []
            by_stage[p.stage].append({
                "id": p.id,
                "file_url": p.file_url,
                "file_name": p.file_name,
                "is_read": p.is_read,
                "created_at": p.created_at.isoformat() if p.created_at else None
            })
        return ApiResponse(code=0, msg="success", data={"photos": by_stage, "list": [{"id": p.id, "stage": p.stage, "file_url": p.file_url, "file_name": p.file_name} for p in photos]})
    except Exception as e:
        logger.error(f"获取施工照片失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取失败")


@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """删除施工照片"""
    try:
        result = await db.execute(
            select(ConstructionPhoto).where(
                ConstructionPhoto.id == photo_id,
                ConstructionPhoto.user_id == user_id
            )
        )
        photo = result.scalar_one_or_none()
        if not photo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="照片不存在")
        await db.delete(photo)
        await db.commit()
        return ApiResponse(code=0, msg="success", data=None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除施工照片失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除失败")


class MovePhotoRequest(BaseModel):
    stage: str


@router.put("/{photo_id}/move")
async def move_photo(
    photo_id: int,
    request: MovePhotoRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """移动照片到其他阶段"""
    try:
        if request.stage not in STAGES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的阶段")
        result = await db.execute(
            select(ConstructionPhoto).where(
                ConstructionPhoto.id == photo_id,
                ConstructionPhoto.user_id == user_id
            )
        )
        photo = result.scalar_one_or_none()
        if not photo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="照片不存在")
        photo.stage = request.stage
        await db.commit()
        return ApiResponse(code=0, msg="success", data={"stage": photo.stage})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"移动照片失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="操作失败")

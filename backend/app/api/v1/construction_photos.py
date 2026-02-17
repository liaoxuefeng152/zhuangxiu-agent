"""
装修决策Agent - 施工照片API (P15/P17/P29)
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_user_id, get_user_id_for_upload
from app.models import ConstructionPhoto
from app.schemas import ApiResponse
from app.api.v1.quotes import upload_file_to_oss
from app.services.oss_service import oss_service

router = APIRouter(prefix="/construction-photos", tags=["施工照片"])
import logging
logger = logging.getLogger(__name__)

# 前端 P15 拍照页传入 material/plumbing 等 legacy 格式，需与之一致（勿用 STAGE_ORDER 的 S00-S05）
STAGES = ["material", "plumbing", "carpentry", "woodwork", "painting", "installation"]


class RegisterPhotoRequest(BaseModel):
    """直传 OSS 后注册照片记录"""
    stage: str = Field(..., description="material|plumbing|...")
    key: str = Field(..., description="OSS object key，如 construction/material/xxx.jpg")


class MovePhotoRequest(BaseModel):
    stage: str


@router.post("/register")
async def register_photo(
    request: RegisterPhotoRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    直传 OSS 完成后注册照片记录
    前端先拿 policy 直传 OSS，成功后调用此接口写入 DB
    """
    try:
        if request.stage not in STAGES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的阶段")
        if not request.key.startswith(f"construction/{request.stage}/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="key 路径不合法")

        # 施工照片使用照片 bucket；存 object_key，前端通过 /oss/sign-url 获取临时 URL
        object_key = request.key
        file_name = object_key.split("/")[-1] or "photo"

        photo = ConstructionPhoto(
            user_id=user_id,
            stage=request.stage,
            file_url=object_key,
            file_name=file_name,
            is_read=False,
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
                "created_at": photo.created_at.isoformat() if photo.created_at else None,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"注册照片失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="注册失败")


@router.post("/upload")
async def upload_photo(
    stage: str = Query(..., description="material|plumbing|carpentry|woodwork|painting|installation"),
    user_id: int = Depends(get_user_id_for_upload),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """上传施工照片（支持 query/form 鉴权，兼容微信 uploadFile）"""
    try:
        fsize = getattr(file, 'size', None)
        logger.info(f"施工照片上传: stage={stage}, user_id={user_id}, filename={getattr(file, 'filename', None)}, size={fsize}")
        if stage not in STAGES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的阶段")
        max_size = 20 * 1024 * 1024  # 施工照片放宽到 20MB（手机原图较大）
        if fsize is not None and fsize > max_size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"文件过大，最大{max_size // (1024*1024)}MB")
        if fsize is not None and fsize == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上传文件为空")
        # 微信小程序 tempFilePath 可能无扩展名，施工照片一律按 jpg 处理
        allowed = settings.ALLOWED_FILE_TYPES or ["pdf", "jpg", "jpeg", "png"]
        fname = file.filename or "photo.jpg"
        ext = (fname.split(".")[-1] or "jpg").lower()
        if ext not in allowed:
            ext = "jpg"

        # 上传到OSS（统一使用OSS服务，施工照片使用照片bucket，生命周期1年）
        file_url = upload_file_to_oss(file, "construction", user_id, is_photo=True)
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
        photo_list = []
        for p in photos:
            # 生成签名URL供前端预览使用
            signed_url = None
            if p.file_url:
                try:
                    signed_url = oss_service.sign_url_for_key(p.file_url, expires=3600)
                except Exception as e:
                    logger.warning(f"生成签名URL失败: {p.file_url}, 错误: {e}")
                    signed_url = p.file_url  # 回退到原始URL
            
            if p.stage not in by_stage:
                by_stage[p.stage] = []
            by_stage[p.stage].append({
                "id": p.id,
                "file_url": signed_url or p.file_url,  # 使用签名URL
                "url": signed_url or p.file_url,  # 添加url字段供前端使用
                "object_key": p.file_url,  # 保留原始object_key
                "file_name": p.file_name,
                "is_read": p.is_read,
                "created_at": p.created_at.isoformat() if p.created_at else None
            })
            
            photo_list.append({
                "id": p.id,
                "stage": p.stage,
                "file_url": signed_url or p.file_url,  # 使用签名URL
                "url": signed_url or p.file_url,  # 添加url字段供前端使用
                "object_key": p.file_url,  # 保留原始object_key
                "file_name": p.file_name
            })
            
        return ApiResponse(code=0, msg="success", data={"photos": by_stage, "list": photo_list})
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

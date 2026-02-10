"""
装修决策Agent - 消息中心API (P14)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
import logging
from typing import Optional
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import Message
from app.schemas import ApiResponse
from app.services.message_service import create_message

router = APIRouter(prefix="/messages", tags=["消息中心"])
logger = logging.getLogger(__name__)


class MessageCreateRequest(BaseModel):
    """创建消息（系统/业务侧写入施工提醒、报告通知等）"""
    category: str = Field(..., description="progress|report|system|acceptance|customer_service")
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=500)
    link_url: Optional[str] = Field(None, max_length=512)


@router.get("")
async def list_messages(
    user_id: int = Depends(get_user_id),
    category: Optional[str] = Query(None, description="system|progress|payment"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """获取消息列表"""
    try:
        offset = (page - 1) * page_size
        stmt = select(Message).where(Message.user_id == user_id)
        if category:
            stmt = stmt.where(Message.category == category)
        stmt = stmt.order_by(Message.created_at.desc()).limit(page_size).offset(offset)
        result = await db.execute(stmt)
        messages = result.scalars().all()

        count_stmt = select(func.count(Message.id)).where(Message.user_id == user_id)
        if category:
            count_stmt = count_stmt.where(Message.category == category)
        total = (await db.execute(count_stmt)).scalar() or 0

        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": [
                    {
                        "id": m.id,
                        "category": m.category,
                        "title": m.title,
                        "content": m.content,
                        "summary": m.summary,
                        "is_read": m.is_read,
                        "link_url": m.link_url,
                        "created_at": m.created_at.isoformat() if m.created_at else None
                    }
                    for m in messages
                ],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        )
    except Exception as e:
        logger.error(f"获取消息列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取消息失败")


@router.get("/unread-count")
async def get_unread_count(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取未读消息数量"""
    try:
        stmt = select(func.count(Message.id)).where(
            Message.user_id == user_id,
            Message.is_read == False
        )
        count = (await db.execute(stmt)).scalar() or 0
        return ApiResponse(code=0, msg="success", data={"count": count})
    except Exception as e:
        logger.error(f"获取未读数失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取失败")


@router.put("/{msg_id}/read")
async def mark_read(
    msg_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """标记单条消息已读"""
    try:
        result = await db.execute(
            select(Message).where(Message.id == msg_id, Message.user_id == user_id)
        )
        msg = result.scalar_one_or_none()
        if not msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")
        msg.is_read = True
        await db.commit()
        return ApiResponse(code=0, msg="success", data=None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记已读失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="操作失败")


@router.post("")
async def create_message_api(
    request: MessageCreateRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建一条消息（用于施工提醒、报告通知、系统通知等）"""
    try:
        if request.category not in ("progress", "report", "system", "acceptance", "customer_service"):
            raise HTTPException(status_code=400, detail="category 无效")
        msg = await create_message(
            db, user_id,
            category=request.category,
            title=request.title,
            content=request.content,
            summary=request.summary,
            link_url=request.link_url,
        )
        await db.commit()
        await db.refresh(msg)
        return ApiResponse(
            code=0,
            msg="success",
            data={"id": msg.id, "title": msg.title, "created_at": msg.created_at.isoformat() if msg.created_at else None}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建消息失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="创建失败")


@router.put("/read-all")
async def mark_all_read(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """一键已读"""
    try:
        stmt = update(Message).where(
            Message.user_id == user_id,
            Message.is_read == False
        ).values(is_read=True)
        await db.execute(stmt)
        await db.commit()
        return ApiResponse(code=0, msg="success", data=None)
    except Exception as e:
        logger.error(f"一键已读失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="操作失败")

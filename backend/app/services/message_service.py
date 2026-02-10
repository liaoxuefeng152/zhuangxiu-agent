"""
消息创建服务：供 API 与业务侧（验收完成、支付成功等）写入消息中心
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models import Message


async def create_message(
    db: AsyncSession,
    user_id: int,
    category: str,
    title: str,
    content: Optional[str] = None,
    summary: Optional[str] = None,
    link_url: Optional[str] = None,
) -> Message:
    """
    创建一条消息（施工提醒/报告通知/系统消息等）
    category: progress | report | system | acceptance | customer_service
    """
    msg = Message(
        user_id=user_id,
        category=category,
        title=title,
        content=content or "",
        summary=summary,
        link_url=link_url,
        is_read=False,
    )
    db.add(msg)
    await db.flush()
    return msg

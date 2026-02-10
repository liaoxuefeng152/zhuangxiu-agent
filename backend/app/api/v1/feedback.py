"""
装修决策Agent - 意见反馈API (P24)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import Feedback
from app.schemas import ApiResponse

router = APIRouter(prefix="/feedback", tags=["意见反馈"])
import logging
logger = logging.getLogger(__name__)


class FeedbackSubmitRequest(BaseModel):
    """反馈提交 (P22 支持反馈类型：AI验收认可/不认可/误判等)"""
    content: str
    images: Optional[List[str]] = None
    feedback_type: Optional[str] = "other"
    sub_type: Optional[str] = None


@router.post("")
async def submit_feedback(
    request: FeedbackSubmitRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """提交意见反馈"""
    try:
        content = (request.content or "").strip()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请输入反馈内容")
        fb = Feedback(
            user_id=user_id,
            content=content,
            images=request.images,
            status="pending",
            feedback_type=(request.feedback_type or "other")[:30],
            sub_type=(request.sub_type or "")[:30] if request.sub_type else None,
        )
        db.add(fb)
        await db.commit()
        await db.refresh(fb)
        return ApiResponse(
            code=0,
            msg="提交成功，感谢您的反馈",
            data={"id": fb.id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提交反馈失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="提交失败")

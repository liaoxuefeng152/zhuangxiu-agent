"""
装修决策Agent - AI监理咨询API (P36)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import (
    User,
    AcceptanceAnalysis,
    AIConsultSession,
    AIConsultMessage,
    AIConsultQuotaUsage,
)
from app.schemas import ApiResponse

router = APIRouter(prefix="/consultation", tags=["AI监理咨询"])
logger = logging.getLogger(__name__)

FREE_QUOTA_PER_MONTH = 3
AI_CONSULT_PRICE = 9.9
HUMAN_CONSULT_PRICE = 49


def _year_month() -> str:
    return datetime.now().strftime("%Y-%m")


class CreateSessionRequest(BaseModel):
    acceptance_analysis_id: Optional[int] = None
    stage: Optional[str] = None


class SendMessageRequest(BaseModel):
    session_id: int
    content: Optional[str] = None
    images: Optional[List[str]] = None


@router.get("/quota")
async def get_quota(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取AI咨询额度（免费用户本月剩余次数、是否会员）"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        is_member = user.is_member or False
        if is_member:
            return ApiResponse(
                code=0,
                msg="success",
                data={"is_member": True, "free_remaining": -1, "description": "会员无限次咨询"},
            )
        ym = _year_month()
        row = await db.execute(
            select(AIConsultQuotaUsage).where(
                AIConsultQuotaUsage.user_id == user_id,
                AIConsultQuotaUsage.year_month == ym,
            )
        )
        quota = row.scalar_one_or_none()
        used = quota.used_count if quota else 0
        remaining = max(0, FREE_QUOTA_PER_MONTH - used)
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "is_member": False,
                "free_remaining": remaining,
                "free_total": FREE_QUOTA_PER_MONTH,
                "description": f"本月剩余{remaining}次免费咨询",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取额度失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取失败")


@router.post("/session")
async def create_session(
    request: CreateSessionRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """创建咨询会话（携带验收报告上下文）"""
    try:
        session = AIConsultSession(
            user_id=user_id,
            acceptance_analysis_id=request.acceptance_analysis_id,
            stage=request.stage,
            status="active",
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "session_id": session.id,
                "acceptance_analysis_id": session.acceptance_analysis_id,
                "stage": session.stage,
            },
        )
    except Exception as e:
        logger.error(f"创建会话失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建失败")


@router.get("/session/{session_id}/context")
async def get_session_context(
    session_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取会话关联的验收报告上下文（P36 顶部展示）"""
    try:
        result = await db.execute(
            select(AIConsultSession).where(
                AIConsultSession.id == session_id,
                AIConsultSession.user_id == user_id,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
        if not session.acceptance_analysis_id:
            return ApiResponse(code=0, msg="success", data={"stage": session.stage, "issues": []})
        aa = await db.execute(
            select(AcceptanceAnalysis).where(
                AcceptanceAnalysis.id == session.acceptance_analysis_id,
                AcceptanceAnalysis.user_id == user_id,
            )
        )
        analysis = aa.scalar_one_or_none()
        if not analysis:
            return ApiResponse(code=0, msg="success", data={"stage": session.stage, "issues": []})
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "stage": analysis.stage or session.stage,
                "issues": analysis.issues or [],
                "acceptance_analysis_id": analysis.id,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取上下文失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取失败")


@router.post("/message")
async def send_message(
    request: SendMessageRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """发送用户消息并返回AI回复（模拟AI，实际可调LLM）"""
    try:
        result = await db.execute(
            select(AIConsultSession).where(
                AIConsultSession.id == request.session_id,
                AIConsultSession.user_id == user_id,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
        user_row = await db.execute(select(User).where(User.id == user_id))
        user = user_row.scalar_one_or_none()
        is_member = user and user.is_member
        if not is_member:
            ym = _year_month()
            quota_row = await db.execute(
                select(AIConsultQuotaUsage).where(
                    AIConsultQuotaUsage.user_id == user_id,
                    AIConsultQuotaUsage.year_month == ym,
                )
            )
            quota = quota_row.scalar_one_or_none()
            if not quota:
                quota = AIConsultQuotaUsage(user_id=user_id, year_month=ym, used_count=0)
                db.add(quota)
                await db.flush()
            if quota.used_count >= FREE_QUOTA_PER_MONTH:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="本月免费额度已用完，可购买单次咨询或升级会员",
                )
            quota.used_count += 1
        msg_user = AIConsultMessage(
            session_id=session.id,
            role="user",
            content=request.content,
            images=request.images,
        )
        db.add(msg_user)
        await db.flush()
        reply = "根据您当前的验收情况，建议先按规范整改后再复检。若问题较复杂，可转接人工监理获得更专业解答。"
        msg_ai = AIConsultMessage(
            session_id=session.id,
            role="assistant",
            content=reply,
        )
        db.add(msg_ai)
        await db.commit()
        await db.refresh(msg_ai)
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "user_message_id": msg_user.id,
                "assistant_message_id": msg_ai.id,
                "reply": reply,
                "suggest_transfer": False,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发送消息失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="发送失败")


@router.get("/session/{session_id}/messages")
async def list_messages(
    session_id: int,
    user_id: int = Depends(get_user_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取会话消息历史"""
    try:
        result = await db.execute(
            select(AIConsultSession).where(
                AIConsultSession.id == session_id,
                AIConsultSession.user_id == user_id,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
        offset = (page - 1) * page_size
        msgs = await db.execute(
            select(AIConsultMessage)
            .where(AIConsultMessage.session_id == session_id)
            .order_by(AIConsultMessage.id.asc())
            .limit(page_size)
            .offset(offset)
        )
        messages = msgs.scalars().all()
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": [
                    {
                        "id": m.id,
                        "role": m.role,
                        "content": m.content,
                        "images": m.images,
                        "created_at": m.created_at.isoformat() if m.created_at else None,
                    }
                    for m in messages
                ],
                "page": page,
                "page_size": page_size,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取消息列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取失败")


@router.post("/session/{session_id}/transfer-human")
async def transfer_human(
    session_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """转接人工监理（需付费或使用会员额度，此处仅标记会话为人工模式）"""
    try:
        result = await db.execute(
            select(AIConsultSession).where(
                AIConsultSession.id == session_id,
                AIConsultSession.user_id == user_id,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
        session.is_human = True
        session.human_started_at = datetime.now()
        session.paid_amount = HUMAN_CONSULT_PRICE
        await db.commit()
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "session_id": session.id,
                "is_human": True,
                "message": "已转接人工监理，请等待回复",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"转接人工失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="转接失败")


@router.get("/sessions")
async def list_sessions(
    user_id: int = Depends(get_user_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """咨询记录列表（按验收报告分组）"""
    try:
        offset = (page - 1) * page_size
        result = await db.execute(
            select(AIConsultSession)
            .where(AIConsultSession.user_id == user_id)
            .order_by(AIConsultSession.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        sessions = result.scalars().all()
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": [
                    {
                        "id": s.id,
                        "acceptance_analysis_id": s.acceptance_analysis_id,
                        "stage": s.stage,
                        "status": s.status,
                        "is_human": s.is_human,
                        "created_at": s.created_at.isoformat() if s.created_at else None,
                    }
                    for s in sessions
                ],
                "page": page,
                "page_size": page_size,
            },
        )
    except Exception as e:
        logger.error(f"获取会话列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取失败")

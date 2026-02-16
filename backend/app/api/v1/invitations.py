"""
装修决策Agent - 邀请系统API（V2.6.8新增）
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import logging
import uuid

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import User, InvitationRecord, FreeUnlockEntitlement
from app.schemas import (
    ApiResponse, InvitationStatus, EntitlementStatus, EntitlementType,
    CreateInvitationRequest, CreateInvitationResponse, CheckInvitationStatusResponse,
    FreeUnlockEntitlementResponse, UseFreeUnlockRequest, UseFreeUnlockResponse
)

router = APIRouter(prefix="/invitations", tags=["邀请系统"])
logger = logging.getLogger(__name__)

# 邀请奖励配置
INVITATION_REWARD_TYPE = "free_unlock"  # 邀请奖励类型
INVITATION_REWARD_EXPIRE_DAYS = 30  # 邀请奖励有效期（天）


@router.post("/create", response_model=CreateInvitationResponse)
async def create_invitation(
    request: CreateInvitationRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    创建邀请（V2.6.8新增）
    生成邀请码和邀请链接，用户可分享给好友
    """
    try:
        # 获取用户信息
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        # 确保用户有邀请码
        if not user.invitation_code:
            # 生成邀请码：INV + 用户ID（6位补零）
            user.invitation_code = f"INV{user.id:06d}"
            await db.commit()

        # 生成邀请链接（假设前端域名）
        base_url = "https://your-domain.com"  # TODO: 从配置中获取
        invitation_url = f"{base_url}/invite/{user.invitation_code}"

        # 生成邀请文案
        invitation_text = f"我在用【装修避坑管家】查公司、审报价合同，装修少踩坑。邀请你一起用～ 点击链接注册：{invitation_url}"

        return CreateInvitationResponse(
            invitation_code=user.invitation_code,
            invitation_url=invitation_url,
            invitation_text=invitation_text
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建邀请失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建邀请失败"
        )


@router.get("/status", response_model=CheckInvitationStatusResponse)
async def check_invitation_status(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    检查邀请状态（V2.6.8新增）
    获取用户的邀请记录和可用权益
    """
    try:
        # 获取邀请记录
        invitations_result = await db.execute(
            select(InvitationRecord)
            .where(InvitationRecord.inviter_id == user_id)
            .order_by(InvitationRecord.created_at.desc())
        )
        invitations = invitations_result.scalars().all()

        # 统计邀请数据
        total_invited = len(invitations)
        successful_invites = len([i for i in invitations if i.status == "accepted"])
        pending_invites = len([i for i in invitations if i.status == "pending"])

        # 获取可用权益
        entitlements_result = await db.execute(
            select(FreeUnlockEntitlement)
            .where(
                and_(
                    FreeUnlockEntitlement.user_id == user_id,
                    FreeUnlockEntitlement.status == "available",
                    or_(
                        FreeUnlockEntitlement.expires_at.is_(None),
                        FreeUnlockEntitlement.expires_at > datetime.now()
                    )
                )
            )
        )
        available_entitlements = len(entitlements_result.scalars().all())

        # 格式化邀请记录
        invitation_list = []
        for inv in invitations:
            # 获取被邀请人信息
            invitee_result = await db.execute(select(User).where(User.id == inv.invitee_id))
            invitee = invitee_result.scalar_one_or_none()

            invitation_list.append({
                "id": inv.id,
                "invitee_nickname": invitee.nickname if invitee else "未知用户",
                "invitee_phone": invitee.phone if invitee else None,
                "status": inv.status,
                "reward_granted": inv.reward_granted,
                "created_at": inv.created_at.isoformat() if inv.created_at else None
            })

        return CheckInvitationStatusResponse(
            total_invited=total_invited,
            successful_invites=successful_invites,
            pending_invites=pending_invites,
            available_entitlements=available_entitlements,
            invitations=invitation_list
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"检查邀请状态失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="检查邀请状态失败"
        )


@router.get("/entitlements", response_model=List[FreeUnlockEntitlementResponse])
async def get_free_unlock_entitlements(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取免费解锁权益列表（V2.6.8新增）
    """
    try:
        result = await db.execute(
            select(FreeUnlockEntitlement)
            .where(FreeUnlockEntitlement.user_id == user_id)
            .order_by(FreeUnlockEntitlement.created_at.desc())
        )
        entitlements = result.scalars().all()

        return [
            FreeUnlockEntitlementResponse(
                id=ent.id,
                entitlement_type=EntitlementType(ent.entitlement_type),
                report_type=ent.report_type,
                report_id=ent.report_id,
                status=EntitlementStatus(ent.status),
                expires_at=ent.expires_at,
                created_at=ent.created_at
            )
            for ent in entitlements
        ]

    except Exception as e:
        logger.error(f"获取免费解锁权益失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取免费解锁权益失败"
        )


@router.post("/use-free-unlock", response_model=UseFreeUnlockResponse)
async def use_free_unlock(
    request: UseFreeUnlockRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    使用免费解锁权益（V2.6.8新增）
    使用一个可用的免费解锁权益来解锁报告
    """
    try:
        # 查找可用的通用权益（未指定具体报告）
        result = await db.execute(
            select(FreeUnlockEntitlement)
            .where(
                and_(
                    FreeUnlockEntitlement.user_id == user_id,
                    FreeUnlockEntitlement.status == "available",
                    FreeUnlockEntitlement.report_type.is_(None),  # 通用权益
                    FreeUnlockEntitlement.report_id.is_(None),    # 通用权益
                    or_(
                        FreeUnlockEntitlement.expires_at.is_(None),
                        FreeUnlockEntitlement.expires_at > datetime.now()
                    )
                )
            )
            .order_by(FreeUnlockEntitlement.created_at.asc())  # 使用最早创建的权益
            .limit(1)
        )
        entitlement = result.scalar_one_or_none()

        if not entitlement:
            return UseFreeUnlockResponse(
                success=False,
                message="没有可用的免费解锁权益"
            )

        # 更新权益状态
        entitlement.status = "used"
        entitlement.used_at = datetime.now()
        entitlement.report_type = request.report_type
        entitlement.report_id = request.report_id

        await db.commit()

        logger.info(f"用户 {user_id} 使用免费解锁权益 {entitlement.id} 解锁 {request.report_type} 报告 {request.report_id}")

        return UseFreeUnlockResponse(
            success=True,
            entitlement_id=entitlement.id,
            message="免费解锁成功"
        )

    except Exception as e:
        logger.error(f"使用免费解锁权益失败: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="使用免费解锁权益失败"
        )


@router.post("/check-invitation-code")
async def check_invitation_code(
    invitation_code: str = Query(..., description="邀请码"),
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    检查邀请码并记录邀请关系（V2.6.8新增）
    新用户注册时调用，检查邀请码有效性并建立邀请关系
    """
    try:
        # 查找邀请人
        inviter_result = await db.execute(
            select(User).where(User.invitation_code == invitation_code)
        )
        inviter = inviter_result.scalar_one_or_none()

        if not inviter:
            return ApiResponse(
                code=1,
                msg="邀请码无效",
                data=None
            )

        # 检查是否已经邀请过自己
        if inviter.id == user_id:
            return ApiResponse(
                code=2,
                msg="不能邀请自己",
                data=None
            )

        # 检查是否已经存在邀请记录
        existing_result = await db.execute(
            select(InvitationRecord)
            .where(
                and_(
                    InvitationRecord.inviter_id == inviter.id,
                    InvitationRecord.invitee_id == user_id
                )
            )
        )
        existing_record = existing_result.scalar_one_or_none()

        if existing_record:
            return ApiResponse(
                code=3,
                msg="已存在邀请记录",
                data=None
            )

        # 创建邀请记录
        invitation_record = InvitationRecord(
            inviter_id=inviter.id,
            invitee_id=user_id,
            status="accepted",
            reward_type=INVITATION_REWARD_TYPE
        )
        db.add(invitation_record)

        # 更新被邀请人的邀请人字段
        invitee_result = await db.execute(select(User).where(User.id == user_id))
        invitee = invitee_result.scalar_one_or_none()
        if invitee:
            invitee.invited_by = inviter.id

        await db.commit()

        # 为邀请人创建免费解锁权益
        entitlement = FreeUnlockEntitlement(
            user_id=inviter.id,
            entitlement_type="invitation",
            source_id=invitation_record.id,
            status="available",
            expires_at=datetime.now() + timedelta(days=INVITATION_REWARD_EXPIRE_DAYS)
        )
        db.add(entitlement)

        # 更新邀请记录奖励状态
        invitation_record.reward_granted = True
        invitation_record.reward_granted_at = datetime.now()
        invitation_record.status = "rewarded"

        await db.commit()

        logger.info(f"用户 {inviter.id} 邀请用户 {user_id} 成功，获得免费解锁权益")

        return ApiResponse(
            code=0,
            msg="邀请关系建立成功，邀请人获得免费解锁权益",
            data={
                "inviter_nickname": inviter.nickname,
                "reward_granted": True
            }
        )

    except Exception as e:
        logger.error(f"检查邀请码失败: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="检查邀请码失败"
        )

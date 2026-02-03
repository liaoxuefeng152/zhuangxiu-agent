"""
装修决策Agent - 用户相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import httpx
import logging

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.models import User
from app.schemas import (
    WxLoginRequest, WxLoginResponse, UserProfileResponse,
    ApiResponse
)

router = APIRouter(prefix="/users", tags=["用户管理"])
logger = logging.getLogger(__name__)


@router.post("/login", response_model=WxLoginResponse)
async def wx_login(
    request: WxLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    微信小程序登录

    Args:
        request: 登录请求（包含微信code）
        db: 数据库会话

    Returns:
        登录响应（包含JWT token和用户信息）
    """
    try:
        # 调用微信API获取openid
        async with httpx.AsyncClient(timeout=30.0) as client:
            wx_url = "https://api.weixin.qq.com/sns/jscode2session"
            params = {
                "appid": settings.WECHAT_APP_ID,
                "secret": settings.WECHAT_APP_SECRET,
                "js_code": request.code,
                "grant_type": "authorization_code"
            }

            response = await client.get(wx_url, params=params)
            wx_data = response.json()

            if "errcode" in wx_data:
                logger.error(f"微信登录失败: {wx_data}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"微信登录失败: {wx_data.get('errmsg')}"
                )

            openid = wx_data.get("openid")
            unionid = wx_data.get("unionid")

            # 查找或创建用户
            result = await db.execute(select(User).where(User.wx_openid == openid))
            user = result.scalar_one_or_none()

            if not user:
                # 创建新用户
                user = User(
                    wx_openid=openid,
                    wx_unionid=unionid,
                    nickname=f"用户{openid[-6:]}",
                    created_at=datetime.now()
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
                logger.info(f"新用户注册: {openid}")
            else:
                # 更新unionid
                if unionid and not user.wx_unionid:
                    user.wx_unionid = unionid
                    await db.commit()
                logger.info(f"用户登录: {openid}")

            # 生成JWT Token（7天有效期）
            access_token = create_access_token(
                data={"user_id": user.id, "openid": user.wx_openid},
                expires_delta=timedelta(days=7)
            )

            return WxLoginResponse(
                access_token=access_token,
                user_id=user.id,
                openid=user.wx_openid,
                nickname=user.nickname,
                avatar_url=user.avatar_url,
                is_member=user.is_member
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"微信登录异常: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录服务暂时不可用"
        )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户信息

    Args:
        current_user: 当前用户信息（从JWT Token解析）
        db: 数据库会话

    Returns:
        用户信息
    """
    try:
        user_id = current_user["user_id"]

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        return UserProfileResponse(
            user_id=user.id,
            openid=user.wx_openid,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
            phone=user.phone,
            phone_verified=user.phone_verified,
            is_member=user.is_member,
            created_at=user.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        )


@router.put("/profile")
async def update_user_profile(
    current_user: dict = Depends(get_current_user),
    nickname: str = None,
    avatar_url: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户信息

    Args:
        current_user: 当前用户信息（从JWT Token解析）
        nickname: 昵称
        avatar_url: 头像URL
        db: 数据库会话

    Returns:
        更新结果
    """
    try:
        user_id = current_user["user_id"]

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        if nickname:
            user.nickname = nickname
        if avatar_url:
            user.avatar_url = avatar_url

        await db.commit()

        return ApiResponse(
            code=0,
            msg="更新成功",
            data={"user_id": user.id}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户信息失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败"
        )

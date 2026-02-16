"""
装修决策Agent - 用户相关API
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional
import httpx
import logging

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_current_user, get_user_id
from app.models import User, UserSetting
from app.schemas import (
    WxLoginRequest, WxLoginResponse, UserProfileResponse,
    ApiResponse
)

router = APIRouter(prefix="/users", tags=["用户管理"])
logger = logging.getLogger(__name__)


# 开发环境模拟登录 code（仅 DEBUG 时生效）
DEV_LOGIN_CODE = "dev_h5_mock"
DEV_WEAPP_CODE = "dev_weapp_mock"


def _is_debug() -> bool:
    """开发模式：兼容 env 中 DEBUG 为字符串 'True' 的情况"""
    if getattr(settings, "DEBUG", False) is True:
        return True
    if str(getattr(settings, "DEBUG", "")).lower() in ("true", "1"):
        return True
    if os.getenv("DEBUG", "").strip().lower() in ("true", "1"):
        return True
    return False


@router.post("/login", response_model=WxLoginResponse)
async def wx_login(
    request: WxLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    微信小程序登录
    开发环境：当 code=dev_h5_mock 且 DEBUG=True 时，返回模拟用户（用于 H5 本地调试）

    Args:
        request: 登录请求（包含微信code）
        db: 数据库会话

    Returns:
        登录响应（包含JWT token和用户信息）
    """
    try:
        # 开发环境模拟登录：H5/小程序本地调试（Taro.login 在 H5 不可用；小程序可免配置微信凭证测试）
        if request.code in (DEV_LOGIN_CODE, DEV_WEAPP_CODE) and _is_debug():
            try:
                result = await db.execute(select(User).limit(1))
                user = result.scalar_one_or_none()
                if not user:
                    user = User(
                        wx_openid="dev_h5_openid",
                        nickname="H5开发用户",
                        created_at=datetime.now()
                    )
                    db.add(user)
                    await db.commit()
                    await db.refresh(user)
                # 确保 SECRET_KEY 非空，否则 JWT 会报错
                secret = getattr(settings, "SECRET_KEY", None) or os.getenv("SECRET_KEY", "")
                if not secret:
                    raise ValueError("SECRET_KEY 未配置，无法生成 Token（请在 .env 或 docker-compose 中设置）")
                token = create_access_token(
                    data={"user_id": user.id, "openid": user.wx_openid},
                    expires_delta=timedelta(days=7)
                )
                return WxLoginResponse(
                    access_token=token,
                    user_id=user.id,
                    openid=user.wx_openid,
                    nickname=user.nickname,
                    avatar_url=user.avatar_url,
                    is_member=user.is_member
                )
            except Exception as e:  # 开发模式下打出具体原因，便于本地排查
                logger.exception("开发环境模拟登录失败: %s", e)
                detail = str(e) if _is_debug() else "登录服务暂时不可用"
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=detail
                )

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
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户信息（与其它接口一致：支持 Bearer 或 X-User-Id，缺 token 时返回 401）

    Args:
        user_id: 当前用户ID（从 get_user_id 解析）
        db: 数据库会话

    Returns:
        用户信息
    """
    try:

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
            member_expire=getattr(user, "member_expire", None),
            city_code=getattr(user, "city_code", None),
            city_name=getattr(user, "city_name", None),
            points=getattr(user, "points", 0) or 0,  # 用户积分（V2.6.7新增）
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


@router.get("/settings")
async def get_user_settings(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户设置（P19 数据存储期限、提醒等）"""
    try:
        user_id = current_user["user_id"]
        result = await db.execute(select(UserSetting).where(UserSetting.user_id == user_id))
        setting = result.scalar_one_or_none()
        if not setting:
            return ApiResponse(code=0, msg="success", data={
                "storage_duration_months": 12,
                "reminder_days_before": 3,
                "notify_progress": True,
                "notify_acceptance": True,
                "notify_system": True,
            })
        return ApiResponse(code=0, msg="success", data={
            "storage_duration_months": setting.storage_duration_months,
            "reminder_days_before": setting.reminder_days_before,
            "notify_progress": setting.notify_progress,
            "notify_acceptance": setting.notify_acceptance,
            "notify_system": setting.notify_system,
        })
    except Exception as e:
        logger.error(f"获取用户设置失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取失败")


@router.put("/settings")
async def update_user_settings(
    current_user: dict = Depends(get_current_user),
    storage_duration_months: Optional[int] = None,
    reminder_days_before: Optional[int] = None,
    notify_progress: Optional[bool] = None,
    notify_acceptance: Optional[bool] = None,
    notify_system: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """更新用户设置"""
    try:
        user_id = current_user["user_id"]
        result = await db.execute(select(UserSetting).where(UserSetting.user_id == user_id))
        setting = result.scalar_one_or_none()
        if not setting:
            setting = UserSetting(user_id=user_id)
            db.add(setting)
            await db.flush()
        if storage_duration_months is not None and storage_duration_months in (3, 6, 12):
            setting.storage_duration_months = storage_duration_months
        if reminder_days_before is not None and reminder_days_before in (1, 2, 3, 5, 7):
            setting.reminder_days_before = reminder_days_before
        if notify_progress is not None:
            setting.notify_progress = notify_progress
        if notify_acceptance is not None:
            setting.notify_acceptance = notify_acceptance
        if notify_system is not None:
            setting.notify_system = notify_system
        await db.commit()
        return ApiResponse(code=0, msg="设置已更新", data=None)
    except Exception as e:
        logger.error(f"更新用户设置失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新失败")

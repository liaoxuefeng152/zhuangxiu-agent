"""
用户相关数据验证模型
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    """用户登录请求"""
    code: str


class UserProfile(BaseModel):
    """用户信息"""
    user_id: int
    openid: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    phone_verified: bool = False
    is_member: bool = False
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    """更新用户信息"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应"""
    code: int = 0
    msg: str = "success"
    data: UserProfile


class LoginResponse(BaseModel):
    """登录响应"""
    code: int = 0
    msg: str = "success"
    data: dict


class TokenData(BaseModel):
    """Token数据"""
    user_id: Optional[int] = None
    openid: Optional[str] = None

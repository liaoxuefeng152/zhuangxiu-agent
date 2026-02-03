"""
安全认证模块 - JWT Token生成和验证
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer()


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    生成JWT Token

    Args:
        data: 要编码的数据字典
        expires_delta: 过期时间增量

    Returns:
        编码后的JWT Token字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    验证JWT Token并返回用户信息

    Args:
        credentials: HTTP Bearer认证凭证

    Returns:
        包含用户ID和openid的字典

    Raises:
        HTTPException: Token无效或过期时抛出401异常
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        openid: str = payload.get("openid")

        if user_id is None or openid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭证",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {"user_id": user_id, "openid": openid}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(credentials: Dict = Depends(verify_token)) -> Dict:
    """
    获取当前用户信息（依赖注入）

    Args:
        credentials: 从verify_token获取的认证信息

    Returns:
        包含用户ID和openid的字典
    """
    return credentials

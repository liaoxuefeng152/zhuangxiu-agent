"""
API限流中间件
基于slowapi实现全局限流和接口级限流
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# 创建限流器
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"]
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    限流超出异常处理器

    Args:
        request: 请求对象
        exc: 异常对象

    Returns:
        JSON响应
    """
    logger.warning(
        f"API限流触发: {request.client.host}, 路径: {request.url.path}",
        extra={
            "ip": request.client.host,
            "path": request.url.path,
            "method": request.method
        }
    )

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "code": 429,
            "msg": "请求过于频繁，请稍后再试",
            "error_id": None,
            "data": None
        }
    )


class RateLimitConfig:
    """限流配置"""

    # 敏感接口限流规则
    SENSITIVE_ENDPOINTS = {
        "/api/v1/companies/scan": "10/minute",  # 公司扫描
        "/api/v1/quotes/upload": "5/minute",     # 文件上传
        "/api/v1/contracts/analyze": "5/minute", # 合同分析
        "/api/v1/payments/create": "3/minute",   # 创建订单
    }

    @classmethod
    def get_limit(cls, endpoint: str) -> str:
        """
        获取端点的限流规则

        Args:
            endpoint: 端点路径

        Returns:
            限流规则字符串
        """
        return cls.SENSITIVE_ENDPOINTS.get(endpoint, None)

"""
全局异常处理器
统一处理应用中的各种异常，返回标准化的错误响应
"""
import uuid
import traceback
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """应用基础异常类"""

    def __init__(
        self,
        message: str = "服务器内部错误",
        code: int = 500,
        error_id: str = None,
        details: dict = None
    ):
        self.message = message
        self.code = code
        self.error_id = error_id or str(uuid.uuid4())
        self.details = details or {}
        super().__init__(self.message)


class UnauthorizedException(AppException):
    """未授权异常"""

    def __init__(self, message: str = "未授权访问"):
        super().__init__(message, code=401)


class ForbiddenException(AppException):
    """禁止访问异常"""

    def __init__(self, message: str = "禁止访问"):
        super().__init__(message, code=403)


class NotFoundException(AppException):
    """资源未找到异常"""

    def __init__(self, message: str = "资源未找到"):
        super().__init__(message, code=404)


class ValidationException(AppException):
    """验证异常"""

    def __init__(self, message: str = "数据验证失败", details: dict = None):
        super().__init__(message, code=422, details=details)


class RateLimitException(AppException):
    """限流异常"""

    def __init__(self, message: str = "请求过于频繁，请稍后再试"):
        super().__init__(message, code=429)


class DatabaseException(AppException):
    """数据库异常"""

    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message, code=500)


class ExternalServiceException(AppException):
    """外部服务异常"""

    def __init__(self, message: str = "外部服务调用失败"):
        super().__init__(message, code=502)


def format_exception_response(
    message: str,
    code: int,
    error_id: str = None,
    data: any = None
) -> dict:
    """
    格式化异常响应

    Args:
        message: 错误消息
        code: 错误代码
        error_id: 错误ID
        data: 额外数据

    Returns:
        标准化的错误响应
    """
    response = {
        "code": code,
        "msg": message,
        "error_id": error_id,
        "data": data
    }
    return response


async def app_exception_handler(request: Request, exc: AppException):
    """应用异常处理器"""
    logger.error(
        f"应用异常 [{exc.error_id}]: {exc.message}",
        extra={
            "error_id": exc.error_id,
            "code": exc.code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details
        }
    )

    return JSONResponse(
        status_code=exc.code,
        content=format_exception_response(
            message=exc.message,
            code=exc.code,
            error_id=exc.error_id,
            data=exc.details if exc.code != 500 else None
        )
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    error_id = str(uuid.uuid4())
    logger.warning(
        f"HTTP异常 [{error_id}]: {exc.detail}",
        extra={
            "error_id": error_id,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=format_exception_response(
            message=exc.detail,
            code=exc.status_code,
            error_id=error_id
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """验证异常处理器"""
    error_id = str(uuid.uuid4())
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"][1:])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(
        f"验证异常 [{error_id}]: {errors}",
        extra={
            "error_id": error_id,
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=format_exception_response(
            message="数据验证失败",
            code=422,
            error_id=error_id,
            data={"errors": errors}
        )
    )


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    error_id = str(uuid.uuid4())

    # 记录完整的错误堆栈
    logger.error(
        f"未捕获异常 [{error_id}]: {str(exc)}",
        exc_info=True,
        extra={
            "error_id": error_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__
        }
    )

    # 生产环境不返回详细错误信息
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_exception_response(
            message="服务器内部错误",
            code=500,
            error_id=error_id
        )
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """数据库异常处理器"""
    error_id = str(uuid.uuid4())

    logger.error(
        f"数据库异常 [{error_id}]: {str(exc)}",
        exc_info=True,
        extra={
            "error_id": error_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_exception_response(
            message="数据库操作失败",
            code=500,
            error_id=error_id
        )
    )


def register_exception_handlers(app):
    """注册所有异常处理器"""

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    logger.info("所有异常处理器已注册")

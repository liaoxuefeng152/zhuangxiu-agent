"""
装修决策Agent - FastAPI后端主入口
集成限流、异常处理、日志记录等中间件
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any
import uuid

from app.core.config import settings
from app.core.database import init_db, get_pool_status
from app.core.logger import get_logger, request_context
from app.core.exceptions import register_exception_handlers
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler, RateLimitConfig
from slowapi.errors import RateLimitExceeded
from app.services.redis_cache import init_cache, close_cache
from app.services.risk_analyzer import get_ai_provider_name
from app.api.v1 import api_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("正在初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")

    logger.info("正在初始化Redis缓存...")
    await init_cache()
    logger.info("Redis缓存初始化完成")

    logger.info("AI分析渠道: " + get_ai_provider_name())
    logger.info("装修决策Agent后端服务启动完成")
    yield

    # 关闭时的清理工作
    logger.info("正在关闭服务...")
    await close_cache()
    logger.info("应用关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(
        title="装修决策Agent API",
        description="为装修用户提供公司风险检测、报价单审核、合同解读等服务",
        version="2.2.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan,
    )

    # 注册限流器
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # CORS中间件配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )

    # Gzip压缩
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 请求上下文中间件
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        """请求上下文中间件"""
        request_id = str(uuid.uuid4())
        request_context.set({
            'request_id': request_id,
            'path': request.url.path,
            'method': request.method,
            'user_agent': request.headers.get('user-agent', '')
        })

        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id
        return response

    # 注册所有异常处理器
    register_exception_handlers(app)

    # 健康检查接口
    @app.get("/health")
    @limiter.limit("60/minute")
    async def health_check(request: Request) -> Dict[str, Any]:
        """健康检查接口"""
        pool_status = await get_pool_status()
        return {
            "code": 0,
            "msg": "success",
            "data": {
                "status": "healthy",
                "version": "2.2.0",
                "database": pool_status
            }
        }

    # 数据库连接池监控接口
    @app.get("/internal/monitor/pool-status")
    async def pool_status_monitor() -> Dict[str, Any]:
        """数据库连接池状态监控"""
        try:
            pool_status = await get_pool_status()
            return {
                "code": 0,
                "msg": "success",
                "data": pool_status
            }
        except Exception as e:
            logger.error(f"获取连接池状态失败: {e}")
            return {
                "code": 500,
                "msg": "获取连接池状态失败",
                "data": None
            }

    # 注册路由
    app.include_router(api_router, prefix="/api/v1")

    logger.info("FastAPI应用创建完成")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )
"""
装修决策Agent - 数据库配置（简化版）
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
import logging

logger = logging.getLogger(__name__)

# 直接从环境变量获取（绕过 settings 可能的格式问题）
DATABASE_URL = os.getenv("DATABASE_URL", "")

# 强制使用 asyncpg 驱动
if DATABASE_URL and "postgresql+asyncpg://" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql+asyncpg://")

if not DATABASE_URL:
    logger.warning("DATABASE_URL 未设置，数据库连接将不可用")

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False,
    future=True,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """初始化数据库（创建表）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def get_pool_status():
    """获取连接池状态"""
    return {
        "checked_in": engine.pool.checkedin(),
        "checked_out": engine.pool.checkedout(),
        "size": engine.pool.size(),
        "overflow": engine.pool.overflow(),
    }

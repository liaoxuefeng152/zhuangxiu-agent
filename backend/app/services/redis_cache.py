"""
Redis缓存服务
实现缓存机制，减少重复计算和第三方API调用
"""
import json
import redis.asyncio as redis
from typing import Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis缓存服务"""

    def __init__(self):
        """初始化Redis客户端"""
        self.client = None

    async def connect(self):
        """连接Redis"""
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            await self.client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self.client = None

    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存

        Args:
            key: 缓存键

        Returns:
            缓存值，不存在则返回None
        """
        if not self.client:
            return None

        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"获取缓存失败: {key}, 错误: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒），默认1小时

        Returns:
            是否设置成功
        """
        if not self.client:
            return False

        try:
            await self.client.setex(
                key,
                expire,
                json.dumps(value, ensure_ascii=False)
            )
            logger.debug(f"缓存设置成功: {key}, 过期时间: {expire}秒")
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {key}, 错误: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        if not self.client:
            return False

        try:
            await self.client.delete(key)
            logger.debug(f"缓存删除成功: {key}")
            return True
        except Exception as e:
            logger.error(f"删除缓存失败: {key}, 错误: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            是否存在
        """
        if not self.client:
            return False

        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"检查缓存失败: {key}, 错误: {e}")
            return False

    async def hget(self, name: str, key: str) -> Optional[Any]:
        """
        获取哈希表字段

        Args:
            name: 哈希表名称
            key: 字段名

        Returns:
            字段值，不存在则返回None
        """
        if not self.client:
            return None

        try:
            value = await self.client.hget(name, key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"获取哈希字段失败: {name}.{key}, 错误: {e}")
            return None

    async def hset(self, name: str, key: str, value: Any) -> bool:
        """
        设置哈希表字段

        Args:
            name: 哈希表名称
            key: 字段名
            value: 字段值

        Returns:
            是否设置成功
        """
        if not self.client:
            return False

        try:
            await self.client.hset(
                name,
                key,
                json.dumps(value, ensure_ascii=False)
            )
            return True
        except Exception as e:
            logger.error(f"设置哈希字段失败: {name}.{key}, 错误: {e}")
            return False

    async def hgetall(self, name: str) -> dict:
        """
        获取整个哈希表

        Args:
            name: 哈希表名称

        Returns:
            哈希表内容
        """
        if not self.client:
            return {}

        try:
            result = await self.client.hgetall(name)
            return {k: json.loads(v) for k, v in result.items()}
        except Exception as e:
            logger.error(f"获取哈希表失败: {name}, 错误: {e}")
            return {}


# 创建全局缓存服务实例
cache = RedisCache()


async def init_cache():
    """初始化缓存服务"""
    await cache.connect()


async def close_cache():
    """关闭缓存服务"""
    await cache.disconnect()

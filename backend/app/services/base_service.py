"""
基础服务模块
实现API调用的重试机制、超时控制和断路器保护
"""
import httpx
import asyncio
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from circuitbreaker import circuit
import logging

logger = logging.getLogger(__name__)


# 重试策略：最多重试3次，使用指数退避
retry_strategy = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
)


@circuit(failure_threshold=5, recovery_timeout=60)
async def call_with_circuit_breaker(url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
    """
    带断路器保护的API调用

    Args:
        url: API URL
        method: HTTP方法
        **kwargs: 其他参数

    Returns:
        响应JSON数据

    Raises:
        Exception: 调用失败时抛出异常
    """
    timeout = kwargs.pop('timeout', 30)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()


class BaseService:
    """基础服务类"""

    def __init__(self, base_url: str = None, default_timeout: int = 30):
        """
        初始化基础服务

        Args:
            base_url: 基础URL
            default_timeout: 默认超时时间（秒）
        """
        self.base_url = base_url.rstrip('/') if base_url else None
        self.default_timeout = default_timeout

    @retry_strategy
    async def call_api(
        self,
        endpoint: str,
        method: str = "GET",
        params: Dict[str, Any] = None,
        json_data: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        带重试机制的API调用

        Args:
            endpoint: API端点
            method: HTTP方法
            params: URL参数
            json_data: JSON数据
            headers: 请求头
            timeout: 超时时间（秒）

        Returns:
            响应JSON数据

        Raises:
            Exception: 调用失败时抛出异常
        """
        timeout = timeout or self.default_timeout

        if self.base_url:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
        else:
            url = endpoint

        try:
            logger.info(f"调用API: {method} {url}")

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method,
                    url,
                    params=params,
                    json=json_data,
                    headers=headers
                )
                response.raise_for_status()

                result = response.json()
                logger.info(f"API调用成功: {url}, 状态码: {response.status_code}")
                return result

        except httpx.TimeoutException as e:
            logger.error(f"API调用超时: {url}, 错误: {e}")
            raise Exception(f"API调用超时: {url}")

        except httpx.HTTPStatusError as e:
            logger.error(f"API调用失败: {url}, 状态码: {e.response.status_code}, 错误: {e}")
            raise Exception(f"API调用失败: {url}, 状态码: {e.response.status_code}")

        except httpx.RequestError as e:
            logger.error(f"API请求失败: {url}, 错误: {e}")
            raise Exception(f"API请求失败: {url}")

        except Exception as e:
            logger.error(f"未知错误: {url}, 错误: {e}")
            raise

    async def call_api_with_retry(
        self,
        endpoint: str,
        method: str = "GET",
        **kwargs
    ) -> Dict[str, Any]:
        """
        带重试和断路器保护的API调用

        Args:
            endpoint: API端点
            method: HTTP方法
            **kwargs: 其他参数

        Returns:
            响应JSON数据
        """
        if self.base_url:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
        else:
            url = endpoint

        return await call_with_circuit_breaker(url, method, **kwargs)

    async def parallel_call(
        self,
        calls: list
    ) -> list:
        """
        并行调用多个API

        Args:
            calls: 调用列表，每个元素为 (endpoint, method, kwargs) 元组

        Returns:
            响应列表
        """
        tasks = []
        for call in calls:
            endpoint, method, kwargs = call
            tasks.append(self.call_api(endpoint, method, **kwargs))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"并行调用失败: {calls[i][0]}, 错误: {result}")

        return results

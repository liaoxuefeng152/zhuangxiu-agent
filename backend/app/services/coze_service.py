"""
装修决策Agent - 扣子智能体服务
用于调用扣子智能体分析图片，替代阿里云OCR
"""
import json
import logging
import asyncio
from typing import Dict, Optional, Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class CozeService:
    """扣子智能体服务"""

    def __init__(self):
        self.api_base = settings.COZE_API_BASE or "https://api.coze.cn"
        self.api_token = settings.COZE_API_TOKEN
        self.bot_id = settings.COZE_BOT_ID
        self.site_url = settings.COZE_SITE_URL
        self.site_token = settings.COZE_SITE_TOKEN
        self.project_id = settings.COZE_PROJECT_ID
        
        # 检查配置
        self.use_site_api = bool(self.site_url and self.site_token)
        self.use_open_api = bool(self.api_token and self.bot_id)
        
        if not self.use_site_api and not self.use_open_api:
            logger.warning("扣子智能体配置不完整，功能将不可用")
            logger.warning("请配置 COZE_SITE_URL 和 COZE_SITE_TOKEN 或 COZE_API_TOKEN 和 COZE_BOT_ID")
        
        logger.info(f"扣子智能体服务初始化: 使用{'站点API' if self.use_site_api else '开放平台API' if self.use_open_api else '无可用配置'}")
    
    async def analyze_quote(self, image_url: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        分析报价单图片
        
        Args:
            image_url: 图片URL（OSS签名URL）
            user_id: 用户ID（可选）
            
        Returns:
            分析结果字典，如果失败返回None
        """
        try:
            logger.info(f"开始分析报价单图片: {image_url[:100]}..., 用户ID: {user_id}")
            
            # 构建提示词
            prompt = """请分析这份装修报价单图片，返回JSON格式的结构化数据，包含以下字段：
1. total_price: 总价（数字）
2. risk_score: 风险评分（0-100整数）
3. high_risk_items: 高风险项目列表（数组，每个项目包含name和reason）
4. warning_items: 警告项目列表（数组，每个项目包含name和reason）
5. missing_items: 缺失项目列表（数组，每个项目包含name和suggestion）
6. overpriced_items: 价格过高项目列表（数组，每个项目包含name、current_price和market_price）
7. market_ref_price: 市场参考价（数字或字符串）
8. suggestions: 总体建议列表（数组）
9. summary: 分析总结（字符串）

请确保返回的是纯JSON格式，不要包含其他文本。"""
            
            if self.use_site_api:
                result = await self._call_site_api(image_url, prompt, user_id)
            elif self.use_open_api:
                result = await self._call_open_api(image_url, prompt, user_id)
            else:
                logger.error("扣子智能体配置不完整，无法调用")
                return None
            
            if result:
                logger.info(f"扣子智能体分析成功，结果类型: {type(result)}")
                return result
            else:
                logger.error("扣子智能体分析失败，返回None")
                return None
                
        except Exception as e:
            logger.error(f"扣子智能体分析异常: {e}", exc_info=True)
            return None
    
    async def _call_site_api(self, image_url: str, prompt: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        调用扣子站点API
        
        Args:
            image_url: 图片URL
            prompt: 提示词
            user_id: 用户ID
            
        Returns:
            分析结果
        """
        try:
            # 构建请求URL
            api_url = f"{self.site_url.rstrip('/')}/stream_run"
            logger.info(f"调用扣子站点API: {api_url}")
            
            # 构建请求数据
            data = {
                "project_id": self.project_id,
                "user_id": str(user_id) if user_id else "anonymous",
                "query": prompt,
                "files": [{"type": "image", "url": image_url}],
                "auto_save_history": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.site_token}",
                "Content-Type": "application/json"
            }
            
            # 设置超时（60秒）
            timeout = httpx.Timeout(60.0, connect=10.0)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(api_url, json=data, headers=headers)
                response.raise_for_status()
                
                # 解析响应
                result_text = response.text
                logger.debug(f"扣子站点API响应: {result_text[:500]}...")
                
                # 尝试解析JSON
                try:
                    result_data = json.loads(result_text)
                    return self._parse_coze_response(result_data)
                except json.JSONDecodeError:
                    # 如果不是JSON，尝试提取JSON部分
                    return self._extract_json_from_text(result_text)
                    
        except httpx.TimeoutException:
            logger.error("扣子站点API调用超时（60秒）")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"扣子站点API HTTP错误: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"扣子站点API调用异常: {e}", exc_info=True)
            return None
    
    async def _call_open_api(self, image_url: str, prompt: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        调用扣子开放平台API
        
        Args:
            image_url: 图片URL
            prompt: 提示词
            user_id: 用户ID
            
        Returns:
            分析结果
        """
        try:
            # 构建请求URL
            api_url = f"{self.api_base.rstrip('/')}/v1/chat"
            logger.info(f"调用扣子开放平台API: {api_url}")
            
            # 构建请求数据
            data = {
                "bot_id": self.bot_id,
                "user_id": str(user_id) if user_id else "anonymous",
                "query": prompt,
                "stream": False,
                "auto_save_history": False
            }
            
            # 如果有图片URL，添加到消息中
            if image_url:
                data["query"] = f"{prompt}\n\n图片URL: {image_url}"
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            # 设置超时（60秒）
            timeout = httpx.Timeout(60.0, connect=10.0)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(api_url, json=data, headers=headers)
                response.raise_for_status()
                
                # 解析响应
                result_data = response.json()
                logger.debug(f"扣子开放平台API响应: {json.dumps(result_data, ensure_ascii=False)[:500]}...")
                
                return self._parse_coze_response(result_data)
                
        except httpx.TimeoutException:
            logger.error("扣子开放平台API调用超时（60秒）")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"扣子开放平台API HTTP错误: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"扣子开放平台API调用异常: {e}", exc_info=True)
            return None
    
    def _parse_coze_response(self, response_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        解析扣子API响应
        
        Args:
            response_data: 扣子API返回的数据
            
        Returns:
            解析后的结果
        """
        try:
            # 站点API响应格式
            if "content" in response_data:
                content = response_data["content"]
                return self._extract_json_from_text(content)
            
            # 开放平台API响应格式
            elif "messages" in response_data:
                messages = response_data["messages"]
                for message in messages:
                    if message.get("type") == "answer" and "content" in message:
                        content = message["content"]
                        return self._extract_json_from_text(content)
            
            # 其他格式
            elif "text" in response_data:
                content = response_data["text"]
                return self._extract_json_from_text(content)
            
            # 如果响应本身就是JSON对象，直接返回
            elif isinstance(response_data, dict):
                # 检查是否包含需要的字段
                expected_fields = ["total_price", "risk_score", "high_risk_items", "suggestions"]
                if any(field in response_data for field in expected_fields):
                    return response_data
            
            logger.warning(f"无法识别的扣子响应格式: {response_data}")
            return None
            
        except Exception as e:
            logger.error(f"解析扣子响应失败: {e}", exc_info=True)
            return None
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        从文本中提取JSON
        
        Args:
            text: 包含JSON的文本
            
        Returns:
            提取的JSON对象，如果失败返回包含raw_text的字典
        """
        try:
            # 尝试直接解析
            if text.strip().startswith("{") and text.strip().endswith("}"):
                return json.loads(text)
            
            # 尝试查找JSON对象
            import re
            json_pattern = r'\{[^{}]*\}'
            matches = re.findall(json_pattern, text, re.DOTALL)
            
            for match in matches:
                try:
                    # 尝试补全可能的缺失括号
                    if match.count("{") > match.count("}"):
                        match += "}" * (match.count("{") - match.count("}"))
                    elif match.count("}") > match.count("{"):
                        match = "{" * (match.count("}") - match.count("{")) + match
                    
                    result = json.loads(match)
                    if isinstance(result, dict):
                        return result
                except json.JSONDecodeError:
                    continue
            
            # 如果没有找到有效的JSON，返回原始文本
            logger.warning(f"无法从文本中提取JSON，返回原始文本: {text[:200]}...")
            return {"raw_text": text}
            
        except Exception as e:
            logger.error(f"提取JSON失败: {e}", exc_info=True)
            return {"raw_text": text}
    
    async def analyze_contract(self, image_url: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        分析合同图片
        
        Args:
            image_url: 图片URL
            user_id: 用户ID
            
        Returns:
            分析结果
        """
        try:
            prompt = """请分析这份装修合同图片，返回JSON格式的结构化数据，包含以下字段：
1. contract_type: 合同类型（字符串）
2. risk_score: 风险评分（0-100整数）
3. high_risk_clauses: 高风险条款列表（数组，每个条款包含clause和reason）
4. missing_clauses: 缺失条款列表（数组，每个条款包含clause和suggestion）
5. unfair_clauses: 不公平条款列表（数组，每个条款包含clause和reason）
6. suggestions: 修改建议列表（数组）
7. summary: 分析总结（字符串）

请确保返回的是纯JSON格式，不要包含其他文本。"""
            
            if self.use_site_api:
                result = await self._call_site_api(image_url, prompt, user_id)
            elif self.use_open_api:
                result = await self._call_open_api(image_url, prompt, user_id)
            else:
                logger.error("扣子智能体配置不完整，无法调用")
                return None
            
            return result
            
        except Exception as e:
            logger.error(f"合同分析异常: {e}", exc_info=True)
            return None
    
    async def analyze_acceptance(self, image_url: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        分析验收单图片
        
        Args:
            image_url: 图片URL
            user_id: 用户ID
            
        Returns:
            分析结果
        """
        try:
            prompt = """请分析这份装修验收单图片，返回JSON格式的结构化数据，包含以下字段：
1. acceptance_status: 验收状态（通过/不通过/部分通过）
2. quality_score: 质量评分（0-100整数）
3. issues: 问题列表（数组，每个问题包含item、description和severity）
4. passed_items: 通过项目列表（数组）
5. suggestions: 整改建议列表（数组）
6. summary: 分析总结（字符串）

请确保返回的是纯JSON格式，不要包含其他文本。"""
            
            if self.use_site_api:
                result = await self._call_site_api(image_url, prompt, user_id)
            elif self.use_open_api:
                result = await self._call_open_api(image_url, prompt, user_id)
            else:
                logger.error("扣子智能体配置不完整，无法调用")
                return None
            
            return result
            
        except Exception as e:
            logger.error(f"验收单分析异常: {e}", exc_info=True)
            return None


# 创建全局实例
coze_service = CozeService()

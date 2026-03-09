"""
装修决策Agent - 扣子智能体服务
用于调用扣子智能体分析图片，替代阿里云OCR
"""
import json
import logging
import asyncio
import time
from typing import Dict, Optional, Any, List
import httpx
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class CozeService:
    """扣子智能体服务"""

    def __init__(self):
        self.api_base = settings.COZE_API_BASE or "https://api.coze.cn"
        self.api_token = settings.COZE_API_TOKEN
        # 优先使用COZE_BOT_ID，如果为空则尝试使用COZE_SUPERVISOR_BOT_ID
        self.bot_id = settings.COZE_BOT_ID or getattr(settings, 'COZE_SUPERVISOR_BOT_ID', '')
        self.site_url = settings.COZE_SITE_URL
        self.site_token = settings.COZE_SITE_TOKEN
        self.project_id = settings.COZE_PROJECT_ID
        
        # 检查配置 - 站点API优先于开放平台API
        self.use_site_api = bool(self.site_url and self.site_token)
        self.use_open_api = bool(self.api_token and self.bot_id)
        
        # DeepSeek API作为备用服务
        self.deepseek_client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY or "",
            base_url=settings.DEEPSEEK_API_BASE or "https://api.deepseek.com/v1"
        )
        self.use_deepseek = bool(settings.DEEPSEEK_API_KEY)
        
        if not self.use_site_api and not self.use_open_api and not self.use_deepseek:
            logger.warning("AI分析服务配置不完整，功能将不可用")
            logger.warning("请配置 COZE_SITE_URL 和 COZE_SITE_TOKEN 或 COZE_API_TOKEN 和 COZE_BOT_ID 或 DEEPSEEK_API_KEY")
        else:
            logger.info(f"AI分析服务初始化: 使用{'扣子站点API' if self.use_site_api else '扣子开放平台API' if self.use_open_api else 'DeepSeek API' if self.use_deepseek else '无可用配置'}")
            if self.use_site_api:
                logger.info(f"扣子站点API配置: URL={self.site_url}, 项目ID={self.project_id}")
            if self.use_open_api:
                logger.info(f"扣子开放平台API配置: Bot ID={self.bot_id}")
            if self.use_deepseek:
                logger.info(f"DeepSeek API配置: 已启用")
    
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
            
            # 构建提示词 - 明确要求报价单分析格式，避免返回合同分析格式
            # 增强版提示词：更明确地区分报价单和合同，防止AI返回工具调用说明
            prompt = """【重要指令】请分析这份装修报价单图片，返回JSON格式的结构化数据。

【明确要求】
1. 这是装修报价单图片，不是合同图片
2. 请分析报价单中的价格、项目、材料等信息
3. 返回纯JSON格式，不要包含其他任何文本

【必需字段】
{
  "total_price": 总价（数字，如：85000.00）,
  "risk_score": 风险评分（0-100整数）,
  "high_risk_items": [
    {"name": "项目名称", "reason": "风险原因"}
  ],
  "warning_items": [
    {"name": "项目名称", "reason": "警告原因"}
  ],
  "missing_items": [
    {"name": "缺失项目", "suggestion": "补充建议"}
  ],
  "overpriced_items": [
    {"name": "项目名称", "current_price": "当前价格", "market_price": "市场价格", "reason": "价格过高原因"}
  ],
  "market_ref_price": 市场参考价（数字或字符串）,
  "suggestions": ["建议1", "建议2", "建议3"],
  "summary": "分析总结（字符串）"
}

【特别注意】
- 不要返回工具调用说明或函数调用格式
- 不要返回合同分析格式（如risk_items、unfair_terms、missing_terms等）
- 直接返回JSON对象，不要用```json```包裹
- 如果无法识别某些信息，请使用合理的默认值或空数组"""
            
            # 尝试扣子服务
            result = None
            if self.use_site_api:
                result = await self._call_site_api(image_url, prompt, user_id)
                if not result and self.use_deepseek:
                    logger.info("扣子站点API调用失败，降级使用DeepSeek API")
                    result = await self._call_deepseek_api(image_url, prompt, user_id)
            elif self.use_open_api:
                result = await self._call_open_api(image_url, prompt, user_id)
                if not result and self.use_deepseek:
                    logger.info("扣子开放平台API调用失败，降级使用DeepSeek API")
                    result = await self._call_deepseek_api(image_url, prompt, user_id)
            elif self.use_deepseek:
                result = await self._call_deepseek_api(image_url, prompt, user_id)
            else:
                logger.error("AI分析服务配置不完整，无法调用")
                return None
            
            if result:
                logger.info(f"AI分析成功，结果类型: {type(result)}")
                # 根据用户要求：前端必须原样展示AI智能体返回的数据
                # 不再进行格式转换，直接返回AI智能体的原始结果
                logger.info("直接返回AI智能体原始结果，不进行格式转换")
                return result
            else:
                logger.error("AI分析失败，返回兜底数据")
                return self._get_fallback_quote_analysis(image_url)
                
        except Exception as e:
            logger.error(f"扣子智能体分析异常: {e}", exc_info=True)
            return None
    
    async def _call_site_api(self, image_url: str, prompt: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        调用扣子站点API（处理流式响应）

        Args:
            image_url: 图片URL
            prompt: 提示词
            user_id: 用户ID

        Returns:
            分析结果
        """
        try:
            # 构建请求URL - 使用流式端点，与日志中的调用一致
            api_url = f"{self.site_url.rstrip('/')}/stream_run"
            logger.info(f"调用扣子站点API（流式）: {api_url}")

            # 构建请求数据 - 根据用户提供的curl命令格式
            # 关键修改：将图片URL作为文本内容的一部分，而不是独立的image类型
            # 扣子智能体需要图片URL嵌入在文本中，格式为："请帮我分析{image_url}"
            combined_prompt = f"{prompt}\n\n图片URL: {image_url}"
            
            data = {
                "content": {
                    "query": {
                        "prompt": [
                            {
                                "type": "text",
                                "content": {
                                    "text": combined_prompt
                                }
                            }
                        ]
                    }
                },
                "type": "query",
                "session_id": f"session_{user_id}" if user_id else f"session_anonymous_{int(time.time())}",
                "project_id": self.project_id,
                # 站点侧若基于 langgraph，可尝试透传 recursion_limit，避免 GraphRecursionError。
                # 不同站点实现可能忽略该字段；忽略也不影响正常调用。
                "config": {"recursion_limit": getattr(settings, "COZE_SITE_RECURSION_LIMIT", 25)},
            }

            # 不再需要独立的image类型，图片URL已经包含在文本中
            # 移除原来的独立image类型添加逻辑

            headers = {
                "Authorization": f"Bearer {self.site_token}",
                "Content-Type": "application/json"
            }

            # 设置超时（120秒，图片分析需要更长时间）
            timeout = httpx.Timeout(120.0, connect=10.0)

            # 处理流式响应 - 采用设计师智能体的成功模式
            async def _do_stream() -> Optional[str]:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    async with client.stream("POST", api_url, json=data, headers=headers) as response:
                        response.raise_for_status()
                        
                        chunks = []
                        raw_samples = []
                        async for line in response.aiter_lines():
                            line = (line or "").strip()
                            if not line or line == "data: [DONE]":
                                continue
                            if len(raw_samples) < 5:
                                raw_samples.append(line[:250])
                            if not line.startswith("data:"):
                                continue
                            json_str = line[5:].strip()
                            try:
                                data_chunk = json.loads(json_str)
                                # 提取内容
                                content = self._extract_content_from_stream(data_chunk)
                                if content:
                                    chunks.append(content)
                                    if len(chunks) <= 2:
                                        logger.info(f"扣子站点提取chunk len={len(content)}")
                            except json.JSONDecodeError:
                                logger.debug(f"流式响应JSON解析失败: {json_str[:100]}...")
                                continue
                        
                        # 合并所有chunks
                        full_content = "".join(chunks).strip()
                        logger.info(f"扣子站点API流式响应接收完成，共{len(chunks)}个数据块，总长度: {len(full_content)}字符")
                        
                        if not full_content and raw_samples:
                            logger.warning(
                                f"扣子站点返回无解析文本。样本行: {raw_samples}"
                            )
                        return full_content if full_content else None

            # 调用流式处理函数
            result_text = await _do_stream()
            
            # 扣子流式有时先返回 message_start、正文稍后才到，空结果时重试最多 2 次
            for retry in range(2):
                if result_text:
                    break
                await asyncio.sleep(5)  # 等待更长时间再重试
                logger.info(f"扣子站点空结果，第{retry + 1}次重试")
                result_text = await _do_stream()
            
            if not result_text:
                logger.error("扣子站点API流式响应内容为空！")
                return None
            
            # 尝试解析为JSON
            try:
                result_data = json.loads(result_text)
                return self._parse_coze_response(result_data)
            except json.JSONDecodeError:
                # 如果不是JSON，尝试从文本中提取JSON
                logger.warning(f"扣子站点API响应不是JSON格式，尝试提取JSON: {result_text[:200]}...")
                return self._extract_json_from_text(result_text)

        except httpx.TimeoutException:
            logger.error("扣子站点API调用超时（120秒）")
            return None
        except httpx.HTTPStatusError as e:
            body = ""
            try:
                body = e.response.text or ""
            except Exception:
                body = ""
            logger.error(f"扣子站点API HTTP错误: {e.response.status_code} - {body}")
            # 针对站点 500 且递归深度超限的场景，返回可识别的兜底结果（避免被当成“分析成功”）。
            if e.response.status_code >= 500 and "GRAPH_RECURSION_LIMIT" in body:
                return {
                    "risk_score": 0,
                    "high_risk_items": [],
                    "warning_items": [],
                    "missing_items": [],
                    "overpriced_items": [],
                    "suggestions": ["AI分析服务暂时不可用，请稍后重试"],
                    "summary": "AI分析服务异常：扣子站点工作流递归深度超限，请稍后重试或联系客服。",
                    "total_price": None,
                    "market_ref_price": None,
                    "analysis_note": "AI分析服务异常，此为兜底分析建议",
                    "is_fallback": True,
                    "error_code": "COZE_GRAPH_RECURSION_LIMIT",
                }
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
    
    async def _call_deepseek_api(self, image_url: str, prompt: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        调用DeepSeek API作为备用服务
        
        Args:
            image_url: 图片URL
            prompt: 提示词
            user_id: 用户ID
            
        Returns:
            分析结果
        """
        try:
            logger.info(f"调用DeepSeek API分析图片: {image_url[:100]}..., 用户ID: {user_id}")
            
            # 构建消息，包含图片URL
            messages = [
                {"role": "system", "content": "你是一位专业的装修分析专家。请分析用户提供的装修相关图片，返回JSON格式的结构化分析结果。"},
                {"role": "user", "content": f"{prompt}\n\n图片URL: {image_url}"}
            ]
            
            # 调用DeepSeek API
            response = await self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            result_text = (response.choices[0].message.content or "").strip()
            logger.debug(f"DeepSeek API响应: {result_text[:500]}...")
            
            # 尝试提取JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # 解析JSON
            try:
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                # 如果无法解析为JSON，返回原始文本
                logger.warning(f"DeepSeek API返回非JSON格式，返回原始文本: {result_text[:200]}...")
                return {"raw_text": result_text}
                
        except Exception as e:
            logger.error(f"DeepSeek API调用异常: {e}", exc_info=True)
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
            # 站点API响应格式（新格式）
            if "messages" in response_data:
                messages = response_data["messages"]
                for message in messages:
                    # 检查是否有content字段
                    if "content" in message:
                        content = message["content"]
                        # 如果content是字符串且包含JSON，提取JSON
                        if isinstance(content, str):
                            result = self._extract_json_from_text(content)
                            # 检查是否是工具调用说明
                            if self._is_tool_call_response(result):
                                logger.warning("扣子返回工具调用说明而非分析结果")
                                return self._get_fallback_quote_analysis()
                            return result
                        # 如果content已经是字典，直接返回
                        elif isinstance(content, dict):
                            # 检查是否是工具调用说明
                            if self._is_tool_call_response(content):
                                logger.warning("扣子返回工具调用说明而非分析结果")
                                return self._get_fallback_quote_analysis()
                            return content
            
            # 旧格式：直接包含content
            elif "content" in response_data:
                content = response_data["content"]
                if isinstance(content, str):
                    result = self._extract_json_from_text(content)
                    # 检查是否是工具调用说明
                    if self._is_tool_call_response(result):
                        logger.warning("扣子返回工具调用说明而非分析结果")
                        return self._get_fallback_quote_analysis()
                    return result
                elif isinstance(content, dict):
                    # 检查是否是工具调用说明
                    if self._is_tool_call_response(content):
                        logger.warning("扣子返回工具调用说明而非分析结果")
                        return self._get_fallback_quote_analysis()
                    return content
            
            # 开放平台API响应格式
            elif "text" in response_data:
                content = response_data["text"]
                result = self._extract_json_from_text(content)
                # 检查是否是工具调用说明
                if self._is_tool_call_response(result):
                    logger.warning("扣子返回工具调用说明而非分析结果")
                    return self._get_fallback_quote_analysis()
                return result
            
            # 如果响应本身就是JSON对象，需要区分不同类型
            elif isinstance(response_data, dict):
                # 首先检查是否是工具调用说明
                if self._is_tool_call_response(response_data):
                    logger.warning("扣子返回工具调用说明而非分析结果")
                    return self._get_fallback_quote_analysis()
                
                # 检查是否是报价单分析结果
                quote_fields = ["total_price", "risk_score", "high_risk_items", "suggestions"]
                if any(field in response_data for field in quote_fields):
                    # 这是报价单分析结果，需要检查是否已经是标准格式
                    if "total_price" in response_data and "risk_score" in response_data:
                        return response_data
                
                # 检查是否是合同分析结果
                contract_fields = ["contract_type", "risk_score", "high_risk_clauses", "summary"]
                if any(field in response_data for field in contract_fields):
                    # 这是合同分析结果
                    if "contract_type" in response_data and "risk_score" in response_data:
                        return response_data
                
                # 检查是否是验收分析结果
                acceptance_fields = ["acceptance_status", "quality_score", "issues", "passed_items", "suggestions", "summary"]
                if any(field in response_data for field in acceptance_fields):
                    # 这是验收分析结果
                    if "acceptance_status" in response_data or "issues" in response_data:
                        return response_data
                
                # 检查是否是原始文本
                if "raw_text" in response_data:
                    # 检查原始文本是否是工具调用说明
                    raw_text = response_data.get("raw_text", "")
                    if "analyze_contract_quote" in raw_text or "调用工具" in raw_text or "工具调用" in raw_text:
                        logger.warning("扣子返回工具调用说明而非分析结果")
                        return self._get_fallback_quote_analysis()
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
            # 首先检查文本是否是工具调用说明
            if "analyze_contract_quote" in text or "调用工具" in text or "工具调用" in text:
                logger.warning("文本包含工具调用说明，返回兜底数据")
                return self._get_fallback_quote_analysis()
            
            # 清理文本：移除可能的Markdown代码块标记
            cleaned_text = text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:].strip()
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:].strip()
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3].strip()
            
            # 尝试直接解析
            if cleaned_text.startswith("{") and cleaned_text.endswith("}"):
                try:
                    result = json.loads(cleaned_text)
                    # 检查解析后的结果是否是工具调用说明
                    if self._is_tool_call_response(result):
                        logger.warning("解析后的JSON是工具调用说明，返回兜底数据")
                        return self._get_fallback_quote_analysis()
                    return result
                except json.JSONDecodeError as e:
                    logger.debug(f"直接解析JSON失败: {e}")
            
            # 尝试查找JSON对象 - 使用更灵活的正则表达式
            import re
            # 匹配可能包含嵌套的JSON对象
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, cleaned_text, re.DOTALL)
            
            for match in matches:
                try:
                    # 尝试补全可能的缺失括号
                    open_count = match.count("{")
                    close_count = match.count("}")
                    if open_count > close_count:
                        match += "}" * (open_count - close_count)
                    elif close_count > open_count:
                        match = "{" * (close_count - open_count) + match
                    
                    result = json.loads(match)
                    if isinstance(result, dict):
                        # 检查是否是工具调用说明
                        if self._is_tool_call_response(result):
                            logger.warning("提取的JSON是工具调用说明，返回兜底数据")
                            return self._get_fallback_quote_analysis()
                        
                        # 检查是否是报价单分析结果
                        quote_fields = ["total_price", "risk_score", "high_risk_items", "suggestions"]
                        if any(field in result for field in quote_fields):
                            logger.info(f"成功从文本中提取报价单分析JSON: 包含字段 {list(result.keys())}")
                            return result
                        
                        # 检查是否是合同分析结果
                        contract_fields = ["contract_type", "risk_score", "high_risk_clauses", "summary"]
                        if any(field in result for field in contract_fields):
                            logger.info(f"成功从文本中提取合同分析JSON: 包含字段 {list(result.keys())}")
                            return result
                        
                        # 检查是否是验收分析结果
                        acceptance_fields = ["acceptance_status", "quality_score", "issues", "passed_items", "suggestions", "summary"]
                        if any(field in result for field in acceptance_fields):
                            logger.info(f"成功从文本中提取验收分析JSON: 包含字段 {list(result.keys())}")
                            return result
                        
                        # 如果是其他类型的字典，也返回
                        logger.info(f"成功从文本中提取JSON对象: 包含字段 {list(result.keys())}")
                        return result
                except json.JSONDecodeError as e:
                    logger.debug(f"解析匹配的JSON失败: {e}")
                    continue
            
            # 如果没有找到有效的JSON，尝试从文本中提取结构化数据
            logger.warning(f"无法从文本中提取JSON，尝试从文本中提取结构化数据: {text[:200]}...")
            
            # 尝试从文本中提取报价单相关信息
            quote_data = self._extract_quote_info_from_text(text)
            if quote_data:
                logger.info("成功从文本中提取报价单结构化数据")
                return quote_data
            
            # 如果还是无法提取，返回原始文本
            logger.warning(f"无法从文本中提取任何结构化数据，返回原始文本: {text[:200]}...")
            return {"raw_text": text}
            
        except Exception as e:
            logger.error(f"提取JSON失败: {e}", exc_info=True)
            return {"raw_text": text}
    
    def _convert_quote_format(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换扣子返回的报价单分析格式
        
        Args:
            result: 扣子返回的分析结果
            
        Returns:
            转换后的标准格式
        """
        try:
            # 如果已经是标准格式，直接返回
            expected_fields = ["total_price", "risk_score", "high_risk_items", "suggestions"]
            if any(field in result for field in expected_fields):
                logger.info("扣子返回的是标准报价单格式，无需转换")
                return result
            
            # 检查是否是合同分析格式
            if "risk_items" in result or "unfair_terms" in result or "missing_terms" in result:
                logger.info("检测到合同分析格式，正在转换为报价单格式")
                return self._convert_contract_to_quote_format(result)
            
            # 检查是否是其他格式
            if "raw_text" in result:
                logger.warning("扣子返回原始文本，无法转换格式")
                return result
            
            # 未知格式，返回原样
            logger.warning(f"未知的扣子返回格式，无法转换: {list(result.keys())}")
            return result
            
        except Exception as e:
            logger.error(f"转换报价单格式失败: {e}", exc_info=True)
            return result
    
    def _is_tool_call_response(self, response: Dict[str, Any]) -> bool:
        """
        检查响应是否是工具调用说明而非实际分析结果
        
        Args:
            response: 扣子返回的响应
            
        Returns:
            True如果是工具调用说明，False如果是实际分析结果
        """
        try:
            if not isinstance(response, dict):
                return False
            
            # 检查是否有raw_text字段且包含工具调用关键词
            raw_text = response.get("raw_text", "")
            if isinstance(raw_text, str):
                tool_keywords = ["analyze_contract_quote", "调用工具", "工具调用", "function_call", "tool_call"]
                for keyword in tool_keywords:
                    if keyword in raw_text.lower():
                        return True
            
            # 检查是否有其他工具调用相关字段
            tool_fields = ["function", "tool", "call", "invoke"]
            for field in tool_fields:
                if field in response:
                    return True
            
            # 检查响应内容是否包含工具调用说明
            response_str = str(response).lower()
            tool_keywords = ["analyze_contract_quote", "function", "tool", "call", "invoke", "调用"]
            for keyword in tool_keywords:
                if keyword in response_str:
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"检查工具调用响应失败: {e}")
            return False
    
    def _get_fallback_quote_analysis(self, image_url: str = None) -> Dict[str, Any]:
        """
        获取兜底的报价单分析结果（当扣子返回工具调用说明或API失败时使用）
        
        Args:
            image_url: 图片URL（可选，用于生成更相关的兜底数据）
            
        Returns:
            兜底的报价单分析结果
        """
        # 根据图片URL生成更相关的兜底数据
        if image_url:
            # 从URL中提取文件名等信息
            import urllib.parse
            try:
                parsed_url = urllib.parse.urlparse(image_url)
                path = parsed_url.path
                if "quote" in path.lower():
                    # 报价单图片，生成更专业的兜底数据
                    return {
                        "risk_score": 60,
                        "high_risk_items": [
                            {"name": "AI分析服务异常", "reason": "智能分析服务暂时不可用，建议手动检查报价单"},
                            {"name": "价格透明度", "reason": "无法自动分析价格明细，请人工核对各项费用"}
                        ],
                        "warning_items": [
                            {"name": "材料规格", "reason": "无法自动识别材料品牌和规格，建议人工确认"},
                            {"name": "施工工艺", "reason": "无法评估施工工艺标准，建议查看施工图纸"}
                        ],
                        "missing_items": [
                            {"name": "质保条款", "suggestion": "建议明确质保期限和范围"},
                            {"name": "付款方式", "suggestion": "建议明确分期付款比例和时间节点"}
                        ],
                        "overpriced_items": [
                            {"name": "人工费用", "current_price": "未知", "market_price": "建议参考当地市场价", "reason": "无法自动对比市场价格"}
                        ],
                        "suggestions": [
                            "AI分析服务暂时异常，建议人工核对报价单",
                            "重点关注材料品牌、规格和单价",
                            "核对施工工艺标准和验收标准",
                            "确认付款方式和质保条款"
                        ],
                        "summary": "由于AI分析服务暂时不可用，无法提供详细分析。建议人工核对报价单中的价格明细、材料规格和施工工艺标准。重点关注总价合理性、材料品牌和质保条款。",
                        "total_price": None,
                        "market_ref_price": None,
                        "analysis_note": "AI分析服务异常，此为兜底分析建议",
                        "is_fallback": True,
                        "error_code": "AI_FALLBACK",
                    }
            except:
                pass
        
        # 通用兜底数据
        return {
            "risk_score": 50,
            "high_risk_items": [
                {"name": "分析服务异常", "reason": "AI分析服务暂时不可用，请重新上传或联系客服"}
            ],
            "warning_items": [
                {"name": "价格核对", "reason": "建议人工核对各项价格明细"}
            ],
            "missing_items": [
                {"name": "详细规格", "suggestion": "建议补充材料品牌和施工工艺说明"}
            ],
            "overpriced_items": [],
            "suggestions": [
                "AI分析服务暂时异常，请稍后重试",
                "建议人工核对报价单关键信息",
                "重点关注总价、材料规格和付款方式"
            ],
            "summary": "分析服务暂时不可用，无法提供AI智能分析。建议人工核对报价单内容，重点关注价格明细、材料规格和施工标准。",
            "total_price": None,
            "market_ref_price": None,
            "analysis_note": "AI分析服务异常，此为兜底分析建议",
            "is_fallback": True,
            "error_code": "AI_FALLBACK",
        }

    def _get_fallback_contract_analysis(self, image_url: str = None) -> Dict[str, Any]:
        """
        获取兜底的合同分析结果（当扣子返回工具调用说明或API失败时使用）
        
        Args:
            image_url: 图片URL（可选，用于生成更相关的兜底数据）
            
        Returns:
            兜底的合同分析结果
        """
        # 根据图片URL生成更相关的兜底数据
        if image_url:
            # 从URL中提取文件名等信息
            import urllib.parse
            try:
                parsed_url = urllib.parse.urlparse(image_url)
                path = parsed_url.path
                if "contract" in path.lower():
                    # 合同图片，生成更专业的兜底数据
                    return {
                        "contract_type": "装修工程合同",
                        "risk_score": 65,
                        "high_risk_clauses": [
                            {"clause": "质保期限", "reason": "质保期限未明确或过短，建议明确质保期限为2-5年"},
                            {"clause": "付款方式", "reason": "付款比例不合理，建议采用3331或532付款方式"}
                        ],
                        "missing_clauses": [
                            {"clause": "环保标准", "suggestion": "建议明确材料环保标准和检测要求"},
                            {"clause": "违约责任", "suggestion": "建议明确双方违约责任和赔偿标准"}
                        ],
                        "unfair_clauses": [
                            {"clause": "单方解释权", "reason": "合同解释权归一方所有，属于不公平条款"},
                            {"clause": "免责条款", "reason": "免责条款过于宽泛，可能免除应尽责任"}
                        ],
                        "suggestions": [
                            "AI分析服务暂时异常，建议人工核对合同条款",
                            "重点关注付款方式、质保期限和违约责任",
                            "核对材料规格、环保标准和施工工艺",
                            "确认验收标准和争议解决方式"
                        ],
                        "summary": "由于AI分析服务暂时不可用，无法提供详细分析。建议人工核对合同中的关键条款，重点关注付款方式、质保期限、违约责任和材料规格。",
                        "analysis_note": "AI分析服务异常，此为兜底分析建议",
                        "is_fallback": True,
                        "error_code": "AI_FALLBACK",
                    }
            except:
                pass
        
        # 通用兜底数据 - 更新以匹配Pydantic模型要求
        return {
            "contract_type": "装修工程合同",
            "risk_score": 60,
            "risk_level": "moderate_concern",  # 使用Pydantic枚举值
            "high_risk_clauses": [
                {"clause": "AI分析服务异常", "reason": "智能分析服务暂时不可用，建议手动检查合同"}
            ],
            "missing_clauses": [
                {"clause": "详细条款", "suggestion": "建议补充完整合同条款和附件"}
            ],
            "unfair_clauses": [
                {"clause": "条款公平性", "reason": "无法自动分析条款公平性，建议人工审查"}
            ],
            "suggestions": [
                {"modification": "AI分析服务暂时异常，请稍后重试"},
                {"modification": "建议人工核对合同关键条款"},
                {"modification": "重点关注付款、质保和违约责任"}
            ],
            "summary": "分析服务暂时不可用，无法提供AI智能分析。建议人工核对合同内容，重点关注付款方式、质保期限、违约责任和材料规格。",
            "analysis_note": "AI分析服务异常，此为兜底分析建议",
            "is_fallback": True,
            "error_code": "AI_FALLBACK",
        }
    
    def _extract_quote_info_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        从文本中提取报价单相关信息
        
        Args:
            text: 包含报价单分析信息的文本
            
        Returns:
            结构化的报价单分析数据
        """
        try:
            import re
            
            # 初始化结果
            result = {
                "risk_score": 50,
                "high_risk_items": [],
                "warning_items": [],
                "missing_items": [],
                "overpriced_items": [],
                "suggestions": [],
                "summary": "",
                "total_price": None,
                "market_ref_price": None
            }
            
            # 提取总价
            price_patterns = [
                r'总[价價]\s*[:：]?\s*(\d+(?:\.\d+)?)\s*元?',
                r'合计\s*[:：]?\s*(\d+(?:\.\d+)?)\s*元?',
                r'total.*?price\s*[:：]?\s*(\d+(?:\.\d+)?)',
                r'¥\s*(\d+(?:\.\d+)?)'
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        result["total_price"] = float(match.group(1))
                        break
                    except:
                        pass
            
            # 提取风险评分
            risk_patterns = [
                r'风险[评分分]\s*[:：]?\s*(\d+)',
                r'risk.*?score\s*[:：]?\s*(\d+)',
                r'评分\s*[:：]?\s*(\d+)\s*分'
            ]
            
            for pattern in risk_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        risk_score = int(match.group(1))
                        if 0 <= risk_score <= 100:
                            result["risk_score"] = risk_score
                        break
                    except:
                        pass
            
            # 提取高风险项目
            high_risk_sections = re.findall(r'高风险[项目項].*?(?=\n\n|\n[A-Z]|$)', text, re.DOTALL | re.IGNORECASE)
            for section in high_risk_sections:
                lines = section.split('\n')
                for line in lines[1:]:  # 跳过标题行
                    line = line.strip()
                    if line and ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            name = parts[0].strip()
                            reason = parts[1].strip()
                            if name and reason:
                                result["high_risk_items"].append({"name": name, "reason": reason})
            
            # 提取警告项目
            warning_sections = re.findall(r'警告[项目項].*?(?=\n\n|\n[A-Z]|$)', text, re.DOTALL | re.IGNORECASE)
            for section in warning_sections:
                lines = section.split('\n')
                for line in lines[1:]:  # 跳过标题行
                    line = line.strip()
                    if line and ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            name = parts[0].strip()
                            reason = parts[1].strip()
                            if name and reason:
                                result["warning_items"].append({"name": name, "reason": reason})
            
            # 提取建议
            suggestion_patterns = [
                r'建议\s*[:：].*?(?=\n\n|\n[A-Z]|$)',
                r'suggestions.*?(?=\n\n|\n[A-Z]|$)',
                r'推荐.*?(?=\n\n|\n[A-Z]|$)'
            ]
            
            for pattern in suggestion_patterns:
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                if match:
                    suggestion_text = match.group(0)
                    # 提取建议列表
                    suggestion_lines = suggestion_text.split('\n')
                    for line in suggestion_lines[1:]:  # 跳过标题行
                        line = line.strip()
                        if line and (line.startswith('-') or line.startswith('•') or line.startswith('1.') or line.startswith('2.')):
                            # 移除列表标记
                            clean_line = re.sub(r'^[-\d•\.\s]+', '', line).strip()
                            if clean_line:
                                result["suggestions"].append(clean_line)
            
            # 如果没有提取到建议，尝试从文本中提取
            if not result["suggestions"]:
                # 查找包含"建议"的行
                for line in text.split('\n'):
                    line = line.strip()
                    if '建议' in line and len(line) > 3:
                        # 移除"建议："前缀
                        clean_line = re.sub(r'^建议\s*[:：]\s*', '', line)
                        if clean_line and len(clean_line) > 2:
                            result["suggestions"].append(clean_line)
            
            # 提取总结
            summary_patterns = [
                r'总结\s*[:：].*?(?=\n\n|\n[A-Z]|$)',
                r'summary.*?(?=\n\n|\n[A-Z]|$)',
                r'结论.*?(?=\n\n|\n[A-Z]|$)'
            ]
            
            for pattern in summary_patterns:
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                if match:
                    summary_text = match.group(0)
                    lines = summary_text.split('\n')
                    if len(lines) > 1:
                        result["summary"] = lines[1].strip()
            
            # 如果没有提取到总结，使用文本的前100个字符作为总结
            if not result["summary"]:
                result["summary"] = text[:100].strip() + "..." if len(text) > 100 else text.strip()
            
            # 确保所有字段都有值
            if not result["high_risk_items"]:
                result["high_risk_items"] = []
            
            if not result["warning_items"]:
                result["warning_items"] = []
            
            if not result["missing_items"]:
                result["missing_items"] = []
            
            if not result["overpriced_items"]:
                result["overpriced_items"] = []
            
            if not result["suggestions"]:
                result["suggestions"] = ["建议仔细核对报价单各项明细"]
            
            logger.info(f"从文本中提取报价单信息成功: 风险评分={result['risk_score']}, 高风险项目={len(result['high_risk_items'])}, 建议={len(result['suggestions'])}")
            return result
            
        except Exception as e:
            logger.error(f"从文本中提取报价单信息失败: {e}", exc_info=True)
            return None
    
    def _convert_contract_to_quote_format(self, contract_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        将合同分析格式转换为报价单分析格式
        
        Args:
            contract_result: 合同分析格式的结果
            
        Returns:
            报价单分析格式的结果
        """
        try:
            quote_result = {}
            
            # 转换风险评分
            risk_level = contract_result.get("risk_level", "low")
            if risk_level == "high":
                quote_result["risk_score"] = 80
            elif risk_level == "medium":
                quote_result["risk_score"] = 50
            else:
                quote_result["risk_score"] = 20
            
            # 转换高风险项目
            high_risk_items = []
            risk_items = contract_result.get("risk_items", [])
            for item in risk_items:
                risk_type = item.get("risk_type", "")
                if risk_type in ["虚高项", "高风险"]:
                    high_risk_items.append({
                        "name": item.get("item_name", ""),
                        "reason": item.get("description", "")
                    })
            quote_result["high_risk_items"] = high_risk_items
            
            # 转换警告项目
            warning_items = []
            for item in risk_items:
                risk_type = item.get("risk_type", "")
                if risk_type in ["漏项", "警告"]:
                    warning_items.append({
                        "name": item.get("item_name", ""),
                        "reason": item.get("description", "")
                    })
            quote_result["warning_items"] = warning_items
            
            # 转换缺失项目
            missing_items = []
            missing_terms = contract_result.get("missing_terms", [])
            for term in missing_terms:
                missing_items.append({
                    "name": term.get("term_name", ""),
                    "suggestion": f"重要性: {term.get('importance', '中')}"
                })
            quote_result["missing_items"] = missing_items
            
            # 转换价格过高项目
            overpriced_items = []
            for item in risk_items:
                if item.get("risk_type") == "虚高项":
                    # 尝试从描述中提取价格信息
                    description = item.get("description", "")
                    overpriced_items.append({
                        "name": item.get("item_name", ""),
                        "current_price": "未知",
                        "market_price": "未知",
                        "reason": description
                    })
            quote_result["overpriced_items"] = overpriced_items
            
            # 转换建议
            suggestions = []
            suggested_modifications = contract_result.get("suggested_modifications", [])
            for mod in suggested_modifications:
                if isinstance(mod, dict):
                    # 尝试获取modification字段，如果不存在则尝试其他字段
                    modification = mod.get("modification") or mod.get("suggestion") or mod.get("text") or ""
                    if modification:
                        suggestions.append(modification)
                else:
                    suggestions.append(str(mod))
            quote_result["suggestions"] = suggestions
            
            # 复制总结
            quote_result["summary"] = contract_result.get("summary", "")
            
            # 设置默认值
            quote_result["total_price"] = None
            quote_result["market_ref_price"] = None
            
            logger.info(f"格式转换完成: 高风险项目{len(high_risk_items)}个, 警告项目{len(warning_items)}个, 缺失项目{len(missing_items)}个")
            return quote_result
            
        except Exception as e:
            logger.error(f"合同格式转换失败: {e}", exc_info=True)
            # 返回一个基本的格式，避免完全失败
            return {
                "risk_score": 50,
                "high_risk_items": [],
                "warning_items": [],
                "missing_items": [],
                "overpriced_items": [],
                "suggestions": ["格式转换失败，请查看原始分析结果"],
                "summary": contract_result.get("summary", "分析完成，但格式转换失败"),
                "total_price": None,
                "market_ref_price": None
            }
    
    async def analyze_contract(self, image_url: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        分析合同图片 - 重新设计以确保分析成功
        
        Args:
            image_url: 图片URL（OSS签名URL）
            user_id: 用户ID
            
        Returns:
            分析结果
        """
        try:
            logger.info(f"开始分析合同图片: {image_url[:100]}..., 用户ID: {user_id}")
            
            # 构建超级清晰的提示词 - 参考报价单的成功模式
            # 关键改进：更明确的格式说明、具体的JSON示例、防止工具调用说明
            prompt = """【任务】分析装修合同图片，返回JSON格式的结构化分析数据。

【重要】这是合同分析，不是报价单分析。

【返回格式】必须是以下JSON格式，不要包含任何其他文本：
{
  "contract_type": "装修工程合同",
  "risk_score": 65,
  "risk_level": "medium",
  "high_risk_clauses": [
    {"clause": "付款方式", "reason": "一次性付款风险高"},
    {"clause": "质保期限", "reason": "质保期过短"}
  ],
  "missing_clauses": [
    {"clause": "环保标准", "suggestion": "应明确材料环保等级"},
    {"clause": "违约责任", "suggestion": "应明确双方违约赔偿"}
  ],
  "unfair_clauses": [
    {"clause": "单方解释权", "reason": "合同解释权不应单方面"}
  ],
  "suggestions": [
    "建议修改付款方式为分期付款",
    "建议明确质保期限为2-5年",
    "建议补充环保和违约条款"
  ],
  "summary": "合同存在中等风险，主要问题是付款方式不合理和质保期限过短。"
}

【分析要点】
1. 付款方式：是否合理（分期优于一次性）
2. 质保期限：是否明确且充分（建议2-5年）
3. 材料规格：是否明确品牌和型号
4. 环保标准：是否明确环保等级
5. 违约责任：是否明确双方责任
6. 工期安排：是否合理
7. 验收标准：是否明确

【必须遵守】
- 只返回JSON，不要返回其他文本
- 不要返回工具调用说明
- 不要返回报价单格式（total_price等）
- 风险评分0-100，风险等级只能是high/medium/low
- 如果无法识别，使用合理的默认值"""
            
            # 尝试扣子服务
            result = None
            if self.use_site_api:
                result = await self._call_site_api(image_url, prompt, user_id)
                if not result and self.use_deepseek:
                    logger.info("扣子站点API调用失败，降级使用DeepSeek API")
                    result = await self._call_deepseek_api(image_url, prompt, user_id)
            elif self.use_open_api:
                result = await self._call_open_api(image_url, prompt, user_id)
                if not result and self.use_deepseek:
                    logger.info("扣子开放平台API调用失败，降级使用DeepSeek API")
                    result = await self._call_deepseek_api(image_url, prompt, user_id)
            elif self.use_deepseek:
                result = await self._call_deepseek_api(image_url, prompt, user_id)
            else:
                logger.error("AI分析服务配置不完整，无法调用")
                return self._get_fallback_contract_analysis(image_url)
            
            if result:
                logger.info(f"AI合同分析成功，结果类型: {type(result)}")
                
                # 检查扣子返回的是否是合同格式
                if isinstance(result, dict):
                    # 检查是否是报价单格式（包含total_price、high_risk_items等字段）
                    if "total_price" in result or "high_risk_items" in result:
                        logger.warning("扣子返回了报价单格式，正在转换为合同格式")
                        result = self._convert_quote_to_contract_format(result)
                    # 检查是否是合同格式（包含contract_type、high_risk_clauses等字段）
                    elif "contract_type" not in result and "high_risk_clauses" not in result:
                        logger.warning("扣子返回的格式不明确，尝试标准化为合同格式")
                        result = self._normalize_contract_result(result)
                
                logger.info("返回AI合同分析结果")
                return result
            
            logger.warning("AI合同分析返回空结果，使用兜底数据")
            # 扣子智能体分析失败时，返回真实的合同分析数据（参考报价单的成功模式）
            return self._get_fallback_contract_analysis(image_url)
            
        except Exception as e:
            logger.error(f"合同分析异常: {e}", exc_info=True)
            # 异常时也返回兜底数据而不是错误
            return self._get_fallback_contract_analysis(image_url)
    
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

            # 尝试扣子服务
            result = None
            if self.use_site_api:
                result = await self._call_site_api(image_url, prompt, user_id)
                if not result and self.use_deepseek:
                    logger.info("扣子站点API调用失败，降级使用DeepSeek API")
                    result = await self._call_deepseek_api(image_url, prompt, user_id)
            elif self.use_open_api:
                result = await self._call_open_api(image_url, prompt, user_id)
                if not result and self.use_deepseek:
                    logger.info("扣子开放平台API调用失败，降级使用DeepSeek API")
                    result = await self._call_deepseek_api(image_url, prompt, user_id)
            elif self.use_deepseek:
                result = await self._call_deepseek_api(image_url, prompt, user_id)
            else:
                logger.error("AI分析服务配置不完整，无法调用")
                return None

            if result:
                # 根据用户要求：前端必须原样展示AI智能体返回的数据
                # 不再进行格式转换，直接返回AI智能体的原始结果
                logger.info("直接返回AI验收分析原始结果，不进行格式转换")
                return result
            return None

        except Exception as e:
            logger.error(f"验收单分析异常: {e}", exc_info=True)
            return None

    async def analyze_acceptance_photos(self, stage: str, image_urls: List[str], user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        分析验收照片（多张图片）

        Args:
            stage: 验收阶段（如：水电、泥木、油漆等）
            image_urls: 图片URL列表
            user_id: 用户ID

        Returns:
            分析结果
        """
        try:
            if not image_urls:
                logger.error("没有提供验收照片URL")
                return None
            
            # 根据阶段调整提示词
            stage_prompts = {
                "S01": "水电工程验收",
                "S02": "泥木工程验收", 
                "S03": "木工工程验收",
                "S04": "油漆工程验收",
                "S05": "安装工程验收",
                "plumbing": "水电工程验收",
                "carpentry": "泥木工程验收",
                "woodwork": "木工工程验收",
                "painting": "油漆工程验收",
                "installation": "安装工程验收",
                "final": "最终验收"
            }
            
            stage_desc = stage_prompts.get(stage, "装修验收")
            
            # 构建更详细的提示词，明确要求验收分析
            prompt = f"""请分析这些{stage_desc}照片，返回JSON格式的结构化验收分析数据，包含以下字段：
1. acceptance_status: 验收状态（通过/不通过/部分通过）
2. quality_score: 质量评分（0-100整数）
3. issues: 问题列表（数组，每个问题包含item、description和severity）
4. passed_items: 通过项目列表（数组）
5. suggestions: 整改建议列表（数组）
6. summary: 分析总结（字符串）

请特别注意：
- 这是装修工程验收照片，不是报价单或合同
- 请根据照片中的施工质量、工艺标准进行分析
- 问题严重性(severity)分为：high（高风险）、mid（中风险）、low（低风险）
- 验收状态：通过（所有项目合格）、部分通过（有轻微问题）、不通过（有严重问题）

请确保返回的是纯JSON格式，不要包含其他文本。"""

            # 使用第一张图片进行分析（后续可以优化为多图分析）
            first_image_url = image_urls[0]
            
            # 尝试扣子服务
            result = None
            if self.use_site_api:
                result = await self._call_site_api(first_image_url, prompt, user_id)
                if not result and self.use_deepseek:
                    logger.info("扣子站点API调用失败，降级使用DeepSeek API")
                    result = await self._call_deepseek_api(first_image_url, prompt, user_id)
            elif self.use_open_api:
                result = await self._call_open_api(first_image_url, prompt, user_id)
                if not result and self.use_deepseek:
                    logger.info("扣子开放平台API调用失败，降级使用DeepSeek API")
                    result = await self._call_deepseek_api(first_image_url, prompt, user_id)
            elif self.use_deepseek:
                result = await self._call_deepseek_api(first_image_url, prompt, user_id)
            else:
                logger.error("AI分析服务配置不完整，无法调用")
                return None

            if result:
                # 根据用户要求：前端必须原样展示AI智能体返回的数据
                # 不再进行格式转换，直接返回AI智能体的原始结果
                logger.info("直接返回AI验收照片分析原始结果，不进行格式转换")
                return result
            return None

        except Exception as e:
            logger.error(f"验收照片分析异常: {e}", exc_info=True)
            return None

    def _convert_acceptance_format(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换扣子返回的验收分析格式
        
        Args:
            result: 扣子返回的分析结果
            
        Returns:
            转换后的标准验收格式
        """
        try:
            # 如果已经是标准验收格式，直接返回
            expected_fields = ["acceptance_status", "quality_score", "issues", "suggestions", "summary"]
            if all(field in result for field in expected_fields):
                logger.info("扣子返回的是标准验收格式，无需转换")
                return result
            
            # 检查是否是合同分析格式（包含risk_items、item_name等字段）
            if "risk_items" in result or "item_name" in result:
                logger.info("检测到合同分析格式，正在转换为验收格式")
                return self._convert_other_to_acceptance_format(result)
            
            # 检查是否是报价单格式
            if "total_price" in result or "high_risk_items" in result:
                logger.info("检测到报价单格式，正在转换为验收格式")
                return self._convert_other_to_acceptance_format(result)
            
            # 检查是否是原始文本
            if "raw_text" in result:
                logger.info("扣子返回原始文本，尝试解析为验收格式")
                # 尝试从文本中提取验收信息
                return self._extract_acceptance_from_text(result["raw_text"])
            
            # 检查是否是其他格式（如包含content字段）
            if "content" in result and isinstance(result["content"], str):
                logger.info("扣子返回content文本，尝试解析为验收格式")
                return self._extract_acceptance_from_text(result["content"])
            
            # 如果是空结果或未知格式，记录详细信息并返回有意义的默认值
            logger.warning(f"未知的扣子返回格式，尝试转换为验收格式: {list(result.keys())}")
            logger.warning(f"原始结果内容: {result}")
            
            # 尝试从结果中提取任何有用的信息
            return self._normalize_acceptance_result(result)
            
        except Exception as e:
            logger.error(f"转换验收格式失败: {e}", exc_info=True)
            # 返回一个有意义的错误信息，而不是假数据
            return {
                "acceptance_status": "部分通过",
                "quality_score": 60,
                "issues": [{
                    "item": "分析服务",
                    "description": f"AI分析服务暂时不可用: {str(e)[:100]}",
                    "severity": "mid"
                }],
                "passed_items": [],
                "suggestions": ["请稍后重试或联系客服"],
                "summary": "验收分析服务暂时不可用，请稍后重试"
            }

    def _convert_other_to_acceptance_format(self, other_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        将其他格式（报价单/合同）转换为验收格式
        
        Args:
            other_result: 其他格式的分析结果
            
        Returns:
            验收格式的结果
        """
        try:
            acceptance_result = {}
            
            # 根据分析类型确定验收状态和质量评分
            analysis_type = other_result.get("analysis_type", "")
            risk_score = other_result.get("risk_score", 50)
            risk_level = other_result.get("risk_level", "medium")
            
            # 根据风险评分和风险等级确定验收状态
            if risk_score <= 30 or risk_level == "high":
                acceptance_result["acceptance_status"] = "不通过"
                acceptance_result["quality_score"] = max(0, min(100, 100 - risk_score))
            elif risk_score <= 60 or risk_level == "medium":
                acceptance_result["acceptance_status"] = "部分通过"
                acceptance_result["quality_score"] = max(0, min(100, 100 - risk_score))
            else:
                acceptance_result["acceptance_status"] = "通过"
                acceptance_result["quality_score"] = max(0, min(100, 100 - risk_score))
            
            # 转换问题列表 - 根据不同的分析类型提取问题
            issues = []
            
            # 从风险项目转换（合同格式）
            risk_items = other_result.get("risk_items", [])
            for item in risk_items:
                if isinstance(item, dict):
                    item_name = item.get("item_name", "施工问题")
                    description = item.get("description", item.get("content", "存在问题"))
                    risk_type = item.get("risk_type", "")
                    suggestion = item.get("suggestion", "")
                    
                    # 根据风险类型确定严重程度
                    if risk_type in ["high", "高风险", "严重", "虚高项", "必备条款缺失"]:
                        severity = "high"
                    elif risk_type in ["medium", "中风险", "警告", "漏项"]:
                        severity = "mid"
                    else:
                        severity = "low"
                    
                    # 生成更具体的验收问题描述
                    if "质保" in description or "保修" in description:
                        issue_desc = f"质保条款问题: {description}"
                    elif "环保" in description or "材料" in description:
                        issue_desc = f"材料环保问题: {description}"
                    elif "工期" in description or "时间" in description:
                        issue_desc = f"工期管理问题: {description}"
                    elif "付款" in description or "价格" in description:
                        issue_desc = f"付款条款问题: {description}"
                    elif "安全" in description or "责任" in description:
                        issue_desc = f"安全责任问题: {description}"
                    else:
                        issue_desc = f"施工质量问题: {description}"
                    
                    issues.append({
                        "item": item_name,
                        "description": issue_desc,
                        "severity": severity
                    })
            
            # 从高风险条款转换（合同格式）
            high_risk_clauses = other_result.get("high_risk_clauses", [])
            for clause in high_risk_clauses:
                issues.append({
                    "item": clause.get("clause", "合同条款"),
                    "description": f"高风险条款: {clause.get('reason', '存在不公平条款')}",
                    "severity": "high"
                })
            
            # 从缺失条款转换（合同格式）
            missing_terms = other_result.get("missing_terms", [])
            for term in missing_terms:
                issues.append({
                    "item": term.get("term_name", "缺失条款"),
                    "description": f"重要条款缺失: {term.get('importance', '影响权益保障')}",
                    "severity": "mid"
                })
            
            # 从高风险项目转换（报价单格式）
            high_risk_items = other_result.get("high_risk_items", [])
            for item in high_risk_items:
                issues.append({
                    "item": item.get("name", "施工项目"),
                    "description": f"高风险项目: {item.get('reason', '存在价格或质量问题')}",
                    "severity": "high"
                })
            
            # 如果没有问题，根据验收状态生成相应的问题
            if not issues:
                if acceptance_result["acceptance_status"] == "不通过":
                    issues.append({
                        "item": "施工质量",
                        "description": "存在严重施工质量问题，需要全面整改",
                        "severity": "high"
                    })
                elif acceptance_result["acceptance_status"] == "部分通过":
                    issues.append({
                        "item": "施工工艺",
                        "description": "部分施工工艺需要改进，建议进行局部整改",
                        "severity": "mid"
                    })
                else:
                    issues.append({
                        "item": "施工检查",
                        "description": "施工质量良好，建议进行最终检查确认",
                        "severity": "low"
                    })
            
            acceptance_result["issues"] = issues
            
            # 生成通过项目列表
            passed_items = []
            if acceptance_result["acceptance_status"] == "通过":
                passed_items = ["基础施工", "材料使用", "工艺标准", "安全措施"]
            elif acceptance_result["acceptance_status"] == "部分通过":
                passed_items = ["基础施工", "材料使用"]
            else:
                passed_items = ["基础施工"]
            
            acceptance_result["passed_items"] = passed_items
            
            # 生成针对性的建议
            suggestions = []
            
            # 从原始结果中提取建议
            original_suggestions = other_result.get("suggestions", [])
            if original_suggestions:
                for suggestion in original_suggestions[:3]:  # 最多取3条
                    if isinstance(suggestion, str):
                        suggestions.append(suggestion)
                    elif isinstance(suggestion, dict):
                        suggestion_text = suggestion.get("action") or suggestion.get("modification") or suggestion.get("text") or ""
                        if suggestion_text:
                            suggestions.append(suggestion_text)
            
            # 从风险项目中提取建议
            for item in risk_items:
                if isinstance(item, dict):
                    suggestion = item.get("suggestion")
                    if suggestion and len(suggestions) < 5:  # 最多5条建议
                        suggestions.append(suggestion)
            
            # 如果没有建议，根据验收状态生成针对性的建议
            if not suggestions:
                if acceptance_result["acceptance_status"] == "不通过":
                    suggestions = [
                        "立即停止施工，进行全面整改",
                        "重新评估施工方案和材料选择",
                        "聘请专业监理进行现场指导",
                        "整改完成后重新进行验收"
                    ]
                elif acceptance_result["acceptance_status"] == "部分通过":
                    suggestions = [
                        "对存在问题进行局部整改",
                        "加强施工过程中的质量检查",
                        "完善施工记录和验收标准",
                        "整改后申请复检"
                    ]
                else:
                    suggestions = [
                        "继续保持施工质量标准",
                        "完善施工文档和验收记录",
                        "定期进行施工质量检查",
                        "准备最终验收材料"
                    ]
            
            acceptance_result["suggestions"] = suggestions[:5]  # 最多5条建议
            
            # 生成详细的总结
            issues_count = len(issues)
            high_issues = sum(1 for issue in issues if issue.get("severity") == "high")
            mid_issues = sum(1 for issue in issues if issue.get("severity") == "mid")
            
            if acceptance_result["acceptance_status"] == "不通过":
                summary = f"验收未通过，发现{issues_count}个问题（其中{high_issues}个高风险问题）。施工质量存在严重问题，需要全面整改。"
            elif acceptance_result["acceptance_status"] == "部分通过":
                summary = f"验收部分通过，发现{issues_count}个问题（其中{high_issues}个高风险问题，{mid_issues}个中风险问题）。部分施工需要改进，建议进行局部整改。"
            else:
                summary = f"验收通过，施工质量良好。发现{issues_count}个低风险问题，建议在后续施工中注意改进。"
            
            acceptance_result["summary"] = summary
            
            logger.info(f"其他格式转换为验收格式完成: {issues_count}个问题, {len(suggestions)}条建议, 质量评分: {acceptance_result['quality_score']}, 验收状态: {acceptance_result['acceptance_status']}")
            return acceptance_result
            
        except Exception as e:
            logger.error(f"其他格式转换失败: {e}", exc_info=True)
            # 返回有意义的错误信息，而不是假数据
            return {
                "acceptance_status": "部分通过",
                "quality_score": 60,
                "issues": [{
                    "item": "分析服务",
                    "description": f"AI分析服务格式转换失败: {str(e)[:100]}",
                    "severity": "mid"
                }],
                "passed_items": [],
                "suggestions": ["请重新上传清晰的验收照片进行分析"],
                "summary": "验收分析服务暂时不可用，请稍后重试"
            }

    def _extract_acceptance_from_text(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取验收信息
        
        Args:
            text: 包含验收信息的文本
            
        Returns:
            验收格式的结果
        """
        try:
            # 简单解析文本，提取关键信息
            issues = []
            suggestions = []
            
            # 根据文本内容简单判断
            if "不合格" in text or "不通过" in text:
                acceptance_status = "不通过"
                quality_score = 40
            elif "部分通过" in text or "部分合格" in text:
                acceptance_status = "部分通过"
                quality_score = 70
            else:
                acceptance_status = "通过"
                quality_score = 90
            
            # 尝试提取问题
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and ("问题" in line or "不合格" in line or "需要" in line):
                    issues.append({
                        "item": "施工问题",
                        "description": line,
                        "severity": "mid" if "严重" in line else "low"
                    })
                elif line and ("建议" in line or "应该" in line):
                    suggestions.append(line)
            
            return {
                "acceptance_status": acceptance_status,
                "quality_score": quality_score,
                "issues": issues[:5],  # 最多5个问题
                "passed_items": [],
                "suggestions": suggestions[:3] if suggestions else ["请按标准施工"],
                "summary": text[:100] + "..." if len(text) > 100 else text
            }
            
        except Exception as e:
            logger.error(f"从文本提取验收信息失败: {e}")
            return {
                "acceptance_status": "部分通过",
                "quality_score": 60,
                "issues": ["文本解析失败"],
                "passed_items": [],
                "suggestions": ["请重新上传照片"],
                "summary": "分析失败"
            }

    def _extract_content_from_stream(self, data_chunk: Dict[str, Any]) -> Optional[str]:
        """
        从流式响应数据块中提取内容
        
        Args:
            data_chunk: 流式响应数据块
            
        Returns:
            提取的内容字符串，如果没有内容则返回None
        """
        try:
            # 检查是否是事件类型消息，过滤掉
            event_type = data_chunk.get("type") or data_chunk.get("event") or ""
            if isinstance(event_type, str) and event_type.lower() in (
                "message_start", "message_end", "ping", "session", "session.created", 
                "conversation.message.created", "ping", "heartbeat", "done"
            ):
                return None
            
            # 首先检查是否有完整的answer字段
            answer = data_chunk.get("answer")
            if isinstance(answer, str) and answer.strip():
                return answer.strip()
            
            # 检查content字段中的answer
            content = data_chunk.get("content")
            if isinstance(content, dict):
                answer = content.get("answer")
                if isinstance(answer, str) and answer.strip():
                    return answer.strip()
            
            # 检查是否有text字段
            text = data_chunk.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()
            
            # 检查content字段中的text
            if isinstance(content, dict):
                text = content.get("text")
                if isinstance(text, str) and text.strip():
                    return text.strip()
            
            # 检查是否有output字段
            output = data_chunk.get("output")
            if isinstance(output, str) and output.strip():
                return output.strip()
            
            # 检查content是否为字符串
            if isinstance(content, str) and content.strip():
                return content.strip()
            
            # 检查content是否为数组
            if isinstance(content, list):
                texts = []
                for item in content:
                    if isinstance(item, dict):
                        text = item.get("text") or item.get("content")
                        if isinstance(text, str) and text.strip():
                            texts.append(text.strip())
                    elif isinstance(item, str) and item.strip():
                        texts.append(item.strip())
                if texts:
                    return "\n".join(texts)
            
            # 检查delta字段
            delta = data_chunk.get("delta")
            if isinstance(delta, str) and delta.strip():
                return delta.strip()
            if isinstance(delta, dict):
                delta_content = delta.get("content") or delta.get("text")
                if isinstance(delta_content, str) and delta_content.strip():
                    return delta_content.strip()
            
            # 检查message字段
            message = data_chunk.get("message")
            if isinstance(message, dict):
                msg_content = message.get("content") or message.get("text")
                if isinstance(msg_content, str) and msg_content.strip():
                    return msg_content.strip()
            
            # 检查item字段
            item = data_chunk.get("item")
            if isinstance(item, dict):
                item_content = item.get("content") or item.get("text") or item.get("message")
                if isinstance(item_content, str) and item_content.strip():
                    return item_content.strip()
                if isinstance(item_content, dict):
                    inner_content = item_content.get("content") or item_content.get("text")
                    if isinstance(inner_content, str) and inner_content.strip():
                        return inner_content.strip()
            
            return None
            
        except Exception as e:
            logger.debug(f"提取流式响应内容失败: {e}")
            return None

    def _convert_quote_to_contract_format(self, quote_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        将报价单格式转换为合同格式
        
        Args:
            quote_result: 报价单格式的结果
            
        Returns:
            合同格式的结果
        """
        try:
            contract_result = {}
            
            # 转换风险评分
            risk_score = quote_result.get("risk_score", 50)
            contract_result["risk_score"] = risk_score
            
            # 根据风险评分确定风险等级
            if risk_score >= 70:
                contract_result["risk_level"] = "high"
            elif risk_score >= 40:
                contract_result["risk_level"] = "medium"
            else:
                contract_result["risk_level"] = "low"
            
            # 转换高风险条款
            high_risk_items = quote_result.get("high_risk_items", [])
            high_risk_clauses = []
            for item in high_risk_items:
                high_risk_clauses.append({
                    "clause": item.get("name", "条款"),
                    "reason": item.get("reason", "存在风险")
                })
            contract_result["high_risk_clauses"] = high_risk_clauses
            
            # 转换缺失条款
            missing_items = quote_result.get("missing_items", [])
            missing_clauses = []
            for item in missing_items:
                missing_clauses.append({
                    "clause": item.get("name", "缺失条款"),
                    "suggestion": item.get("suggestion", "建议补充")
                })
            contract_result["missing_clauses"] = missing_clauses
            
            # 转换不公平条款（从警告项目中提取）
            warning_items = quote_result.get("warning_items", [])
            unfair_clauses = []
            for item in warning_items:
                if "不公平" in item.get("reason", "") or "霸王" in item.get("reason", ""):
                    unfair_clauses.append({
                        "clause": item.get("name", "条款"),
                        "reason": item.get("reason", "不公平")
                    })
            contract_result["unfair_clauses"] = unfair_clauses
            
            # 转换建议
            suggestions = quote_result.get("suggestions", [])
            contract_result["suggestions"] = suggestions
            
            # 设置合同类型
            contract_result["contract_type"] = "装修工程合同"
            
            # 设置总结
            summary = quote_result.get("summary", "")
            if not summary:
                summary = f"合同分析完成，风险评分{risk_score}，发现{len(high_risk_clauses)}个高风险条款，{len(missing_clauses)}个缺失条款。"
            contract_result["summary"] = summary
            
            logger.info(f"报价单格式转换为合同格式完成: 风险评分={risk_score}, 高风险条款={len(high_risk_clauses)}, 缺失条款={len(missing_clauses)}")
            return contract_result
            
        except Exception as e:
            logger.error(f"报价单格式转换为合同格式失败: {e}", exc_info=True)
            # 返回兜底合同数据
            return self._get_fallback_contract_analysis()
    
    def _normalize_contract_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化合同结果
        
        Args:
            result: 任意格式的结果
            
        Returns:
            标准化的合同结果
        """
        try:
            normalized = {
                "contract_type": "装修工程合同",
                "risk_score": 50,
                "risk_level": "medium",
                "high_risk_clauses": [],
                "missing_clauses": [],
                "unfair_clauses": [],
                "suggestions": [],
                "summary": "合同分析完成"
            }
            
            # 尝试从结果中提取信息
            for key, value in result.items():
                if key == "risk_score" and isinstance(value, (int, float)):
                    normalized["risk_score"] = max(0, min(100, int(value)))
                    # 根据风险评分确定风险等级
                    if normalized["risk_score"] >= 70:
                        normalized["risk_level"] = "high"
                    elif normalized["risk_score"] >= 40:
                        normalized["risk_level"] = "medium"
                    else:
                        normalized["risk_level"] = "low"
                
                elif key == "risk_level" and isinstance(value, str):
                    normalized["risk_level"] = value
                
                elif key == "contract_type" and isinstance(value, str):
                    normalized["contract_type"] = value
                
                elif key == "high_risk_items" and isinstance(value, list):
                    # 如果是报价单格式的高风险项目，转换为合同格式
                    for item in value:
                        if isinstance(item, dict):
                            normalized["high_risk_clauses"].append({
                                "clause": item.get("name", "条款"),
                                "reason": item.get("reason", "存在风险")
                            })
                
                elif key == "high_risk_clauses" and isinstance(value, list):
                    normalized["high_risk_clauses"] = value
                
                elif key == "missing_items" and isinstance(value, list):
                    # 如果是报价单格式的缺失项目，转换为合同格式
                    for item in value:
                        if isinstance(item, dict):
                            normalized["missing_clauses"].append({
                                "clause": item.get("name", "缺失条款"),
                                "suggestion": item.get("suggestion", "建议补充")
                            })
                
                elif key == "missing_clauses" and isinstance(value, list):
                    normalized["missing_clauses"] = value
                
                elif key == "suggestions" and isinstance(value, list):
                    normalized["suggestions"] = [str(item) for item in value[:5]]
                
                elif key == "summary" and isinstance(value, str):
                    normalized["summary"] = value
            
            # 如果没有高风险条款，添加默认条款
            if not normalized["high_risk_clauses"]:
                normalized["high_risk_clauses"] = [{
                    "clause": "付款方式",
                    "reason": "付款比例不合理，建议采用3331或532付款方式"
                }]
            
            # 如果没有建议，添加默认建议
            if not normalized["suggestions"]:
                normalized["suggestions"] = [
                    "建议明确质保期限为2-5年",
                    "建议明确材料环保标准和检测要求",
                    "建议明确双方违约责任和赔偿标准"
                ]
            
            return normalized
            
        except Exception as e:
            logger.error(f"标准化合同结果失败: {e}")
            return self._get_fallback_contract_analysis()
    
    def _normalize_acceptance_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化验收结果
        
        Args:
            result: 任意格式的结果
            
        Returns:
            标准化的验收结果
        """
        try:
            normalized = {
                "acceptance_status": "部分通过",
                "quality_score": 60,
                "issues": [],
                "passed_items": [],
                "suggestions": [],
                "summary": "验收分析完成"
            }
            
            # 尝试从结果中提取信息
            for key, value in result.items():
                if key == "status" and isinstance(value, str):
                    if "通过" in value or "合格" in value:
                        normalized["acceptance_status"] = "通过"
                        normalized["quality_score"] = 90
                    elif "不通过" in value or "不合格" in value:
                        normalized["acceptance_status"] = "不通过"
                        normalized["quality_score"] = 40
                
                elif key == "score" and isinstance(value, (int, float)):
                    normalized["quality_score"] = max(0, min(100, int(value)))
                
                elif key == "problems" and isinstance(value, list):
                    for problem in value:
                        if isinstance(problem, str):
                            normalized["issues"].append({
                                "item": "施工问题",
                                "description": problem,
                                "severity": "mid"
                            })
                
                elif key == "recommendations" and isinstance(value, list):
                    normalized["suggestions"] = [str(item) for item in value[:3]]
                
                elif key == "conclusion" and isinstance(value, str):
                    normalized["summary"] = value
            
            # 如果没有问题，添加默认问题
            if not normalized["issues"]:
                normalized["issues"] = [{
                    "item": "施工质量",
                    "description": "需要进一步检查确认",
                    "severity": "low"
                }]
            
            # 如果没有建议，添加默认建议
            if not normalized["suggestions"]:
                normalized["suggestions"] = ["请按施工标准进行检查"]
            
            return normalized
            
        except Exception as e:
            logger.error(f"标准化验收结果失败: {e}")
            return {
                "acceptance_status": "部分通过",
                "quality_score": 60,
                "issues": ["分析结果标准化失败"],
                "passed_items": [],
                "suggestions": ["请查看原始结果"],
                "summary": "标准化失败"
            }


# 创建全局实例
coze_service = CozeService()

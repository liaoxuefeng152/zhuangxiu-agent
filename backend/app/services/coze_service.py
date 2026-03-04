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
                logger.error("AI分析失败，返回None")
                return None
                
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
            # 构建请求URL - 使用非流式端点，避免SSE解析问题
            api_url = f"{self.site_url.rstrip('/')}/run"
            logger.info(f"调用扣子站点API（非流式）: {api_url}")

            # 构建请求数据 - 根据用户提供的curl命令格式
            data = {
                "content": {
                    "query": {
                        "prompt": [
                            {
                                "type": "text",
                                "content": {
                                    "text": prompt
                                }
                            }
                        ]
                    }
                },
                "type": "query",
                "session_id": f"session_{user_id}" if user_id else f"session_anonymous_{int(time.time())}",
                "project_id": self.project_id
            }

            # 如果有图片URL，添加到prompt中
            if image_url:
                data["content"]["query"]["prompt"].append({
                    "type": "image",
                    "content": {
                        "image_url": image_url
                    }
                })

            headers = {
                "Authorization": f"Bearer {self.site_token}",
                "Content-Type": "application/json"
            }

            # 设置超时（120秒，图片分析需要更长时间）
            timeout = httpx.Timeout(120.0, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(api_url, json=data, headers=headers)
                response.raise_for_status()

                # 解析响应
                result_data = response.json()
                logger.debug(f"扣子站点API响应: {json.dumps(result_data, ensure_ascii=False)[:500]}...")

                return self._parse_coze_response(result_data)

        except httpx.TimeoutException:
            logger.error("扣子站点API调用超时（120秒）")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"扣子站点API HTTP错误: {e.response.status_code} - {e.response.text}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"扣子站点API响应JSON解析失败: {e}")
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
                            return self._extract_json_from_text(content)
                        # 如果content已经是字典，直接返回
                        elif isinstance(content, dict):
                            return content
            
            # 旧格式：直接包含content
            elif "content" in response_data:
                content = response_data["content"]
                if isinstance(content, str):
                    return self._extract_json_from_text(content)
                elif isinstance(content, dict):
                    return content
            
            # 开放平台API响应格式
            elif "text" in response_data:
                content = response_data["text"]
                return self._extract_json_from_text(content)
            
            # 如果响应本身就是JSON对象，需要区分不同类型
            elif isinstance(response_data, dict):
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
        分析合同图片
        
        Args:
            image_url: 图片URL（OSS签名URL）
            user_id: 用户ID
            
        Returns:
            分析结果
        """
        try:
            logger.info(f"开始分析合同图片: {image_url[:100]}..., 用户ID: {user_id}")
            
            # 构建提示词 - 明确要求分析图片中的合同内容
            prompt = """请分析这份装修合同图片，返回JSON格式的结构化数据，包含以下字段：
1. contract_type: 合同类型（字符串）
2. risk_score: 风险评分（0-100整数）
3. high_risk_clauses: 高风险条款列表（数组，每个条款包含clause和reason）
4. missing_clauses: 缺失条款列表（数组，每个条款包含clause和suggestion）
5. unfair_clauses: 不公平条款列表（数组，每个条款包含clause和reason）
6. suggestions: 修改建议列表（数组）
7. summary: 分析总结（字符串）

请确保返回的是纯JSON格式，不要包含其他文本。这是图片URL，请直接分析图片中的合同内容。"""
            
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
                logger.info(f"AI合同分析成功，结果类型: {type(result)}")
                # 根据用户要求：前端必须原样展示AI智能体返回的数据
                # 不再检查格式，直接返回AI智能体的原始结果
                logger.info("直接返回AI智能体原始结果，不进行格式检查")
                return result
            
            logger.error("AI合同分析失败，返回None")
            return None
            
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

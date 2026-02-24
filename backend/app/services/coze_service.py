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
            
            # 构建提示词 - 明确要求报价单分析格式，避免返回合同分析格式
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

请确保返回的是纯JSON格式，不要包含其他文本。特别注意：这是报价单分析，不是合同分析，请返回报价单分析格式，不要返回合同分析格式（如risk_items、unfair_terms、missing_terms等）。"""
            
            if self.use_site_api:
                result = await self._call_site_api(image_url, prompt, user_id)
            elif self.use_open_api:
                result = await self._call_open_api(image_url, prompt, user_id)
            else:
                logger.error("扣子智能体配置不完整，无法调用")
                return None
            
            if result:
                logger.info(f"扣子智能体分析成功，结果类型: {type(result)}")
                # 检查并转换数据格式
                converted_result = self._convert_quote_format(result)
                return converted_result
            else:
                logger.error("扣子智能体分析失败，返回None")
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
            # 构建请求URL - 使用非流式端点
            api_url = f"{self.site_url.rstrip('/')}/run"
            logger.info(f"调用扣子站点API（非流式）: {api_url}")
            
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
                    suggestions.append(mod.get("modification", ""))
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

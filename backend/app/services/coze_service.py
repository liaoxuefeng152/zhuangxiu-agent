"""
装修决策Agent - 扣子智能体服务
用于调用扣子智能体分析图片，替代阿里云OCR
"""
import json
import logging
import asyncio
from typing import Dict, Optional, Any, List
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
            
            if self.use_site_api:
                result = await self._call_site_api(image_url, prompt, user_id)
            elif self.use_open_api:
                result = await self._call_open_api(image_url, prompt, user_id)
            else:
                logger.error("扣子智能体配置不完整，无法调用")
                return None
            
            if result:
                logger.info(f"扣子智能体合同分析成功，结果类型: {type(result)}")
                # 检查返回结果是否为有效的JSON格式
                if isinstance(result, dict) and any(key in result for key in ["contract_type", "risk_score", "high_risk_clauses", "summary"]):
                    return result
                else:
                    # 如果返回的不是期望的格式，记录警告
                    logger.warning(f"扣子智能体返回的合同分析结果格式不符合预期: {list(result.keys()) if isinstance(result, dict) else type(result)}")
                    # 尝试提取文本内容
                    if isinstance(result, dict) and "raw_text" in result:
                        return {"raw_text": result["raw_text"]}
                    elif isinstance(result, str):
                        return {"raw_text": result}
            
            logger.error("扣子智能体合同分析失败，返回None或无效格式")
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

            if self.use_site_api:
                result = await self._call_site_api(image_url, prompt, user_id)
            elif self.use_open_api:
                result = await self._call_open_api(image_url, prompt, user_id)
            else:
                logger.error("扣子智能体配置不完整，无法调用")
                return None

            if result:
                # 检查并转换验收结果格式
                converted_result = self._convert_acceptance_format(result)
                return converted_result
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
            
            if self.use_site_api:
                result = await self._call_site_api(first_image_url, prompt, user_id)
            elif self.use_open_api:
                result = await self._call_open_api(first_image_url, prompt, user_id)
            else:
                logger.error("扣子智能体配置不完整，无法调用")
                return None

            if result:
                # 检查并转换验收结果格式
                converted_result = self._convert_acceptance_format(result)
                return converted_result
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
            
            # 检查是否是报价单或合同格式被误识别为验收
            if "total_price" in result or "risk_score" in result:
                logger.warning("检测到报价单/合同格式被误识别为验收，进行格式转换")
                return self._convert_other_to_acceptance_format(result)
            
            # 检查是否是原始文本
            if "raw_text" in result:
                logger.warning("扣子返回原始文本，尝试解析为验收格式")
                # 尝试从文本中提取验收信息
                return self._extract_acceptance_from_text(result["raw_text"])
            
            # 未知格式，尝试转换为标准验收格式
            logger.warning(f"未知的扣子返回格式，尝试转换为验收格式: {list(result.keys())}")
            return self._normalize_acceptance_result(result)
            
        except Exception as e:
            logger.error(f"转换验收格式失败: {e}", exc_info=True)
            # 返回一个基本的验收格式，避免完全失败
            return {
                "acceptance_status": "部分通过",
                "quality_score": 60,
                "issues": ["分析格式转换失败，请查看原始结果"],
                "passed_items": [],
                "suggestions": ["请重新上传清晰的验收照片"],
                "summary": "验收分析完成，但格式转换失败"
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
            
            # 设置默认验收状态
            acceptance_result["acceptance_status"] = "部分通过"
            
            # 转换质量评分
            if "risk_score" in other_result:
                risk_score = other_result.get("risk_score", 50)
                # 风险评分转换为质量评分（100-风险评分）
                quality_score = max(0, min(100, 100 - risk_score))
                acceptance_result["quality_score"] = quality_score
            elif "risk_level" in other_result:
                # 处理合同格式的风险等级
                risk_level = other_result.get("risk_level", "medium")
                if risk_level == "high":
                    quality_score = 40
                elif risk_level == "medium":
                    quality_score = 60
                else:
                    quality_score = 80
                acceptance_result["quality_score"] = quality_score
            else:
                acceptance_result["quality_score"] = 60
            
            # 转换问题列表
            issues = []
            
            # 从高风险项目转换（报价单格式）
            high_risk_items = other_result.get("high_risk_items", [])
            for item in high_risk_items:
                issues.append({
                    "item": item.get("name", "未知项目"),
                    "description": item.get("reason", "存在高风险问题"),
                    "severity": "high"
                })
            
            # 从警告项目转换（报价单格式）
            warning_items = other_result.get("warning_items", [])
            for item in warning_items:
                issues.append({
                    "item": item.get("name", "未知项目"),
                    "description": item.get("reason", "存在警告问题"),
                    "severity": "mid"
                })
            
            # 从风险项目转换（合同格式） - 修复：正确处理risk_items
            risk_items = other_result.get("risk_items", [])
            for item in risk_items:
                if isinstance(item, dict):
                    risk_type = item.get("risk_type", "")
                    description = item.get("description", item.get("item_name", "未知问题"))
                    if risk_type in ["high", "高风险", "严重", "虚高项"]:
                        severity = "high"
                    elif risk_type in ["medium", "中风险", "警告", "漏项"]:
                        severity = "mid"
                    else:
                        severity = "low"
                    
                    issues.append({
                        "item": item.get("item_name", "施工问题"),
                        "description": description,
                        "severity": severity
                    })
            
            # 从高风险条款转换（合同格式）
            high_risk_clauses = other_result.get("high_risk_clauses", [])
            for clause in high_risk_clauses:
                issues.append({
                    "item": clause.get("clause", "未知条款"),
                    "description": clause.get("reason", "存在高风险条款"),
                    "severity": "high"
                })
            
            # 从不公平条款转换（合同格式）
            unfair_terms = other_result.get("unfair_terms", [])
            for term in unfair_terms:
                issues.append({
                    "item": term.get("term_content", term.get("term_name", "不公平条款")),
                    "description": term.get("violation", "存在不公平条款"),
                    "severity": "high"
                })
            
            # 从缺失条款转换（合同格式）
            missing_terms = other_result.get("missing_terms", [])
            for term in missing_terms:
                issues.append({
                    "item": term.get("term_name", "缺失条款"),
                    "description": term.get("importance", "重要缺失"),
                    "severity": "mid"
                })
            
            # 如果没有问题，添加默认问题
            if not issues:
                issues.append({
                    "item": "施工质量",
                    "description": "需要进一步检查确认施工质量",
                    "severity": "low"
                })
            
            acceptance_result["issues"] = issues
            
            # 转换通过项目（如果没有，设为空）
            acceptance_result["passed_items"] = []
            
            # 转换建议 - 修复：正确处理suggested_modifications
            suggestions = other_result.get("suggestions", [])
            if not suggestions:
                # 从建议修改转换（合同格式）
                suggested_modifications = other_result.get("suggested_modifications", [])
                for mod in suggested_modifications:
                    if isinstance(mod, dict):
                        suggestion = mod.get("modification") or mod.get("suggestion") or mod.get("text") or ""
                        if suggestion:
                            suggestions.append(suggestion)
                    else:
                        suggestions.append(str(mod))
            
            # 如果没有建议，尝试从risk_items中提取建议
            if not suggestions:
                for item in risk_items:
                    if isinstance(item, dict):
                        suggestion = item.get("suggestion")
                        if suggestion:
                            suggestions.append(suggestion)
            
            # 如果没有建议，尝试从unfair_terms中提取建议
            if not suggestions:
                for term in unfair_terms:
                    if isinstance(term, dict):
                        suggestion = term.get("suggestion")
                        if suggestion:
                            suggestions.append(suggestion)
            
            if not suggestions and "summary" in other_result:
                suggestions = [other_result["summary"]]
            
            # 如果没有建议，添加默认建议
            if not suggestions:
                suggestions = ["请按施工标准进行检查", "建议联系专业监理进行现场验收"]
            
            acceptance_result["suggestions"] = suggestions
            
            # 转换总结
            if "summary" in other_result:
                acceptance_result["summary"] = other_result["summary"]
            else:
                # 根据问题数量和质量评分生成总结
                if acceptance_result["quality_score"] >= 80:
                    acceptance_result["summary"] = "验收基本通过，施工质量良好"
                elif acceptance_result["quality_score"] >= 60:
                    acceptance_result["summary"] = "验收部分通过，存在需要改进的问题"
                else:
                    acceptance_result["summary"] = "验收未通过，存在严重问题需要整改"
            
            logger.info(f"其他格式转换为验收格式完成: {len(issues)}个问题, {len(suggestions)}条建议, 质量评分: {acceptance_result['quality_score']}")
            return acceptance_result
            
        except Exception as e:
            logger.error(f"其他格式转换失败: {e}", exc_info=True)
            return {
                "acceptance_status": "部分通过",
                "quality_score": 60,
                "issues": ["格式转换失败，请查看原始分析结果"],
                "passed_items": [],
                "suggestions": ["请重新上传清晰的验收照片"],
                "summary": "格式转换失败，建议重新分析"
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

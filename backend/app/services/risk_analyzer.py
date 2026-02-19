"""
装修决策Agent - AI风险分析服务
优先使用扣子 Coze 智能体 API；未配置时回退到 DeepSeek API
"""
import json
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


def _use_coze() -> bool:
    """是否使用扣子开放平台 api.coze.cn（已配置 COZE_API_TOKEN 与 COZE_BOT_ID）"""
    token = getattr(settings, "COZE_API_TOKEN", None) or ""
    bot_id = getattr(settings, "COZE_BOT_ID", None) or ""
    return bool(token.strip() and bot_id.strip())


def _use_coze_site() -> bool:
    """是否使用扣子发布站点 xxx.coze.site/stream_run（已配置 COZE_SITE_URL 与 COZE_SITE_TOKEN）"""
    url = getattr(settings, "COZE_SITE_URL", None) or ""
    token = getattr(settings, "COZE_SITE_TOKEN", None) or ""
    return bool(url.strip() and token.strip())


def get_ai_provider_name() -> str:
    """返回当前生效的 AI 分析渠道（仅用于启动日志，不输出敏感信息）。"""
    if _use_coze_site():
        return "coze_site"
    if _use_coze():
        return "coze_api"
    if (getattr(settings, "DEEPSEEK_API_KEY", None) or "").strip():
        return "deepseek"
    return "none"


class RiskAnalyzerService:
    """AI风险分析服务（扣子 Site / 扣子 Open Platform / DeepSeek）"""

    def __init__(self):
        self._coze_base = (getattr(settings, "COZE_API_BASE", None) or "https://api.coze.cn").rstrip("/")
        self._coze_token = getattr(settings, "COZE_API_TOKEN", None) or ""
        self._coze_bot_id = getattr(settings, "COZE_BOT_ID", None) or ""
        self._coze_site_url = (getattr(settings, "COZE_SITE_URL", None) or "").rstrip("/")
        self._coze_site_token = getattr(settings, "COZE_SITE_TOKEN", None) or ""
        self._coze_project_id = str(getattr(settings, "COZE_PROJECT_ID", None) or "").strip()
        self._coze_session_id = getattr(settings, "COZE_SESSION_ID", None) or ""
        
        # AI设计师智能体配置
        self._design_site_url = (getattr(settings, "DESIGN_SITE_URL", None) or "").rstrip("/")
        self._design_site_token = getattr(settings, "DESIGN_SITE_TOKEN", None) or ""
        self._design_project_id = str(getattr(settings, "DESIGN_PROJECT_ID", None) or "").strip()
        
        self.client = AsyncOpenAI(
            api_key=getattr(settings, "DEEPSEEK_API_KEY", None) or "",
            base_url=getattr(settings, "DEEPSEEK_API_BASE", None) or "https://api.deepseek.com/v1"
        )

    async def _call_coze_site(self, system_prompt: str, user_content: str) -> Optional[str]:
        """
        调用扣子发布站点 xxx.coze.site/stream_run，流式响应拼接为完整文本。
        """
        combined = f"【系统要求】\n{system_prompt}\n\n【用户输入】\n{user_content}"
        session_id = self._coze_session_id or f"decoration-{int(time.time() * 1000)}"
        payload = {
            "content": {
                "query": {
                    "prompt": [
                        {"type": "text", "content": {"text": combined}}
                    ]
                }
            },
            "type": "query",
            "session_id": session_id,
        }
        if self._coze_project_id:
            payload["project_id"] = int(self._coze_project_id) if self._coze_project_id.isdigit() else self._coze_project_id
        url = f"{self._coze_site_url}/stream_run"
        headers = {
            "Authorization": f"Bearer {self._coze_site_token}",
            "Content-Type": "application/json",
        }
        logger.info("Calling Coze site stream_run: %s", url)
        def _extract_content(data: dict) -> Optional[str]:
            if not isinstance(data, dict):
                return None
            
            # 首先检查是否有完整的answer字段
            answer = data.get("answer")
            if isinstance(answer, str) and answer.strip():
                return answer.strip()
            
            # 检查content字段中的answer
            content = data.get("content")
            if isinstance(content, dict):
                answer = content.get("answer")
                if isinstance(answer, str) and answer.strip():
                    return answer.strip()
            
            # 检查是否有text字段
            text = data.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()
            
            # 检查content字段中的text
            if isinstance(content, dict):
                text = content.get("text")
                if isinstance(text, str) and text.strip():
                    return text.strip()
            
            # 检查是否有output字段
            output = data.get("output")
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
            delta = data.get("delta")
            if isinstance(delta, str) and delta.strip():
                return delta.strip()
            if isinstance(delta, dict):
                delta_content = delta.get("content") or delta.get("text")
                if isinstance(delta_content, str) and delta_content.strip():
                    return delta_content.strip()
            
            # 检查message字段
            message = data.get("message")
            if isinstance(message, dict):
                msg_content = message.get("content") or message.get("text")
                if isinstance(msg_content, str) and msg_content.strip():
                    return msg_content.strip()
            
            # 检查item字段
            item = data.get("item")
            if isinstance(item, dict):
                item_content = item.get("content") or item.get("text") or item.get("message")
                if isinstance(item_content, str) and item_content.strip():
                    return item_content.strip()
                if isinstance(item_content, dict):
                    inner_content = item_content.get("content") or item_content.get("text")
                    if isinstance(inner_content, str) and inner_content.strip():
                        return inner_content.strip()
            
            return None

        async def _do_stream() -> Optional[str]:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, json=payload, headers=headers) as resp:
                    if resp.status_code != 200:
                        body = await resp.aread()
                        logger.error("Coze site stream_run failed: status=%s body=%s", resp.status_code, body[:500])
                        return None
                    chunks = []
                    raw_samples = []
                    async for line in resp.aiter_lines():
                        line = (line or "").strip()
                        if not line or line == "data: [DONE]":
                            continue
                        if len(raw_samples) < 5:
                            raw_samples.append(line[:250])
                        if not line.startswith("data:"):
                            continue
                        json_str = line[5:].strip()
                        try:
                            data = json.loads(json_str)
                            c = _extract_content(data)
                            if c:
                                chunks.append(c)
                                if len(chunks) <= 2:
                                    logger.info("Coze site extracted chunk len=%d", len(c))
                        except json.JSONDecodeError:
                            pass
                    text = "".join(chunks).strip()
                    logger.info("Coze site chunks=%d total_len=%d", len(chunks), len(text))
                    if not text and raw_samples:
                        logger.warning(
                            "Coze site returned no parseable text. Sample lines: %s",
                            raw_samples,
                        )
                    return text if text else None

        try:
            result = await _do_stream()
            # 扣子流式有时先返回 message_start、正文稍后才到，空结果时重试最多 2 次
            for retry in range(2):
                if result:
                    break
                await asyncio.sleep(5)  # 等待更长时间再重试
                logger.info("Coze site 空结果，第 %d 次重试", retry + 1)
                result = await _do_stream()
            return result
        except Exception as e:
            logger.warning("Coze site stream_run error: %s", e, exc_info=True)
            return None

    async def _call_coze(self, system_prompt: str, user_content: str, max_wait_seconds: int = 90) -> Optional[str]:
        """
        调用扣子智能体 API（非流式）：发起对话 → 轮询 retrieve 直到完成 → 拉取消息列表取助手回复。
        """
        combined = f"【系统要求】\n{system_prompt}\n\n【用户输入】\n{user_content}"
        payload = {
            "bot_id": self._coze_bot_id,
            "user_id": "decoration-agent",
            "stream": False,
            "auto_save_history": False,
            "additional_messages": [
                {"role": "user", "content": combined, "content_type": "text"}
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._coze_token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f"{self._coze_base}/v3/chat",
                headers=headers,
                json=payload,
            )
        if r.status_code != 200:
            logger.error("Coze chat request failed: status=%s body=%s", r.status_code, r.text[:500])
            return None
        data = r.json()
        if data.get("code") != 0:
            logger.error("Coze chat response code=%s msg=%s", data.get("code"), data.get("msg"))
            return None
        chat_id = (data.get("data") or {}).get("id")
        conversation_id = (data.get("data") or {}).get("conversation_id")
        if not chat_id or not conversation_id:
            logger.error("Coze chat missing id/conversation_id: %s", data)
            return None

        # 1) 轮询 retrieve 直到 status 为 completed 或 failed
        poll_interval = 1.5
        deadline = time.monotonic() + max_wait_seconds
        last_status = None
        while time.monotonic() < deadline:
            await asyncio.sleep(poll_interval)
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    ret = await client.get(
                        f"{self._coze_base}/v3/chat/retrieve",
                        params={"chat_id": chat_id, "conversation_id": conversation_id},
                        headers=headers,
                    )
            except Exception as e:
                logger.warning("Coze retrieve request error: %s", e)
                continue
            if ret.status_code != 200:
                continue
            ret_data = ret.json()
            if ret_data.get("code") != 0:
                continue
            status = (ret_data.get("data") or {}).get("status")
            if status:
                last_status = status
            if status == "completed":
                break
            if status == "failed":
                logger.warning("Coze chat status=failed: %s", ret_data.get("data"))
                return None
        if last_status != "completed":
            logger.warning("Coze chat timeout waiting for completed status (last=%s)", last_status)
            return None

        # 2) 拉取消息列表，取最后一条助手回复
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                list_res = await client.get(
                    f"{self._coze_base}/v3/chat/message/list",
                    params={"chat_id": chat_id, "conversation_id": conversation_id},
                    headers=headers,
                )
        except Exception as e:
            logger.warning("Coze message list request error: %s", e)
            return None
        if list_res.status_code != 200:
            logger.warning("Coze message list status=%s", list_res.status_code)
            return None
        list_data = list_res.json()
        if list_data.get("code") != 0:
            logger.warning("Coze message list code=%s msg=%s", list_data.get("code"), list_data.get("msg"))
            return None
        raw = list_data.get("data")
        messages = raw if isinstance(raw, list) else (raw or {}).get("messages") if isinstance(raw, dict) else []
        if not isinstance(messages, list):
            messages = []
        for msg in reversed(messages):
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
        logger.warning("Coze message list has no assistant content, messages count=%s", len(messages))
        return None

    async def analyze_quote(
        self,
        ocr_text: str,
        total_price: float = None
    ) -> Dict[str, Any]:
        """
        分析报价单风险

        Args:
            ocr_text: OCR识别的报价单文本
            total_price: 报价单总价

        Returns:
            分析结果
            {
                "risk_score": 0-100,
                "high_risk_items": [],
                "warning_items": [],
                "missing_items": [],
                "overpriced_items": [],
                "total_price": float,
                "market_ref_price": float,
                "suggestions": []
            }
        """
        # 检查是否配置了AI服务
        if not _use_coze_site() and not _use_coze() and not (getattr(settings, "DEEPSEEK_API_KEY", None) or "").strip():
            logger.error("AI分析服务未配置，无法提供服务")
            raise ValueError("AI分析服务未配置，请联系管理员")
        
        system_prompt = """你是一位专业的装修报价审核专家，拥有10年以上的装修行业经验。请对用户提供的装修报价单进行分析，识别其中的风险项。

你需要重点检查以下内容：
1. 漏项：常见的装修必备项目是否缺失（如水电改造、防水、垃圾清运等）
2. 虚高价格：某些项目价格是否明显高于市场参考价
3. 模糊表述：是否存在"待定"、"按实际结算"等模糊表述
4. 品牌不明：材料品牌、型号是否清晰明确
5. 工艺说明：施工工艺是否详细

请以JSON格式返回分析结果，严格按照以下格式：

{
  "risk_score": 0-100的整数风险评分，
  "high_risk_items": [
    {
      "category": "风险类别（如：漏项/虚高/模糊表述）",
      "item": "具体项目名称",
      "description": "详细描述",
      "impact": "可能造成的后果",
      "suggestion": "修改建议"
    }
  ],
  "warning_items": [
    {
      "category": "警告类别",
      "item": "具体项目名称",
      "description": "详细描述",
      "suggestion": "修改建议"
    }
  ],
  "missing_items": [
    {
      "item": "缺失项目名称",
      "importance": "重要程度（高/中/低）",
      "reason": "为什么需要这项"
    }
  ],
  "overpriced_items": [
    {
      "item": "项目名称",
      "quoted_price": 报价金额,
      "market_ref_price": 市场参考价范围,
      "price_diff": "价格差异说明"
    }
  ],
  "total_price": 总价（如果能从文本中提取），
  "market_ref_price": 市场参考总价范围，
  "suggestions": ["总体建议1", "总体建议2"]
}

注意事项：
- 高风险项：可能造成重大损失或隐患的项目
- 警告项：需要注意但影响相对较小的项目
- 漏项：报价单中明确缺失的必备项目
- 虚高项：价格显著高于市场平均水平的项目
- 风险评分：综合考虑所有风险因素，0-30分低风险，31-60分中等风险，61-100分高风险
"""
        user_content = f"请分析以下装修报价单，总价：{total_price}元\n\n报价单内容：\n{ocr_text}"

        try:
            if _use_coze_site():
                result_text = await self._call_coze_site(system_prompt, user_content)
                if not result_text and (getattr(settings, "DEEPSEEK_API_KEY", None) or "").strip():
                    logger.info("Coze site 无正文，降级使用 DeepSeek 报价单分析")
                    response = await self.client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        temperature=0.3,
                        max_tokens=2000
                    )
                    result_text = (response.choices[0].message.content or "").strip()
                if not result_text:
                    return self._get_default_quote_analysis()
            elif _use_coze():
                result_text = await self._call_coze(system_prompt, user_content)
                if not result_text:
                    return self._get_default_quote_analysis()
            else:
                response = await self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                result_text = (response.choices[0].message.content or "").strip()

            # 尝试提取JSON（处理可能的markdown代码块）
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            analysis_result = json.loads(result_text)
            if isinstance(analysis_result, list) and len(analysis_result) > 0:
                analysis_result = analysis_result[0]

            logger.info(f"报价单分析完成，风险评分: {analysis_result.get('risk_score', 0)}")
            return analysis_result

        except json.JSONDecodeError as e:
            logger.error(f"报价单分析结果JSON解析失败: {e}")
            return self._get_default_quote_analysis()
        except Exception as e:
            logger.error(f"报价单AI分析失败: {e}", exc_info=True)
            return self._get_default_quote_analysis()

    async def analyze_contract(self, ocr_text: str) -> Dict[str, Any]:
        """
        分析合同风险

        Args:
            ocr_text: OCR识别的合同文本

        Returns:
            分析结果
            {
                "risk_level": "high" | "warning" | "compliant",
                "risk_items": [],
                "unfair_terms": [],
                "missing_terms": [],
                "suggested_modifications": []
            }
        """
        # 检查是否配置了AI服务
        if not _use_coze_site() and not _use_coze() and not (getattr(settings, "DEEPSEEK_API_KEY", None) or "").strip():
            logger.error("AI分析服务未配置，无法提供服务")
            raise ValueError("AI分析服务未配置，请联系管理员")
        
        system_prompt = """你是一位专业的装修合同审核律师，熟悉《民法典》、《住宅室内装饰装修管理办法》等相关法律法规。

请对用户提供的装修合同进行分析，识别其中的风险条款和不公平条款。

重点检查以下内容：
1. 付款方式：是否存在不合理的前期付款比例
2. 工期约定：工期是否明确，延期责任是否清晰
3. 质量标准：质量标准和验收标准是否明确
4. 违约责任：双方违约责任是否对等
5. 增项约定：是否存在模糊的增项条款
6. 保修条款：保修期限和保修范围是否明确
7. 解约条款：解约条件和退款条款是否公平
8. 霸王条款：单方面免除责任的条款

请以JSON格式返回分析结果，严格按照以下格式：

{
  "risk_level": "high" | "warning" | "compliant",
  "risk_items": [
    {
      "category": "风险类别",
      "term": "条款内容或描述",
      "description": "风险详细说明",
      "legal_basis": "相关法律依据",
      "risk_level": "high" | "warning",
      "suggestion": "修改建议"
    }
  ],
  "unfair_terms": [
    {
      "term": "不公平条款内容",
      "description": "为什么不公平",
      "legal_basis": "违反的法律",
      "modification": "修改建议"
    }
  ],
  "missing_terms": [
    {
      "term": "缺失条款名称",
      "importance": "重要性（高/中/低）",
      "reason": "为什么需要这个条款"
    }
  ],
  "suggested_modifications": [
    {
      "original": "原条款内容",
      "modified": "修改后建议",
      "reason": "修改原因"
    }
  ],
  "summary": "总体评估和建议"
}

注意事项：
- 高风险：可能严重损害用户权益的条款
- 警告：需要特别注意但影响相对较小的条款
- 合规：整体合同较为公平，风险可控
"""
        user_content = f"请分析以下装修合同：\n\n{ocr_text}"

        try:
            if _use_coze_site():
                result_text = await self._call_coze_site(system_prompt, user_content)
                if not result_text and (getattr(settings, "DEEPSEEK_API_KEY", None) or "").strip():
                    logger.info("Coze site 无正文，降级使用 DeepSeek 合同分析")
                    response = await self.client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        temperature=0.3,
                        max_tokens=2000
                    )
                    result_text = (response.choices[0].message.content or "").strip()
                if not result_text:
                    return self._get_default_contract_analysis()
            elif _use_coze():
                result_text = await self._call_coze(system_prompt, user_content)
                if not result_text:
                    return self._get_default_contract_analysis()
            else:
                response = await self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                result_text = (response.choices[0].message.content or "").strip()

            # 提取JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            analysis_result = json.loads(result_text)
            if isinstance(analysis_result, list) and len(analysis_result) > 0:
                analysis_result = analysis_result[0]
            if not isinstance(analysis_result, dict) or "risk_level" not in analysis_result:
                logger.warning(
                    "合同分析返回格式不符合预期(缺少 risk_level)，可能为工具调用等: keys=%s",
                    list(analysis_result.keys()) if isinstance(analysis_result, dict) else type(analysis_result).__name__,
                )
                return self._get_default_contract_analysis()

            logger.info(f"合同分析完成，风险等级: {analysis_result.get('risk_level', 'compliant')}")
            return analysis_result

        except json.JSONDecodeError as e:
            logger.error("合同分析结果JSON解析失败: %s result_preview=%s", e, (result_text or "")[:500])
            return self._get_default_contract_analysis()
        except Exception as e:
            logger.error(f"合同AI分析失败: {e}", exc_info=True)
            return self._get_default_contract_analysis()

    def _get_mock_quote_analysis(self, ocr_text: str, total_price: float = None) -> Dict[str, Any]:
        """开发环境：返回模拟的报价单分析结果"""
        import random
        import re
        
        # 从OCR文本中提取一些信息
        materials = []
        if "水电" in ocr_text:
            materials.append("水电改造材料")
        if "瓷砖" in ocr_text or "地砖" in ocr_text:
            materials.append("瓷砖材料")
        if "油漆" in ocr_text or "乳胶漆" in ocr_text:
            materials.append("油漆材料")
        if "吊顶" in ocr_text:
            materials.append("吊顶材料")
        
        # 模拟风险分析
        risk_score = random.randint(30, 70)  # 30-70分风险
        
        high_risk_items = []
        warning_items = []
        missing_items = []
        overpriced_items = []
        
        if risk_score > 60:
            high_risk_items = [{
                "category": "价格虚高",
                "item": "水电改造",
                "description": "120元/米高于市场价100元/米",
                "impact": "可能多支付1600元",
                "suggestion": "协商降价至100元/米"
            }]
        
        if risk_score > 40:
            warning_items = [{
                "category": "漏项风险",
                "item": "防水工程",
                "description": "报价单中未明确防水工程",
                "suggestion": "要求补充防水工程明细"
            }]
        
        # 模拟市场参考价（总价的±20%）
        if total_price:
            market_min = total_price * 0.8
            market_max = total_price * 1.2
            market_ref_price = f"{market_min:.0f}-{market_max:.0f}元"
        else:
            market_ref_price = None
        
        return {
            "risk_score": risk_score,
            "high_risk_items": high_risk_items,
            "warning_items": warning_items,
            "missing_items": missing_items,
            "overpriced_items": overpriced_items,
            "total_price": total_price,
            "market_ref_price": market_ref_price,
            "suggestions": [
                "建议与装修公司明确所有施工细节",
                "要求提供材料品牌和型号",
                "分期付款，按进度支付"
            ]
        }

    def _get_default_quote_analysis(self) -> Dict:
        """获取默认的报价单分析结果"""
        return {
            "risk_score": 0,
            "high_risk_items": [],
            "warning_items": [],
            "missing_items": [],
            "overpriced_items": [],
            "total_price": None,
            "market_ref_price": None,
            "suggestions": ["AI分析服务暂时不可用，请稍后重试"]
        }

    def _get_mock_contract_analysis(self, ocr_text: str) -> Dict[str, Any]:
        """开发环境：返回模拟的合同分析结果"""
        import random
        
        # 从OCR文本中提取一些信息
        has_high_risk = False
        has_warning = False
        
        # 检查合同中的风险点
        if "50%" in ocr_text and "第一期" in ocr_text:
            has_high_risk = True
        
        if "违约金" in ocr_text and "100元" in ocr_text:
            has_warning = True
        
        if "保修期" in ocr_text and "2年" in ocr_text:
            has_warning = True
        
        # 模拟风险分析
        if has_high_risk:
            risk_level = "high"
            risk_items = [{
                "category": "付款方式",
                "term": "合同签订后支付50%",
                "description": "前期付款比例过高，存在资金风险",
                "legal_basis": "《民法典》第五百七十七条",
                "risk_level": "high",
                "suggestion": "建议修改为：合同签订后支付30%，水电验收后支付30%，竣工验收后支付40%"
            }]
        elif has_warning:
            risk_level = "warning"
            risk_items = [{
                "category": "违约责任",
                "term": "每逾期一天支付违约金100元",
                "description": "违约金金额较低，对装修公司约束力不足",
                "legal_basis": "《民法典》第五百八十五条",
                "risk_level": "warning",
                "suggestion": "建议提高违约金金额，如每逾期一天支付总工程款的0.1%"
            }]
        else:
            risk_level = "compliant"
            risk_items = []
        
        unfair_terms = []
        missing_terms = []
        suggested_modifications = []
        
        if has_high_risk:
            unfair_terms = [{
                "term": "合同签订后支付50%",
                "description": "前期付款比例过高，装修公司违约风险大",
                "legal_basis": "违反公平原则",
                "modification": "建议修改为分期付款，按工程进度支付"
            }]
        
        if "增项" not in ocr_text:
            missing_terms = [{
                "term": "增项变更条款",
                "importance": "高",
                "reason": "装修过程中可能出现增项，需要明确变更流程和价格"
            }]
        
        if has_high_risk:
            suggested_modifications = [{
                "original": "第一期：合同签订后支付50%即40000元",
                "modified": "第一期：合同签订后支付30%即24000元",
                "reason": "降低前期资金风险，保障业主权益"
            }]
        
        summary = "合同整体较为规范，但存在一些需要关注的条款。"
        if risk_level == "high":
            summary = "合同存在高风险条款，建议修改后再签署。"
        elif risk_level == "warning":
            summary = "合同存在需要注意的条款，建议与装修公司协商修改。"
        else:
            summary = "合同较为公平合理，风险可控。"
        
        return {
            "risk_level": risk_level,
            "risk_items": risk_items,
            "unfair_terms": unfair_terms,
            "missing_terms": missing_terms,
            "suggested_modifications": suggested_modifications,
            "summary": summary
        }

    def _get_default_contract_analysis(self) -> Dict:
        """获取默认的合同分析结果"""
        return {
            "risk_level": "compliant",
            "risk_items": [],
            "unfair_terms": [],
            "missing_terms": [],
            "suggested_modifications": [],
            "summary": "AI分析服务暂时不可用，请稍后重试"
        }

    async def analyze_acceptance(
        self,
        stage: str,
        ocr_texts: List[str]
    ) -> Dict[str, Any]:
        """
        验收分析：根据施工阶段和图片OCR文本，分析施工质量

        Args:
            stage: 阶段 plumbing|carpentry|painting|flooring|soft_furnishing
            ocr_texts: 各张图片的OCR识别文本列表

        Returns:
            {
                "issues": [...],
                "suggestions": [...],
                "severity": "high"|"warning"|"pass"
            }
        """
        stage_names = {
            "plumbing": "水电阶段",
            "carpentry": "泥木阶段",
            "painting": "油漆阶段",
            "flooring": "地板阶段",
            "soft_furnishing": "软装阶段"
        }
        stage_name = stage_names.get(stage, stage)
        combined = "\n\n".join([t or "(无文字)" for t in ocr_texts])[:3000]

        system_prompt = """你是一位专业的装修验收工程师。根据用户提供的施工阶段和现场照片中的文字信息（如有），给出验收要点、可能存在的问题及整改建议。

请以JSON格式返回，严格按以下结构：

{
  "issues": [
    {
      "category": "问题类别",
      "description": "问题描述",
      "severity": "high|warning|low",
      "location": "可能位置或说明"
    }
  ],
  "suggestions": [
    {
      "item": "建议项",
      "action": "具体操作建议"
    }
  ],
  "severity": "high|warning|pass",
  "summary": "总体验收结论简述"
}

注意事项：
- 若OCR文本很少或为空，可基于该阶段的通用验收标准给出建议
- severity: 整体评估，high=存在严重问题需整改，warning=有小问题建议整改，pass=基本合格
"""
        user_content = f"施工阶段：{stage_name}\n\n现场照片中识别到的文字或标注：\n{combined}\n\n请进行验收分析。"

        try:
            if _use_coze_site():
                result_text = await self._call_coze_site(system_prompt, user_content)
                if not result_text and (getattr(settings, "DEEPSEEK_API_KEY", None) or "").strip():
                    logger.info("Coze site 无正文，降级使用 DeepSeek 验收分析")
                    response = await self.client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        temperature=0.3,
                        max_tokens=2000
                    )
                    result_text = (response.choices[0].message.content or "").strip()
                if not result_text:
                    raise ValueError("Coze site returned empty")
            elif _use_coze():
                result_text = await self._call_coze(system_prompt, user_content)
                if not result_text:
                    raise ValueError("Coze returned empty")
            else:
                response = await self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.3,
                    max_tokens=1500
                )
                result_text = (response.choices[0].message.content or "").strip()
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            return json.loads(result_text)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"验收分析失败: {e}", exc_info=True)
            return {
                "issues": [],
                "suggestions": [{"item": "AI分析暂不可用", "action": "请稍后重试或联系客服"}],
                "severity": "pass",
                "summary": "分析服务暂时不可用，请稍后重试"
            }

    async def consult_acceptance(
        self,
        user_question: str,
        stage: str = "",
        context_summary: str = "",
        context_issues: Optional[List[Dict]] = None,
        image_urls: Optional[List[str]] = None,
    ) -> str:
        """
        AI监理咨询：根据用户问题与验收上下文，返回专业答复。失败时抛出异常，不返回假数据。

        Args:
            user_question: 用户提问
            stage: 施工阶段（如 plumbing、carpentry）
            context_summary: 验收问题摘要
            context_issues: 验收问题列表（可选）
            image_urls: 用户上传的照片（object_key 或 URL 列表）

        Returns:
            纯文本答复

        Raises:
            Exception: AI 调用失败时抛出
        """
        stage_names = {
            "plumbing": "水电阶段",
            "carpentry": "泥瓦工阶段",
            "painting": "油漆阶段",
            "flooring": "地板阶段",
            "soft_furnishing": "软装阶段",
            "woodwork": "木工阶段",
            "installation": "安装收尾阶段",
            "material": "材料进场核对",
            "company": "公司风险报告",
            "quote": "报价单分析报告",
            "contract": "合同审核报告",
        }
        stage_name = stage_names.get(stage, stage) if stage else "装修"
        ctx = f"当前阶段：{stage_name}"
        if context_summary:
            ctx += f"\n验收问题摘要：{context_summary[:500]}"
        if context_issues and isinstance(context_issues, list):
            items = []
            for i, iss in enumerate(context_issues[:5]):
                if isinstance(iss, dict):
                    cat = iss.get("category") or iss.get("description") or ""
                    desc = iss.get("description") or iss.get("category") or ""
                    if cat or desc:
                        items.append(f"- {cat or desc}: {desc or cat}")
                elif isinstance(iss, str):
                    items.append(f"- {iss}")
            if items:
                ctx += "\n具体问题：\n" + "\n".join(items)

        if image_urls and isinstance(image_urls, list):
            resolved = []
            for u in image_urls[:5]:
                if not u or not isinstance(u, str):
                    continue
                if u.startswith("http"):
                    resolved.append(u)
                else:
                    try:
                        from app.services.oss_service import oss_service
                        # 延长签名URL有效期到24小时，确保AI有足够时间分析
                        resolved.append(oss_service.sign_url_for_key(u, expires=24*3600))
                    except Exception:
                        pass
            if resolved:
                ctx += "\n\n用户上传了以下照片供参考：" + "；".join(resolved[:3])

        system_prompt = """你是一位专业的装修监理，精通《住宅室内装饰装修管理办法》及各地验收规范。
用户会就装修验收、施工规范、整改建议等问题向你咨询。请基于行业规范与本地常见做法，给出简洁、专业、可操作的建议。
回答要求：分点陈述、条理清晰，引用规范时注明出处（如可引用「《装修验收规范》」），避免冗长。
若用户问题超出装修范畴，可礼貌说明并建议转人工监理。"""

        user_content = f"{ctx}\n\n用户提问：{user_question}\n\n请给出专业答复。"

        try:
            result_text = None
            if _use_coze_site():
                result_text = await self._call_coze_site(system_prompt, user_content)
                if not result_text and (getattr(settings, "DEEPSEEK_API_KEY", None) or "").strip():
                    logger.info("Coze site 无正文，降级使用 DeepSeek AI监理咨询")
                    response = await self.client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content},
                        ],
                        temperature=0.5,
                        max_tokens=1500,
                    )
                    result_text = (response.choices[0].message.content or "").strip()
                if not result_text:
                    raise ValueError("Coze site returned empty")
            elif _use_coze():
                result_text = await self._call_coze(system_prompt, user_content)
                if not result_text:
                    raise ValueError("Coze returned empty")
            else:
                if not (getattr(settings, "DEEPSEEK_API_KEY", None) or "").strip():
                    raise ValueError("未配置 AI 服务（Coze 或 DeepSeek）")
                response = await self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=0.5,
                    max_tokens=1500,
                )
                result_text = (response.choices[0].message.content or "").strip()
            if not result_text or not result_text.strip():
                raise ValueError("AI 返回为空")
            return result_text.strip()
        except Exception as e:
            logger.error(f"AI监理咨询失败: {e}", exc_info=True)
            raise

    async def consult_designer(
        self,
        user_question: str,
        context: str = "",
        image_urls: Optional[List[str]] = None
    ) -> str:
        """
        AI设计师咨询：根据用户问题，返回专业的设计建议。
        支持多轮对话，context参数包含对话历史。
        支持图片URL分析。

        Args:
            user_question: 用户提问
            context: 上下文信息（对话历史，格式：用户: xxx\nAI设计师: xxx\n用户: xxx）
            image_urls: 图片URL列表，用于户型图分析（可以是完整的签名URL或OSS object_key）

        Returns:
            纯文本答复

        Raises:
            Exception: AI 调用失败时抛出
        """
        # 检查是否配置了AI设计师智能体
        if not self._design_site_url or not self._design_site_token:
            logger.error("AI设计师智能体未配置，无法提供服务")
            raise ValueError("AI设计师服务未配置，请联系管理员")
        
        # 检查配置是否有效
        if not self._design_site_url.startswith("http"):
            logger.error("AI设计师站点URL配置无效: %s", self._design_site_url)
            raise ValueError("AI设计师服务配置错误，请联系管理员")
        
        if not self._design_site_token.startswith("eyJ"):
            logger.error("AI设计师Token配置无效")
            raise ValueError("AI设计师服务配置错误，请联系管理员")
        
        # 构建系统提示词，支持多轮对话和图片分析
        system_prompt = """你是一位专业的AI装修设计师 - 漫游视频生成器，精通各种装修风格、材料选择、空间规划、色彩搭配和预算控制。
用户会就装修设计相关问题向你咨询，包括但不限于：
1. 装修风格选择（现代简约、北欧、中式、工业风等）
2. 空间布局和功能规划
3. 材料选择和搭配建议
4. 色彩搭配和灯光设计
5. 预算控制和性价比建议
6. 装修流程和时间规划
7. 户型图分析和改造建议
8. 效果图生成和漫游视频规划

请基于专业知识和行业最佳实践，给出简洁、专业、可操作的建议。
回答要求：分点陈述、条理清晰，结合具体案例说明，避免冗长。

重要：你正在与用户进行多轮对话，请基于对话历史理解用户的意图和上下文。
如果用户的问题与之前的对话相关，请确保回答具有连贯性。

特别说明：如果用户上传了户型图，请基于户型图进行分析，给出：
1. 户型优缺点分析
2. 空间布局优化建议
3. 功能分区规划
4. 装修风格推荐
5. 预算估算建议
6. 效果图和漫游视频生成思路

若用户问题超出装修设计范畴，可礼貌说明并建议咨询相关专业人士。"""

        # 构建用户输入内容
        user_content_parts = []
        
        # 添加对话历史
        if context:
            user_content_parts.append(f"以下是之前的对话历史：\n{context}")
        
        # 添加用户问题
        user_content_parts.append(f"用户最新提问：{user_question}")
        
        # 添加图片信息 - 处理图片URL，确保AI设计师智能体能够访问
        if image_urls and len(image_urls) > 0:
            # 处理图片URL：如果是完整的签名URL，需要确保它是有效的
            processed_image_urls = []
            for url in image_urls[:5]:  # 最多处理5张图片
                if not url or not isinstance(url, str):
                    continue
                
                # 如果是完整的URL，直接使用
                if url.startswith("http"):
                    processed_image_urls.append(url)
                else:
                    # 如果是OSS object_key，生成24小时有效的签名URL
                    try:
                        from app.services.oss_service import oss_service
                        # 延长签名URL有效期到24小时，确保AI有足够时间分析
                        signed_url = oss_service.sign_url_for_key(url, expires=24*3600)
                        processed_image_urls.append(signed_url)
                    except Exception as e:
                        logger.warning(f"无法为object_key生成签名URL: {url}, error: {e}")
                        continue
            
            if processed_image_urls:
                image_info = f"\n\n用户上传了{len(processed_image_urls)}张户型图/装修图片，请基于图片内容进行分析。"
                user_content_parts.append(image_info)
                
                # 将图片URL添加到上下文中，确保AI设计师智能体能够访问
                for i, url in enumerate(processed_image_urls[:3]):  # 最多显示3张图片的URL
                    user_content_parts.append(f"图片{i+1}: {url}")
                
                if len(processed_image_urls) > 3:
                    user_content_parts.append(f"...等{len(processed_image_urls)}张图片")
                
                # 如果是户型图，添加具体分析要求
                if len(processed_image_urls) == 1:
                    user_content_parts.append("请重点分析这张户型图，给出：\n1. 户型优缺点分析\n2. 空间布局优化建议\n3. 功能分区规划\n4. 装修风格推荐\n5. 预算估算建议\n6. 效果图和漫游视频生成思路")
        
        user_content = "\n\n".join(user_content_parts)

        try:
            # 使用AI设计师智能体的配置调用扣子站点
            result_text = await self._call_designer_site(system_prompt, user_content)
            if not result_text:
                logger.error("AI设计师返回空结果")
                raise ValueError("AI设计师服务返回空结果，请稍后重试")
            
            return result_text.strip()
        except Exception as e:
            logger.error(f"AI设计师咨询失败: {e}", exc_info=True)
            # 失败时抛出异常，不返回模拟数据
            raise ValueError(f"AI设计师服务暂时不可用: {str(e)}")

    async def _call_designer_site(self, system_prompt: str, user_content: str) -> Optional[str]:
        """
        调用AI设计师扣子发布站点，流式响应拼接为完整文本。
        """
        combined = f"【系统要求】\n{system_prompt}\n\n【用户输入】\n{user_content}"
        session_id = f"designer-{int(time.time() * 1000)}"
        payload = {
            "content": {
                "query": {
                    "prompt": [
                        {"type": "text", "content": {"text": combined}}
                    ]
                }
            },
            "type": "query",
            "session_id": session_id,
        }
        if self._design_project_id:
            payload["project_id"] = int(self._design_project_id) if self._design_project_id.isdigit() else self._design_project_id
        
        url = f"{self._design_site_url}"
        headers = {
            "Authorization": f"Bearer {self._design_site_token}",
            "Content-Type": "application/json",
        }
        logger.info("Calling AI designer site: %s", url)
        
        # 复用_coze_site的响应解析逻辑
        def _extract_content(data: dict) -> Optional[str]:
            if not isinstance(data, dict):
                return None
            ev_type = data.get("type") or data.get("event") or ""
            if isinstance(ev_type, str) and ev_type.lower() in (
                "message_start", "message_end", "ping", "session", "session.created", "conversation.message.created"
            ):
                return None
            c = data.get("content") or data.get("text") or data.get("answer") or data.get("output")
            if isinstance(c, str) and c.strip():
                return c
            if isinstance(c, dict):
                ans = c.get("answer") or c.get("thinking")
                if isinstance(ans, str) and ans.strip() and not ans.strip().startswith("<["):
                    return ans
            if isinstance(c, list):
                texts = []
                for p in c:
                    if isinstance(p, dict):
                        t = p.get("text") or p.get("content")
                        if isinstance(t, str) and t.strip():
                            texts.append(t)
                    elif isinstance(p, str) and p.strip():
                        texts.append(p)
                if texts:
                    return "\n".join(texts)
            delta = data.get("delta")
            if isinstance(delta, str) and delta.strip():
                return delta
            if isinstance(delta, dict):
                c = delta.get("content") or delta.get("text")
                if isinstance(c, str) and c.strip():
                    return c
                if isinstance(c, list):
                    for p in c:
                        if isinstance(p, dict) and (p.get("type") == "text" or "text" in p):
                            t = p.get("text") or p.get("content")
                            if isinstance(t, str) and t.strip():
                                return t
            msg = data.get("message") or data.get("data")
            if isinstance(msg, dict):
                mc = msg.get("content") or msg.get("text")
                if isinstance(mc, str) and mc.strip():
                    return mc
                if isinstance(mc, list):
                    for p in mc:
                        if isinstance(p, dict):
                            t = p.get("text") or p.get("content")
                            if isinstance(t, str) and t.strip():
                                return t
            parts = data.get("parts")
            if isinstance(parts, list):
                for p in parts:
                    if isinstance(p, dict):
                        c = p.get("text") or p.get("content")
                        if isinstance(c, str) and c.strip():
                            return c
                    elif isinstance(p, str) and p.strip():
                        return p
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    d = first.get("delta") or first.get("message")
                    if isinstance(d, dict):
                        c = d.get("content") or d.get("text")
                        if isinstance(c, str) and c.strip():
                            return c
            # 扣子可能用 item.message.content
            item = data.get("item")
            if isinstance(item, dict):
                msg = item.get("message") or item.get("content")
                if isinstance(msg, dict):
                    mc = msg.get("content") or msg.get("text")
                    if isinstance(mc, str) and mc.strip():
                        return mc
                    if isinstance(mc, list):
                        for p in mc:
                            if isinstance(p, dict):
                                t = p.get("text") or p.get("content")
                                if isinstance(t, str) and t.strip():
                                    return t
                elif isinstance(msg, str) and msg.strip():
                    return msg
            return None

        async def _do_stream() -> Optional[str]:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, json=payload, headers=headers) as resp:
                    if resp.status_code != 200:
                        body = await resp.aread()
                        logger.error("AI designer site failed: status=%s body=%s", resp.status_code, body[:500])
                        return None
                    chunks = []
                    raw_samples = []
                    async for line in resp.aiter_lines():
                        line = (line or "").strip()
                        if not line or line == "data: [DONE]":
                            continue
                        if len(raw_samples) < 5:
                            raw_samples.append(line[:250])
                        if not line.startswith("data:"):
                            continue
                        json_str = line[5:].strip()
                        try:
                            data = json.loads(json_str)
                            c = _extract_content(data)
                            if c:
                                chunks.append(c)
                                if len(chunks) <= 2:
                                    logger.info("AI designer extracted chunk len=%d", len(c))
                        except json.JSONDecodeError:
                            pass
                    text = "".join(chunks).strip()
                    logger.info("AI designer chunks=%d total_len=%d", len(chunks), len(text))
                    if not text and raw_samples:
                        logger.warning(
                            "AI designer returned no parseable text. Sample lines: %s",
                            raw_samples,
                        )
                    return text if text else None

        try:
            result = await _do_stream()
            # 空结果时重试最多 2 次
            for retry in range(2):
                if result:
                    break
                await asyncio.sleep(5)
                logger.info("AI designer 空结果，第 %d 次重试", retry + 1)
                result = await _do_stream()
            return result
        except Exception as e:
            logger.warning("AI designer site error: %s", e, exc_info=True)
            return None

    def _get_mock_designer_response(self, user_question: str, context: str = "") -> str:
        """开发环境：返回模拟的AI设计师回答"""
        import random
        
        # 常见装修设计问题
        responses = {
            "风格": "现代简约风格注重功能性和简洁的线条，常用黑白灰为主色调，搭配木质元素。适合小户型，能最大化空间感。",
            "预算": "装修预算需要根据面积、材料、人工等因素来定。一般建议：硬装占60%，软装占30%，预留10%作为应急。",
            "材料": "地板推荐实木复合地板，性价比高且环保。墙面建议使用环保乳胶漆，颜色选择浅色系能增加空间感。",
            "色彩": "小户型建议使用浅色系，如米白、浅灰、淡蓝，能增加空间感。可以局部用亮色点缀，如黄色抱枕、绿色植物。",
            "布局": "客厅布局要考虑动线流畅，沙发不要正对大门。卧室床的位置要避开窗户，保证私密性和舒适性。",
            "灯光": "建议采用多层次照明：主灯提供基础照明，射灯/筒灯突出重点区域，台灯/落地灯营造氛围。",
            "收纳": "充分利用垂直空间，定制到顶的衣柜和储物柜。使用多功能家具，如带储物功能的床、沙发。",
            "环保": "选择E0级或ENF级环保板材，使用水性漆代替油性漆。装修后通风至少3个月再入住。"
        }
        
        # 根据用户问题匹配回答
        question_lower = user_question.lower()
        for key in responses:
            if key in question_lower:
                return responses[key]
        
        # 默认回答
        default_responses = [
            "作为AI设计师，我建议您首先明确装修预算和风格偏好，然后根据房屋结构和功能需求进行规划。",
            "装修设计需要考虑功能、美观和预算的平衡。建议先确定主要功能区域，再考虑风格和材料选择。",
            "好的设计应该以人为本，充分考虑居住者的生活习惯和需求。建议从实际使用场景出发进行设计。",
            "装修是一个系统工程，建议分阶段进行：先确定整体风格和布局，再选择材料和色彩，最后考虑细节装饰。"
        ]
        
        return random.choice(default_responses)


# 创建全局实例
risk_analyzer_service = RiskAnalyzerService()

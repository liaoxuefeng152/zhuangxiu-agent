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
            c = data.get("content") or data.get("text") or data.get("answer") or data.get("output")
            if isinstance(c, str):
                return c
            if isinstance(c, dict):
                ans = c.get("answer") or c.get("thinking")
                if isinstance(ans, str) and ans.strip() and not ans.strip().startswith("<["):
                    return ans
            delta = data.get("delta")
            if isinstance(delta, str):
                return delta
            if isinstance(delta, dict):
                c = delta.get("content") or delta.get("text")
                if isinstance(c, str):
                    return c
            msg = data.get("message") or data.get("data")
            if isinstance(msg, dict):
                c = msg.get("content") or msg.get("text")
                if isinstance(c, str):
                    return c
            parts = data.get("parts")
            if isinstance(parts, list):
                for p in parts:
                    if isinstance(p, dict):
                        c = p.get("text") or p.get("content")
                        if isinstance(c, str):
                            return c
                    elif isinstance(p, str):
                        return p
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    d = first.get("delta") or first.get("message")
                    if isinstance(d, dict):
                        c = d.get("content") or d.get("text")
                        if isinstance(c, str):
                            return c
            return None

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
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
                        if len(raw_samples) < 3:
                            raw_samples.append(line[:200])
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


# 创建全局实例
risk_analyzer_service = RiskAnalyzerService()

"""
装修决策Agent - AI风险分析服务
使用DeepSeek API进行智能风险分析
"""
import json
import logging
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class RiskAnalyzerService:
    """AI风险分析服务"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_BASE
        )

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

        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请分析以下装修报价单，总价：{total_price}元\n\n报价单内容：\n{ocr_text}"}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            result_text = response.choices[0].message.content.strip()

            # 尝试提取JSON（处理可能的markdown代码块）
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            analysis_result = json.loads(result_text)

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

        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请分析以下装修合同：\n\n{ocr_text}"}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            result_text = response.choices[0].message.content.strip()

            # 提取JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            analysis_result = json.loads(result_text)

            logger.info(f"合同分析完成，风险等级: {analysis_result.get('risk_level', 'compliant')}")
            return analysis_result

        except json.JSONDecodeError as e:
            logger.error(f"合同分析结果JSON解析失败: {e}")
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


# 创建全局实例
risk_analyzer_service = RiskAnalyzerService()

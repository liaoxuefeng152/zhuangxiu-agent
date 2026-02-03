"""
装修决策Agent - 天眼查API服务
用于查询企业风险数据
"""
import httpx
import logging
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class TianyanchaService:
    """天眼查服务类"""

    def __init__(self):
        self.base_url = "https://open.tianyancha.com/openapi"
        self.token = settings.TIANYANCHA_TOKEN
        self.timeout = 10.0

    async def _request(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        method: str = "GET"
    ) -> Optional[Dict]:
        """发送HTTP请求"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}{endpoint}"

                # 添加认证参数
                if params is None:
                    params = {}
                params["token"] = self.token

                response = await client.request(method, url, params=params)
                response.raise_for_status()

                data = response.json()

                # 检查天眼查响应状态
                if data.get("error_code") != 0:
                    logger.error(f"天眼查API错误: {data.get('error_code')} - {data.get('error_msg')}")
                    return None

                return data.get("result")

        except httpx.TimeoutException:
            logger.error("天眼查API请求超时")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"天眼查API HTTP错误: {e}")
            return None
        except Exception as e:
            logger.error(f"天眼查API请求异常: {e}", exc_info=True)
            return None

    async def get_company_detail(self, company_name: str) -> Optional[Dict]:
        """
        获取企业详细信息

        Args:
            company_name: 企业名称

        Returns:
            企业信息字典
        """
        params = {
            "name": company_name,
            "type": "search",
            "ps": 1,  # 页大小
            "pn": 1   # 页码
        }

        return await self._request("/company/getDetailByName", params)

    async def get_company_risks(self, company_name: str) -> Optional[Dict]:
        """
        获取企业风险信息

        Args:
            company_name: 企业名称

        Returns:
            风险信息字典
        """
        params = {
            "name": company_name
        }

        return await self._request("/company/risk", params)

    async def get_company_legal_actions(self, company_name: str) -> Optional[List]:
        """
        获取企业法律诉讼信息

        Args:
            company_name: 企业名称

        Returns:
            法律诉讼列表
        """
        params = {
            "name": company_name,
            "ps": 10,
            "pn": 1
        }

        result = await self._request("/company/lawsuit", params)
        if result:
            return result.get("items", [])
        return []

    async def get_company_complaints(self, company_name: str) -> Optional[List]:
        """
        获取企业投诉信息

        Args:
            company_name: 企业名称

        Returns:
            投诉列表
        """
        params = {
            "name": company_name,
            "ps": 10,
            "pn": 1
        }

        result = await self._request("/company/complaint", params)
        if result:
            return result.get("items", [])
        return []

    async def analyze_company_risk(self, company_name: str) -> Dict:
        """
        综合分析企业风险

        Args:
            company_name: 企业名称

        Returns:
            风险分析结果
        {
            "risk_level": "high" | "warning" | "compliant",
            "risk_score": 0-100,
            "risk_reasons": [],
            "complaint_count": 0,
            "legal_risks": []
        }
        """
        risk_analysis = {
            "risk_level": "compliant",
            "risk_score": 0,
            "risk_reasons": [],
            "complaint_count": 0,
            "legal_risks": []
        }

        try:
            # 并发请求多个数据源
            import asyncio

            detail_task = self.get_company_detail(company_name)
            risk_task = self.get_company_risks(company_name)
            legal_task = self.get_company_legal_actions(company_name)
            complaint_task = self.get_company_complaints(company_name)

            detail_result, risk_result, legal_result, complaint_result = await asyncio.gather(
                detail_task, risk_task, legal_task, complaint_task,
                return_exceptions=True
            )

            # 分析企业基础信息
            if detail_result:
                # 检查企业经营状态
                if detail_result.get("status") != "存续":
                    risk_analysis["risk_reasons"].append("企业经营状态异常")
                    risk_analysis["risk_score"] += 30

                # 检查成立时间（小于1年风险较高）
                est_date = detail_result.get("estiblishTime")
                if est_date:
                    from datetime import datetime
                    try:
                        est_datetime = datetime.strptime(est_date.split()[0], "%Y-%m-%d")
                        years = (datetime.now() - est_datetime).days / 365
                        if years < 1:
                            risk_analysis["risk_reasons"].append("企业成立时间不足1年")
                            risk_analysis["risk_score"] += 20
                    except:
                        pass

            # 分析风险数据
            if risk_result:
                risk_count = risk_result.get("count", 0)
                if risk_count > 5:
                    risk_analysis["risk_reasons"].append(f"企业存在{risk_count}条风险记录")
                    risk_analysis["risk_score"] += 40
                elif risk_count > 0:
                    risk_analysis["risk_reasons"].append(f"企业存在{risk_count}条风险记录")
                    risk_analysis["risk_score"] += 15

            # 分析法律诉讼
            if legal_result and isinstance(legal_result, list):
                lawsuit_count = len(legal_result)
                if lawsuit_count > 5:
                    risk_analysis["risk_reasons"].append(f"企业涉及{lawsuit_count}起法律诉讼")
                    risk_analysis["risk_score"] += 35
                    risk_analysis["legal_risks"] = legal_result[:5]
                elif lawsuit_count > 0:
                    risk_analysis["risk_reasons"].append(f"企业涉及{lawsuit_count}起法律诉讼")
                    risk_analysis["risk_score"] += 10
                    risk_analysis["legal_risks"] = legal_result

            # 分析投诉记录
            if complaint_result and isinstance(complaint_result, list):
                complaint_count = len(complaint_result)
                risk_analysis["complaint_count"] = complaint_count

                # 检查是否有跑路相关的投诉
                run_risks = [c for c in complaint_result if "跑路" in c.get("title", "") or "失联" in c.get("title", "")]
                if run_risks:
                    risk_analysis["risk_reasons"].append("存在跑路/失联相关投诉记录")
                    risk_analysis["risk_score"] += 50

                if complaint_count > 10:
                    risk_analysis["risk_reasons"].append(f"存在{complaint_count}条投诉记录")
                    risk_analysis["risk_score"] += 30
                elif complaint_count > 3:
                    risk_analysis["risk_reasons"].append(f"存在{complaint_count}条投诉记录")
                    risk_analysis["risk_score"] += 10

            # 确定风险等级
            if risk_analysis["risk_score"] >= 70:
                risk_analysis["risk_level"] = "high"
            elif risk_analysis["risk_score"] >= 30:
                risk_analysis["risk_level"] = "warning"
            else:
                risk_analysis["risk_level"] = "compliant"

            # 限制分数范围
            risk_analysis["risk_score"] = min(risk_analysis["risk_score"], 100)

        except Exception as e:
            logger.error(f"企业风险分析失败: {e}", exc_info=True)
            # 返回默认风险分析
            risk_analysis["risk_reasons"].append("风险分析服务暂时不可用")

        return risk_analysis


# 创建全局实例
tianyancha_service = TianyanchaService()

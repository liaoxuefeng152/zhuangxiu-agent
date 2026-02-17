"""
装修决策Agent - 聚合数据API服务
用于查询企业工商信息和法律案件信息
"""
import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)


class JuhechaService:
    """聚合数据服务类"""

    def __init__(self):
        # 司法企业查询配置
        self.sifa_base_url = settings.JUHECHA_API_BASE
        self.sifa_token = settings.JUHECHA_TOKEN
        self.sifa_endpoint = settings.JUHECHA_SIFA_ENDPOINT
        
        # 企业工商信息查询配置
        self.enterprise_base_url = settings.JUHECHA_ENTERPRISE_API_BASE
        self.enterprise_token = settings.SIMPLE_LIST_TOKEN
        self.enterprise_endpoint = settings.JUHECHA_ENTERPRISE_ENDPOINT
        
        self.timeout = 10.0

    def _has_valid_sifa_token(self) -> bool:
        """检查是否配置了有效的司法企业查询 Token"""
        t = (self.sifa_token or "").strip()
        return bool(t) and t not in ("xxx", "your_token", "your_token_here")
    
    def _has_valid_enterprise_token(self) -> bool:
        """检查是否配置了有效的企业工商信息 Token"""
        t = (self.enterprise_token or "").strip()
        return bool(t) and t not in ("xxx", "your_token", "your_token_here")

    async def _request_sifa(
        self,
        params: Dict[str, Any] = None,
        method: str = "GET"
    ) -> Optional[Dict]:
        """发送HTTP请求到司法企业查询API"""
        if not self._has_valid_sifa_token():
            logger.debug("司法企业查询 Token 未配置，跳过 API 调用")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.sifa_base_url}{self.sifa_endpoint}"

                # 添加认证参数
                if params is None:
                    params = {}
                params["key"] = self.sifa_token

                response = await client.request(method, url, params=params)
                response.raise_for_status()

                data = response.json()

                # 检查聚合数据响应状态
                if data.get("error_code") != 0:
                    logger.error(f"司法企业查询API错误: {data.get('error_code')} - {data.get('reason')}")
                    return None

                return data.get("result")

        except httpx.TimeoutException:
            logger.error("司法企业查询API请求超时")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"司法企业查询API HTTP错误: {e}")
            return None
        except Exception as e:
            logger.error(f"司法企业查询API请求异常: {e}", exc_info=True)
            return None
    
    async def _request_enterprise(
        self,
        params: Dict[str, Any] = None,
        method: str = "GET"
    ) -> Optional[Dict]:
        """发送HTTP请求到企业工商信息API"""
        if not self._has_valid_enterprise_token():
            logger.debug("企业工商信息 Token 未配置，跳过 API 调用")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.enterprise_base_url}{self.enterprise_endpoint}"

                # 添加认证参数
                if params is None:
                    params = {}
                params["key"] = self.enterprise_token

                response = await client.request(method, url, params=params)
                response.raise_for_status()

                data = response.json()

                # 检查聚合数据响应状态
                if data.get("error_code") != 0:
                    logger.error(f"企业工商信息API错误: {data.get('error_code')} - {data.get('reason')}")
                    return None

                return data.get("result")

        except httpx.TimeoutException:
            logger.error("企业工商信息API请求超时")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"企业工商信息API HTTP错误: {e}")
            return None
        except Exception as e:
            logger.error(f"企业工商信息API请求异常: {e}", exc_info=True)
            return None

    async def search_company_legal_cases(self, company_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        查询公司法律案件信息（司法企业查询）
        
        Args:
            company_name: 公司名称
            limit: 最多返回条数
            
        Returns:
            法律案件列表
            [
                {
                    "type": "cpws",  # 裁判文书
                    "title": "案件标题",
                    "date": "2021年05月18日",
                    "content": "案件内容摘要",
                    "data_type_zh": "裁判文书"
                },
                ...
            ]
        """
        if not company_name or len(company_name.strip()) < 2:
            return []
        
        if not self._has_valid_sifa_token():
            return []
        
        try:
            params = {
                "keyword": company_name.strip(),
                "range": limit,
                "pageno": 1
            }
            
            result = await self._request_sifa(params)
            if not result:
                return []
            
            # 解析返回的法律案件
            cases = self._parse_legal_cases(result)
            return cases[:limit]
            
        except Exception as e:
            logger.error(f"查询公司法律案件失败: {e}", exc_info=True)
            return []

    def _parse_legal_cases(self, api_result: Dict) -> List[Dict[str, Any]]:
        """
        解析聚合数据返回的法律案件信息
        
        Args:
            api_result: API返回的result字段
            
        Returns:
            解析后的案件列表
        """
        cases = []
        
        # 获取案件列表
        case_list = api_result.get("list", [])
        if not isinstance(case_list, list):
            return cases
        
        # 案件类型映射
        case_type_mapping = {
            "cpws": "裁判文书",
            "ajlc": "案件流程",
            "bgt": "执行公告",
            "fygg": "法院公告",
            "ktgg": "开庭公告",
            "pmgg": "拍卖公告",
            "shixin": "失信被执行人",
            "sifacdk": "司法查控",
            "zxgg": "限制高消费"
        }
        
        for item in case_list:
            try:
                data_type = item.get("dataType", "")
                title = item.get("title", "")
                date_str = item.get("sortTimeString", "")
                content = item.get("body", "")
                
                # 截取内容摘要
                content_summary = content[:200] if content else ""
                
                case = {
                    "type": data_type,
                    "title": title,
                    "date": date_str,
                    "content": content_summary,
                    "data_type_zh": case_type_mapping.get(data_type, data_type),
                    "entry_id": item.get("entryId", "")
                }
                
                cases.append(case)
            except Exception as e:
                logger.debug(f"解析案件信息失败: {e}")
                continue
        
        return cases

    async def analyze_company_legal_risk(self, company_name: str) -> Dict[str, Any]:
        """
        分析公司法律风险
        
        Args:
            company_name: 公司名称
            
        Returns:
            法律风险分析结果
            {
                "legal_case_count": 4,
                "recent_case_date": "2021年05月18日",
                "case_types": ["裁判文书", "案件流程"],
                "decoration_related_cases": 2,
                "risk_score_adjustment": 30,
                "risk_reasons": ["存在4起法律案件", "存在装饰装修合同纠纷"],
                "recent_cases": [...]  # 最近5条案件
            }
        """
        legal_analysis = {
            "legal_case_count": 0,
            "recent_case_date": "",
            "case_types": [],
            "decoration_related_cases": 0,
            "risk_score_adjustment": 0,
            "risk_reasons": [],
            "recent_cases": []
        }
        
        try:
            # 获取法律案件
            cases = await self.search_company_legal_cases(company_name, limit=20)
            if not cases:
                return legal_analysis
            
            # 基本统计
            legal_analysis["legal_case_count"] = len(cases)
            legal_analysis["recent_cases"] = cases[:5]  # 只保留最近5条
            
            # 案件类型统计
            case_types = set()
            for case in cases:
                case_type = case.get("data_type_zh", "")
                if case_type:
                    case_types.add(case_type)
            legal_analysis["case_types"] = list(case_types)
            
            # 查找最近案件日期
            if cases:
                legal_analysis["recent_case_date"] = cases[0].get("date", "")
            
            # 检查是否有装修相关案件
            decoration_keywords = ["装饰", "装修", "装潢", "家装", "工装", "室内设计"]
            decoration_cases = []
            for case in cases:
                title = case.get("title", "").lower()
                content = case.get("content", "").lower()
                
                for keyword in decoration_keywords:
                    if keyword in title or keyword in content:
                        decoration_cases.append(case)
                        break
            
            legal_analysis["decoration_related_cases"] = len(decoration_cases)
            
            # 计算风险评分调整
            risk_adjustment = 0
            
            # 根据案件数量调整
            case_count = legal_analysis["legal_case_count"]
            if case_count > 10:
                risk_adjustment += 50
                legal_analysis["risk_reasons"].append(f"存在{case_count}起法律案件，风险较高")
            elif case_count > 5:
                risk_adjustment += 30
                legal_analysis["risk_reasons"].append(f"存在{case_count}起法律案件")
            elif case_count > 0:
                risk_adjustment += 15
                legal_analysis["risk_reasons"].append(f"存在{case_count}起法律案件")
            
            # 根据装修相关案件调整
            decoration_count = legal_analysis["decoration_related_cases"]
            if decoration_count > 0:
                risk_adjustment += 25
                legal_analysis["risk_reasons"].append(f"存在{decoration_count}起装修相关纠纷")
            
            # 根据案件类型调整
            if "失信被执行人" in case_types:
                risk_adjustment += 40
                legal_analysis["risk_reasons"].append("存在失信被执行人记录")
            
            if "限制高消费" in case_types:
                risk_adjustment += 30
                legal_analysis["risk_reasons"].append("存在限制高消费记录")
            
            legal_analysis["risk_score_adjustment"] = min(risk_adjustment, 100)
            
        except Exception as e:
            logger.error(f"分析公司法律风险失败: {e}", exc_info=True)
        
        return legal_analysis

    async def search_enterprise_info(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        查询企业工商信息（模糊查询）
        
        Args:
            keyword: 搜索关键词（公司名称）
            limit: 最多返回条数
            
        Returns:
            企业信息列表
            [
                {
                    "name": "耒阳市怡馨装饰设计工程有限公司",
                    "credit_no": "91430481338544507E",
                    "reg_no": "430481000038468",
                    "oper_name": "梁国平",
                    "start_date": "2015-04-09",
                    "id": "38e6edd5-070c-24b5-9c48-a07de00ed17c"
                },
                ...
            ]
        """
        if not keyword or len(keyword.strip()) < 2:
            return []
        
        if not self._has_valid_enterprise_token():
            return []
        
        try:
            params = {
                "keyword": keyword.strip(),
                "pageSize": limit,
                "pageNum": 1
            }
            
            result = await self._request_enterprise(params)
            if not result:
                return []
            
            # 解析返回的企业信息
            enterprises = self._parse_enterprise_info(result)
            return enterprises[:limit]
            
        except Exception as e:
            logger.error(f"查询企业工商信息失败: {e}", exc_info=True)
            return []

    def _parse_enterprise_info(self, api_result: Dict) -> List[Dict[str, Any]]:
        """
        解析聚合数据返回的企业工商信息
        
        Args:
            api_result: API返回的result字段
            
        Returns:
            解析后的企业信息列表
        """
        enterprises = []
        
        # 获取企业列表
        data = api_result.get("data", {})
        items = data.get("items", [])
        if not isinstance(items, list):
            return enterprises
        
        for item in items:
            try:
                enterprise = {
                    "name": item.get("name", ""),
                    "credit_no": item.get("credit_no", ""),  # 统一社会信用代码
                    "reg_no": item.get("reg_no", ""),        # 注册号
                    "oper_name": item.get("oper_name", ""),  # 法人
                    "start_date": item.get("start_date", ""), # 成立日期
                    "id": item.get("id", "")                 # 企业ID
                }
                
                # 过滤空值
                if enterprise["name"]:
                    enterprises.append(enterprise)
            except Exception as e:
                logger.debug(f"解析企业信息失败: {e}")
                continue
        
        return enterprises

    async def get_enterprise_detail(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        获取企业详细信息（精确匹配）
        
        Args:
            company_name: 公司名称（精确匹配）
            
        Returns:
            企业详细信息
            {
                "name": "耒阳市怡馨装饰设计工程有限公司",
                "credit_no": "91430481338544507E",
                "reg_no": "430481000038468",
                "oper_name": "梁国平",
                "start_date": "2015-04-09",
                "id": "38e6edd5-070c-24b5-9c48-a07de00ed17c",
                "enterprise_age": 9  # 企业年龄（年）
            }
        """
        if not company_name:
            return None
        
        try:
            # 先进行模糊查询
            enterprises = await self.search_enterprise_info(company_name, limit=5)
            if not enterprises:
                return None
            
            # 尝试精确匹配
            target_enterprise = None
            for enterprise in enterprises:
                if enterprise["name"] == company_name:
                    target_enterprise = enterprise
                    break
            
            # 如果没有精确匹配，使用第一个结果
            if not target_enterprise and enterprises:
                target_enterprise = enterprises[0]
            
            if not target_enterprise:
                return None
            
            # 计算企业年龄
            enterprise_age = 0
            start_date = target_enterprise.get("start_date")
            if start_date:
                try:
                    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                    current_datetime = datetime.now()
                    days_diff = (current_datetime - start_datetime).days
                    enterprise_age = max(0, days_diff // 365)  # 计算年数
                except:
                    pass
            
            # 添加企业年龄信息
            target_enterprise["enterprise_age"] = enterprise_age
            
            return target_enterprise
            
        except Exception as e:
            logger.error(f"获取企业详细信息失败: {e}", exc_info=True)
            return None

    async def analyze_company_comprehensive(self, company_name: str) -> Dict[str, Any]:
        """
        综合分析公司信息（工商信息 + 法律风险）
        
        Args:
            company_name: 公司名称
            
        Returns:
            综合分析结果
            {
                "enterprise_info": {
                    "name": "耒阳市怡馨装饰设计工程有限公司",
                    "credit_no": "91430481338544507E",
                    "reg_no": "430481000038468",
                    "oper_name": "梁国平",
                    "start_date": "2015-04-09",
                    "enterprise_age": 9
                },
                "legal_analysis": {
                    "legal_case_count": 4,
                    "decoration_related_cases": 2,
                    "risk_score_adjustment": 30,
                    "risk_reasons": ["存在4起法律案件", "存在2起装修相关纠纷"],
                    "recent_cases": [...]
                },
                "risk_summary": {
                    "risk_level": "warning",
                    "risk_score": 30,
                    "recommendation": "建议谨慎合作，注意装修相关纠纷风险"
                }
            }
        """
        comprehensive_analysis = {
            "enterprise_info": None,
            "legal_analysis": None,
            "risk_summary": {
                "risk_level": "compliant",
                "risk_score": 0,
                "recommendation": "企业合规，可正常合作"
            }
        }
        
        try:
            import asyncio
            
            # 并发获取企业信息和法律风险分析
            enterprise_task = self.get_enterprise_detail(company_name)
            legal_task = self.analyze_company_legal_risk(company_name)
            
            enterprise_result, legal_result = await asyncio.gather(
                enterprise_task, legal_task, return_exceptions=True
            )
            
            # 处理企业信息结果
            if isinstance(enterprise_result, dict):
                comprehensive_analysis["enterprise_info"] = enterprise_result
            else:
                logger.warning(f"获取企业信息失败: {enterprise_result}")
            
            # 处理法律分析结果
            if isinstance(legal_result, dict):
                comprehensive_analysis["legal_analysis"] = legal_result
                
                # 基于法律分析计算风险摘要
                risk_score = legal_result.get("risk_score_adjustment", 0)
                comprehensive_analysis["risk_summary"]["risk_score"] = risk_score
                
                if risk_score >= 70:
                    comprehensive_analysis["risk_summary"]["risk_level"] = "needs_attention"
                    comprehensive_analysis["risk_summary"]["recommendation"] = "发现较多法律记录，建议重点关注并详细审查合同条款"
                elif risk_score >= 30:
                    comprehensive_analysis["risk_summary"]["risk_level"] = "moderate_concern"
                    comprehensive_analysis["risk_summary"]["recommendation"] = "存在部分法律记录，建议关注相关风险并完善合同约定"
                else:
                    comprehensive_analysis["risk_summary"]["risk_level"] = "compliant"
                    comprehensive_analysis["risk_summary"]["recommendation"] = "未发现重大法律风险记录，可参考常规合作流程"
            else:
                logger.warning(f"获取法律分析失败: {legal_result}")
            
        except Exception as e:
            logger.error(f"综合分析公司信息失败: {e}", exc_info=True)
        
        return comprehensive_analysis


# 创建全局实例
juhecha_service = JuhechaService()

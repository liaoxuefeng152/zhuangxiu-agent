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
        查询公司法律案件信息（使用风鸟API进行司法企业查询）
        
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
        
        try:
            # 使用风鸟API进行司法企业查询
            from .fengniao_service import fengniao_service
            
            # 调用风鸟API查询法律案件
            cases = await fengniao_service.search_company_legal_cases(company_name, limit)
            return cases
            
        except Exception as e:
            logger.error(f"查询公司法律案件失败: {e}", exc_info=True)
            return []

    def _parse_legal_cases(self, api_result: Dict) -> List[Dict[str, Any]]:
        """
        解析聚合数据返回的法律案件信息
        
        Args:
            api_result: API返回的result字段
            
        Returns:
            解析后的案件列表（包含详细字段）
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
        
        # 案由关键词映射
        cause_keywords = {
            "合同": ["合同", "协议", "约定", "违约", "履行"],
            "装修": ["装饰", "装修", "装潢", "家装", "工装", "室内设计"],
            "劳务": ["劳务", "工资", "薪酬", "劳动", "雇佣"],
            "质量": ["质量", "合格", "标准", "缺陷", "瑕疵"],
            "付款": ["付款", "支付", "欠款", "债务", "债权"],
            "侵权": ["侵权", "损害", "赔偿", "损失", "伤害"]
        }
        
        for item in case_list:
            try:
                data_type = item.get("dataType", "")
                title = item.get("title", "")
                date_str = item.get("sortTimeString", "")
                content = item.get("body", "")
                entry_id = item.get("entryId", "")
                
                # 截取内容摘要
                content_summary = content[:200] if content else ""
                
                # 解析案件类型
                case_type = case_type_mapping.get(data_type, data_type)
                
                # 分析案由
                cause = self._analyze_case_cause(title, content)
                
                # 分析判决结果
                result = self._analyze_case_result(content)
                
                # 提取相关法条
                related_laws = self._extract_related_laws(content)
                
                # 生成案件编号
                case_no = self._generate_case_no(entry_id, date_str)
                
                case = {
                    "type": data_type,
                    "title": title,
                    "date": date_str,
                    "content": content_summary,
                    "data_type_zh": case_type,
                    "entry_id": entry_id,
                    "case_type": case_type,  # 案件类型
                    "cause": cause,  # 案由
                    "result": result,  # 判决结果
                    "related_laws": related_laws,  # 相关法条
                    "case_no": case_no  # 案件编号
                }
                
                cases.append(case)
            except Exception as e:
                logger.debug(f"解析案件信息失败: {e}")
                continue
        
        return cases
    
    def _analyze_case_cause(self, title: str, content: str) -> str:
        """分析案件案由"""
        text = (title + " " + content).lower()
        
        # 案由关键词映射
        cause_mapping = {
            "合同": ["合同", "协议", "约定", "违约", "履行", "解除", "终止"],
            "装修": ["装饰", "装修", "装潢", "家装", "工装", "室内设计", "施工", "工程"],
            "劳务": ["劳务", "工资", "薪酬", "劳动", "雇佣", "加班", "社保"],
            "质量": ["质量", "合格", "标准", "缺陷", "瑕疵", "不合格", "验收"],
            "付款": ["付款", "支付", "欠款", "债务", "债权", "拖欠", "催收"],
            "侵权": ["侵权", "损害", "赔偿", "损失", "伤害", "人身", "财产"],
            "租赁": ["租赁", "出租", "承租", "租金", "押金", "转租"],
            "买卖": ["买卖", "销售", "购买", "货物", "商品", "产品"]
        }
        
        for cause, keywords in cause_mapping.items():
            for keyword in keywords:
                if keyword in text:
                    return cause
        
        return "其他"
    
    def _analyze_case_result(self, content: str) -> str:
        """分析案件判决结果"""
        if not content:
            return "未知"
        
        content_lower = content.lower()
        
        # 判决结果关键词
        if any(word in content_lower for word in ["支持", "胜诉", "胜诉方", "原告胜诉", "上诉人胜诉"]):
            return "支持原告诉求"
        elif any(word in content_lower for word in ["驳回", "败诉", "败诉方", "原告败诉", "上诉人败诉"]):
            return "驳回原告诉求"
        elif any(word in content_lower for word in ["调解", "和解", "协商", "达成协议"]):
            return "调解结案"
        elif any(word in content_lower for word in ["撤诉", "撤回", "放弃"]):
            return "撤诉"
        elif any(word in content_lower for word in ["部分支持", "部分驳回"]):
            return "部分支持"
        
        return "审理中"
    
    def _extract_related_laws(self, content: str) -> List[str]:
        """提取相关法条"""
        if not content:
            return []
        
        # 常见装修相关法条
        common_laws = [
            "《民法典》",
            "《合同法》",
            "《建筑法》",
            "《消费者权益保护法》",
            "《产品质量法》",
            "《劳动法》",
            "《民事诉讼法》"
        ]
        
        related_laws = []
        for law in common_laws:
            if law in content:
                related_laws.append(law)
        
        # 如果没有找到具体法条，添加通用法条
        if not related_laws and ("合同" in content or "协议" in content):
            related_laws.append("《民法典》合同编")
        
        return related_laws
    
    def _generate_case_no(self, entry_id: str, date_str: str) -> str:
        """生成案件编号"""
        if entry_id:
            # 使用entry_id的一部分作为案件编号
            return f"案{entry_id[-8:]}" if len(entry_id) >= 8 else f"案{entry_id}"
        elif date_str:
            # 使用日期作为案件编号
            try:
                # 尝试解析日期
                date_part = date_str.replace("年", "").replace("月", "").replace("日", "").replace("-", "")[:8]
                return f"案{date_part}"
            except:
                return f"案{date_str[:10]}"
        
        return "案未知"

    async def analyze_company_legal_risk(self, company_name: str) -> Dict[str, Any]:
        """
        分析公司法律案件信息（只返回原始数据，不做评价）
        
        Args:
            company_name: 公司名称
            
        Returns:
            法律案件分析结果（只包含原始数据）
            {
                "legal_case_count": 4,
                "recent_case_date": "2021年05月18日",
                "case_types": ["裁判文书", "案件流程"],
                "decoration_related_cases": 2,
                "recent_cases": [...]  # 最近5条案件
            }
        """
        legal_analysis = {
            "legal_case_count": 0,
            "recent_case_date": "",
            "case_types": [],
            "decoration_related_cases": 0,
            "recent_cases": []
        }
        
        try:
            # 使用风鸟API进行法律案件分析
            from .fengniao_service import fengniao_service
            
            # 调用风鸟API分析法律风险
            fengniao_result = await fengniao_service.analyze_company_legal_risk(company_name)
            
            if fengniao_result:
                legal_analysis.update(fengniao_result)
            
        except Exception as e:
            logger.error(f"分析公司法律案件失败: {e}", exc_info=True)
        
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
        综合分析公司信息（工商信息 + 法律案件信息）
        只返回原始数据，不做任何评价
        
        Args:
            company_name: 公司名称
            
        Returns:
            综合分析结果（只包含原始数据）
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
                    "recent_cases": [...]
                }
            }
        """
        comprehensive_analysis = {
            "enterprise_info": None,
            "legal_analysis": None
        }
        
        try:
            import asyncio
            
            # 并发获取企业信息和法律案件分析
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
            else:
                logger.warning(f"获取法律分析失败: {legal_result}")
            
        except Exception as e:
            logger.error(f"综合分析公司信息失败: {e}", exc_info=True)
        
        return comprehensive_analysis


# 创建全局实例
juhecha_service = JuhechaService()

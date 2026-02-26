"""
装修决策Agent - 风鸟企业涉诉API服务
用于查询企业涉诉数据（替代聚合查的司法企业查询功能）
"""
import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)


class FengniaoService:
    """风鸟企业涉诉服务类"""

    def __init__(self):
        # 风鸟API配置
        self.api_host = settings.FENGNIAO_API_HOST
        self.api_path = settings.FENGNIAO_API_PATH
        self.appcode = settings.FENGNIAO_APPCODE
        
        self.timeout = 10.0

    def _has_valid_config(self) -> bool:
        """检查是否配置了有效的风鸟API配置"""
        host = (self.api_host or "").strip()
        path = (self.api_path or "").strip()
        appcode = (self.appcode or "").strip()
        
        return bool(host) and bool(path) and bool(appcode) and appcode not in ("xxx", "your_appcode")

    async def _request_fengniao(
        self,
        params: Dict[str, Any] = None,
        method: str = "GET"
    ) -> Optional[Dict]:
        """发送HTTP请求到风鸟API"""
        if not self._has_valid_config():
            logger.debug("风鸟API配置未配置，跳过 API 调用")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.api_host}{self.api_path}"
                
                # 添加认证参数
                headers = {
                    "Authorization": f"APPCODE {self.appcode}",
                    "Content-Type": "application/json; charset=UTF-8"
                }
                
                # 风鸟API使用POST请求，参数在body中
                if params is None:
                    params = {}
                
                # 风鸟API需要的参数格式
                request_body = {
                    "companyName": params.get("keyword", ""),
                    "pageNo": params.get("pageNo", 1),
                    "pageSize": params.get("pageSize", 10)
                }
                
                response = await client.request(method, url, json=request_body, headers=headers)
                response.raise_for_status()

                data = response.json()

                # 检查风鸟API响应状态
                if data.get("code") != 200:
                    logger.error(f"风鸟API错误: {data.get('code')} - {data.get('message')}")
                    return None

                return data.get("data")

        except httpx.TimeoutException:
            logger.error("风鸟API请求超时")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"风鸟API HTTP错误: {e}")
            return None
        except Exception as e:
            logger.error(f"风鸟API请求异常: {e}", exc_info=True)
            return None

    async def search_company_legal_cases(self, company_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        查询公司法律案件信息（风鸟企业涉诉查询）
        
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
        
        if not self._has_valid_config():
            return []
        
        try:
            params = {
                "keyword": company_name.strip(),
                "pageNo": 1,
                "pageSize": limit
            }
            
            result = await self._request_fengniao(params)
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
        解析风鸟API返回的法律案件信息
        
        Args:
            api_result: API返回的data字段
            
        Returns:
            解析后的案件列表（包含详细字段）
        """
        cases = []
        
        # 获取案件列表
        case_list = api_result.get("list", [])
        if not isinstance(case_list, list):
            return cases
        
        # 案件类型映射（根据风鸟API返回的字段调整）
        case_type_mapping = {
            "cpws": "裁判文书",
            "ajlc": "案件流程",
            "bgt": "执行公告",
            "fygg": "法院公告",
            "ktgg": "开庭公告",
            "pmgg": "拍卖公告",
            "shixin": "失信被执行人",
            "zxgg": "限制高消费",
            "default": "法律文书"
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
                # 风鸟API返回的字段可能不同，需要根据实际响应调整
                data_type = item.get("caseType", "default")
                title = item.get("caseName", "")
                date_str = item.get("judgeDate", "")
                content = item.get("content", "")
                case_id = item.get("caseId", "")
                
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
                case_no = self._generate_case_no(case_id, date_str)
                
                case = {
                    "type": data_type,
                    "title": title,
                    "date": date_str,
                    "content": content_summary,
                    "data_type_zh": case_type,
                    "entry_id": case_id,
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
    
    def _generate_case_no(self, case_id: str, date_str: str) -> str:
        """生成案件编号"""
        if case_id:
            # 使用case_id的一部分作为案件编号
            return f"案{case_id[-8:]}" if len(case_id) >= 8 else f"案{case_id}"
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
            
        except Exception as e:
            logger.error(f"分析公司法律案件失败: {e}", exc_info=True)
        
        return legal_analysis


# 创建全局实例
fengniao_service = FengniaoService()

"""
其他数据验证模型
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class CompanyScanRequest(BaseModel):
    """公司扫描请求"""
    company_name: str


class CompanyScanResponse(BaseModel):
    """公司扫描响应"""
    task_id: int
    status: str
    created_at: datetime


class CompanyScanResult(BaseModel):
    """公司扫描结果"""
    scan_id: int
    company_name: str
    risk_level: str
    risk_score: int
    risk_reasons: List[str]
    complaint_count: int
    legal_risks: Optional[List[Dict[str, Any]]] = None
    created_at: datetime


class QuoteUploadResponse(BaseModel):
    """报价单上传响应"""
    task_id: int
    resource_id: int
    status: str
    created_at: datetime


class QuoteAnalysisResult(BaseModel):
    """报价单分析结果"""
    quote_id: int
    file_url: str
    status: str
    total_amount: Optional[float] = None
    item_count: Optional[int] = None
    suspicious_items: Optional[List[Dict[str, Any]]] = None
    risk_level: Optional[str] = None
    suggestions: Optional[List[str]] = None
    created_at: datetime


class ContractUploadResponse(BaseModel):
    """合同上传响应"""
    task_id: int
    resource_id: int
    status: str
    created_at: datetime


class ContractAnalysisResult(BaseModel):
    """合同分析结果"""
    contract_id: int
    file_url: str
    status: str
    risk_level: Optional[str] = None
    risk_clauses: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[str]] = None
    created_at: datetime


class ConstructionSchedule(BaseModel):
    """施工进度计划"""
    construction_id: int
    start_date: Optional[str] = None
    current_stage: Optional[str] = None
    stages: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class PaymentRequest(BaseModel):
    """支付请求"""
    order_type: str
    resource_type: str
    resource_id: int


class PaymentResponse(BaseModel):
    """支付响应"""
    order_id: int
    order_no: str
    amount: float
    status: str
    pay_url: Optional[str] = None
    created_at: datetime


class OrderResponse(BaseModel):
    """订单响应"""
    order_id: int
    order_no: str
    order_type: str
    resource_type: str
    resource_id: int
    amount: float
    status: str
    created_at: datetime


class ApiResponse(BaseModel):
    """通用API响应"""
    code: int = 0
    msg: str = "success"
    data: Optional[Any] = None


class StatsResponse(BaseModel):
    """统计响应"""
    total: int
    recent_count: int

"""
装修决策Agent - Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """用户角色"""
    NORMAL = "normal"
    MEMBER = "member"


class RiskLevel(str, Enum):
    """风险等级"""
    HIGH = "high"
    WARNING = "warning"
    COMPLIANT = "compliant"


class ScanStatus(str, Enum):
    """扫描状态"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "pending"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderType(str, Enum):
    """订单类型"""
    REPORT_SINGLE = "report_single"
    REPORT_PACKAGE = "report_package"
    SUPERVISION_SINGLE = "supervision_single"
    SUPERVISION_PACKAGE = "supervision_package"


# ============ 用户相关 ============
class WxLoginRequest(BaseModel):
    """微信登录请求"""
    code: str = Field(..., description="微信登录凭证")


class WxLoginResponse(BaseModel):
    """微信登录响应"""
    access_token: str
    user_id: int
    openid: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    is_member: bool = False


class UserProfileResponse(BaseModel):
    """用户信息响应"""
    user_id: int
    openid: str
    nickname: Optional[str]
    avatar_url: Optional[str]
    phone: Optional[str]
    phone_verified: bool
    is_member: bool
    city_code: Optional[str] = None
    city_name: Optional[str] = None
    created_at: datetime


# ============ 公司检测相关 ============
class CompanyScanRequest(BaseModel):
    """公司检测请求"""
    company_name: str = Field(..., min_length=3, max_length=200, description="公司名称")


class CompanyScanResponse(BaseModel):
    """公司检测响应"""
    id: int
    company_name: str
    risk_level: RiskLevel
    risk_score: int
    risk_reasons: List[str]
    complaint_count: int
    legal_risks: List[Dict[str, Any]]
    status: ScanStatus
    created_at: datetime


# ============ 报价单相关 ============
class QuoteUploadRequest(BaseModel):
    """报价单上传请求"""
    file_url: str
    file_name: str
    file_size: int
    file_type: str


class QuoteUploadResponse(BaseModel):
    """报价单上传响应"""
    task_id: int
    file_name: str
    file_type: str
    status: str


class QuoteAnalysisResponse(BaseModel):
    """报价单分析响应"""
    id: int
    file_name: str
    status: ScanStatus
    risk_score: Optional[int]
    high_risk_items: List[Dict[str, Any]]
    warning_items: List[Dict[str, Any]]
    missing_items: List[Dict[str, Any]]
    overpriced_items: List[Dict[str, Any]]
    total_price: Optional[float]
    market_ref_price: Optional[float]
    is_unlocked: bool
    created_at: datetime
    # V2.6.2优化：分析进度提示
    analysis_progress: Optional[Dict[str, Any]] = None
    # AI分析完整结果（包含材料清单等详细信息）
    result_json: Optional[Dict[str, Any]] = None
    # OCR识别结果
    ocr_result: Optional[Dict[str, Any]] = None


# ============ 合同相关 ============
class ContractUploadRequest(BaseModel):
    """合同上传请求"""
    file_url: str
    file_name: str
    file_size: int
    file_type: str


class ContractUploadResponse(BaseModel):
    """合同上传响应"""
    task_id: int
    file_name: str
    file_type: str
    status: str


class ContractAnalysisResponse(BaseModel):
    """合同分析响应（与前端报告页、API 文档一致）"""
    id: int
    file_name: str
    status: ScanStatus
    risk_level: Optional[RiskLevel]
    risk_items: List[Dict[str, Any]]
    unfair_terms: List[Dict[str, Any]]
    missing_terms: List[Dict[str, Any]]
    suggested_modifications: List[Dict[str, Any]]
    summary: Optional[str] = None
    is_unlocked: bool
    created_at: datetime
    # V2.6.2优化：分析进度提示
    analysis_progress: Optional[Dict[str, Any]] = None
    # AI分析完整结果（包含详细信息）
    result_json: Optional[Dict[str, Any]] = None
    # OCR识别结果
    ocr_result: Optional[Dict[str, Any]] = None


# ============ 施工进度相关 ============
class ConstructionStage(str, Enum):
    """施工阶段 PRD V15.3 六阶段 S00-S05"""
    S00 = "S00"  # 材料进场人工核对
    S01 = "S01"  # 隐蔽工程
    S02 = "S02"  # 泥瓦工
    S03 = "S03"  # 木工
    S04 = "S04"  # 油漆
    S05 = "S05"  # 安装收尾
    # 兼容旧
    MATERIAL = "material"
    PLUMBING = "plumbing"
    CARPENTRY = "carpentry"
    WOODWORK = "woodwork"
    PAINTING = "painting"
    INSTALLATION = "installation"
    FLOORING = "flooring"
    SOFT_FURNISHING = "soft_furnishing"


class StageStatus(str, Enum):
    """阶段状态 PRD 互锁"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CHECKED = "checked"        # S00 人工核对通过
    PASSED = "passed"          # S01-S05 AI验收通过
    NEED_RECTIFY = "need_rectify"
    PENDING_RECHECK = "pending_recheck"


class StartDateRequest(BaseModel):
    """设置开工日期请求（V2.6.2优化：支持自定义阶段周期）"""
    start_date: datetime = Field(..., description="开工日期")
    # V2.6.2优化：自定义阶段周期（可选），格式：{"S00": 3, "S01": 7, ...}
    custom_durations: Optional[Dict[str, int]] = Field(None, description="自定义阶段周期（天）")


class UpdateStageStatusRequest(BaseModel):
    """更新阶段状态请求（支持 S00-S05 与 checked/passed）"""
    stage: str = Field(..., description="S00|S01|...|S05 或旧键 material 等")
    status: str = Field(..., description="pending|checked|passed|need_rectify|pending_recheck|completed 等")


class CalibrateStageRequest(BaseModel):
    """阶段时间校准请求 FR-015"""
    stage: str = Field(..., description="S00-S05")
    manual_start_date: Optional[datetime] = None
    manual_acceptance_date: Optional[datetime] = None


class ConstructionResponse(BaseModel):
    """施工进度响应"""
    id: int
    start_date: Optional[datetime]
    estimated_end_date: Optional[datetime]
    progress_percentage: int
    is_delayed: bool
    delay_days: int
    stages: Dict[str, Dict[str, Any]]
    notes: Optional[str]


# ============ 订单相关 ============
class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    order_type: OrderType
    resource_type: str  # quote, contract
    resource_id: int


class CreateOrderResponse(BaseModel):
    """创建订单响应"""
    order_id: int
    order_no: str
    order_type: str
    amount: float
    status: str


class PaymentRequest(BaseModel):
    """支付请求"""
    order_id: int


class PaymentResponse(BaseModel):
    """支付响应"""
    order_no: str
    pay_sign: str
    timestamp: str
    nonce_str: str


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    order_no: str
    order_type: str
    amount: float
    status: OrderStatus
    paid_at: Optional[datetime]
    created_at: datetime


# ============ 通用响应 ============
class ApiResponse(BaseModel):
    """通用API响应"""
    code: int = Field(default=0, description="响应码")
    msg: str = Field(default="success", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")


class ListResponse(BaseModel):
    """列表响应"""
    code: int = 0
    msg: str = "success"
    data: Dict[str, Any]

"""
装修决策Agent - 数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, ForeignKey, Boolean, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    wx_openid = Column(String(128), unique=True, nullable=False, index=True)
    wx_unionid = Column(String(128), index=True)
    nickname = Column(String(50))
    avatar_url = Column(String(512))
    phone = Column(String(11), index=True)
    phone_verified = Column(Boolean, default=False)
    is_member = Column(Boolean, default=False)
    city_code = Column(String(20))
    city_name = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联关系
    quotes = relationship("Quote", back_populates="user")
    contracts = relationship("Contract", back_populates="user")
    companies = relationship("CompanyScan", back_populates="user")
    orders = relationship("Order", back_populates="user")
    constructions = relationship("Construction", back_populates="user")
    messages = relationship("Message", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    construction_photos = relationship("ConstructionPhoto", back_populates="user")
    acceptance_analyses = relationship("AcceptanceAnalysis", back_populates="user")
    user_setting = relationship("UserSetting", back_populates="user", uselist=False)
    refund_requests = relationship("RefundRequest", back_populates="user")
    ai_consult_sessions = relationship("AIConsultSession", back_populates="user")
    acceptance_appeals = relationship("AcceptanceAppeal", back_populates="user")
    special_applications = relationship("SpecialApplication", back_populates="user")
    material_checks = relationship("MaterialCheck", back_populates="user")


class CompanyScan(Base):
    """公司风险扫描记录"""
    __tablename__ = "company_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String(200), nullable=False, index=True)
    risk_level = Column(String(20))  # high, warning, compliant
    risk_score = Column(Integer)  # 0-100
    risk_reasons = Column(JSON)  # 风险原因列表
    complaint_count = Column(Integer, default=0)
    legal_risks = Column(JSON)  # 法律风险列表
    status = Column(String(20), default="completed")  # pending, completed, failed
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    # 关联关系
    user = relationship("User", back_populates="companies")


class Quote(Base):
    """报价单表"""
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_url = Column(String(512), nullable=False)
    file_name = Column(String(200))
    file_size = Column(Integer)
    file_type = Column(String(20))  # pdf, jpg, png
    status = Column(String(20), default="pending")  # pending, analyzing, completed, failed

    # OCR结果
    ocr_result = Column(JSON)  # OCR识别的文本内容

    # AI分析结果
    result_json = Column(JSON)  # 完整分析结果
    risk_score = Column(Integer)  # 风险评分
    high_risk_items = Column(JSON)  # 高风险项列表
    warning_items = Column(JSON)  # 警告项列表
    missing_items = Column(JSON)  # 漏项列表
    overpriced_items = Column(JSON)  # 虚高项列表

    # 报告解锁状态
    is_unlocked = Column(Boolean, default=False)
    unlock_type = Column(String(20))  # single, package, first_free, member

    # V2.6.2优化：分析进度提示
    analysis_progress = Column(JSON)  # {"step": "ocr|analyzing|generating", "progress": 0-100, "message": "提示信息"}

    # 元数据
    total_price = Column(Float)  # 总价
    market_ref_price = Column(Float)  # 市场参考价
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联关系
    user = relationship("User", back_populates="quotes")


class Contract(Base):
    """合同表"""
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_url = Column(String(512), nullable=False)
    file_name = Column(String(200))
    file_size = Column(Integer)
    file_type = Column(String(20))
    status = Column(String(20), default="pending")

    # OCR结果
    ocr_result = Column(JSON)

    # AI分析结果
    result_json = Column(JSON)
    risk_level = Column(String(20))
    risk_items = Column(JSON)  # 风险条款列表
    unfair_terms = Column(JSON)  # 不公平条款
    missing_terms = Column(JSON)  # 缺失条款
    suggested_modifications = Column(JSON)  # 修改建议

    # 报告解锁状态
    is_unlocked = Column(Boolean, default=False)
    unlock_type = Column(String(20))  # single, package, first_free, member

    # V2.6.2优化：分析进度提示
    analysis_progress = Column(JSON)  # {"step": "ocr|analyzing|generating", "progress": 0-100, "message": "提示信息"}

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联关系
    user = relationship("User", back_populates="contracts")


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_no = Column(String(32), unique=True, index=True)

    # 订单类型
    order_type = Column(String(20))  # report_single, report_package, supervision_single, supervision_package

    # 关联资源
    resource_type = Column(String(20))  # quote, contract, company
    resource_id = Column(Integer)

    # 价格信息
    amount = Column(Float, nullable=False)
    original_amount = Column(Float)  # 原价（套餐时使用）

    # 订单状态
    status = Column(String(20), default="pending")  # pending, paid, completed, cancelled, refunded

    # 支付信息
    payment_method = Column(String(20))  # wechat
    transaction_id = Column(String(64), index=True)
    paid_at = Column(DateTime)

    # 其他信息（Python 不能用 metadata，与 Declarative 保留名冲突，故用 order_metadata 映射 DB 列 metadata）
    order_metadata = Column(JSON, name="metadata")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联关系
    user = relationship("User", back_populates="orders")


class Construction(Base):
    """施工进度管理表"""
    __tablename__ = "constructions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 开工信息
    start_date = Column(DateTime)
    estimated_end_date = Column(DateTime)
    actual_end_date = Column(DateTime)

    # 进度信息
    progress_percentage = Column(Integer, default=0)  # 0-100
    is_delayed = Column(Boolean, default=False)
    delay_days = Column(Integer, default=0)

    # 阶段进度（JSON存储各阶段状态）
    stages = Column(JSON)
    """
    {
        "plumbing": {"status": "completed", "start_date": "2026-01-20", "end_date": "2026-01-29"},
        "carpentry": {"status": "in_progress", "start_date": "2026-01-30", "end_date": "2026-02-18"},
        "painting": {"status": "pending", "start_date": "2026-02-19", "end_date": "2026-02-28"},
        "flooring": {"status": "pending", "start_date": "2026-03-01", "end_date": "2026-03-05"},
        "soft_furnishing": {"status": "pending", "start_date": "2026-03-06", "end_date": "2026-03-12"}
    }
    """

    # 备注
    notes = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联关系
    user = relationship("User", back_populates="constructions")


class Message(Base):
    """消息表 P14"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(20), nullable=False)  # system, progress, payment
    title = Column(String(200), nullable=False)
    content = Column(Text)
    summary = Column(String(500))
    is_read = Column(Boolean, default=False)
    link_url = Column(String(512))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="messages")


class Feedback(Base):
    """意见反馈表 P24"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    images = Column(JSON)
    status = Column(String(20), default="pending")
    reply = Column(Text)
    feedback_type = Column(String(30), default="other")
    sub_type = Column(String(30))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="feedbacks")


class ConstructionPhoto(Base):
    """施工照片表 P15/P17"""
    __tablename__ = "construction_photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stage = Column(String(30), nullable=False)
    file_url = Column(String(512), nullable=False)
    file_name = Column(String(200))
    is_read = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="construction_photos")


class AcceptanceAnalysis(Base):
    """验收分析表 P30"""
    __tablename__ = "acceptance_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stage = Column(String(30))
    file_urls = Column(JSON, nullable=False)
    result_json = Column(JSON)
    issues = Column(JSON)
    suggestions = Column(JSON)
    severity = Column(String(20))
    status = Column(String(20), default="completed")
    result_status = Column(String(30), default="completed")  # passed | need_rectify | failed | pending_recheck
    recheck_count = Column(Integer, default=0)
    rectified_at = Column(DateTime)
    rectified_photo_urls = Column(JSON)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="acceptance_analyses")
    ai_consult_sessions = relationship("AIConsultSession", back_populates="acceptance_analysis")
    appeals = relationship("AcceptanceAppeal", back_populates="acceptance_analysis")


class UserSetting(Base):
    """用户设置表 P19"""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    storage_duration_months = Column(Integer, default=12)
    reminder_days_before = Column(Integer, default=3)
    notify_progress = Column(Boolean, default=True)
    notify_acceptance = Column(Boolean, default=True)
    notify_system = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="user_setting")


class RefundRequest(Base):
    """退款申请表 P34"""
    __tablename__ = "refund_requests"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(String(100), nullable=False)
    note = Column(Text)
    refund_amount = Column(Float)
    status = Column(String(20), default="pending")
    reviewed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="refund_requests")


class AIConsultSession(Base):
    """AI监理咨询会话表 P36"""
    __tablename__ = "ai_consult_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    acceptance_analysis_id = Column(Integer, ForeignKey("acceptance_analyses.id"))
    stage = Column(String(30))
    status = Column(String(20), default="active")
    is_human = Column(Boolean, default=False)
    human_started_at = Column(DateTime)
    paid_amount = Column(Float, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="ai_consult_sessions")
    acceptance_analysis = relationship("AcceptanceAnalysis", back_populates="ai_consult_sessions")
    messages = relationship("AIConsultMessage", back_populates="session", order_by="AIConsultMessage.id")


class AIConsultMessage(Base):
    """AI监理咨询消息表"""
    __tablename__ = "ai_consult_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("ai_consult_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text)
    images = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

    session = relationship("AIConsultSession", back_populates="messages")


class AIConsultQuotaUsage(Base):
    """用户月度AI咨询免费额度使用"""
    __tablename__ = "ai_consult_quota_usage"
    __table_args__ = (UniqueConstraint("user_id", "year_month", name="uq_quota_user_ym"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    year_month = Column(String(7), nullable=False)
    used_count = Column(Integer, default=0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AcceptanceAppeal(Base):
    """验收申诉表 P30 FR-026"""
    __tablename__ = "acceptance_appeals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    acceptance_analysis_id = Column(Integer, ForeignKey("acceptance_analyses.id"), nullable=False)
    stage = Column(String(30), nullable=False)
    reason = Column(Text, nullable=False)
    images = Column(JSON)
    status = Column(String(20), default="pending")
    reviewed_at = Column(DateTime)
    review_note = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="acceptance_appeals")
    acceptance_analysis = relationship("AcceptanceAnalysis", back_populates="appeals")


class SpecialApplication(Base):
    """特殊申请表 P09 FR-016：自主装修豁免 / 争议申诉"""
    __tablename__ = "special_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    application_type = Column(String(30), nullable=False)  # exemption | dispute_appeal
    stage = Column(String(30))
    content = Column(Text, nullable=False)
    images = Column(JSON)
    status = Column(String(20), default="pending")
    reviewed_at = Column(DateTime)
    review_note = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="special_applications")


class MaterialCheck(Base):
    """材料进场人工核对主表 P37"""
    __tablename__ = "material_checks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quote_id = Column(Integer, ForeignKey("quotes.id"))
    result = Column(String(20), nullable=False)  # pass | fail
    problem_note = Column(Text)
    submitted_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="material_checks")
    items = relationship("MaterialCheckItem", back_populates="material_check", cascade="all, delete-orphan")


class MaterialCheckItem(Base):
    """材料核对明细 P37"""
    __tablename__ = "material_check_items"

    id = Column(Integer, primary_key=True, index=True)
    material_check_id = Column(Integer, ForeignKey("material_checks.id"), nullable=False)
    material_name = Column(String(200), nullable=False)
    spec_brand = Column(String(200))
    quantity = Column(String(50))
    photo_urls = Column(JSON, default=list)
    doc_certificate_url = Column(String(512))
    doc_quality_url = Column(String(512))
    doc_ccc_url = Column(String(512))
    created_at = Column(DateTime, server_default=func.now())

    material_check = relationship("MaterialCheck", back_populates="items")


class Material(Base):
    """材料库表（V2.6.2优化：材料库建设）"""
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    material_name = Column(String(200), nullable=False, index=True)  # 材料名称
    category = Column(String(50), index=True)  # 类别：主材/辅材
    spec_brand = Column(String(200))  # 规格/品牌
    unit = Column(String(20))  # 单位：kg/m²/个等
    typical_price_range = Column(JSON)  # 典型价格区间：{"min": 10, "max": 50, "unit": "元/kg"}
    city_code = Column(String(20), index=True)  # 城市代码（可选，用于本地化价格）
    description = Column(Text)  # 材料描述
    is_active = Column(Boolean, default=True)  # 是否启用
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
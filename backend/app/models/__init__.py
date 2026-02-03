"""
装修决策Agent - 数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, ForeignKey, Boolean, Enum as SQLEnum
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
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联关系
    quotes = relationship("Quote", back_populates="user")
    contracts = relationship("Contract", back_populates="user")
    companies = relationship("CompanyScan", back_populates="user")
    orders = relationship("Order", back_populates="user")
    constructions = relationship("Construction", back_populates="user")


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
    unlock_type = Column(String(20))  # single, package

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
    unlock_type = Column(String(20))

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

    # 其他信息
    ordeer_metadata = Column(JSON)
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

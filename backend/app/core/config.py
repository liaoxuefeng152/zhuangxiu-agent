"""
装修决策Agent - 核心配置
"""
import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "装修决策Agent"
    DEBUG: bool = False
    VERSION: str = "2.1.0"

    # 数据库配置 - 必须从环境变量读取
    DATABASE_URL: str = ""
    DATABASE_POOL_SIZE: int = 10  # 优化：减少连接池大小
    DATABASE_MAX_OVERFLOW: int = 10  # 优化：减少溢出连接数
    DATABASE_POOL_TIMEOUT: int = 30  # 连接超时时间（秒）
    DATABASE_POOL_RECYCLE: int = 3600  # 连接回收时间（秒，1小时）

    # Redis配置
    REDIS_URL: str = ""
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # 微信小程序配置 - 必须从环境变量读取
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""

    # 微信支付配置 - 必须从环境变量读取
    WECHAT_MCH_ID: str = ""
    WECHAT_API_KEY: str = ""
    WECHAT_NOTIFY_URL: str = ""

    # 阿里云配置 - 必须从环境变量读取
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_OCR_ENDPOINT: str = "ocr-api.cn-hangzhou.aliyuncs.com"
    ALIYUN_OSS_BUCKET: str = ""
    ALIYUN_OSS_ENDPOINT: str = "oss-cn-hangzhou.aliyuncs.com"

    # 天眼查API配置 - 必须从环境变量读取
    TIANYANCHA_TOKEN: str = ""

    # DeepSeek API配置 - 必须从环境变量读取
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"

    # JWT配置 - 必须从环境变量读取
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "jpg", "jpeg", "png"]
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/jpg"
    ]

    # CORS配置 - 生产环境必须指定具体域名
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:10086",  # 开发环境
    ]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE"]
    ALLOWED_HEADERS: List[str] = ["Authorization", "Content-Type", "X-User-Id"]

    # API限流配置
    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: str = "200/minute"
    SCAN_RATE_LIMIT: str = "10/minute"  # 公司扫描限流
    UPLOAD_RATE_LIMIT: str = "5/minute"  # 文件上传限流

    # 报告定价配置
    REPORT_SINGLE_PRICE: float = 9.9
    REPORT_THREE_PRICE: float = 25.0
    SUPERVISION_SINGLE_PRICE: float = 99.0
    SUPERVISION_PACKAGE_PRICE: float = 268.0

    # 施工阶段默认时长（天）
    STAGE_DURATION: dict = {
        "plumbing": 10,  # 水电
        "carpentry": 20,  # 泥木
        "painting": 10,  # 油漆
        "flooring": 5,  # 地板
        "soft_furnishing": 6  # 软装
    }

    class Config:
        env_file = ".env"
        case_sensitive = True

    @classmethod
    def validate(cls, v):
        """验证关键配置"""
        # 生产环境强制验证
        if not v.DEBUG:
            # 数据库配置验证
            if not v.DATABASE_URL:
                raise ValueError("生产环境必须设置DATABASE_URL环境变量")
            if "decoration123" in v.DATABASE_URL:
                raise ValueError("请修改默认数据库密码")

            # JWT密钥验证
            if not v.SECRET_KEY:
                raise ValueError("生产环境必须设置SECRET_KEY环境变量")
            if v.SECRET_KEY == "your-secret-key-change-in-production":
                raise ValueError("请修改默认SECRET_KEY")

            # 微信配置验证
            if not v.WECHAT_APP_ID or not v.WECHAT_APP_SECRET:
                raise ValueError("生产环境必须设置WECHAT_APP_ID和WECHAT_APP_SECRET")

            # 阿里云配置验证
            if not v.ALIYUN_ACCESS_KEY_ID or not v.ALIYUN_ACCESS_KEY_SECRET:
                raise ValueError("生产环境必须设置阿里云访问密钥")

            # CORS配置验证
            if not v.ALLOWED_ORIGINS:
                raise ValueError("生产环境必须配置ALLOWED_ORIGINS")
            if "*" in v.ALLOWED_ORIGINS:
                raise ValueError("生产环境不能使用通配符CORS配置")

        return v


# 创建配置实例并验证
settings = Settings()
settings.validate(settings)
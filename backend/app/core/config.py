"""
装修决策Agent - 核心配置
"""
import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "装修决策Agent"
    DEBUG: bool = False

    @field_validator("DEBUG", mode="before")
    @classmethod
    def coerce_debug(cls, v):
        """兼容环境变量 DEBUG=True 为字符串的情况"""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.strip().lower() in ("true", "1", "yes")
        return bool(v)

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
    # 微信公众平台「接口配置信息」URL 验证用 Token（与后台填写的 Token 一致）
    WECHAT_CALLBACK_TOKEN: str = ""
    # 微信模板消息 - 家装服务进度提醒（方案已生成），模板内容含 {{方案名称.DATA}}
    WECHAT_TEMPLATE_PROGRESS_REMINDER: str = ""

    # 微信支付配置 - 必须从环境变量读取
    WECHAT_MCH_ID: str = ""
    WECHAT_API_KEY: str = ""
    WECHAT_NOTIFY_URL: str = ""

    # 阿里云配置 - 必须从环境变量读取
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_OCR_ENDPOINT: str = "ocr-api.cn-hangzhou.aliyuncs.com"
    ALIYUN_OSS_BUCKET: str = ""  # banners使用的bucket
    ALIYUN_OSS_BUCKET1: str = ""  # 照片上传使用的bucket
    ALIYUN_OSS_ENDPOINT: str = "oss-cn-hangzhou.aliyuncs.com"

    # 天眼查API配置 - 必须从环境变量读取
    TIANYANCHA_TOKEN: str = ""

    # 聚合数据API配置 - 必须从环境变量读取
    JUHECHA_TOKEN: str = ""
    JUHECHA_API_BASE: str = "http://v.juhe.cn"
    JUHECHA_SIFA_ENDPOINT: str = "/sifa/ent"  # 司法企业查询
    
    # 聚合数据企业工商信息API配置
    SIMPLE_LIST_TOKEN: str = ""
    JUHECHA_ENTERPRISE_API_BASE: str = "http://japi.juhe.cn"
    JUHECHA_ENTERPRISE_ENDPOINT: str = "/enterprise/simpleList"  # 企业工商信息查询

    # DeepSeek API配置（与扣子二选一，用于报价/合同/验收 AI 分析）
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"

    # 扣子 Coze 智能体 API（优先于 DeepSeek：若配置则用扣子，否则用 DeepSeek）
    # 方式一：扣子开放平台 api.coze.cn（需 COZE_API_TOKEN + COZE_BOT_ID）
    COZE_API_TOKEN: str = ""   # 扣子开放平台个人访问令牌 PAT 或 OAuth Access Token
    COZE_BOT_ID: str = ""     # 扣子平台部署的智能体 Bot ID
    COZE_API_BASE: str = "https://api.coze.cn"  # 可选，默认国内
    # 方式二：扣子发布站点 xxx.coze.site/stream_run（需 COZE_SITE_URL + COZE_SITE_TOKEN）
    COZE_SITE_URL: str = ""   # 如 https://9n37hmztzw.coze.site
    COZE_SITE_TOKEN: str = "" # Bearer Token
    COZE_PROJECT_ID: str = "" # project_id，如 7603691852046368804
    COZE_SESSION_ID: str = "" # 可选，不填则每次请求生成新 session
    
    # AI设计师智能体配置（扣子平台部署）
    DESIGN_SITE_URL: str = ""   # AI设计师站点URL，如 https://66g9ffxgrz.coze.site/stream_run
    DESIGN_SITE_TOKEN: str = "" # AI设计师Bearer Token
    DESIGN_PROJECT_ID: str = "" # AI设计师project_id

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

    # 报告定价配置（V2.6.2优化）
    REPORT_SINGLE_PRICE: float = 9.9
    REPORT_THREE_PRICE: float = 25.0  # 已废弃，会员改为无限解锁
    SUPERVISION_SINGLE_PRICE: float = 99.0
    SUPERVISION_PACKAGE_PRICE: float = 268.0
    
    # 会员定价配置（V2.6.2优化）
    MEMBER_MONTHLY_PRICE: float = 29.9   # 月付
    MEMBER_QUARTERLY_PRICE: float = 69.9  # 季付
    MEMBER_YEARLY_PRICE: float = 268.0   # 年付（优惠）

    # 施工阶段默认时长（天）PRD V2.6.1 对齐 V15.3 六阶段 S00-S05
    STAGE_DURATION: dict = {
        "S00": 3,   # 材料进场人工核对
        "S01": 7,   # 隐蔽工程
        "S02": 10,  # 泥瓦工
        "S03": 7,   # 木工
        "S04": 7,   # 油漆
        "S05": 5,   # 安装收尾
        # 兼容旧键
        "material": 3,
        "plumbing": 7,
        "carpentry": 10,
        "woodwork": 7,
        "painting": 7,
        "installation": 5,
        "flooring": 5,
        "soft_furnishing": 6,
    }
    # 六阶段顺序（PRD S00→S05）
    STAGE_ORDER: list = ["S00", "S01", "S02", "S03", "S04", "S05"]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # 允许额外的环境变量

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def dev_secret_default(cls, v: str):
        """SECRET_KEY 为空时优先用环境变量，再兜底默认值（生产环境由 validate 校验）"""
        if v:
            return v
        return os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

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

            # 阿里云配置验证（注释：生产环境可以使用ECS RAM角色，无需AccessKey）
            # 如果使用RAM角色，可以不设置ALIYUN_ACCESS_KEY_ID和ALIYUN_ACCESS_KEY_SECRET
            # 但需要确保ECS实例已绑定正确的RAM角色

            # CORS配置验证
            if not v.ALLOWED_ORIGINS:
                raise ValueError("生产环境必须配置ALLOWED_ORIGINS")
            if "*" in v.ALLOWED_ORIGINS:
                raise ValueError("生产环境不能使用通配符CORS配置")

        return v


# 创建配置实例并验证
settings = Settings()
settings.validate(settings)

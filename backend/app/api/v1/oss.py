"""
OSS 直传 - 后端签名 + 前端直传（阿里云最佳实践）
"""
import base64
import hmac
import hashlib
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import settings
from app.core.security import get_user_id
from app.schemas import ApiResponse
from app.services.oss_service import oss_service
import logging

router = APIRouter(prefix="/oss", tags=["OSS直传"])
logger = logging.getLogger(__name__)


@router.get("/upload-policy")
async def get_upload_policy(
    stage: str = Query(..., description="material|plumbing|carpentry|woodwork|painting|installation"),
    user_id: int = Depends(get_user_id),
):
    """
    获取 OSS PostObject 直传所需的 policy 和签名
    前端拿到后直接 POST 到 OSS，实现「后端签名 + 前端直传」
    若 OSS 未配置，返回 available=false，前端应走后端代理上传（如 /acceptance/upload-photo）
    """
    # OSS 未配置时返回 200 + available=false，避免 503 导致前端报错；前端可回退到后端代理上传
    has_key = bool(settings.ALIYUN_ACCESS_KEY_ID and settings.ALIYUN_ACCESS_KEY_SECRET)
    has_bucket = bool(settings.ALIYUN_OSS_BUCKET1 and (settings.ALIYUN_OSS_ENDPOINT or "oss-cn-hangzhou.aliyuncs.com"))
    if not has_key or not has_bucket:
        logger.info("OSS upload-policy: 未配置或配置不完整，返回 available=false")
        return ApiResponse(
            code=0,
            msg="OSS 未配置，请使用后端代理上传",
            data={
                "available": False,
                "reason": "oss_not_configured",
                "message": "OSS 未配置。请在服务器环境变量中配置 ALIYUN_ACCESS_KEY_ID、ALIYUN_ACCESS_KEY_SECRET、ALIYUN_OSS_BUCKET1（如 zhuangxiu-images-dev-photo）。",
            },
        )

    valid_stages = ["material", "plumbing", "carpentry", "woodwork", "painting", "installation"]
    if stage not in valid_stages:
        raise HTTPException(status_code=400, detail="无效的阶段")

    dir_prefix = f"construction/{stage}/"
    expire_seconds = 600
    max_size = settings.MAX_UPLOAD_SIZE or (10 * 1024 * 1024)

    expire_gmt = (datetime.utcnow() + timedelta(seconds=expire_seconds)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    policy_dict = {
        "expiration": expire_gmt,
        "conditions": [
            ["content-length-range", 1, max_size],
            ["starts-with", "$key", dir_prefix],
            ["in", "$content-type", ["image/jpeg", "image/png", "image/jpg"]],
        ],
    }
    policy_str = json.dumps(policy_dict, separators=(",", ":"))
    policy_b64 = base64.b64encode(policy_str.encode("utf-8")).decode("utf-8")

    signature = base64.b64encode(
        hmac.new(
            settings.ALIYUN_ACCESS_KEY_SECRET.encode("utf-8"),
            policy_b64.encode("utf-8"),
            hashlib.sha1,
        ).digest()
    ).decode("utf-8")

    # 使用照片bucket
    endpoint = settings.ALIYUN_OSS_ENDPOINT or "oss-cn-hangzhou.aliyuncs.com"
    host = f"https://{settings.ALIYUN_OSS_BUCKET1}.{endpoint}"

    return ApiResponse(
        code=0,
        msg="success",
        data={
            "available": True,
            "host": host,
            "policy": policy_b64,
            "OSSAccessKeyId": settings.ALIYUN_ACCESS_KEY_ID,
            "signature": signature,
            "dir": dir_prefix,
            "expire": expire_seconds,
        },
    )


@router.get("/sign-url")
async def get_sign_url(
    object_key: str = Query(..., description="OSS 对象键"),
    user_id: int = Depends(get_user_id),
):
    """
    获取私有对象的临时签名 URL，用于前端展示图片等。
    过期时间 3600 秒（1 小时）。
    """
    try:
        url = oss_service.sign_url_for_key(object_key, expires=3600)
        return ApiResponse(code=0, msg="success", data={"url": url})
    except Exception as e:
        logger.error(f"sign-url 失败: object_key={object_key}, error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail="生成签名 URL 失败")

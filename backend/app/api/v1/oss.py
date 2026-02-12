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
    """
    if not settings.ALIYUN_ACCESS_KEY_ID or not settings.ALIYUN_ACCESS_KEY_SECRET:
        raise HTTPException(status_code=503, detail="OSS 未配置，暂不支持直传")

    if not settings.ALIYUN_OSS_BUCKET or not settings.ALIYUN_OSS_ENDPOINT:
        raise HTTPException(status_code=503, detail="OSS Bucket 未配置")

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

    host = f"https://{settings.ALIYUN_OSS_BUCKET}.{settings.ALIYUN_OSS_ENDPOINT}"

    return ApiResponse(
        code=0,
        msg="success",
        data={
            "host": host,
            "policy": policy_b64,
            "OSSAccessKeyId": settings.ALIYUN_ACCESS_KEY_ID,
            "signature": signature,
            "dir": dir_prefix,
            "expire": expire_seconds,
        },
    )

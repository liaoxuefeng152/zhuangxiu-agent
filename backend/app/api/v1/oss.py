"""
OSS 相关 API
提供文件上传、下载、管理等接口
使用ECS RAM角色自动获取凭证，无需AccessKey
"""
import hashlib
import hmac
import base64
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_user_id
from app.core.config import settings
from app.services.oss_service import oss_service

router = APIRouter()


@router.get("/oss/config")
async def get_oss_config(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取OSS前端直传配置（使用RAM角色，无需AccessKey）
    
    返回前端SDK需要的配置，用于直接上传到OSS
    """
    try:
        # 检查OSS配置
        if not settings.ALIYUN_OSS_BUCKET1:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": 503,
                    "msg": "OSS 未配置。请在服务器环境变量中配置 ALIYUN_OSS_BUCKET1（如 zhuangxiu-images-dev-photo）。",
                    "data": None
                }
            )
        
        # 使用ECS RAM角色，无需AccessKey
        # OSS服务会自动通过元数据服务获取临时凭证
        
        # 生成策略条件
        expiration = int(time.time()) + 3600  # 1小时后过期
        
        # 构建上传策略
        policy_dict = {
            "expiration": f"{expiration}",  # 策略过期时间
            "conditions": [
                {"bucket": settings.ALIYUN_OSS_BUCKET1},
                ["starts-with", "$key", "acceptance/"],
                ["content-length-range", 0, 10485760]  # 10MB限制
            ]
        }
        
        # 将策略转换为JSON字符串
        import json
        policy = json.dumps(policy_dict, separators=(',', ':'))
        
        # Base64编码策略
        policy_base64 = base64.b64encode(policy.encode()).decode()
        
        # 使用RAM角色，无需签名（前端直传使用PostObject方式）
        # 注意：由于使用RAM角色，我们无法在服务端生成签名
        # 前端需要使用STS临时凭证或PostObject方式
        
        return {
            "code": 200,
            "msg": "OSS配置获取成功",
            "data": {
                "bucket": settings.ALIYUN_OSS_BUCKET1,
                "endpoint": settings.ALIYUN_OSS_ENDPOINT,
                "policy": policy_base64,
                "expiration": expiration,
                "use_ram_role": True,  # 标识使用RAM角色
                "note": "使用ECS RAM角色自动获取凭证，前端请使用PostObject方式上传"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": 500,
                "msg": f"获取OSS配置失败: {str(e)}",
                "data": None
            }
        )


@router.get("/oss/sts-token")
async def get_sts_token(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取STS临时凭证（备用接口）
    
    如果前端需要STS token，可以通过此接口获取
    注意：使用RAM角色时，通常不需要STS token
    """
    try:
        # 检查OSS配置
        if not settings.ALIYUN_OSS_BUCKET1:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": 503,
                    "msg": "OSS 未配置。请在服务器环境变量中配置 ALIYUN_OSS_BUCKET1。",
                    "data": None
                }
            )
        
        # 使用RAM角色时，建议前端直接使用PostObject方式
        # 如果需要STS token，需要调用阿里云STS服务
        
        return {
            "code": 200,
            "msg": "使用ECS RAM角色，建议前端使用PostObject方式上传",
            "data": {
                "bucket": settings.ALIYUN_OSS_BUCKET1,
                "endpoint": settings.ALIYUN_OSS_ENDPOINT,
                "use_ram_role": True,
                "recommendation": "前端请使用PostObject方式上传，无需STS token",
                "documentation": "https://help.aliyun.com/zh/oss/developer-reference/postobject"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": 500,
                "msg": f"获取STS token失败: {str(e)}",
                "data": None
            }
        )


@router.get("/oss/test-connection")
async def test_oss_connection(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    测试OSS连接是否正常
    
    验证ECS RAM角色是否正常工作
    """
    try:
        # 测试OSS服务连接
        if not oss_service.auth:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": 503,
                    "msg": "OSS服务未初始化，请检查ECS实例是否绑定RAM角色",
                    "data": None
                }
            )
        
        # 尝试获取bucket信息
        bucket_info = None
        if oss_service.photo_bucket:
            try:
                bucket_info = oss_service.photo_bucket.get_bucket_info()
            except Exception as e:
                # 记录错误但不抛出，可能权限不足
                pass
        
        return {
            "code": 200,
            "msg": "OSS连接测试完成",
            "data": {
                "oss_configured": bool(settings.ALIYUN_OSS_BUCKET1),
                "oss_initialized": bool(oss_service.auth),
                "bucket_accessible": bool(bucket_info),
                "use_ram_role": True,
                "ram_role_status": "使用ECS RAM角色自动获取凭证",
                "recommendation": "确保ECS实例已绑定RAM角色 'zhuangxiu-ecs-role'"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": 500,
                "msg": f"测试OSS连接失败: {str(e)}",
                "data": None
            }
        )

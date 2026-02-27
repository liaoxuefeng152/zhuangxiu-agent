"""
OSS文件存储服务 - 修复版本
修复RAM角色认证问题，确保照片上传正常工作
"""
import oss2
from app.core.config import settings
from fastapi import UploadFile
import logging
import time
import random
from typing import Optional, Dict
import requests

logger = logging.getLogger(__name__)


class OSSServiceFixed:
    """OSS文件存储服务 - 修复RAM角色认证问题"""

    def __init__(self):
        """初始化OSS客户端 - 修复RAM角色认证"""
        try:
            # 记录配置信息
            logger.info(f"OSS配置检查 - ALIYUN_ACCESS_KEY_ID: {'已配置' if getattr(settings, 'ALIYUN_ACCESS_KEY_ID', None) else '未配置'}")
            logger.info(f"OSS配置检查 - ALIYUN_OSS_BUCKET1: {getattr(settings, 'ALIYUN_OSS_BUCKET1', '未配置')}")
            logger.info(f"OSS配置检查 - ALIYUN_OSS_ENDPOINT: {getattr(settings, 'ALIYUN_OSS_ENDPOINT', '未配置')}")
            
            # 优先使用AccessKey认证
            access_key_id = getattr(settings, 'ALIYUN_ACCESS_KEY_ID', None)
            access_key_secret = getattr(settings, 'ALIYUN_ACCESS_KEY_SECRET', None)
            
            if access_key_id and access_key_secret:
                # 使用AccessKey认证
                self.auth = oss2.Auth(access_key_id, access_key_secret)
                logger.info("OSS客户端初始化 - 使用AccessKey认证")
                logger.info(f"AccessKey ID: {access_key_id[:10]}...")
            else:
                # 使用RAM角色自动获取凭证
                logger.info("OSS客户端初始化 - 使用RAM角色自动获取凭证")
                self.auth = self._get_ram_role_auth()
            
            # 初始化buckets
            self._init_buckets()
            
            # 测试连接
            self._test_connection()
            
        except Exception as e:
            logger.error(f"OSS客户端初始化失败: {e}", exc_info=True)
            self.auth = None
            self.bucket = None
            self.photo_bucket = None

    def _get_ram_role_auth(self):
        """获取RAM角色认证"""
        try:
            # 获取RAM角色名称
            role_url = 'http://100.100.100.200/latest/meta-data/ram/security-credentials/'
            response = requests.get(role_url, timeout=2)
            if response.status_code == 200:
                role_name = response.text.strip()
                logger.info(f"检测到ECS RAM角色: {role_name}")
                
                # 获取临时凭证
                cred_url = f'http://100.100.100.200/latest/meta-data/ram/security-credentials/{role_name}'
                cred_response = requests.get(cred_url, timeout=2)
                if cred_response.status_code == 200:
                    credentials = cred_response.json()
                    access_key_id = credentials.get('AccessKeyId')
                    access_key_secret = credentials.get('AccessKeySecret')
                    security_token = credentials.get('SecurityToken')
                    
                    if access_key_id and access_key_secret:
                        logger.info(f"获取RAM角色临时凭证成功: {access_key_id[:10]}...")
                        # 使用带SecurityToken的认证
                        auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
                        return auth
                    else:
                        logger.error("RAM角色凭证信息不完整")
                else:
                    logger.error(f"获取RAM角色凭证失败，状态码: {cred_response.status_code}")
            else:
                logger.error(f"获取RAM角色名称失败，状态码: {response.status_code}")
        except Exception as e:
            logger.error(f"获取RAM角色认证失败: {e}")
        
        # 如果RAM角色认证失败，返回None
        logger.warning("RAM角色认证失败，返回None")
        return None

    def _init_buckets(self):
        """初始化buckets"""
        # banners使用的bucket
        if settings.ALIYUN_OSS_BUCKET and self.auth:
            self.bucket = oss2.Bucket(
                self.auth,
                settings.ALIYUN_OSS_ENDPOINT,
                settings.ALIYUN_OSS_BUCKET
            )
            logger.info(f"初始化Banners Bucket: {settings.ALIYUN_OSS_BUCKET}, Endpoint: {settings.ALIYUN_OSS_ENDPOINT}")
        else:
            self.bucket = None
            if not settings.ALIYUN_OSS_BUCKET:
                logger.warning("ALIYUN_OSS_BUCKET未配置，Banners功能不可用")
            elif not self.auth:
                logger.warning("OSS认证未配置，Banners功能不可用")
        
        # 照片上传使用的bucket
        if settings.ALIYUN_OSS_BUCKET1 and self.auth:
            self.photo_bucket = oss2.Bucket(
                self.auth,
                settings.ALIYUN_OSS_ENDPOINT,
                settings.ALIYUN_OSS_BUCKET1
            )
            logger.info(f"初始化照片Bucket: {settings.ALIYUN_OSS_BUCKET1}, Endpoint: {settings.ALIYUN_OSS_ENDPOINT}")
        else:
            self.photo_bucket = None
            if not settings.ALIYUN_OSS_BUCKET1:
                logger.warning("ALIYUN_OSS_BUCKET1未配置，照片上传功能不可用")
            elif not self.auth:
                logger.warning("OSS认证未配置，照片上传功能不可用")

    def _test_connection(self):
        """测试OSS连接是否正常"""
        try:
            if self.bucket:
                bucket_info = self.bucket.get_bucket_info()
                logger.info(f"OSS连接测试成功 - Bucket: {bucket_info.name}, 区域: {bucket_info.location}")
            elif self.photo_bucket:
                bucket_info = self.photo_bucket.get_bucket_info()
                logger.info(f"OSS连接测试成功 - Photo Bucket: {bucket_info.name}, 区域: {bucket_info.location}")
            else:
                logger.warning("没有可用的OSS Bucket配置")
        except Exception as e:
            logger.warning(f"OSS连接测试失败（可能权限不足或网络问题）: {e}")

    def upload_file(self, file_data: bytes, filename: str,
                    bucket_name: Optional[str] = None, expires_days: Optional[int] = None) -> str:
        """
        上传文件到OSS
        """
        # 选择bucket：照片使用photo_bucket，其他使用默认bucket
        bucket = self.photo_bucket if bucket_name == 'photo' else self.bucket
        
        if not bucket:
            logger.warning(f"OSS未配置或初始化失败，返回模拟URL: {filename}")
            return f"https://mock-oss.example.com/{filename}"
            
        try:
            bucket.put_object(filename, file_data)
            logger.info(f"文件上传成功: {filename}, Bucket: {bucket.bucket_name}")
            return filename
        except Exception as e:
            logger.error(f"文件上传失败: {filename}, 错误: {e}")
            raise

    def upload_upload_file(self, file: UploadFile, file_type: str, user_id: Optional[int] = None, 
                          is_photo: bool = True) -> str:
        """
        上传FastAPI UploadFile到OSS
        """
        # 生成文件名
        fname = file.filename or "photo.jpg"
        ext = (fname.split(".")[-1] or "jpg").lower()
        
        timestamp = int(time.time())
        random_num = random.randint(1000, 9999)
        
        if user_id:
            filename = f"{file_type}/{user_id}/{timestamp}_{random_num}.{ext}"
        else:
            filename = f"{file_type}/{timestamp}_{random_num}.{ext}"

        # 读取文件内容
        file_content = file.file.read()
        file.file.seek(0)  # 重置文件指针

        # 选择bucket
        bucket_name = 'photo' if is_photo else None
        
        object_key = self.upload_file(file_content, filename, bucket_name=bucket_name)
        
        if object_key.startswith("https://mock-oss.example.com"):
            return object_key

        logger.info(f"文件上传成功，object_key: {object_key}")
        return object_key

    def sign_url_for_key(self, object_key: str, expires: int = 3600) -> str:
        """
        根据对象键生成临时签名 URL
        """
        if object_key.startswith("https://"):
            return object_key
            
        import urllib.parse
        try:
            decoded_key = urllib.parse.unquote(object_key)
        except:
            decoded_key = object_key
            
        # 按路径前缀选择 bucket
        if decoded_key.startswith(("acceptance/", "construction/", "material-check/", "designer/")):
            bucket = self.photo_bucket
        else:
            bucket = self.bucket
            
        if not bucket:
            logger.warning(f"OSS 未配置，无法签名: {decoded_key}")
            return object_key
            
        try:
            signed_url = bucket.sign_url("GET", decoded_key, expires, slash_safe=True)
            logger.info(f"生成签名 URL 成功: {decoded_key}, 过期: {expires}秒")
            return signed_url
        except Exception as e:
            logger.error(f"生成签名 URL 失败: {decoded_key}, 错误: {e}", exc_info=True)
            raise


# 创建全局OSS服务实例
oss_service_fixed = OSSServiceFixed()

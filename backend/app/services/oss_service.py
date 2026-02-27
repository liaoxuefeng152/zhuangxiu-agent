"""
OSS文件存储服务
实现安全的文件上传和访问控制
统一所有照片上传到阿里云OSS
- 照片上传到 zhuangxiu-images-dev-photo (ALIYUN_OSS_BUCKET1)
- banners使用 zhuangxiu-images-dev (ALIYUN_OSS_BUCKET)

安全架构：使用ECS实例RAM角色自动获取临时凭证，无需AccessKey
"""
import oss2
from app.core.config import settings
from fastapi import UploadFile
import logging
import time
import random
from typing import Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StorageCache:
    """简单的存储使用情况缓存"""
    
    def __init__(self):
        self.cache: Dict[int, dict] = {}
        self.cache_timestamps: Dict[int, float] = {}
        self.cache_ttl = 3600  # 缓存1小时
        
    def get(self, user_id: int) -> Optional[dict]:
        """获取缓存数据"""
        if user_id not in self.cache:
            return None
            
        # 检查缓存是否过期
        if time.time() - self.cache_timestamps.get(user_id, 0) > self.cache_ttl:
            del self.cache[user_id]
            del self.cache_timestamps[user_id]
            return None
            
        return self.cache[user_id]
    
    def set(self, user_id: int, data: dict):
        """设置缓存数据"""
        self.cache[user_id] = data
        self.cache_timestamps[user_id] = time.time()
        
    def clear(self, user_id: int = None):
        """清除缓存"""
        if user_id:
            if user_id in self.cache:
                del self.cache[user_id]
            if user_id in self.cache_timestamps:
                del self.cache_timestamps[user_id]
        else:
            self.cache.clear()
            self.cache_timestamps.clear()


class OSSService:
    """OSS文件存储服务 - 使用ECS RAM角色自动获取凭证"""

    def __init__(self):
        """初始化OSS客户端 - 优先使用AccessKey，降级到RAM角色"""
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
            
            # 初始化缓存
            self.storage_cache = StorageCache()
            
            # 测试连接
            self._test_connection()
            
        except Exception as e:
            logger.error(f"OSS客户端初始化失败: {e}", exc_info=True)
            self.auth = None
            self.bucket = None
            self.photo_bucket = None
            self.storage_cache = StorageCache()

    def _get_ram_role_auth(self):
        """获取RAM角色认证"""
        try:
            # 获取RAM角色名称
            import requests
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
                # 简单测试：获取bucket信息
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
        上传文件到OSS（私有读写，不设置 ACL）

        Args:
            file_data: 文件二进制数据
            filename: 文件名（会包含路径前缀）
            bucket_name: 指定bucket名称（None则使用默认bucket）
            expires_days: 文件过期天数（None则不设置过期时间）

        Returns:
            文件在OSS中的对象键
        """
        # 选择bucket：照片使用photo_bucket，其他使用默认bucket
        bucket = self.photo_bucket if bucket_name == 'photo' else self.bucket
        
        if not bucket:
            logger.warning(f"OSS未配置或初始化失败，返回模拟URL: {filename}")
            return f"https://mock-oss.example.com/{filename}"
            
        try:
            bucket.put_object(filename, file_data)

            # 注意：文件生命周期规则需要在OSS控制台配置
            logger.info(f"文件上传成功: {filename}, Bucket: {bucket.bucket_name}, 建议生命周期: {expires_days}天")
            return filename

        except Exception as e:
            logger.error(f"文件上传失败: {filename}, 错误: {e}")
            raise

    def upload_upload_file(self, file: UploadFile, file_type: str, user_id: Optional[int] = None, 
                          is_photo: bool = True) -> str:
        """
        上传FastAPI UploadFile到OSS（统一入口，私有读写）

        Args:
            file: FastAPI UploadFile对象
            file_type: 文件类型（quote/contract/acceptance/construction/material-check）
            user_id: 用户ID（可选，用于路径组织）
            is_photo: 是否为照片（True使用照片bucket，False使用默认bucket）

        Returns:
            对象键（object_key），用于后续通过 sign_url_for_key 获取临时访问 URL
        """
        # 生成文件名
        fname = file.filename or "photo.jpg"
        ext = (fname.split(".")[-1] or "jpg").lower()
        
        # 统一文件路径格式：{type}/{user_id}/{timestamp}_{random}.{ext}
        timestamp = int(time.time())
        random_num = random.randint(1000, 9999)
        
        if user_id:
            filename = f"{file_type}/{user_id}/{timestamp}_{random_num}.{ext}"
        else:
            filename = f"{file_type}/{timestamp}_{random_num}.{ext}"

        # 读取文件内容
        file_content = file.file.read()
        file.file.seek(0)  # 重置文件指针

        # 选择bucket和设置生命周期
        bucket_name = 'photo' if is_photo else None
        expires_days = 365 if is_photo else None  # 照片生命周期1年
        
        object_key = self.upload_file(file_content, filename,
                                      bucket_name=bucket_name, expires_days=expires_days)
        
        if object_key.startswith("https://mock-oss.example.com"):
            return object_key

        logger.info(f"文件上传成功，object_key: {object_key}")
        return object_key

    def sign_url_for_key(self, object_key: str, expires: int = 3600) -> str:
        """
        根据对象键生成临时签名 URL（私有 Bucket + 私有 Object 访问方式）
        直接使用OSS SDK生成的签名URL，不做任何修改

        Args:
            object_key: OSS 对象键；若以 https:// 开头则视为模拟 URL 直接返回
            expires: 过期时间（秒），默认 1 小时

        Returns:
            临时访问 URL
        """
        if object_key.startswith("https://"):
            return object_key
            
        # 解码URL编码的object_key（如果已经被编码）
        import urllib.parse
        try:
            # 尝试解码，如果已经是解码状态则保持不变
            decoded_key = urllib.parse.unquote(object_key)
        except:
            decoded_key = object_key
            
        # 按路径前缀选择 bucket：验收/施工/材料/设计师等在 photo_bucket，其余在默认 bucket
        if decoded_key.startswith(("acceptance/", "construction/", "material-check/", "designer/")):
            bucket = self.photo_bucket
        else:
            bucket = self.bucket
            
        if not bucket:
            logger.warning(f"OSS 未配置，无法签名: {decoded_key}")
            return object_key
            
        try:
            # 直接使用OSS SDK生成的签名URL，不做任何修改
            signed_url = bucket.sign_url("GET", decoded_key, expires, slash_safe=True)
            
            logger.info(f"生成签名 URL 成功: {decoded_key}, 过期: {expires}秒")
            logger.info(f"URL: {signed_url[:100]}...")

            return signed_url
            
        except Exception as e:
            logger.error(f"生成签名 URL 失败: {decoded_key}, 错误: {e}", exc_info=True)
            raise

    def generate_signed_url(self, filename: str, expires: int = 3600) -> str:
        """
        生成临时签名URL（默认 bucket，保留兼容）

        Args:
            filename: 文件名
            expires: 过期时间（秒），默认1小时

        Returns:
            临时访问URL
        """
        try:
            url = self.bucket.sign_url('GET', filename, expires)
            logger.info(f"生成签名URL成功: {filename}, 过期时间: {expires}秒")
            return url

        except Exception as e:
            logger.error(f"生成签名URL失败: {filename}, 错误: {e}")
            raise

    def delete_file(self, filename: str) -> bool:
        """
        删除文件

        Args:
            filename: 文件名

        Returns:
            是否删除成功
        """
        try:
            self.bucket.delete_object(filename)
            logger.info(f"文件删除成功: {filename}")
            return True

        except Exception as e:
            logger.error(f"文件删除失败: {filename}, 错误: {e}")
            return False

    def get_user_storage_usage(self, user_id: int, force_refresh: bool = False) -> dict:
        """
        获取用户在OSS上的真实存储使用情况
        
        Args:
            user_id: 用户ID
            force_refresh: 是否强制刷新缓存
            
        Returns:
            存储使用情况字典，包含总大小、文件数量、按类型统计等信息
        """
        try:
            # 检查缓存
            if not force_refresh:
                cached_data = self.storage_cache.get(user_id)
                if cached_data:
                    logger.info(f"使用缓存数据 for user {user_id}")
                    return cached_data
            
            # 如果没有配置OSS，返回模拟数据
            if not self.auth or not self.photo_bucket:
                logger.warning(f"OSS未配置，返回模拟存储数据 for user {user_id}")
                result = {
                    "total_size_bytes": 0,
                    "total_size_mb": 0.0,
                    "file_count": 0,
                    "by_type": {},
                    "estimated": True
                }
                self.storage_cache.set(user_id, result)
                return result
            
            # 定义要搜索的文件类型前缀
            file_types = [
                ("construction", f"construction/{user_id}/"),
                ("acceptance", f"acceptance/{user_id}/"),
                ("material-check", f"material-check/{user_id}/"),
                ("quote", f"quote/{user_id}/"),
                ("contract", f"contract/{user_id}/"),
                ("company", f"company/{user_id}/")
            ]
            
            total_size_bytes = 0
            total_file_count = 0
            by_type = {}
            
            # 遍历所有文件类型，统计每个bucket
            buckets_to_check = [
                (self.photo_bucket, ["construction", "acceptance", "material-check"]),
                (self.bucket, ["quote", "contract", "company"])
            ]
            
            for bucket, types_in_bucket in buckets_to_check:
                if not bucket:
                    continue
                    
                for file_type, prefix in file_types:
                    if file_type not in types_in_bucket:
                        continue
                        
                    try:
                        # 使用分页查询，避免一次性加载过多文件
                        marker = ""
                        type_size_bytes = 0
                        type_file_count = 0
                        
                        while True:
                            result = bucket.list_objects(
                                prefix=prefix,
                                marker=marker,
                                max_keys=100  # 每次最多查询100个文件
                            )
                            
                            for obj in result.object_list:
                                type_size_bytes += obj.size
                                type_file_count += 1
                            
                            total_size_bytes += type_size_bytes
                            total_file_count += type_file_count
                            
                            # 记录该类型的统计信息
                            if type_file_count > 0:
                                by_type[file_type] = {
                                    "count": type_file_count,
                                    "size_bytes": type_size_bytes,
                                    "size_mb": round(type_size_bytes / (1024 * 1024), 2)
                                }
                            
                            if not result.is_truncated:
                                break
                                
                            marker = result.next_marker
                            
                    except Exception as e:
                        logger.error(f"统计{file_type}类型文件失败: {e}")
                        continue
            
            # 计算总大小（MB）
            total_size_mb = round(total_size_bytes / (1024 * 1024), 2)
            
            result = {
                "total_size_bytes": total_size_bytes,
                "total_size_mb": total_size_mb,
                "file_count": total_file_count,
                "by_type": by_type,
                "estimated": False,
                "cached": False,
                "timestamp": time.time()
            }
            
            logger.info(f"用户{user_id}存储使用统计: {total_file_count}个文件, {total_size_mb}MB")
            
            # 缓存结果
            self.storage_cache.set(user_id, result)
            return result
            
        except Exception as e:
            logger.error(f"获取用户{user_id}存储使用情况失败: {e}")
            # 出错时返回空数据
            result = {
                "total_size_bytes": 0,
                "total_size_mb": 0.0,
                "file_count": 0,
                "by_type": {},
                "estimated": True,
                "error": str(e),
                "cached": False,
                "timestamp": time.time()
            }
            # 即使出错也缓存，避免频繁重试
            self.storage_cache.set(user_id, result)
            return result


# 创建全局OSS服务实例
oss_service = OSSService()

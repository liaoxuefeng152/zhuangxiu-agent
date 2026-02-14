"""
OSS文件存储服务
实现安全的文件上传和访问控制
统一所有照片上传到阿里云OSS
- 照片上传到 zhuangxiu-images-dev-photo (ALIYUN_OSS_BUCKET1)
- banners使用 zhuangxiu-images-dev (ALIYUN_OSS_BUCKET)
"""
import oss2
from app.core.config import settings
from fastapi import UploadFile
import logging
import time
import random
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OSSService:
    """OSS文件存储服务"""

    def __init__(self):
        """初始化OSS客户端"""
        if not settings.ALIYUN_ACCESS_KEY_ID or not settings.ALIYUN_ACCESS_KEY_SECRET:
            logger.warning("OSS配置不存在，将使用模拟URL")
            self.auth = None
            self.bucket = None
            self.photo_bucket = None
            return
            
        self.auth = oss2.Auth(
            settings.ALIYUN_ACCESS_KEY_ID,
            settings.ALIYUN_ACCESS_KEY_SECRET
        )
        
        # banners使用的bucket
        if settings.ALIYUN_OSS_BUCKET:
            self.bucket = oss2.Bucket(
                self.auth,
                settings.ALIYUN_OSS_ENDPOINT,
                settings.ALIYUN_OSS_BUCKET
            )
        else:
            self.bucket = None
            
        # 照片上传使用的bucket
        if settings.ALIYUN_OSS_BUCKET1:
            self.photo_bucket = oss2.Bucket(
                self.auth,
                settings.ALIYUN_OSS_ENDPOINT,
                settings.ALIYUN_OSS_BUCKET1
            )
        else:
            self.photo_bucket = None

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
            logger.warning(f"OSS未配置，返回模拟URL: {filename}")
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

        Args:
            object_key: OSS 对象键；若以 https:// 开头则视为模拟 URL 直接返回
            expires: 过期时间（秒），默认 1 小时

        Returns:
            临时访问 URL
        """
        if object_key.startswith("https://"):
            return object_key
        # 按路径前缀选择 bucket：验收/施工/材料等在 photo_bucket，其余在默认 bucket
        if object_key.startswith(("acceptance/", "construction/", "material-check/")):
            bucket = self.photo_bucket
        else:
            bucket = self.bucket
        if not bucket:
            logger.warning(f"OSS 未配置，无法签名: {object_key}")
            return object_key
        try:
            url = bucket.sign_url("GET", object_key, expires)
            # 强制 HTTPS，避免 Bucket 仅允许 HTTPS 时出现 403
            if url.startswith("http://"):
                url = "https://" + url[7:]
            logger.info(f"生成签名 URL 成功: {object_key}, 过期: {expires}秒")
            return url
        except Exception as e:
            logger.error(f"生成签名 URL 失败: {object_key}, 错误: {e}")
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


# 创建全局OSS服务实例
oss_service = OSSService()

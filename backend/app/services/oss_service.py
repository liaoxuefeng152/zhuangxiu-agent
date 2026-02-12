"""
OSS文件存储服务
实现安全的文件上传和访问控制
统一所有照片上传到阿里云OSS
"""
import oss2
from app.core.config import settings
from fastapi import UploadFile
import logging
import time
import random
from typing import Optional

logger = logging.getLogger(__name__)


class OSSService:
    """OSS文件存储服务"""

    def __init__(self):
        """初始化OSS客户端"""
        if not settings.ALIYUN_ACCESS_KEY_ID or not settings.ALIYUN_ACCESS_KEY_SECRET:
            logger.warning("OSS配置不存在，将使用模拟URL")
            self.bucket = None
            return
            
        self.auth = oss2.Auth(
            settings.ALIYUN_ACCESS_KEY_ID,
            settings.ALIYUN_ACCESS_KEY_SECRET
        )
        self.bucket = oss2.Bucket(
            self.auth,
            settings.ALIYUN_OSS_ENDPOINT,
            settings.ALIYUN_OSS_BUCKET
        )

    def upload_file(self, file_data: bytes, filename: str, acl: str = 'public-read') -> str:
        """
        上传文件到OSS

        Args:
            file_data: 文件二进制数据
            filename: 文件名（会包含路径前缀）
            acl: 访问权限，默认为public-read（公共读，便于小程序直接访问）

        Returns:
            文件在OSS中的对象键
        """
        if not self.bucket:
            logger.warning(f"OSS未配置，返回模拟URL: {filename}")
            return f"https://mock-oss.example.com/{filename}"
            
        try:
            # 上传文件
            self.bucket.put_object(filename, file_data)

            # 设置访问权限（公共读，便于小程序直接访问）
            self.bucket.put_object_acl(filename, acl)

            logger.info(f"文件上传成功: {filename}, ACL: {acl}")
            return filename

        except Exception as e:
            logger.error(f"文件上传失败: {filename}, 错误: {e}")
            raise

    def upload_upload_file(self, file: UploadFile, file_type: str, user_id: Optional[int] = None) -> str:
        """
        上传FastAPI UploadFile到OSS（统一入口）

        Args:
            file: FastAPI UploadFile对象
            file_type: 文件类型（quote/contract/acceptance/construction/material-check）
            user_id: 用户ID（可选，用于路径组织）

        Returns:
            文件URL
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

        # 上传到OSS
        object_key = self.upload_file(file_content, filename, acl='public-read')
        
        # 返回完整URL
        if object_key.startswith("https://mock-oss.example.com"):
            return object_key
        
        file_url = f"https://{settings.ALIYUN_OSS_BUCKET}.{settings.ALIYUN_OSS_ENDPOINT}/{object_key}"
        logger.info(f"文件上传成功，URL: {file_url}")
        return file_url

    def generate_signed_url(self, filename: str, expires: int = 3600) -> str:
        """
        生成临时签名URL

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

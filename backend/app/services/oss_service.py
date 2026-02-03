"""
OSS文件存储服务
实现安全的文件上传和访问控制
"""
import oss2
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class OSSService:
    """OSS文件存储服务"""

    def __init__(self):
        """初始化OSS客户端"""
        self.auth = oss2.Auth(
            settings.ALIYUN_ACCESS_KEY_ID,
            settings.ALIYUN_ACCESS_KEY_SECRET
        )
        self.bucket = oss2.Bucket(
            self.auth,
            settings.ALIYUN_OSS_ENDPOINT,
            settings.ALIYUN_OSS_BUCKET
        )

    def upload_file(self, file_data: bytes, filename: str, acl: str = 'private') -> str:
        """
        上传文件到OSS

        Args:
            file_data: 文件二进制数据
            filename: 文件名（会包含路径前缀）
            acl: 访问权限，默认为private（私有）

        Returns:
            文件在OSS中的对象键
        """
        try:
            # 上传文件
            self.bucket.put_object(filename, file_data)

            # 设置访问权限为私有
            self.bucket.put_object_acl(filename, acl)

            logger.info(f"文件上传成功: {filename}, ACL: {acl}")
            return filename

        except Exception as e:
            logger.error(f"文件上传失败: {filename}, 错误: {e}")
            raise

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

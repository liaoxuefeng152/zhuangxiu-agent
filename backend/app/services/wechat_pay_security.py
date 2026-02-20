"""
微信支付安全工具类 - 安全的密钥读取、签名生成、数据解密
遵循微信支付V3规范，实现安全的密钥管理和加密操作
"""
import os
import base64
import logging
from typing import Optional, Tuple
from pathlib import Path
import stat
import hashlib
import hmac
import time
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)


class WeChatPaySecurityError(Exception):
    """微信支付安全相关异常"""
    pass


class WeChatPaySecurity:
    """
    微信支付安全工具类
    
    功能：
    1. 安全的密钥文件读取（AES密钥、RSA私钥）
    2. 微信支付V3 RSA-SHA256签名生成
    3. 微信支付V3 AES-GCM敏感数据解密
    4. 文件权限校验和安全日志记录
    """
    
    # 默认密钥文件路径
    DEFAULT_AES_KEY_PATH = "/etc/wechat_secrets/aes_key.txt"
    DEFAULT_RSA_KEY_PATH = "/etc/wechat_secrets/private_key.pem"
    
    def __init__(
        self,
        aes_key_path: Optional[str] = None,
        rsa_key_path: Optional[str] = None
    ):
        """
        初始化微信支付安全工具
        
        Args:
            aes_key_path: AES密钥文件路径，默认 /etc/wechat_secrets/aes_key.txt
            rsa_key_path: RSA私钥文件路径，默认 /etc/wechat_secrets/private_key.pem
        """
        self.aes_key_path = Path(aes_key_path or self.DEFAULT_AES_KEY_PATH)
        self.rsa_key_path = Path(rsa_key_path or self.DEFAULT_RSA_KEY_PATH)
        
        # 缓存密钥，避免重复读取
        self._aes_key: Optional[bytes] = None
        self._rsa_private_key = None
        
        logger.info(f"微信支付安全工具初始化完成，AES密钥路径: {self.aes_key_path}, RSA密钥路径: {self.rsa_key_path}")
    
    def _validate_file_permissions(self, file_path: Path) -> None:
        """
        验证文件权限
        
        Args:
            file_path: 文件路径
            
        Raises:
            WeChatPaySecurityError: 文件权限不安全
        """
        try:
            stat_info = file_path.stat()
            mode = stat_info.st_mode
            
            # 检查文件权限：应该只有所有者有读写权限 (600)
            if mode & (stat.S_IRWXG | stat.S_IRWXO):
                raise WeChatPaySecurityError(
                    f"文件权限不安全: {file_path}。"
                    f"当前权限: {oct(mode)[-3:]}，应为 600 (仅所有者可读写)"
                )
            
            # 检查文件所有者是否为root
            if stat_info.st_uid != 0:
                logger.warning(f"文件 {file_path} 的所有者不是root用户")
                
        except FileNotFoundError:
            raise WeChatPaySecurityError(f"密钥文件不存在: {file_path}")
        except PermissionError:
            raise WeChatPaySecurityError(f"没有权限访问密钥文件: {file_path}")
    
    def _read_aes_key(self) -> bytes:
        """
        安全读取AES密钥文件
        
        Returns:
            bytes: 解码后的AES密钥（32字节）
            
        Raises:
            WeChatPaySecurityError: 读取或解码失败
        """
        if self._aes_key is not None:
            return self._aes_key
            
        try:
            # 验证文件权限
            self._validate_file_permissions(self.aes_key_path)
            
            # 读取文件内容
            with open(self.aes_key_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                raise WeChatPaySecurityError(f"AES密钥文件为空: {self.aes_key_path}")
            
            # Base64解码
            try:
                aes_key = base64.b64decode(content)
            except Exception as e:
                raise WeChatPaySecurityError(f"AES密钥Base64解码失败: {e}")
            
            # 验证密钥长度（AES-256需要32字节）
            if len(aes_key) != 32:
                raise WeChatPaySecurityError(
                    f"AES密钥长度不正确: 期望32字节，实际{len(aes_key)}字节"
                )
            
            self._aes_key = aes_key
            logger.info("AES密钥读取成功（不记录密钥内容）")
            return aes_key
            
        except WeChatPaySecurityError:
            raise
        except Exception as e:
            raise WeChatPaySecurityError(f"读取AES密钥失败: {e}")
    
    def _read_rsa_private_key(self):
        """
        安全读取RSA私钥文件
        
        Returns:
            cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey: RSA私钥对象
            
        Raises:
            WeChatPaySecurityError: 读取或解析失败
        """
        if self._rsa_private_key is not None:
            return self._rsa_private_key
            
        try:
            # 验证文件权限
            self._validate_file_permissions(self.rsa_key_path)
            
            # 读取文件内容
            with open(self.rsa_key_path, 'r', encoding='utf-8') as f:
                key_content = f.read()
            
            if not key_content:
                raise WeChatPaySecurityError(f"RSA私钥文件为空: {self.rsa_key_path}")
            
            # 解析私钥（支持PKCS1和PKCS8格式）
            try:
                # 尝试PKCS1格式
                private_key = serialization.load_pem_private_key(
                    key_content.encode('utf-8'),
                    password=None,
                    backend=default_backend()
                )
            except Exception:
                try:
                    # 尝试PKCS8格式
                    private_key = serialization.load_pem_private_key(
                        key_content.encode('utf-8'),
                        password=None,
                        backend=default_backend()
                    )
                except Exception as e:
                    raise WeChatPaySecurityError(f"解析RSA私钥失败: {e}")
            
            self._rsa_private_key = private_key
            logger.info("RSA私钥读取成功（不记录密钥内容）")
            return private_key
            
        except WeChatPaySecurityError:
            raise
        except Exception as e:
            raise WeChatPaySecurityError(f"读取RSA私钥失败: {e}")
    
    def generate_v3_signature(
        self,
        method: str,
        url: str,
        timestamp: int,
        nonce: str,
        body: str = ""
    ) -> str:
        """
        生成微信支付V3签名
        
        遵循微信支付V3签名规范：
        签名串格式：HTTP_METHOD\nURL\nTIMESTAMP\nNONCE\nBODY\n
        算法：RSA-SHA256
        
        Args:
            method: HTTP方法，如 'GET', 'POST'
            url: 请求URL（不包含协议和域名）
            timestamp: 时间戳（秒）
            nonce: 随机字符串
            body: 请求体（JSON字符串），GET请求可为空
            
        Returns:
            str: Base64编码的签名
            
        Raises:
            WeChatPaySecurityError: 签名生成失败
        """
        try:
            # 构建签名串
            sign_str = f"{method}\n{url}\n{timestamp}\n{nonce}\n{body}\n"
            
            # 获取RSA私钥
            private_key = self._read_rsa_private_key()
            
            # 使用RSA-SHA256签名
            signature = private_key.sign(
                sign_str.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # Base64编码
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            
            logger.info(f"微信支付V3签名生成成功: method={method}, url={url}, timestamp={timestamp}")
            return signature_b64
            
        except Exception as e:
            logger.error(f"微信支付V3签名生成失败: {e}")
            raise WeChatPaySecurityError(f"签名生成失败: {e}")
    
    def decrypt_v3_data(
        self,
        associated_data: str,
        nonce: str,
        ciphertext: str
    ) -> str:
        """
        解密微信支付V3敏感数据
        
        遵循微信支付V3数据解密规范：
        算法：AES-GCM
        
        Args:
            associated_data: 关联数据
            nonce: 随机串
            ciphertext: Base64编码的密文
            
        Returns:
            str: 解密后的明文（JSON字符串）
            
        Raises:
            WeChatPaySecurityError: 解密失败
        """
        try:
            # 获取AES密钥
            aes_key = self._read_aes_key()
            
            # Base64解码密文
            try:
                ciphertext_bytes = base64.b64decode(ciphertext)
            except Exception as e:
                raise WeChatPaySecurityError(f"密文Base64解码失败: {e}")
            
            # 创建AES-GCM解密器
            aesgcm = AESGCM(aes_key)
            
            # 解密数据
            # 微信支付V3规范：associated_data为空字符串时使用b''
            associated_data_bytes = associated_data.encode('utf-8') if associated_data else b''
            nonce_bytes = nonce.encode('utf-8')
            
            try:
                plaintext_bytes = aesgcm.decrypt(
                    nonce_bytes,
                    ciphertext_bytes,
                    associated_data_bytes
                )
            except Exception as e:
                raise WeChatPaySecurityError(f"AES-GCM解密失败: {e}")
            
            # 解码为字符串
            plaintext = plaintext_bytes.decode('utf-8')
            
            logger.info("微信支付V3数据解密成功（不记录解密内容）")
            return plaintext
            
        except WeChatPaySecurityError:
            raise
        except Exception as e:
            logger.error(f"微信支付V3数据解密失败: {e}")
            raise WeChatPaySecurityError(f"数据解密失败: {e}")
    
    def generate_authorization_header(
        self,
        mch_id: str,
        serial_no: str,
        method: str,
        url: str,
        body: str = ""
    ) -> str:
        """
        生成微信支付V3 Authorization请求头
        
        Args:
            mch_id: 商户号
            serial_no: 商户证书序列号
            method: HTTP方法
            url: 请求URL
            body: 请求体（JSON字符串）
            
        Returns:
            str: Authorization请求头值
        """
        try:
            # 生成时间戳和随机串
            timestamp = int(time.time())
            nonce = hashlib.md5(str(timestamp).encode('utf-8')).hexdigest()
            
            # 生成签名
            signature = self.generate_v3_signature(method, url, timestamp, nonce, body)
            
            # 构建Authorization头
            auth_header = (
                f'WECHATPAY2-SHA256-RSA2048 '
                f'mchid="{mch_id}",'
                f'serial_no="{serial_no}",'
                f'timestamp="{timestamp}",'
                f'nonce_str="{nonce}",'
                f'signature="{signature}"'
            )
            
            logger.info(f"微信支付V3 Authorization头生成成功: mch_id={mch_id}")
            return auth_header
            
        except Exception as e:
            logger.error(f"生成Authorization头失败: {e}")
            raise WeChatPaySecurityError(f"生成Authorization头失败: {e}")
    
    def verify_v3_signature(
        self,
        signature: str,
        timestamp: str,
        nonce: str,
        body: str,
        serial_no: str,
        certificate: bytes
    ) -> bool:
        """
        验证微信支付V3回调签名（简化版，实际需要完整的证书链验证）
        
        Args:
            signature: 微信返回的签名
            timestamp: 时间戳
            nonce: 随机串
            body: 回调请求体
            serial_no: 证书序列号
            certificate: 微信支付平台证书
            
        Returns:
            bool: 签名是否有效
        """
        try:
            # 构建验证串（与生成签名时相同）
            verify_str = f"{timestamp}\n{nonce}\n{body}\n"
            
            # Base64解码签名
            signature_bytes = base64.b64decode(signature)
            
            # 加载微信支付平台证书
            cert = serialization.load_pem_x509_certificate(
                certificate,
                backend=default_backend()
            )
            
            # 获取证书公钥
            public_key = cert.public_key()
            
            # 验证签名
            public_key.verify(
                signature_bytes,
                verify_str.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            logger.info("微信支付V3回调签名验证成功")
            return True
            
        except Exception as e:
            logger.warning(f"微信支付V3回调签名验证失败: {e}")
            return False
    
    def clear_cache(self) -> None:
        """清除缓存的密钥（安全考虑）"""
        self._aes_key = None
        self._rsa_private_key = None
        logger.info("微信支付密钥缓存已清除")


# 全局实例（单例模式，按需使用）
_wechat_pay_security_instance: Optional[WeChatPaySecurity] = None


def get_wechat_pay_security(
    aes_key_path: Optional[str] = None,
    rsa_key_path: Optional[str] = None
) -> WeChatPaySecurity:
    """
    获取微信支付安全工具实例（单例模式）
    
    Args:
        aes_key_path: AES密钥文件路径
        rsa_key_path: RSA私钥文件路径
        
    Returns:
        WeChatPaySecurity: 微信支付安全工具实例
    """
    global _wechat_pay_security_instance
    
    if _wechat_pay_security_instance is None:
        _wechat_pay_security_instance = WeChatPaySecurity(
            aes_key_path=aes_key_path,
            rsa_key_path=rsa_key_path
        )
    
    return _wechat_pay_security_instance


# 使用示例
if __name__ == "__main__":
    # 示例：初始化工具
    security = get_wechat_pay_security()
    
    try:
        # 示例1：生成微信支付V3签名
        signature = security.generate_v3_signature(
            method="POST",
            url="/v3/pay/transactions/jsapi",
            timestamp=int(time.time()),
            nonce="random_nonce_123",
            body=json.dumps({"appid": "wx1234567890", "mchid": "1230000109"})
        )
        print(f"生成的签名: {signature[:50]}...")
        
        # 示例2：解密回调数据
        # 假设收到微信支付回调
        associated_data = "transaction"
        nonce = "4tT2HrLQ1e8P5kY9"
        ciphertext = "Cip...Base64密文..."  # 实际密文
        
        # 解密（示例，需要真实数据）
        # plaintext = security.decrypt_v3_data(associated_data, nonce, ciphertext)
        # print(f"解密结果: {plaintext}")
        
        # 示例3：生成Authorization头
        auth_header = security.generate_authorization_header(
            mch_id="1230000109",
            serial_no="1DCF55C1C33140B4A3C0F8B67B6E5A7C",
            method="POST",
            url="/v3/pay/transactions/jsapi",
            body=json.dumps({"appid": "wx1234567890", "mchid": "1230000109"})
        )
        print(f"Authorization头: {auth_header[:100]}...")
        
    except WeChatPaySecurityError as e:
        print(f"微信支付安全操作失败: {e}")
    except Exception as e:
        print(f"未知错误: {e}")

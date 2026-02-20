"""
微信支付安全工具测试
测试安全的密钥读取、签名生成和数据解密功能
"""
import os
import sys
import tempfile
import base64
from pathlib import Path
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.wechat_pay_security import WeChatPaySecurity, WeChatPaySecurityError


def create_test_key_files():
    """创建测试用的密钥文件"""
    temp_dir = tempfile.mkdtemp()
    
    # 创建AES密钥文件（Base64编码的32字节密钥）
    aes_key = os.urandom(32)
    aes_key_b64 = base64.b64encode(aes_key).decode('utf-8')
    aes_key_path = Path(temp_dir) / "aes_key.txt"
    with open(aes_key_path, 'w') as f:
        f.write(aes_key_b64)
    
    # 创建RSA私钥文件（PKCS1格式）
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS1,
        encryption_algorithm=serialization.NoEncryption()
    )
    rsa_key_path = Path(temp_dir) / "private_key.pem"
    with open(rsa_key_path, 'wb') as f:
        f.write(private_key_pem)
    
    # 设置文件权限（模拟生产环境）
    os.chmod(aes_key_path, 0o600)
    os.chmod(rsa_key_path, 0o600)
    
    return temp_dir, aes_key_path, rsa_key_path, aes_key, private_key


class TestWeChatPaySecurity:
    """微信支付安全工具测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir, self.aes_key_path, self.rsa_key_path, self.aes_key, self.private_key = create_test_key_files()
        self.security = WeChatPaySecurity(
            aes_key_path=str(self.aes_key_path),
            rsa_key_path=str(self.rsa_key_path)
        )
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_with_default_paths(self):
        """测试使用默认路径初始化"""
        security = WeChatPaySecurity()
        assert security.aes_key_path == Path(WeChatPaySecurity.DEFAULT_AES_KEY_PATH)
        assert security.rsa_key_path == Path(WeChatPaySecurity.DEFAULT_RSA_KEY_PATH)
    
    def test_init_with_custom_paths(self):
        """测试使用自定义路径初始化"""
        security = WeChatPaySecurity(
            aes_key_path=str(self.aes_key_path),
            rsa_key_path=str(self.rsa_key_path)
        )
        assert security.aes_key_path == self.aes_key_path
        assert security.rsa_key_path == self.rsa_key_path
    
    def test_validate_file_permissions_success(self):
        """测试文件权限验证成功"""
        # 应该不会抛出异常
        self.security._validate_file_permissions(self.aes_key_path)
        self.security._validate_file_permissions(self.rsa_key_path)
    
    def test_validate_file_permissions_failure(self):
        """测试文件权限验证失败"""
        # 创建权限不安全的文件
        insecure_file = Path(self.temp_dir) / "insecure.txt"
        insecure_file.write_text("test")
        os.chmod(insecure_file, 0o644)  # 组和其他用户可读
        
        with pytest.raises(WeChatPaySecurityError, match="文件权限不安全"):
            self.security._validate_file_permissions(insecure_file)
    
    def test_read_aes_key_success(self):
        """测试读取AES密钥成功"""
        aes_key = self.security._read_aes_key()
        assert len(aes_key) == 32
        assert aes_key == self.aes_key
    
    def test_read_aes_key_invalid_base64(self):
        """测试读取无效Base64编码的AES密钥"""
        invalid_aes_path = Path(self.temp_dir) / "invalid_aes.txt"
        invalid_aes_path.write_text("not-valid-base64!")
        os.chmod(invalid_aes_path, 0o600)
        
        security = WeChatPaySecurity(aes_key_path=str(invalid_aes_path))
        with pytest.raises(WeChatPaySecurityError, match="AES密钥Base64解码失败"):
            security._read_aes_key()
    
    def test_read_aes_key_wrong_length(self):
        """测试读取长度不正确的AES密钥"""
        wrong_key = os.urandom(16)  # 16字节，不是32字节
        wrong_key_b64 = base64.b64encode(wrong_key).decode('utf-8')
        
        wrong_aes_path = Path(self.temp_dir) / "wrong_aes.txt"
        wrong_aes_path.write_text(wrong_key_b64)
        os.chmod(wrong_aes_path, 0o600)
        
        security = WeChatPaySecurity(aes_key_path=str(wrong_aes_path))
        with pytest.raises(WeChatPaySecurityError, match="AES密钥长度不正确"):
            security._read_aes_key()
    
    def test_read_rsa_private_key_success(self):
        """测试读取RSA私钥成功"""
        private_key = self.security._read_rsa_private_key()
        assert private_key is not None
        
        # 验证密钥格式
        key_numbers = private_key.private_numbers()
        assert key_numbers.p is not None
        assert key_numbers.q is not None
    
    def test_generate_v3_signature_success(self):
        """测试生成V3签名成功"""
        method = "POST"
        url = "/v3/pay/transactions/jsapi"
        timestamp = 1646386800
        nonce = "random_nonce_123"
        body = '{"appid":"wx1234567890","mchid":"1230000109"}'
        
        signature = self.security.generate_v3_signature(
            method=method,
            url=url,
            timestamp=timestamp,
            nonce=nonce,
            body=body
        )
        
        # 验证签名格式（Base64）
        assert isinstance(signature, str)
        assert len(signature) > 0
        
        # 验证是有效的Base64
        try:
            base64.b64decode(signature)
        except Exception:
            pytest.fail("签名不是有效的Base64编码")
    
    def test_generate_v3_signature_empty_body(self):
        """测试生成V3签名（空请求体）"""
        method = "GET"
        url = "/v3/pay/transactions/id/123456"
        timestamp = 1646386800
        nonce = "random_nonce_456"
        
        signature = self.security.generate_v3_signature(
            method=method,
            url=url,
            timestamp=timestamp,
            nonce=nonce,
            body=""
        )
        
        assert isinstance(signature, str)
        assert len(signature) > 0
    
    def test_decrypt_v3_data_success(self):
        """测试解密V3数据成功"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        # 准备测试数据
        associated_data = "transaction"
        nonce = os.urandom(12)  # AES-GCM需要12字节的nonce
        plaintext = '{"out_trade_no":"DECO20260220123000123","transaction_id":"420000001202602201234567890"}'
        
        # 使用AES-GCM加密
        aesgcm = AESGCM(self.aes_key)
        ciphertext = aesgcm.encrypt(
            nonce,
            plaintext.encode('utf-8'),
            associated_data.encode('utf-8') if associated_data else b''
        )
        
        # Base64编码密文
        ciphertext_b64 = base64.b64encode(ciphertext).decode('utf-8')
        nonce_str = base64.b64encode(nonce).decode('utf-8')
        
        # 解密
        decrypted = self.security.decrypt_v3_data(
            associated_data=associated_data,
            nonce=nonce_str,
            ciphertext=ciphertext_b64
        )
        
        assert decrypted == plaintext
    
    def test_decrypt_v3_data_invalid_ciphertext(self):
        """测试解密无效密文"""
        with pytest.raises(WeChatPaySecurityError, match="密文Base64解码失败"):
            self.security.decrypt_v3_data(
                associated_data="transaction",
                nonce="invalid_nonce",
                ciphertext="not-valid-base64!"
            )
    
    def test_generate_authorization_header(self):
        """测试生成Authorization头"""
        mch_id = "1230000109"
        serial_no = "1DCF55C1C33140B4A3C0F8B67B6E5A7C"
        method = "POST"
        url = "/v3/pay/transactions/jsapi"
        body = '{"appid":"wx1234567890","mchid":"1230000109"}'
        
        auth_header = self.security.generate_authorization_header(
            mch_id=mch_id,
            serial_no=serial_no,
            method=method,
            url=url,
            body=body
        )
        
        # 验证Authorization头格式
        assert auth_header.startswith("WECHATPAY2-SHA256-RSA2048 ")
        assert f'mchid="{mch_id}"' in auth_header
        assert f'serial_no="{serial_no}"' in auth_header
        assert "timestamp=" in auth_header
        assert "nonce_str=" in auth_header
        assert "signature=" in auth_header
    
    def test_clear_cache(self):
        """测试清除缓存"""
        # 先读取密钥，填充缓存
        self.security._read_aes_key()
        self.security._read_rsa_private_key()
        
        # 清除缓存
        self.security.clear_cache()
        
        # 验证缓存已清除
        assert self.security._aes_key is None
        assert self.security._rsa_private_key is None
    
    def test_file_not_found_error(self):
        """测试文件不存在错误"""
        non_existent_path = Path(self.temp_dir) / "non_existent.txt"
        
        security = WeChatPaySecurity(aes_key_path=str(non_existent_path))
        with pytest.raises(WeChatPaySecurityError, match="密钥文件不存在"):
            security._read_aes_key()
    
    def test_permission_error(self):
        """测试权限错误"""
        # 创建没有读取权限的文件
        no_permission_file = Path(self.temp_dir) / "no_permission.txt"
        no_permission_file.write_text("test")
        os.chmod(no_permission_file, 0o000)  # 无权限
        
        security = WeChatPaySecurity(aes_key_path=str(no_permission_file))
        with pytest.raises(WeChatPaySecurityError, match="没有权限访问密钥文件"):
            security._read_aes_key()
        
        # 恢复权限以便清理
        os.chmod(no_permission_file, 0o644)


if __name__ == "__main__":
    """运行测试"""
    print("运行微信支付安全工具测试...")
    
    # 创建测试实例
    test = TestWeChatPaySecurity()
    test.setup_method()
    
    try:
        # 运行关键测试
        print("1. 测试初始化...")
        test.test_init_with_custom_paths()
        
        print("2. 测试文件权限验证...")
        test.test_validate_file_permissions_success()
        
        print("3. 测试读取AES密钥...")
        test.test_read_aes_key_success()
        
        print("4. 测试读取RSA私钥...")
        test.test_read_rsa_private_key_success()
        
        print("5. 测试生成V3签名...")
        test.test_generate_v3_signature_success()
        
        print("6. 测试生成Authorization头...")
        test.test_generate_authorization_header()
        
        print("7. 测试清除缓存...")
        test.test_clear_cache()
        
        print("\n✅ 所有测试通过！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        test.teardown_method()

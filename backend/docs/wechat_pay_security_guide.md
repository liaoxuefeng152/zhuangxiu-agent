# 微信支付安全工具使用指南

## 概述

本文档介绍如何安全地使用微信支付V3接口，包括密钥读取、签名生成和数据解密功能。所有功能都通过`WeChatPaySecurity`工具类实现，确保密钥安全和管理规范。

## 核心功能

### 1. 安全的密钥文件读取
- 从安全路径读取AES密钥和RSA私钥
- 文件权限校验（必须为600，仅root可读写）
- 密钥格式验证和长度检查
- 不记录密钥内容到日志

### 2. 微信支付V3签名生成
- 遵循微信支付V3签名规范
- 使用RSA-SHA256算法
- 支持HTTP方法、URL、时间戳、随机串和请求体签名

### 3. 微信支付V3数据解密
- 遵循微信支付V3数据解密规范
- 使用AES-GCM算法
- 支持关联数据、随机串和密文解密

## 快速开始

### 1. 初始化工具

```python
from app.services.wechat_pay_security import get_wechat_pay_security

# 使用默认路径（/etc/wechat_secrets/）
security = get_wechat_pay_security()

# 或指定自定义路径
security = get_wechat_pay_security(
    aes_key_path="/path/to/aes_key.txt",
    rsa_key_path="/path/to/private_key.pem"
)
```

### 2. 生成微信支付V3签名

```python
import time
import json

# 准备签名参数
method = "POST"
url = "/v3/pay/transactions/jsapi"
timestamp = int(time.time())
nonce = "random_nonce_123"
body = json.dumps({
    "appid": "wx1234567890",
    "mchid": "1230000109",
    "description": "测试支付",
    "out_trade_no": "DECO20260220123000123",
    "amount": {"total": 100}
})

# 生成签名
signature = security.generate_v3_signature(
    method=method,
    url=url,
    timestamp=timestamp,
    nonce=nonce,
    body=body
)

print(f"生成的签名: {signature}")
```

### 3. 生成Authorization请求头

```python
# 生成完整的Authorization头
auth_header = security.generate_authorization_header(
    mch_id="1230000109",
    serial_no="1DCF55C1C33140B4A3C0F8B67B6E5A7C",
    method="POST",
    url="/v3/pay/transactions/jsapi",
    body=body
)

print(f"Authorization头: {auth_header}")
```

### 4. 解密微信支付V3回调数据

```python
# 微信支付V3回调数据
associated_data = "transaction"
nonce = "4tT2HrLQ1e8P5kY9"
ciphertext = "Cip...Base64密文..."  # 实际密文

# 解密数据
try:
    decrypted_data = security.decrypt_v3_data(
        associated_data=associated_data,
        nonce=nonce,
        ciphertext=ciphertext
    )
    
    # 解析解密后的JSON
    data = json.loads(decrypted_data)
    print(f"解密后的数据: {data}")
    
except Exception as e:
    print(f"解密失败: {e}")
```

### 5. 在支付回调中使用

```python
from fastapi import Request
from app.services.wechat_pay_security import get_wechat_pay_security
import json

async def wechat_pay_callback(request: Request):
    """微信支付V3回调处理"""
    security = get_wechat_pay_security()
    
    # 获取请求数据
    data = await request.json()
    
    if "resource" in data:
        resource = data["resource"]
        
        # 解密敏感数据
        decrypted = security.decrypt_v3_data(
            associated_data=resource.get("associated_data", ""),
            nonce=resource.get("nonce", ""),
            ciphertext=resource.get("ciphertext", "")
        )
        
        # 处理解密后的订单数据
        order_data = json.loads(decrypted)
        order_no = order_data.get("out_trade_no")
        transaction_id = order_data.get("transaction_id")
        
        # 更新订单状态...
        
    return {"code": "SUCCESS", "message": "OK"}
```

## 密钥文件管理

### 1. 密钥文件位置
- AES密钥：`/etc/wechat_secrets/aes_key.txt`
- RSA私钥：`/etc/wechat_secrets/private_key.pem`

### 2. 文件权限要求
```bash
# 设置正确的文件权限
chmod 600 /etc/wechat_secrets/aes_key.txt
chmod 600 /etc/wechat_secrets/private_key.pem

# 设置正确的文件所有者
chown root:root /etc/wechat_secrets/aes_key.txt
chown root:root /etc/wechat_secrets/private_key.pem
```

### 3. 密钥格式
- **AES密钥**：Base64编码的32字节密钥
- **RSA私钥**：PKCS1或PKCS8格式的PEM文件

## 错误处理

### 常见错误及解决方案

1. **文件权限错误**
   ```
   WeChatPaySecurityError: 文件权限不安全: /etc/wechat_secrets/aes_key.txt
   ```
   **解决方案**：检查文件权限是否为600，所有者是否为root

2. **密钥格式错误**
   ```
   WeChatPaySecurityError: AES密钥Base64解码失败
   ```
   **解决方案**：检查AES密钥是否为有效的Base64编码

3. **密钥长度错误**
   ```
   WeChatPaySecurityError: AES密钥长度不正确: 期望32字节，实际XX字节
   ```
   **解决方案**：确保AES密钥为32字节（Base64解码后）

4. **签名生成失败**
   ```
   WeChatPaySecurityError: 签名生成失败
   ```
   **解决方案**：检查RSA私钥格式是否正确，是否有读取权限

## 安全最佳实践

### 1. 密钥安全
- ✅ 密钥文件存储在安全目录（`/etc/wechat_secrets/`）
- ✅ 文件权限设置为600（仅root可读写）
- ✅ 不在代码中硬编码密钥
- ✅ 不在日志中记录密钥内容
- ✅ 密钥按需读取，不常驻内存

### 2. 代码安全
- ✅ 使用异常处理捕获所有错误
- ✅ 验证输入参数的有效性
- ✅ 遵循最小权限原则
- ✅ 定期清理密钥缓存

### 3. 运维安全
- ✅ 定期轮换密钥
- ✅ 监控密钥文件访问日志
- ✅ 使用文件完整性监控
- ✅ 定期审计密钥使用情况

## 集成到现有支付系统

### 1. 更新支付API
现有的支付API已经集成了新的安全工具：
- `generate_wechat_v3_signature()`：生成V3签名
- `decrypt_wechat_v3_data()`：解密V3数据
- `payment_notify()`：支持V2和V3回调

### 2. 向后兼容
- 保留V2 MD5签名函数（`generate_wechat_pay_sign()`）
- 支付回调同时支持V2 XML和V3 JSON格式
- 逐步迁移到V3接口

## 测试验证

### 1. 单元测试
```python
# 测试密钥读取
def test_key_reading():
    security = get_wechat_pay_security()
    
    # 测试文件权限验证
    with pytest.raises(WeChatPaySecurityError):
        security._validate_file_permissions(Path("/tmp/insecure_file"))
    
    # 测试密钥读取
    aes_key = security._read_aes_key()
    assert len(aes_key) == 32
    
    rsa_key = security._read_rsa_private_key()
    assert rsa_key is not None
```

### 2. 集成测试
```python
# 测试完整支付流程
def test_payment_flow():
    # 生成订单
    order = create_order(...)
    
    # 生成支付参数
    pay_params = pay_order(...)
    
    # 验证签名
    assert validate_signature(pay_params["paySign"])
    
    # 模拟支付回调
    callback_response = payment_notify(...)
    assert callback_response["code"] == "SUCCESS"
```

## 部署检查清单

### 上线前检查
- [ ] 密钥文件已正确放置到`/etc/wechat_secrets/`
- [ ] 文件权限已设置为600
- [ ] 文件所有者已设置为root
- [ ] 密钥格式正确（AES: Base64 32字节，RSA: PEM格式）
- [ ] 依赖包已安装（`cryptography`）
- [ ] 代码已通过测试
- [ ] 日志配置正确（不记录密钥）
- [ ] 监控告警已配置

### 上线后验证
- [ ] 支付创建功能正常
- [ ] 支付签名生成正常
- [ ] 支付回调处理正常
- [ ] 数据解密功能正常
- [ ] 错误处理机制正常
- [ ] 日志记录完整但不包含敏感信息

## 故障排除

### 1. 支付回调失败
**症状**：微信支付回调返回失败
**检查项**：
- 确认密钥文件路径正确
- 确认文件权限为600
- 检查Nginx/Apache配置，确保能正确转发回调
- 查看应用日志，确认解密过程无错误

### 2. 签名验证失败
**症状**：微信支付API返回签名错误
**检查项**：
- 确认时间戳正确（使用服务器时间）
- 确认随机串唯一
- 确认请求体格式正确（JSON字符串）
- 确认URL路径正确（不包含协议和域名）

### 3. 数据解密失败
**症状**：回调数据解密失败
**检查项**：
- 确认AES密钥正确（Base64解码后32字节）
- 确认关联数据（associated_data）正确
- 确认随机串（nonce）正确
- 确认密文（ciphertext）为有效的Base64编码

## 支持与联系

如有问题，请联系：
- 技术负责人：后端开发团队
- 紧急联系人：系统运维团队
- 文档维护：技术文档团队

---

**版本历史**：
- v1.0.0 (2026-02-20): 初始版本，微信支付V3安全工具集成
- v1.1.0 (2026-02-20): 添加完整的使用示例和部署指南

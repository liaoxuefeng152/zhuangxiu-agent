# OCR配置修复指南

## 当前问题

OCR API调用失败，错误信息：
```
InvalidAccessKeyId.NotFound - Specified access key is not found
```

## 修复步骤

### 1. 检查当前配置

当前`.env`文件中的配置示例：
```env
ALIYUN_ACCESS_KEY_ID=你的AccessKey_ID
ALIYUN_ACCESS_KEY_SECRET=你的AccessKey_Secret
ALIYUN_OCR_ENDPOINT=ocr-api.cn-hangzhou.aliyuncs.com
```

### 2. 获取有效的Access Key

1. **登录阿里云控制台**
   - 访问：https://ram.console.aliyun.com/manage/ak
   - 使用您的阿里云账号登录

2. **创建Access Key**
   - 点击"创建AccessKey"
   - 选择"继续使用AccessKey"
   - 记录AccessKey ID和AccessKey Secret（Secret只显示一次）

3. **授权OCR服务权限**
   - 确保该AccessKey有OCR服务的访问权限
   - 如果使用RAM子账号，需要授权`AliyunOCRFullAccess`权限

### 3. 更新.env配置

将新的AccessKey信息更新到`.env`文件：

```env
# =================阿里云配置（必填）================
ALIYUN_ACCESS_KEY_ID=你的新AccessKey_ID
ALIYUN_ACCESS_KEY_SECRET=你的新AccessKey_Secret
ALIYUN_OCR_ENDPOINT=ocr-api.cn-hangzhou.aliyuncs.com
```

### 4. 验证配置

运行验证脚本：
```bash
python verify-ocr-config.py
```

运行OCR测试：
```bash
python test-ocr-direct.py
```

### 5. 重启后端服务

更新配置后，需要重启后端服务使配置生效：
```bash
# 如果使用Docker
docker-compose restart backend

# 如果直接运行
# 停止当前服务，然后重新启动
```

## 测试

配置修复后，运行完整测试：
```bash
python test-e2e-complete.py
```

## 注意事项

1. **AccessKey安全**
   - 不要将AccessKey提交到代码仓库
   - 确保`.env`文件在`.gitignore`中
   - 定期轮换AccessKey

2. **权限要求**
   - AccessKey需要有OCR服务的访问权限
   - 如果使用OSS，还需要OSS的访问权限

3. **费用**
   - OCR服务按调用次数收费
   - 注意控制调用频率，避免产生意外费用

4. **开发环境**
   - 当前代码在开发环境下（DEBUG=True）会使用模拟OCR文本
   - 生产环境必须配置有效的OCR AccessKey

## 当前状态

✅ **功能测试通过**：在开发环境下，使用模拟OCR文本，所有功能正常工作
⚠️ **OCR配置待修复**：需要更新有效的AccessKey才能使用真实OCR识别

# 前端连接问题修复方案

## 问题分析
这是**前端问题**。错误信息显示：
```
uploadFile:fail Error: connect ECONNREFUSED 120.26.201.61:443
```

前端尝试连接到HTTPS端口443，但：
1. 阿里云开发环境后端运行在HTTP端口8001
2. nginx没有运行，也没有监听443端口
3. 前端配置应该是`http://120.26.201.61:8001/api/v1`

## 解决方案

### 1. 检查前端环境配置
用户需要确保使用正确的环境配置文件：

```bash
# 切换到阿里云开发环境配置
cd frontend
cp .env.development.aliyun .env.development
```

### 2. 重新编译前端
```bash
# 重新编译微信小程序
npm run dev:weapp
```

### 3. 验证配置
`.env.development`文件应该包含：
```
TARO_APP_API_BASE_URL=http://120.26.201.61:8001/api/v1
```

### 4. 检查后端服务状态
阿里云开发环境后端已启动：
- 后端服务：`decoration-backend-dev` (端口8001)
- 健康检查：`http://120.26.201.61:8001/health` ✅ 正常

### 5. 测试合同上传接口
```bash
# 测试合同上传接口
curl -X POST http://120.26.201.61:8001/api/v1/contracts/upload \
  -F "file=@test_contract.jpg" \
  -H "Authorization: Bearer <token>"
```

## 注意事项
1. **不要使用HTTPS**：开发环境没有配置SSL证书
2. **使用HTTP端口8001**：后端直接暴露在8001端口
3. **微信开发者工具**：需要配置不校验合法域名（开发环境）
4. **重新编译**：修改环境配置后必须重新编译

## 快速修复命令
```bash
# 1. 切换到正确配置
cd /Users/mac/zhuangxiu-agent/frontend
cp .env.development.aliyun .env.development

# 2. 重新编译
npm run dev:weapp

# 3. 在微信开发者工具中重新导入项目
```

## 验证步骤
1. 检查`.env.development`文件内容
2. 重新编译前端
3. 在微信开发者工具中测试合同上传
4. 查看控制台日志确认API地址

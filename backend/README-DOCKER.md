# 家装AI助手 - Docker 部署指南

## 概述

本项目使用 Docker 和 Docker Compose 进行容器化部署，支持开发和生产环境。

## 安全架构（重要更新）

### 🛡️ 无 AccessKey 安全架构

项目已升级为使用 **ECS 实例 RAM 角色**自动获取临时凭证，无需在代码或环境变量中配置 AccessKey/Secret。

#### 核心优势
- ✅ **更安全**：无需硬编码或存储长期有效的 AccessKey/Secret
- ✅ **自动轮换**：临时凭证自动刷新，无需手动管理
- ✅ **权限最小化**：RAM 角色按需授权，遵循最小权限原则
- ✅ **审计跟踪**：所有操作可追溯到具体的 ECS 实例

#### 部署要求
1. **ECS 实例必须绑定 RAM 角色**：`zhuangxiu-ecs-role`
2. **RAM 角色权限**：
   - OSS Bucket 读写权限（开发环境可读写删，生产环境仅读写）
   - OCR 服务使用权限
3. **无需配置**：`ALIYUN_ACCESS_KEY_ID` 和 `ALIYUN_ACCESS_KEY_SECRET`

## 环境配置

### 环境变量文件

项目支持多个环境，通过不同的 `.env` 文件切换：

1. **开发环境**：`.env.dev`
   ```bash
   cp .env.example .env.dev
   # 编辑 .env.dev 配置开发环境参数
   ```

2. **生产环境**：`.env.prod`
   ```bash
   cp .env.example .env.prod
   # 编辑 .env.prod 配置生产环境参数
   ```

### 关键配置说明

#### 阿里云配置（使用 RAM 角色）
```env
# 开发环境
ALIYUN_OSS_BUCKET=zhuangxiu-images-dev
ALIYUN_OSS_BUCKET1=zhuangxiu-images-dev-photo
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OCR_ENDPOINT=ocr-api.cn-hangzhou.aliyuncs.com

# 生产环境  
ALIYUN_OSS_BUCKET=zhuangxiu-images
ALIYUN_OSS_BUCKET1=zhuangxiu-images-photo
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OCR_ENDPOINT=ocr-api.cn-hangzhou.aliyuncs.com
```

**注意**：不再需要配置 `ALIYUN_ACCESS_KEY_ID` 和 `ALIYUN_ACCESS_KEY_SECRET`。

#### 数据库配置
```env
# 开发环境
DB_HOST=decoration-postgres-dev
DB_NAME=zhuangxiu_dev
DB_USER=decoration_dev

# 生产环境
DB_HOST=postgres-prod
DB_NAME=zhuangxiu_prod
DB_USER=zhuangxiu_user
```

#### 微信小程序配置
```env
# 开发环境（测试 AppID）
WECHAT_APP_ID=wxf1a6494a57c73f11

# 生产环境（正式 AppID）
WECHAT_APP_ID=wx8a976249ea20a859
```

## Docker 部署

### 1. 开发环境部署

```bash
# 使用开发环境配置
export COMPOSE_PROFILES=dev
docker compose -f docker-compose.dev.yml up -d

# 查看日志
docker compose -f docker-compose.dev.yml logs -f backend
```

### 2. 生产环境部署

```bash
# 使用生产环境配置
docker compose -f docker-compose.prod.yml up -d

# 查看日志
docker compose -f docker-compose.prod.yml logs -f backend
```

### 3. 服务器开发环境部署

```bash
# 使用服务器开发环境配置
docker compose -f docker-compose.server-dev.yml up -d
```

## 服务说明

### 后端服务 (backend)
- **端口**：8000（开发）、8001（生产）
- **健康检查**：`http://localhost:8000/health`
- **API 文档**：`http://localhost:8000/docs`

### 数据库服务 (postgres)
- **端口**：5432
- **开发数据库**：`zhuangxiu_dev`
- **生产数据库**：`zhuangxiu_prod`

### Redis 服务
- **端口**：6379
- **开发环境**：DB 1
- **生产环境**：DB 0

## 部署验证

### 1. 配置检查
```bash
# 检查生产环境配置
./scripts/test-prod-deployment.sh

# 验证 RAM 角色配置
./scripts/verify-ram-role.sh
```

### 2. 服务健康检查
```bash
# 检查后端服务
curl -f http://localhost:8000/health

# 检查数据库连接
docker exec -it zhuangxiu-backend-prod python -c "from app.core.database import test_db_connection; test_db_connection()"

# 检查 Redis 连接
docker exec -it zhuangxiu-backend-prod python -c "from app.core.redis_client import test_redis_connection; test_redis_connection()"
```

### 3. OSS 连接测试（验证 RAM 角色）
```bash
# 通过 API 测试 OSS 连接
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/oss/test-connection
```

## 阿里云 ECS 部署（生产环境）

### 1. 准备 ECS 实例
1. 创建 ECS 实例（建议：2核4G以上）
2. 绑定 RAM 角色：`zhuangxiu-ecs-role`
3. 确保安全组开放端口：80、443、8001

### 2. RAM 角色配置
```bash
# 在 ECS 实例上验证 RAM 角色
curl http://100.100.100.200/latest/meta-data/ram/security-credentials/

# 应返回类似：
# zhuangxiu-ecs-role
```

### 3. 部署步骤
```bash
# 1. 克隆代码
git clone <repository-url>
cd zhuangxiu-agent

# 2. 配置生产环境变量
cp .env.example .env.prod
vim .env.prod  # 编辑生产环境配置

# 3. 启动服务
docker compose -f docker-compose.prod.yml up -d

# 4. 验证部署
curl -f https://lakeli.top/health
```

## 故障排除

### RAM 角色相关问题

#### 问题：OSS/OCR 服务无法连接
**可能原因**：
1. ECS 实例未绑定 RAM 角色
2. RAM 角色权限不足
3. 元数据服务不可用

**解决方案**：
```bash
# 1. 验证 RAM 角色
./scripts/verify-ram-role.sh

# 2. 检查元数据服务
curl -v http://100.100.100.200/latest/meta-data/

# 3. 检查阿里云控制台
# - 确认 ECS 实例已绑定 RAM 角色
# - 确认 RAM 角色有 OSS 和 OCR 权限
```

#### 问题：前端文件上传失败
**可能原因**：前端未适配 RAM 角色上传方式

**解决方案**：
1. 前端使用 PostObject 方式上传
2. 或通过后端代理上传

### 数据库相关问题

#### 问题：数据库连接失败
```bash
# 检查数据库服务状态
docker compose -f docker-compose.prod.yml ps postgres-prod

# 检查数据库日志
docker compose -f docker-compose.prod.yml logs postgres-prod
```

### 微信相关问题

#### 问题：微信登录失败
1. 检查 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET` 是否正确
2. 检查微信公众平台配置
3. 检查网络连通性

## 更新与维护

### 1. 更新代码
```bash
# 拉取最新代码
git pull

# 重启服务
docker compose -f docker-compose.prod.yml restart backend
```

### 2. 查看日志
```bash
# 查看实时日志
docker compose -f docker-compose.prod.yml logs -f backend

# 查看特定时间段的日志
docker compose -f docker-compose.prod.yml logs --since="2024-01-01" backend
```

### 3. 备份与恢复
```bash
# 数据库备份
docker exec -t postgres-prod pg_dump -U zhuangxiu_user zhuangxiu_prod > backup_$(date +%Y%m%d).sql

# 数据库恢复
cat backup.sql | docker exec -i postgres-prod psql -U zhuangxiu_user zhuangxiu_prod
```

## 监控与告警

### 1. 健康监控
- 定期访问 `/health` 端点
- 监控服务日志
- 设置磁盘空间告警

### 2. 性能监控
- 监控 CPU、内存使用率
- 监控数据库连接数
- 监控 API 响应时间

### 3. 安全监控
- 监控异常登录
- 监控文件上传异常
- 定期检查 RAM 角色权限

## 总结

项目已成功升级为无 AccessKey 安全架构，通过 ECS RAM 角色自动管理阿里云服务凭证。这种架构提供了更高的安全性和可维护性，同时简化了部署配置。

**关键要点**：
1. 不再需要配置 `ALIYUN_ACCESS_KEY_ID/SECRET`
2. ECS 实例必须绑定 `zhuangxiu-ecs-role` RAM 角色
3. RAM 角色需要 OSS 和 OCR 权限
4. 应用自动通过元数据服务获取临时凭证

如需帮助，请参考项目中的验证脚本或查看阿里云官方文档。

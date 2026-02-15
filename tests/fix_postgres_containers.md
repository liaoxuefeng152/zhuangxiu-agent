# PostgreSQL容器问题诊断和修复

## 问题描述

服务器上发现有两个PostgreSQL容器：
1. `decoration-postgres-prod` - 可能是旧的生产环境数据库
2. `zhuangxiu-postgres-dev` - 开发环境数据库

但根据`docker-compose.dev.yml`配置，应该只有一个开发环境数据库容器 `decoration-postgres-dev`。

## 诊断步骤

### 1. 检查容器状态

```bash
# SSH登录服务器
ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61

# 查看所有PostgreSQL容器
docker ps -a | grep postgres

# 查看容器详细信息
docker inspect decoration-postgres-prod
docker inspect zhuangxiu-postgres-dev
```

### 2. 检查容器来源

```bash
# 查看哪个docker-compose文件启动了这些容器
cd /root/project/dev/zhuangxiu-agent

# 检查docker-compose.dev.yml
docker compose -f docker-compose.dev.yml ps

# 检查是否有其他docker-compose文件
ls -la docker-compose*.yml

# 查看所有运行中的容器
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
```

### 3. 检查数据卷

```bash
# 查看PostgreSQL相关的数据卷
docker volume ls | grep postgres

# 查看每个容器使用的数据卷
docker inspect decoration-postgres-prod | grep -A 10 Mounts
docker inspect zhuangxiu-postgres-dev | grep -A 10 Mounts
```

## 可能的原因

1. **旧容器未清理**: `decoration-postgres-prod`可能是之前的生产环境数据库，没有停止和删除
2. **多个docker-compose文件**: 可能有多个docker-compose文件同时运行
3. **手动启动的容器**: 可能有人手动启动了另一个PostgreSQL容器

## 修复方案

### 方案1: 清理旧容器（推荐）

如果`decoration-postgres-prod`是旧的生产环境数据库，且不再需要：

```bash
# 1. 停止旧容器
docker stop decoration-postgres-prod

# 2. 删除旧容器（⚠️ 注意：这会删除容器，但不会删除数据卷）
docker rm decoration-postgres-prod

# 3. 如果确定不需要数据，删除数据卷（⚠️ 危险操作，会丢失数据）
docker volume rm <volume_name>
```

### 方案2: 统一使用开发环境数据库

确保只使用一个开发环境数据库：

```bash
# 1. 停止所有PostgreSQL容器
docker stop decoration-postgres-prod zhuangxiu-postgres-dev

# 2. 使用docker-compose启动开发环境
cd /root/project/dev/zhuangxiu-agent
docker compose -f docker-compose.dev.yml up -d postgres

# 3. 验证容器状态
docker compose -f docker-compose.dev.yml ps postgres
```

### 方案3: 检查后端连接配置

确保后端连接到正确的数据库：

```bash
# 查看后端容器的环境变量
docker exec zhuangxiu-backend-dev env | grep DATABASE_URL

# 应该看到类似：
# DATABASE_URL=postgresql+asyncpg://decoration:decoration123@postgres:5432/zhuangxiu_prod
```

## 正确的开发环境配置

根据`docker-compose.dev.yml`，开发环境应该：

1. **只有一个PostgreSQL容器**: `decoration-postgres-dev`
2. **数据库名**: `zhuangxiu_dev` ⚠️（开发环境使用 `zhuangxiu_dev`，不是 `zhuangxiu_prod`）
3. **用户名**: `decoration`
4. **密码**: `decoration123`
5. **端口**: `5432:5432`

## 验证步骤

```bash
# 1. 确认只有一个PostgreSQL容器运行
docker ps | grep postgres

# 应该只看到一个容器：decoration-postgres-dev

# 2. 连接数据库验证（开发环境数据库：zhuangxiu_dev）
docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -d zhuangxiu_dev -c "SELECT version();"

# 3. 检查数据
docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -d zhuangxiu_dev -c "SELECT COUNT(*) FROM constructions;"
```

## 建议

1. **统一命名**: 开发环境统一使用`decoration-postgres-dev`
2. **清理旧容器**: 如果`decoration-postgres-prod`不再需要，应该停止并删除
3. **文档化**: 记录哪个容器是开发环境，哪个是生产环境
4. **环境隔离**: 如果确实需要生产环境数据库，应该使用不同的docker-compose文件（如`docker-compose.prod.yml`）

## 快速修复命令

```bash
# 一键修复：停止旧容器，启动正确的开发环境数据库
cd /root/project/dev/zhuangxiu-agent

# 停止旧容器（如果存在）
docker stop decoration-postgres-prod 2>/dev/null || true

# 启动开发环境数据库
docker compose -f docker-compose.dev.yml up -d postgres

# 验证
docker compose -f docker-compose.dev.yml ps postgres
```

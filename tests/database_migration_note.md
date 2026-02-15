# 数据库名称修复说明

## 问题

开发环境数据库名称配置不一致：
- `.env` 文件中配置为 `zhuangxiu_dev`
- `docker-compose.dev.yml` 中配置为 `zhuangxiu_prod`（错误）

## 修复内容

已将所有开发环境配置统一为 `zhuangxiu_dev`：

1. ✅ `docker-compose.dev.yml` - 已更新
   - `POSTGRES_DB: zhuangxiu_dev`
   - `DATABASE_URL: postgresql+asyncpg://decoration:decoration123@postgres:5432/zhuangxiu_dev`
   - healthcheck 中的数据库名也更新为 `zhuangxiu_dev`

2. ✅ `tests/database_query_guide.md` - 已更新所有查询示例

3. ✅ `backend/README-DOCKER.md` - 已更新文档

## 部署步骤

### 如果数据库已存在（需要迁移数据）

**重要**: 服务器上有两个PostgreSQL容器，需要先确定使用哪个容器。

```bash
# 1. SSH登录服务器
ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61

# 2. 进入项目目录
cd /root/project/dev/zhuangxiu-agent

# 3. 检查哪个容器是开发环境使用的
docker ps | grep postgres
# 如果看到 decoration-postgres-prod 和 zhuangxiu-postgres-dev
# 需要确认后端连接的是哪个

# 4. 检查后端连接配置
docker exec zhuangxiu-backend-dev env | grep DATABASE_URL

# 5. 在正确的容器中创建新数据库（假设是 decoration-postgres-dev）
# 如果旧数据库是 zhuangxiu_prod，先备份
docker exec decoration-postgres-dev pg_dump -U decoration -d zhuangxiu_prod > /tmp/zhuangxiu_prod_backup.sql

# 6. 创建新的开发数据库
docker exec decoration-postgres-dev psql -U decoration -c "CREATE DATABASE zhuangxiu_dev;"

# 7. 导入数据到新数据库
docker exec -i decoration-postgres-dev psql -U decoration -d zhuangxiu_dev < /tmp/zhuangxiu_prod_backup.sql

# 8. 更新docker-compose配置（已更新）
git pull

# 9. 如果使用 docker-compose.dev.yml，重启PostgreSQL容器
docker compose -f docker-compose.dev.yml down postgres
docker compose -f docker-compose.dev.yml up -d postgres

# 10. 验证数据库
docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -d zhuangxiu_dev -c "SELECT COUNT(*) FROM constructions;"
```

**或者使用自动化脚本**:
```bash
# 使用提供的脚本自动创建和迁移
chmod +x tests/create_zhuangxiu_dev_database.sh
./tests/create_zhuangxiu_dev_database.sh
```

### 如果是全新部署

```bash
# 1. 更新代码
git pull

# 2. 停止旧容器
docker compose -f docker-compose.dev.yml down

# 3. 删除旧数据卷（⚠️ 会丢失数据，仅用于全新部署）
docker volume rm zhuangxiu-agent_postgres_data_dev

# 4. 启动新容器（会自动创建 zhuangxiu_dev 数据库）
docker compose -f docker-compose.dev.yml up -d postgres

# 5. 验证
docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -d zhuangxiu_dev -c "\l"
```

## 验证

```bash
# 检查数据库是否存在
docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -c "\l" | grep zhuangxiu

# 应该看到：
# zhuangxiu_dev  | decoration | UTF8     | ...

# 检查后端连接
docker exec zhuangxiu-backend-dev env | grep DATABASE_URL

# 应该看到：
# DATABASE_URL=postgresql+asyncpg://decoration:decoration123@postgres:5432/zhuangxiu_dev
```

## 注意事项

1. **生产环境**: 生产环境应该使用 `zhuangxiu_prod` 数据库名
2. **开发环境**: 开发环境使用 `zhuangxiu_dev` 数据库名
3. **数据迁移**: 如果现有数据在 `zhuangxiu_prod` 中，需要先备份再迁移
4. **环境变量**: `.env` 文件中的 `DATABASE_URL` 已经正确配置为 `zhuangxiu_dev`

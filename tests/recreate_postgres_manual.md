# 方案3: 重新创建PostgreSQL容器 - 手动执行步骤

## ⚠️ 重要警告

**此操作会永久删除所有数据库数据！**

请确保：
1. 不需要保留现有数据
2. 或者已经备份了重要数据

## 执行步骤

### 步骤1: SSH登录服务器

```bash
ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61
cd /root/project/dev/zhuangxiu-agent
```

### 步骤2: 更新代码（确保使用最新配置）

```bash
git pull
```

### 步骤3: 停止并删除PostgreSQL容器

```bash
# 停止容器
docker compose -f docker-compose.dev.yml down postgres

# 或者如果容器名不同，直接停止
docker stop decoration-postgres-dev
docker rm decoration-postgres-dev
```

### 步骤4: 删除数据卷（⚠️ 会丢失所有数据）

```bash
# 查找数据卷
docker volume ls | grep postgres

# 删除数据卷（替换为实际的数据卷名）
docker volume rm zhuangxiu-agent_postgres_data_dev

# 或者删除所有未使用的数据卷（谨慎使用）
# docker volume prune -f
```

### 步骤5: 重新创建容器

```bash
# 使用新配置创建容器（会自动创建 zhuangxiu_dev 数据库）
docker compose -f docker-compose.dev.yml up -d postgres
```

### 步骤6: 验证数据库

```bash
# 等待容器启动（约10秒）
sleep 10

# 检查容器状态
docker compose -f docker-compose.dev.yml ps postgres

# 检查数据库列表
docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -c "\l" | grep zhuangxiu

# 应该看到：zhuangxiu_dev

# 验证数据库可连接
docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -d zhuangxiu_dev -c "SELECT version();"
```

### 步骤7: 重启后端（使用新数据库）

```bash
# 重启后端容器
docker compose -f docker-compose.dev.yml restart backend

# 验证后端连接配置
docker exec zhuangxiu-backend-dev env | grep DATABASE_URL

# 应该看到：DATABASE_URL=postgresql+asyncpg://decoration:decoration123@postgres:5432/zhuangxiu_dev
```

### 步骤8: 初始化数据库表（如果需要）

如果数据库是全新的，需要创建表结构：

```bash
# 方法1: 如果后端有自动迁移功能，重启后端即可

# 方法2: 手动运行迁移脚本（如果有）
# docker compose -f docker-compose.dev.yml exec backend python -m alembic upgrade head

# 方法3: 检查后端日志，看是否有自动创建表的日志
docker logs zhuangxiu-backend-dev --tail 50
```

## 一键执行脚本

如果不想手动执行，可以使用提供的脚本：

```bash
cd /root/project/dev/zhuangxiu-agent
git pull
chmod +x tests/recreate_postgres_container.sh
./tests/recreate_postgres_container.sh
```

脚本会自动执行所有步骤，并在执行前要求确认。

## 验证清单

执行完成后，验证以下内容：

- [ ] PostgreSQL容器运行正常
- [ ] 数据库 `zhuangxiu_dev` 存在
- [ ] 后端容器连接配置正确
- [ ] 后端可以正常启动（检查日志）
- [ ] API可以正常访问（如果后端已启动）

## 常见问题

### Q1: 容器启动失败

```bash
# 查看容器日志
docker logs decoration-postgres-dev

# 检查端口是否被占用
netstat -tuln | grep 5432
```

### Q2: 数据库无法连接

```bash
# 检查容器健康状态
docker ps | grep postgres

# 检查数据库是否已创建
docker exec decoration-postgres-dev psql -U decoration -c "\l"
```

### Q3: 后端连接失败

```bash
# 检查后端环境变量
docker exec zhuangxiu-backend-dev env | grep DATABASE_URL

# 检查后端日志
docker logs zhuangxiu-backend-dev --tail 50 | grep -i database
```

## 回滚方案

如果出现问题，可以：

1. **恢复旧容器**（如果数据卷未删除）:
   ```bash
   docker volume ls  # 查找旧数据卷
   docker run -d --name decoration-postgres-dev \
     -v <old_volume_name>:/var/lib/postgresql/data \
     -e POSTGRES_DB=zhuangxiu_prod \
     -e POSTGRES_USER=decoration \
     -e POSTGRES_PASSWORD=decoration123 \
     -p 5432:5432 \
     postgres:15
   ```

2. **从备份恢复**（如果有备份）:
   ```bash
   docker exec -i decoration-postgres-dev psql -U decoration -d zhuangxiu_dev < /path/to/backup.sql
   ```

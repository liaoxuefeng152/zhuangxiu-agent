#!/bin/bash
# 修复数据库名称：从 zhuangxiu_prod 改为 zhuangxiu_dev

echo "=========================================="
echo "修复开发环境数据库名称"
echo "=========================================="

# 检查哪个容器是开发环境使用的
echo -e "\n1. 检查PostgreSQL容器状态:"
docker ps | grep postgres

echo -e "\n2. 检查当前数据库:"
echo "--- decoration-postgres-prod ---"
docker exec decoration-postgres-prod psql -U decoration -c "\l" | grep zhuangxiu || echo "无法连接或数据库不存在"

echo -e "\n--- zhuangxiu-postgres-dev ---"
docker exec zhuangxiu-postgres-dev psql -U decoration -c "\l" | grep zhuangxiu || echo "无法连接或数据库不存在"

echo -e "\n3. 检查后端连接的是哪个数据库:"
docker exec zhuangxiu-backend-dev env | grep DATABASE_URL || echo "后端容器不存在或未运行"

echo -e "\n=========================================="
echo "修复步骤:"
echo "=========================================="
echo ""
echo "方案1: 在现有容器中创建新数据库（推荐，保留数据）"
echo "  docker exec decoration-postgres-dev psql -U decoration -c \"CREATE DATABASE zhuangxiu_dev;\""
echo "  docker exec decoration-postgres-dev pg_dump -U decoration -d zhuangxiu_prod | docker exec -i decoration-postgres-dev psql -U decoration -d zhuangxiu_dev"
echo ""
echo "方案2: 重新创建容器（会丢失数据，仅用于全新部署）"
echo "  docker compose -f docker-compose.dev.yml down postgres"
echo "  docker volume rm zhuangxiu-agent_postgres_data_dev"
echo "  docker compose -f docker-compose.dev.yml up -d postgres"
echo ""
echo "方案3: 使用docker-compose.dev.yml中的postgres服务（如果容器名是decoration-postgres-dev）"
echo "  docker compose -f docker-compose.dev.yml down postgres"
echo "  docker compose -f docker-compose.dev.yml up -d postgres"
echo "=========================================="

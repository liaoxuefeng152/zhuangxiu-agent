#!/bin/bash
# 检查PostgreSQL容器情况

echo "=========================================="
echo "检查PostgreSQL容器"
echo "=========================================="

echo -e "\n1. 所有PostgreSQL容器:"
docker ps -a | grep postgres

echo -e "\n2. 检查容器详细信息:"
echo "--- decoration-postgres-prod ---"
docker inspect decoration-postgres-prod 2>/dev/null | grep -E "(Image|Status|Created|Mounts|Env)" | head -20

echo -e "\n--- zhuangxiu-postgres-dev ---"
docker inspect zhuangxiu-postgres-dev 2>/dev/null | grep -E "(Image|Status|Created|Mounts|Env)" | head -20

echo -e "\n3. 检查docker-compose文件:"
echo "--- docker-compose.dev.yml中的postgres服务 ---"
grep -A 20 "postgres:" docker-compose.dev.yml 2>/dev/null | head -25

echo -e "\n4. 检查是否有其他docker-compose文件启动了postgres:"
find . -name "docker-compose*.yml" -exec echo "文件: {}" \; -exec grep -l "postgres" {} \;

echo -e "\n5. 检查容器使用的数据卷:"
docker volume ls | grep postgres

echo -e "\n6. 检查哪个容器在使用5432端口:"
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep 5432

echo -e "\n=========================================="
echo "建议:"
echo "1. 如果decoration-postgres-prod是旧的生产环境数据库，可以停止它"
echo "2. 开发环境应该只使用zhuangxiu-postgres-dev或decoration-postgres-dev"
echo "3. 检查是否有多个docker-compose文件同时运行"
echo "=========================================="

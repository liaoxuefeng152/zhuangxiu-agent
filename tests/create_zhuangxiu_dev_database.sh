#!/bin/bash
# 在现有PostgreSQL容器中创建 zhuangxiu_dev 数据库并迁移数据

set -e

CONTAINER_NAME="decoration-postgres-dev"
DB_USER="decoration"
OLD_DB="zhuangxiu_prod"
NEW_DB="zhuangxiu_dev"

echo "=========================================="
echo "创建开发环境数据库: $NEW_DB"
echo "=========================================="

# 检查容器是否存在
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ 错误: 容器 $CONTAINER_NAME 不存在或未运行"
    echo "请先启动容器: docker compose -f docker-compose.dev.yml up -d postgres"
    exit 1
fi

# 检查新数据库是否已存在
if docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$NEW_DB"; then
    echo "⚠️  数据库 $NEW_DB 已存在"
    read -p "是否删除并重新创建? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除现有数据库..."
        docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -c "DROP DATABASE IF EXISTS $NEW_DB;"
    else
        echo "取消操作"
        exit 0
    fi
fi

# 创建新数据库
echo "1. 创建数据库 $NEW_DB..."
docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -c "CREATE DATABASE $NEW_DB;"

# 检查旧数据库是否存在
if docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$OLD_DB"; then
    echo "2. 发现旧数据库 $OLD_DB，开始迁移数据..."
    
    # 备份旧数据库
    echo "   备份旧数据库..."
    docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$OLD_DB" > /tmp/zhuangxiu_prod_backup_$(date +%Y%m%d_%H%M%S).sql
    
    # 导入数据到新数据库
    echo "   导入数据到新数据库..."
    docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$NEW_DB" < /tmp/zhuangxiu_prod_backup_*.sql
    
    echo "✅ 数据迁移完成"
else
    echo "2. 未找到旧数据库 $OLD_DB，跳过数据迁移"
    echo "   新数据库 $NEW_DB 已创建（空数据库）"
fi

# 验证
echo ""
echo "3. 验证数据库:"
docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$NEW_DB" -c "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';"

echo ""
echo "=========================================="
echo "✅ 完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 更新后端环境变量 DATABASE_URL 指向 $NEW_DB"
echo "2. 重启后端容器: docker compose -f docker-compose.dev.yml restart backend"
echo "3. 验证连接: docker exec zhuangxiu-backend-dev env | grep DATABASE_URL"
echo ""

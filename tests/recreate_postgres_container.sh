#!/bin/bash
# 方案3: 重新创建PostgreSQL容器（会丢失数据）

set -e

echo "=========================================="
echo "⚠️  警告：此操作会删除所有数据库数据！"
echo "=========================================="
echo ""
echo "此脚本将："
echo "1. 停止并删除PostgreSQL容器"
echo "2. 删除PostgreSQL数据卷（所有数据将被永久删除）"
echo "3. 重新创建容器，使用新配置创建 zhuangxiu_dev 数据库"
echo ""
read -p "确认继续？(输入 YES 继续): " confirm

if [ "$confirm" != "YES" ]; then
    echo "操作已取消"
    exit 0
fi

echo ""
echo "=========================================="
echo "开始重新创建PostgreSQL容器"
echo "=========================================="

# 1. 停止并删除PostgreSQL容器
echo ""
echo "1. 停止并删除PostgreSQL容器..."
docker compose -f docker-compose.dev.yml down postgres

# 2. 查找并删除数据卷
echo ""
echo "2. 查找PostgreSQL数据卷..."
VOLUME_NAME=$(docker volume ls | grep postgres_data_dev | awk '{print $2}' || echo "")

if [ -n "$VOLUME_NAME" ]; then
    echo "   找到数据卷: $VOLUME_NAME"
    echo "   删除数据卷（会丢失所有数据）..."
    docker volume rm "$VOLUME_NAME" || echo "   数据卷删除失败或不存在"
else
    echo "   未找到 postgres_data_dev 数据卷"
fi

# 3. 重新创建容器
echo ""
echo "3. 重新创建PostgreSQL容器（使用新配置 zhuangxiu_dev）..."
docker compose -f docker-compose.dev.yml up -d postgres

# 4. 等待容器健康检查
echo ""
echo "4. 等待PostgreSQL容器启动..."
sleep 5

# 检查容器状态
if docker ps | grep -q "decoration-postgres-dev"; then
    echo "   ✅ 容器已启动"
else
    echo "   ❌ 容器启动失败"
    exit 1
fi

# 5. 等待数据库就绪
echo ""
echo "5. 等待数据库就绪..."
for i in {1..30}; do
    if docker exec decoration-postgres-dev pg_isready -U decoration -d zhuangxiu_dev > /dev/null 2>&1; then
        echo "   ✅ 数据库已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ⚠️  数据库启动超时，但继续验证..."
    else
        echo "   等待中... ($i/30)"
        sleep 1
    fi
done

# 6. 验证数据库
echo ""
echo "6. 验证数据库..."
echo "   检查数据库列表:"
docker exec decoration-postgres-dev psql -U decoration -c "\l" | grep zhuangxiu || echo "   未找到 zhuangxiu 数据库"

echo ""
echo "   检查 zhuangxiu_dev 数据库:"
if docker exec decoration-postgres-dev psql -U decoration -d zhuangxiu_dev -c "SELECT version();" > /dev/null 2>&1; then
    echo "   ✅ zhuangxiu_dev 数据库存在且可连接"
    echo ""
    echo "   数据库表数量:"
    docker exec decoration-postgres-dev psql -U decoration -d zhuangxiu_dev -c "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';"
else
    echo "   ❌ zhuangxiu_dev 数据库不存在或无法连接"
    echo "   检查容器日志:"
    docker logs decoration-postgres-dev --tail 20
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 重启后端容器以使用新数据库:"
echo "   docker compose -f docker-compose.dev.yml restart backend"
echo ""
echo "2. 验证后端连接:"
echo "   docker exec zhuangxiu-backend-dev env | grep DATABASE_URL"
echo ""
echo "3. 如果需要初始化数据库表，运行迁移脚本或让后端自动创建"
echo ""

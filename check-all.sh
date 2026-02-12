#!/bin/bash
# 开发环境：使用 docker-compose.dev.yml
COMPOSE_FILE="docker-compose.dev.yml"
echo "🔍 完整系统状态检查（开发环境）"
echo "=================="

echo "1. 所有容器状态:"
docker-compose -f "$COMPOSE_FILE" ps

echo -e "\n2. 后端服务日志（最近5条）:"
docker-compose -f "$COMPOSE_FILE" logs backend --tail=5

echo -e "\n3. 数据库连接测试:"
docker-compose -f "$COMPOSE_FILE" exec postgres psql -U decoration -d zhuangxiu_prod -c "SELECT 1;" 2>/dev/null && echo "✅ 数据库连接正常" || echo "❌ 数据库连接失败"

echo -e "\n4. Redis连接测试:"
docker-compose -f "$COMPOSE_FILE" exec redis redis-cli ping 2>/dev/null && echo "✅ Redis连接正常" || echo "❌ Redis连接失败"

echo -e "\n5. 网络连通性:"
docker-compose -f "$COMPOSE_FILE" exec backend curl -s -o /dev/null -w "后端到数据库: %{http_code}\n" postgres:5432 2>/dev/null || echo "网络测试"

echo -e "\n6. 服务端口:"
netstat -tlnp | grep :8000 && echo "✅ 端口8000已监听" || echo "⚠️  端口8000未监听"

echo -e "\n🎯 访问地址:"
echo "后端API:  http://localhost:8000"
echo "API文档:  http://localhost:8000/docs"
echo "健康检查: http://localhost:8000/health"

#!/bin/bash
# 快速重启后端服务脚本
# 使用方法: ./scripts/restart-backend.sh [prod|dev]

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 获取环境参数，默认为 prod
ENV=${1:-prod}

if [ "$ENV" = "prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    PORT=8000
elif [ "$ENV" = "dev" ]; then
    COMPOSE_FILE="docker-compose.server-dev.yml"
    PORT=8001
else
    echo "错误: 无效的环境参数 '$ENV'"
    echo "使用方法: $0 [prod|dev]"
    exit 1
fi

echo -e "${YELLOW}重启后端服务 ($ENV 环境)...${NC}"

# 重启服务
docker-compose -f "$COMPOSE_FILE" restart backend

# 等待服务就绪
sleep 3

# 检查健康状态
if curl -f -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 服务重启成功${NC}"
else
    echo -e "${YELLOW}警告: 健康检查失败，请查看日志${NC}"
    echo "查看日志: docker-compose -f $COMPOSE_FILE logs -f backend"
fi

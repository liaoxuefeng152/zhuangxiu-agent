#!/bin/bash
# 阿里云部署脚本 - 构建并重启后端服务
# 使用方法: ./scripts/deploy-aliyun.sh [prod|dev]

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取环境参数，默认为 prod
ENV=${1:-prod}

if [ "$ENV" = "prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    SERVICE_NAME="backend"
    PORT=8000
elif [ "$ENV" = "dev" ]; then
    COMPOSE_FILE="docker-compose.server-dev.yml"
    SERVICE_NAME="backend"
    PORT=8001
else
    echo -e "${RED}错误: 无效的环境参数 '$ENV'${NC}"
    echo "使用方法: $0 [prod|dev]"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}开始部署到阿里云 ($ENV 环境)${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查必要文件
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}错误: 找不到文件 $COMPOSE_FILE${NC}"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}警告: 找不到 .env 文件，请确保环境变量已配置${NC}"
fi

# 1. 停止现有容器
echo -e "${YELLOW}[1/4] 停止现有容器...${NC}"
docker-compose -f "$COMPOSE_FILE" down || true

# 2. 构建新镜像
echo -e "${YELLOW}[2/4] 构建后端镜像...${NC}"
docker-compose -f "$COMPOSE_FILE" build --no-cache backend

# 3. 启动服务
echo -e "${YELLOW}[3/4] 启动服务...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d

# 4. 等待服务就绪
echo -e "${YELLOW}[4/4] 等待服务就绪...${NC}"
sleep 5

# 检查健康状态
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 服务健康检查通过${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}等待服务启动... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ 服务启动超时，请检查日志${NC}"
    echo "查看日志: docker-compose -f $COMPOSE_FILE logs -f $SERVICE_NAME"
    exit 1
fi

# 显示服务状态
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "服务信息:"
echo "  - 环境: $ENV"
echo "  - 端口: $PORT"
echo "  - 健康检查: http://localhost:$PORT/health"
echo "  - API 文档: http://localhost:$PORT/api/docs"
echo ""
echo "常用命令:"
echo "  - 查看日志: docker-compose -f $COMPOSE_FILE logs -f $SERVICE_NAME"
echo "  - 重启服务: docker-compose -f $COMPOSE_FILE restart $SERVICE_NAME"
echo "  - 停止服务: docker-compose -f $COMPOSE_FILE down"
echo ""

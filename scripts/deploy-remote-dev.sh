#!/bin/bash
# 远程部署脚本 - 通过SSH连接到阿里云服务器并部署开发环境
# 使用方法: ./scripts/deploy-remote-dev.sh [user@hostname]

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 获取SSH连接信息
if [ -z "$1" ]; then
    echo -e "${RED}错误: 请提供SSH连接信息${NC}"
    echo "使用方法: $0 user@hostname"
    echo "示例: $0 root@120.26.201.61"
    exit 1
fi

SSH_HOST=$1
REMOTE_DIR="/root/zhuangxiu-agent"  # 根据实际情况修改

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}开始远程部署到开发环境${NC}"
echo -e "${GREEN}服务器: $SSH_HOST${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. 上传代码（如果需要）
read -p "是否上传最新代码到服务器? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}上传代码...${NC}"
    rsync -avz --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
        ./backend/ $SSH_HOST:$REMOTE_DIR/backend/
    rsync -avz docker-compose.server-dev.yml $SSH_HOST:$REMOTE_DIR/
    rsync -avz scripts/deploy-aliyun.sh $SSH_HOST:$REMOTE_DIR/scripts/
    echo -e "${GREEN}代码上传完成${NC}"
fi

# 2. 在远程服务器执行部署
echo -e "${YELLOW}在远程服务器执行部署...${NC}"
ssh $SSH_HOST "cd $REMOTE_DIR && chmod +x scripts/deploy-aliyun.sh && ./scripts/deploy-aliyun.sh dev"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}远程部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"

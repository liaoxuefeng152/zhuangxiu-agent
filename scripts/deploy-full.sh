#!/bin/bash
# 完整部署流程：提交代码到Git -> 推送到远程 -> 在服务器上拉取 -> 构建 -> 重启
# 使用方法: ./scripts/deploy-full.sh [dev|prod] [server_user@server_ip] [server_path]

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 参数
ENV=${1:-dev}
SSH_HOST=${2:-"root@120.26.201.61"}
SERVER_PATH=${3:-"/root/zhuangxiu-agent"}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}完整部署流程${NC}"
echo -e "${BLUE}环境: $ENV${NC}"
echo -e "${BLUE}服务器: $SSH_HOST${NC}"
echo -e "${BLUE}========================================${NC}"

# 1. 检查Git状态
echo -e "${YELLOW}[1/5] 检查Git状态...${NC}"
cd "$(dirname "$0")/.."
git status --short

# 2. 添加所有更改
echo -e "${YELLOW}[2/5] 添加所有更改到Git...${NC}"
git add -A

# 检查是否有更改需要提交
if git diff --staged --quiet; then
    echo -e "${YELLOW}没有需要提交的更改${NC}"
else
    # 3. 提交更改
    echo -e "${YELLOW}[3/5] 提交更改...${NC}"
    COMMIT_MSG="部署更新: $(date '+%Y-%m-%d %H:%M:%S') - 更新部署配置和脚本"
    git commit -m "$COMMIT_MSG" || {
        echo -e "${RED}提交失败，可能没有更改或需要设置Git用户信息${NC}"
        exit 1
    }
    
    # 4. 推送到远程
    echo -e "${YELLOW}[4/5] 推送到GitHub...${NC}"
    git push origin main || {
        echo -e "${RED}推送失败，请检查网络连接和Git权限${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ 代码已推送到GitHub${NC}"
fi

# 5. 在服务器上拉取并部署
echo -e "${YELLOW}[5/5] 在服务器上拉取代码并部署...${NC}"
ssh $SSH_HOST "cd $SERVER_PATH && \
    echo '拉取最新代码...' && \
    git pull origin main && \
    echo '执行部署脚本...' && \
    chmod +x scripts/deploy-aliyun.sh scripts/restart-backend.sh && \
    ./scripts/deploy-aliyun.sh $ENV"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"

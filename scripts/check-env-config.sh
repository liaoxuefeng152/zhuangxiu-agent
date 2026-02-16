#!/bin/bash
# 检查服务器环境变量配置是否与.env文件一致
# 使用方法: ./scripts/check-env-config.sh [server_user@server_ip] [server_path]

set -e

SSH_HOST=${1:-"root@120.26.201.61"}
SERVER_PATH=${2:-"/root/project/dev/zhuangxiu-agent"}

echo "=========================================="
echo "环境配置检查"
echo "服务器: $SSH_HOST"
echo "=========================================="
echo ""

ssh $SSH_HOST "cd $SERVER_PATH && \
    echo '=== 关键配置对比 ===' && \
    echo '' && \
    echo '1. DATABASE_URL:' && \
    docker exec zhuangxiu-backend-dev env | grep '^DATABASE_URL=' && \
    echo '   .env文件:' && \
    grep '^DATABASE_URL=' .env | head -1 && \
    echo '' && \
    echo '2. REDIS_URL:' && \
    docker exec zhuangxiu-backend-dev env | grep '^REDIS_URL=' && \
    echo '   .env文件:' && \
    grep '^REDIS_URL=' .env | head -1 && \
    echo '' && \
    echo '3. DB_USER:' && \
    docker exec zhuangxiu-backend-dev env | grep '^DB_USER=' && \
    echo '   .env文件:' && \
    grep '^DB_USER=' .env && \
    echo '' && \
    echo '4. REDIS_DB:' && \
    docker exec zhuangxiu-backend-dev env | grep '^REDIS_DB=' && \
    echo '   .env文件:' && \
    grep '^REDIS_DB=' .env && \
    echo '' && \
    echo '5. DEBUG:' && \
    docker exec zhuangxiu-backend-dev env | grep '^DEBUG=' && \
    echo '   .env文件:' && \
    grep '^DEBUG=' .env && \
    echo '' && \
    echo '6. WECHAT_APP_ID:' && \
    docker exec zhuangxiu-backend-dev env | grep '^WECHAT_APP_ID=' && \
    echo '   .env文件:' && \
    grep '^WECHAT_APP_ID=' .env && \
    echo '' && \
    echo '7. COZE_SITE_URL:' && \
    docker exec zhuangxiu-backend-dev env | grep '^COZE_SITE_URL=' && \
    echo '   .env文件:' && \
    grep '^COZE_SITE_URL=' .env && \
    echo '' && \
    echo '=== 服务状态 ===' && \
    curl -s http://localhost:8001/health | python3 -m json.tool 2>/dev/null || echo '健康检查失败'"

echo ""
echo "=========================================="
echo "检查完成"
echo "=========================================="

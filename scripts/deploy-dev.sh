#!/bin/bash
# 开发环境部署脚本
# 使用: ./scripts/deploy-dev.sh

set -e

echo "=========================================="
echo "开发环境部署脚本 v1.0"
echo "=========================================="

# 配置参数
SSH_KEY="~/zhuangxiu-agent1.pem"
SSH_HOST="120.26.201.61"
TARGET_DIR="/root/project/dev/zhuangxiu-agent"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 检查参数
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "用法: $0 [--skip-build]"
    echo "  --skip-build: 跳过Docker构建，只重启服务"
    exit 0
fi

SKIP_BUILD=false
if [ "$1" = "--skip-build" ]; then
    SKIP_BUILD=true
    info "跳过Docker构建模式"
fi

info "SSH主机: $SSH_HOST"
info "目标目录: $TARGET_DIR"

# 1. 检查Git状态
info "检查Git状态..."
if [ -n "$(git status --porcelain)" ]; then
    warn "Git工作区有未提交的更改"
    read -p "是否继续部署？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "部署已取消"
        exit 0
    fi
fi

# 2. 推送到远程dev分支
info "推送到远程dev分支..."
git push origin dev
if [ $? -ne 0 ]; then
    warn "Git推送失败，但继续部署流程..."
fi

# 3. 部署到开发环境
info "部署到开发环境..."
ssh -i "$SSH_KEY" "root@$SSH_HOST" "
    set -e
    echo '切换到开发环境目录...'
    cd \"$TARGET_DIR\"
    
    echo '检查当前分支...'
    CURRENT_BRANCH=\$(git branch --show-current)
    if [ \"\$CURRENT_BRANCH\" != \"dev\" ]; then
        echo '当前不在dev分支，切换到dev分支...'
        git checkout dev
    fi
    
    echo '拉取最新代码...'
    git pull origin dev
    
    echo '检查开发环境配置文件...'
    if [ ! -f \"docker-compose.dev.yml\" ]; then
        echo '错误：未找到docker-compose.dev.yml'
        echo '请确保开发环境配置文件存在'
        exit 1
    fi
    
    echo '检查环境变量文件...'
    if [ ! -f \".env.dev\" ] && [ ! -f \"config/dev/.env.dev\" ]; then
        warn '未找到.env.dev文件，请确保环境变量已配置'
    fi
    
    # 构建和启动服务
    if [ \"$SKIP_BUILD\" = \"true\" ]; then
        echo '跳过构建，只重启服务...'
        docker compose -f docker-compose.dev.yml restart backend
    else
        echo '重新构建后端服务...'
        docker compose -f docker-compose.dev.yml build backend --no-cache
        echo '启动服务...'
        docker compose -f docker-compose.dev.yml up -d backend
    fi
    
    echo '等待服务启动...'
    sleep 5
    
    echo '检查服务状态...'
    docker compose -f docker-compose.dev.yml ps
    
    echo '检查后端服务健康状态...'
    if curl -f http://localhost:8001/health >/dev/null 2>&1; then
        echo '✅ 后端服务健康检查通过'
    else
        warn '后端服务健康检查失败，查看日志...'
        docker compose -f docker-compose.dev.yml logs backend --tail=20
    fi
    
    echo '开发环境部署完成！'
    echo '服务地址: http://$SSH_HOST:8001'
"

if [ $? -eq 0 ]; then
    info "开发环境部署成功！"
    info "服务地址: http://$SSH_HOST:8001"
    info "健康检查: http://$SSH_HOST:8001/health"
else
    error "开发环境部署失败"
fi

echo "=========================================="
echo "部署脚本执行完成"
echo "=========================================="

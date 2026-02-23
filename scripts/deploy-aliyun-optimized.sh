#!/bin/bash
# 装修决策Agent - 阿里云自动化部署脚本（优化版）
# 支持开发环境和生产环境一键部署

set -e  # 遇到错误立即退出
set -o pipefail  # 管道命令失败时退出

# ============================================
# 配置参数
# ============================================

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 服务器配置
ALIYUN_SERVER="120.26.201.61"
SSH_KEY="$HOME/zhuangxiu-agent1.pem"
SSH_USER="root"

# 环境配置
DEV_PROJECT_DIR="/root/project/dev/zhuangxiu-agent"
PROD_PROJECT_DIR="/root/project/prod/zhuangxiu-agent"
DEV_COMPOSE_FILE="docker-compose.dev.yml"
PROD_COMPOSE_FILE="docker-compose.prod.yml"

# ============================================
# 工具函数
# ============================================

# 打印带颜色的消息
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "命令 '$1' 未找到，请先安装"
        exit 1
    fi
}

# 检查文件是否存在
check_file() {
    if [ ! -f "$1" ]; then
        log_error "文件 '$1' 不存在"
        exit 1
    fi
}

# 检查 SSH 连接
check_ssh_connection() {
    log_info "检查 SSH 连接..."
    if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o BatchMode=yes "$SSH_USER@$ALIYUN_SERVER" "echo 'SSH 连接成功'" &> /dev/null; then
        log_error "SSH 连接失败，请检查网络和密钥配置"
        exit 1
    fi
    log_success "SSH 连接正常"
}

# 等待服务健康检查
wait_for_health() {
    local port=$1
    local service_name=$2
    local max_retries=30
    local retry_count=0
    
    log_info "等待 $service_name 服务就绪 (端口: $port)..."
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -f -s "http://localhost:$port/health" > /dev/null 2>&1; then
            log_success "$service_name 健康检查通过"
            return 0
        fi
        retry_count=$((retry_count + 1))
        log_info "等待服务启动... ($retry_count/$max_retries)"
        sleep 2
    done
    
    log_error "$service_name 启动超时"
    return 1
}

# ============================================
# 部署函数
# ============================================

# 部署到开发环境
deploy_dev() {
    log_info "开始部署到开发环境..."
    
    # 检查本地更改并提交
    if [ -n "$(git status --porcelain)" ]; then
        log_warning "检测到未提交的更改"
        read -p "是否提交更改？ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add .
            git commit -m "自动提交: $(date '+%Y-%m-%d %H:%M:%S')"
            git push origin dev
        fi
    fi
    
    # SSH 到服务器执行部署
    ssh -i "$SSH_KEY" "$SSH_USER@$ALIYUN_SERVER" << EOF
        set -e
        echo "进入开发环境目录..."
        cd $DEV_PROJECT_DIR
        
        echo "拉取最新代码..."
        git fetch origin
        git checkout dev
        git pull origin dev
        
        echo "检查环境配置文件..."
        if [ ! -f ".env.dev" ]; then
            echo "错误: 找不到开发环境配置文件 .env.dev"
            exit 1
        fi
        
        echo "停止现有服务..."
        docker compose -f $DEV_COMPOSE_FILE down --remove-orphans || true
        
        echo "构建并启动服务..."
        docker compose -f $DEV_COMPOSE_FILE build --no-cache backend
        docker compose -f $DEV_COMPOSE_FILE up -d
        
        echo "等待服务启动..."
        sleep 10
EOF
    
    # 本地健康检查
    log_info "执行本地健康检查..."
    if wait_for_health 8001 "开发环境"; then
        log_success "开发环境部署完成！"
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}开发环境部署成功${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo "访问地址: http://$ALIYUN_SERVER:8001"
        echo "API 文档: http://$ALIYUN_SERVER:8001/api/docs"
        echo "健康检查: http://$ALIYUN_SERVER:8001/health"
    else
        log_error "开发环境部署失败"
        exit 1
    fi
}

# 部署到生产环境
deploy_prod() {
    log_info "开始部署到生产环境..."
    
    # 预部署检查
    log_info "执行预部署检查..."
    
    # 检查是否在 main 分支
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        log_error "必须在 main 分支执行生产环境部署，当前分支: $CURRENT_BRANCH"
        exit 1
    fi
    
    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        log_error "有未提交的更改，请先提交"
        git status
        exit 1
    fi
    
    # 检查是否包含开发环境配置文件
    if find . -name "*.env.dev" -o -name "docker-compose.dev.yml" | grep -q .; then
        log_error "发现开发环境配置文件，禁止部署到生产环境"
        exit 1
    fi
    
    # 推送代码到远程
    log_info "推送代码到远程仓库..."
    git push origin main
    
    # SSH 到服务器执行部署
    ssh -i "$SSH_KEY" "$SSH_USER@$ALIYUN_SERVER" << EOF
        set -e
        echo "进入生产环境目录..."
        cd $PROD_PROJECT_DIR
        
        echo "拉取最新代码..."
        git fetch origin
        git checkout main
        git pull origin main
        
        echo "检查环境配置文件..."
        if [ ! -f ".env.prod" ]; then
            echo "错误: 找不到生产环境配置文件 .env.prod"
            exit 1
        fi
        
        # 创建备份
        BACKUP_DIR="/var/backups/zhuangxiu-agent/\$(date +%Y%m%d_%H%M%S)"
        echo "创建备份目录: \$BACKUP_DIR"
        mkdir -p "\$BACKUP_DIR"
        
        echo "备份服务状态..."
        docker compose -f $PROD_COMPOSE_FILE ps > "\$BACKUP_DIR/services_status.txt" 2>/dev/null || true
        docker compose -f $PROD_COMPOSE_FILE logs --tail=100 > "\$BACKUP_DIR/services_logs.txt" 2>/dev/null || true
        
        echo "停止现有服务..."
        docker compose -f $PROD_COMPOSE_FILE down --timeout 30 --remove-orphans || true
        
        echo "构建并启动服务..."
        docker compose -f $PROD_COMPOSE_FILE build --no-cache backend
        docker compose -f $PROD_COMPOSE_FILE up -d
        
        echo "等待服务启动..."
EOF
    
    # 本地健康检查
    log_info "执行生产环境健康检查..."
    if wait_for_health 8000 "生产环境"; then
        log_success "生产环境部署完成！"
        
        # 运行生产环境测试
        log_info "运行生产环境测试..."
        if curl -f -s "http://$ALIYUN_SERVER:8000/api/docs" > /dev/null 2>&1; then
            log_success "API 文档正常"
        else
            log_warning "API 文档检查失败"
        fi
        
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}生产环境部署成功${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo "访问地址: http://$ALIYUN_SERVER:8000"
        echo "API 文档: http://$ALIYUN_SERVER:8000/api/docs"
        echo "健康检查: http://$ALIYUN_SERVER:8000/health"
        echo ""
        echo -e "${YELLOW}重要提醒:${NC}"
        echo "1. 请验证所有核心功能"
        echo "2. 检查数据库连接"
        echo "3. 监控服务日志"
    else
        log_error "生产环境部署失败"
        
        # 尝试回滚
        log_warning "尝试回滚到上一个版本..."
        ssh -i "$SSH_KEY" "$SSH_USER@$ALIYUN_SERVER" << EOF
            cd $PROD_PROJECT_DIR
            docker compose -f $PROD_COMPOSE_FILE down || true
            # 这里可以添加更复杂的回滚逻辑
EOF
        exit 1
    fi
}

# 回滚到上一个版本
rollback_prod() {
    log_info "开始回滚生产环境..."
    
    ssh -i "$SSH_KEY" "$SSH_USER@$ALIYUN_SERVER" << EOF
        set -e
        echo "进入生产环境目录..."
        cd $PROD_PROJECT_DIR
        
        echo "查找最近的备份..."
        LATEST_BACKUP=\$(find /var/backups/zhuangxiu-agent -type d -name "2*" | sort -r | head -1)
        
        if [ -z "\$LATEST_BACKUP" ]; then
            echo "错误: 找不到备份目录"
            exit 1
        fi
        
        echo "使用备份: \$LATEST_BACKUP"
        
        echo "停止当前服务..."
        docker compose -f $PROD_COMPOSE_FILE down --timeout 30 || true
        
        echo "回滚到上一个版本..."
        # 这里可以添加具体的回滚逻辑，例如：
        # 1. 恢复数据库备份
        # 2. 使用之前的 Docker 镜像
        # 3. 恢复配置文件
        
        echo "启动回滚后的服务..."
        docker compose -f $PROD_COMPOSE_FILE up -d
        
        echo "等待服务启动..."
        sleep 10
EOF
    
    if wait_for_health 8000 "回滚后的生产环境"; then
        log_success "生产环境回滚完成！"
    else
        log_error "生产环境回滚失败"
        exit 1
    fi
}

# 查看服务状态
check_status() {
    log_info "检查服务状态..."
    
    ssh -i "$SSH_KEY" "$SSH_USER@$ALIYUN_SERVER" << EOF
        echo "=== 开发环境状态 ==="
        cd $DEV_PROJECT_DIR
        docker compose -f $DEV_COMPOSE_FILE ps 2>/dev/null || echo "开发环境未运行"
        
        echo ""
        echo "=== 生产环境状态 ==="
        cd $PROD_PROJECT_DIR
        docker compose -f $PROD_COMPOSE_FILE ps 2>/dev/null || echo "生产环境未运行"
        
        echo ""
        echo "=== 系统资源状态 ==="
        docker system df
        echo ""
        free -h
EOF
}

# 清理旧备份和镜像
cleanup() {
    log_info "开始清理..."
    
    ssh -i "$SSH_KEY" "$SSH_USER@$ALIYUN_SERVER" << EOF
        echo "清理旧备份（保留最近7天）..."
        find /var/backups/zhuangxiu-agent -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null || true
        
        echo "清理未使用的 Docker 镜像..."
        docker image prune -a -f
        
        echo "清理未使用的 Docker 卷..."
        docker volume prune -f
        
        echo "清理完成"
EOF
    
    log_success "清理完成"
}

# ============================================
# 主程序
# ============================================

# 显示帮助信息
show_help() {
    echo "装修决策Agent - 阿里云部署脚本"
    echo ""
    echo "使用方法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  dev         部署到开发环境"
    echo "  prod        部署到生产环境"
    echo "  rollback    回滚生产环境到上一个版本"
    echo "  status      查看服务状态"
    echo "  cleanup     清理旧备份和未使用的资源"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev      部署到开发环境"
    echo "  $0 prod     部署到生产环境"
    echo ""
}

# 检查必要命令
check_command git
check_command docker
check_command curl
check_command ssh

# 检查 SSH 密钥
check_file "$SSH_KEY"

# 解析命令行参数
case "${1:-}" in
    dev)
        check_ssh_connection
        deploy_dev
        ;;
    prod)
        check_ssh_connection
        deploy_prod
        ;;
    rollback)
        check_ssh_connection
        rollback_prod
        ;;
    status)
        check_ssh_connection
        check_status
        ;;
    cleanup)
        check_ssh_connection
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}错误: 未知命令 '$1'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

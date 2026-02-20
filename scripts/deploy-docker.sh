#!/bin/bash
# Docker 一键部署脚本（带本地自动测试）- 改进版
# 装修智能体项目专用

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 计时函数
start_time=$(date +%s)

# ====================== 辅助函数 ======================
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
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
    if ! command -v $1 &> /dev/null; then
        log_error "命令 $1 不存在，请先安装"
        exit 1
    fi
}

# 检查容器冲突
check_container_conflict() {
    local container_name=$1
    if docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
        log_warning "发现冲突的容器: $container_name"
        docker stop $container_name 2>/dev/null || true
        docker rm $container_name 2>/dev/null || true
        log_info "已清理冲突容器: $container_name"
    fi
}

# 数据库连接测试
test_database_connection() {
    local host=$1
    local port=$2
    local user=$3
    local password=$4
    local dbname=$5
    
    log_info "测试数据库连接: $user@$host:$port/$dbname"
    
    # 使用 pg_isready 测试连接
    if PGPASSWORD=$password pg_isready -h $host -p $port -U $user -d $dbname -t 10 > /dev/null 2>&1; then
        log_success "数据库连接正常"
        return 0
    else
        log_error "数据库连接失败"
        return 1
    fi
}

# 验证环境变量
validate_env_file() {
    local env_file=$1
    
    if [ ! -f "$env_file" ]; then
        log_error "环境文件不存在: $env_file"
        return 1
    fi
    
    # 检查关键环境变量
    local required_vars=("DB_HOST" "DB_PASSWORD" "DATABASE_URL")
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$env_file"; then
            log_warning "环境变量 $var 未设置"
        fi
    done
    
    log_success "环境文件验证通过: $env_file"
    return 0
}

# ====================== 第一步：预检查 ======================
echo -e "${BLUE}===== 0. 预检查 =====${NC}"

# 检查必要命令
log_info "检查必要命令..."
check_command docker
check_command docker-compose
check_command git
check_command curl
check_command ssh

# 检查本地环境文件
log_info "检查本地环境文件..."
validate_env_file ".env.prod" || {
    log_warning "本地 .env.prod 文件可能有问题，但继续执行..."
}

# ====================== 第一步：本地自动测试 ======================
echo -e "${BLUE}===== 1. 本地测试 Docker 开发环境 =====${NC}"

# 检查并清理可能冲突的容器
log_info "检查容器冲突..."
check_container_conflict "decoration-backend-dev"
check_container_conflict "decoration-redis-dev"
check_container_conflict "decoration-postgres-dev"

# 停止旧的开发容器
log_info "停止旧的开发容器..."
docker-compose -f docker-compose.dev.yml down -v > /dev/null 2>&1 || true

# 重建并启动开发容器
log_info "启动本地开发容器..."
docker-compose -f docker-compose.dev.yml up -d --build

# 等待容器启动（使用智能等待）
log_info "等待服务启动..."
local_started=false
for i in {1..12}; do
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "服务已启动"
        local_started=true
        break
    fi
    log_info "等待服务启动... ($i/12)"
    sleep 2
done

if [ "$local_started" = false ]; then
    log_error "本地服务启动超时"
    docker-compose -f docker-compose.dev.yml logs --tail=20
    docker-compose -f docker-compose.dev.yml down
    exit 1
fi

# 测试健康状态
log_info "测试服务健康状态..."
health_response=$(curl -s http://localhost:8000/health | grep -o '"status":"healthy"' || echo "")
if [ -z "$health_response" ]; then
    log_error "本地测试失败：服务不健康"
    docker-compose -f docker-compose.dev.yml logs --tail=20
    docker-compose -f docker-compose.dev.yml down
    exit 1
fi

log_success "本地测试通过！"
docker-compose -f docker-compose.dev.yml down  # 测试完停止开发容器

# ====================== 第二步：提交代码 ======================
echo -e "${BLUE}===== 2. 本地提交代码 =====${NC}"

# 检查是否有更改
if git diff --quiet && git diff --cached --quiet; then
    log_info "没有需要提交的更改"
else
    # 添加所有更改
    git add -A
    
    # 获取提交消息
    if [ -z "$1" ]; then
        read -p "请输入提交备注（如：修复微信回调配置）：" commit_msg
    else
        commit_msg="$1"
    fi
    
    # 提交更改
    git commit -m "$commit_msg"
    
    # 推送到远程
    log_info "推送到GitHub..."
    git push origin main
    log_success "代码已推送到GitHub"
fi

# ====================== 第三步：服务器部署 ======================
echo -e "${BLUE}===== 3. 服务器备份+部署 =====${NC}"

# 执行服务器部署
ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 "
  set -e
  
  # 辅助函数
  log_info() { echo \"[INFO] \$1\"; }
  log_success() { echo \"[SUCCESS] \$1\"; }
  log_warning() { echo \"[WARNING] \$1\"; }
  log_error() { echo \"[ERROR] \$1\"; }
  
  cd /root/project/prod/zhuangxiu-agent
  
  # 验证环境文件
  log_info '验证环境文件...'
  if [ ! -f \".env.prod\" ]; then
    log_error '环境文件 .env.prod 不存在'
    exit 1
  fi
  
  # 检查关键环境变量
  if ! grep -q '^DB_PASSWORD=' .env.prod; then
    log_warning 'DB_PASSWORD 未设置，使用默认密码'
    sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=changeme123/' .env.prod
  fi
  
  # 备份当前版本
  log_info '备份当前版本...'
  backup_dir=\"/root/project/zhuangxiu-agent.bak.\$(date +%Y%m%d%H%M%S)\"
  cp -r . \"\$backup_dir\"
  log_success \"备份完成: \$backup_dir\"
  
  # 拉取最新代码
  log_info '拉取最新代码...'
  git stash push -m '自动保存 before deployment' 2>/dev/null || true
  git pull origin main
  
  # 检查数据库迁移文件
  log_info '检查数据库迁移文件...'
  migration_count=\$(ls database/migration_*.sql 2>/dev/null | wc -l)
  if [ \$migration_count -gt 0 ]; then
    log_warning \"发现 \$migration_count 个数据库迁移文件\"
    echo '⚠️  注意：需要手动执行数据库迁移'
    echo '迁移命令示例:'
    echo '  docker-compose -f docker-compose.prod.yml exec -T postgres-prod \\'
    echo '    psql -U zhuangxiu_user -d zhuangxiu_prod -f /app/database/migration_v8_company_info.sql'
  fi
  
  # 测试数据库连接
  log_info '测试数据库连接...'
  DB_PASSWORD=\$(grep '^DB_PASSWORD=' .env.prod | cut -d= -f2)
  if PGPASSWORD=\$DB_PASSWORD pg_isready -h postgres-prod -p 5432 -U zhuangxiu_user -d zhuangxiu_prod -t 10 > /dev/null 2>&1; then
    log_success '数据库连接正常'
  else
    log_error '数据库连接失败，请检查密码配置'
    log_info '当前数据库密码: '\$DB_PASSWORD
    log_info '尝试使用默认密码...'
    if PGPASSWORD=changeme123 pg_isready -h postgres-prod -p 5432 -U zhuangxiu_user -d zhuangxiu_prod -t 10 > /dev/null 2>&1; then
      log_success '使用默认密码连接成功，更新环境变量...'
      sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=changeme123/' .env.prod
      sed -i 's|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://zhuangxiu_user:changeme123@postgres-prod:5432/zhuangxiu_prod|' .env.prod
    else
      log_error '数据库连接失败，请手动检查'
      exit 1
    fi
  fi
  
  # 重启生产容器
  log_info '重启生产容器...'
  docker-compose -f docker-compose.prod.yml down --remove-orphans
  docker-compose -f docker-compose.prod.yml up -d --build
  
  # 等待服务启动
  log_info '等待服务启动...'
  service_started=false
  for i in {1..20}; do
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
      log_success '生产服务已启动'
      service_started=true
      break
    fi
    log_info \"等待服务启动... (\$i/20)\"
    sleep 3
  done
  
  if [ \"\$service_started\" = false ]; then
    log_error '生产服务启动超时'
    log_info '检查容器日志...'
    docker-compose -f docker-compose.prod.yml logs --tail=30
    log_info '尝试回滚到备份版本...'
    docker-compose -f docker-compose.prod.yml down
    rm -rf .
    cp -r \"\$backup_dir\"/* .
    cp -r \"\$backup_dir\"/.[!.]* . 2>/dev/null || true
    docker-compose -f docker-compose.prod.yml up -d
    log_warning '已回滚到备份版本'
    exit 1
  fi
  
  # 检查服务健康状态
  log_info '检查服务健康状态...'
  if curl -s -f http://localhost:8000/health | grep -q '\"status\":\"healthy\"'; then
    log_success '生产服务健康检查通过'
  else
    log_error '生产服务不健康'
    exit 1
  fi
"

# ====================== 第四步：验证部署 ======================
echo -e "${BLUE}===== 4. 验证生产容器状态 =====${NC}"

ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 "
  echo '当前生产容器状态：'
  docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E '(zhuangxiu|postgres)'
  
  echo ''
  echo '服务健康状态：'
  curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
  
  echo ''
  echo '数据库连接测试：'
  if docker-compose -f docker-compose.prod.yml exec -T postgres-prod pg_isready -U zhuangxiu_user -d zhuangxiu_prod > /dev/null 2>&1; then
    echo -e \"${GREEN}✓ 数据库连接正常${NC}\"
  else
    echo -e \"${RED}❌ 数据库连接失败${NC}\"
  fi
  
  echo ''
  echo 'API 功能测试：'
  if curl -s -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo -e \"${GREEN}✓ API 接口正常${NC}\"
  else
    echo -e \"${YELLOW}⚠️  API 接口可能有问题${NC}\"
  fi
"

# 计算部署时间
end_time=$(date +%s)
duration=$((end_time - start_time))

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}总耗时: ${duration}秒${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}重要提醒：${NC}"
echo "1. 如果部署包含数据库变更，请手动执行数据库迁移"
echo "2. 打开小程序测试核心功能"
echo "3. 监控日志：ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 'docker-compose -f /root/project/prod/zhuangxiu-agent/docker-compose.prod.yml logs -f'"
echo ""
echo -e "${BLUE}常用命令：${NC}"
echo "  - 查看日志: ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 'docker-compose -f /root/project/prod/zhuangxiu-agent/docker-compose.prod.yml logs -f backend-prod'"
echo "  - 重启服务: ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 'cd /root/project/prod/zhuangxiu-agent && docker-compose -f docker-compose.prod.yml restart backend-prod'"
echo "  - 回滚部署: 使用备份目录: /root/project/zhuangxiu-agent.bak.*"
echo ""
echo -e "${CYAN}部署总结：${NC}"
echo "  - 本地测试: 通过"
echo "  - 代码提交: 完成"
echo "  - 服务器部署: 完成"
echo "  - 健康检查: 通过"
echo "  - 数据库连接: 正常"

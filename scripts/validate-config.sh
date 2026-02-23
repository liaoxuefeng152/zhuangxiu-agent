#!/bin/bash
# 装修决策Agent - 配置验证脚本
# 用于验证环境配置的正确性和安全性

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 工具函数
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

# 检查环境配置文件
check_env_file() {
    local env_file=$1
    local env_name=$2
    
    log_info "检查 $env_name 环境配置文件: $env_file"
    
    if [ ! -f "$env_file" ]; then
        log_error "配置文件不存在: $env_file"
        return 1
    fi
    
    # 检查文件权限
    local file_perms=$(stat -f "%A" "$env_file" 2>/dev/null || stat -c "%a" "$env_file")
    if [ "$file_perms" -gt 600 ]; then
        log_warning "配置文件权限过宽: $file_perms (建议 600)"
    fi
    
    # 检查关键配置项
    local missing_configs=()
    
    # 必须的配置项
    local required_configs=(
        "DATABASE_URL"
        "REDIS_URL"
        "SECRET_KEY"
        "DEBUG"
        "WECHAT_APP_ID"
        "WECHAT_APP_SECRET"
    )
    
    for config in "${required_configs[@]}"; do
        if ! grep -q "^$config=" "$env_file"; then
            missing_configs+=("$config")
        fi
    done
    
    if [ ${#missing_configs[@]} -gt 0 ]; then
        log_warning "缺少以下配置项:"
        for config in "${missing_configs[@]}"; do
            echo "  - $config"
        done
    else
        log_success "关键配置项完整"
    fi
    
    # 检查调试模式
    if grep -q "^DEBUG=True" "$env_file"; then
        if [ "$env_name" = "生产环境" ]; then
            log_error "生产环境不能设置 DEBUG=True"
            return 1
        else
            log_success "开发环境 DEBUG=True 配置正确"
        fi
    elif grep -q "^DEBUG=False" "$env_file"; then
        if [ "$env_name" = "生产环境" ]; then
            log_success "生产环境 DEBUG=False 配置正确"
        else
            log_warning "开发环境建议设置 DEBUG=True"
        fi
    fi
    
    # 检查弱密码
    local weak_passwords=(
        "password"
        "123456"
        "admin"
        "test"
        "decoration123"
        "your-secret-key-change-in-production"
    )
    
    for weak_pwd in "${weak_passwords[@]}"; do
        if grep -q "$weak_pwd" "$env_file"; then
            log_warning "发现弱密码或默认密码: $weak_pwd"
        fi
    done
    
    # 检查数据库连接字符串格式
    if grep -q "^DATABASE_URL=" "$env_file"; then
        local db_url=$(grep "^DATABASE_URL=" "$env_file" | cut -d'=' -f2-)
        if [[ "$db_url" != postgresql+asyncpg://* ]]; then
            log_warning "数据库连接字符串格式可能不正确: $db_url"
        fi
    fi
    
    return 0
}

# 检查 Docker Compose 文件
check_docker_compose() {
    local compose_file=$1
    local env_name=$2
    
    log_info "检查 $env_name Docker Compose 文件: $compose_file"
    
    if [ ! -f "$compose_file" ]; then
        log_error "Docker Compose 文件不存在: $compose_file"
        return 1
    fi
    
    # 检查版本声明
    if grep -q "^version:" "$compose_file"; then
        log_success "包含版本声明"
    else
        log_warning "缺少版本声明"
    fi
    
    # 检查网络配置
    if grep -q "networks:" "$compose_file"; then
        log_success "包含网络配置"
    else
        log_warning "缺少网络配置"
    fi
    
    # 检查健康检查
    if grep -q "healthcheck:" "$compose_file"; then
        log_success "包含健康检查配置"
    else
        log_warning "缺少健康检查配置"
    fi
    
    # 检查端口映射
    if grep -q "ports:" "$compose_file"; then
        log_success "包含端口映射"
    else
        log_warning "缺少端口映射"
    fi
    
    return 0
}

# 检查项目结构
check_project_structure() {
    log_info "检查项目结构..."
    
    local required_dirs=(
        "backend"
        "frontend"
        "scripts"
        "docs"
        "database"
        "nginx"
    )
    
    local missing_dirs=()
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            missing_dirs+=("$dir")
        fi
    done
    
    if [ ${#missing_dirs[@]} -gt 0 ]; then
        log_warning "缺少以下目录:"
        for dir in "${missing_dirs[@]}"; do
            echo "  - $dir"
        done
    else
        log_success "项目结构完整"
    fi
    
    # 检查关键文件
    local required_files=(
        "backend/requirements.txt"
        "backend/Dockerfile"
        "frontend/package.json"
        "README.md"
        ".gitignore"
        ".env.example"
    )
    
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        log_warning "缺少以下文件:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
    else
        log_success "关键文件完整"
    fi
    
    return 0
}

# 检查 Git 配置
check_git_config() {
    log_info "检查 Git 配置..."
    
    # 检查 .gitignore
    if [ -f ".gitignore" ]; then
        # 检查是否忽略了敏感文件
        local ignored_patterns=(
            "*.env"
            "*.env.*"
            "*.pem"
            "*.key"
            "*.secret"
            "node_modules/"
            "__pycache__/"
            ".DS_Store"
        )
        
        local missing_patterns=()
        
        for pattern in "${ignored_patterns[@]}"; do
            if ! grep -q "$pattern" ".gitignore"; then
                missing_patterns+=("$pattern")
            fi
        done
        
        if [ ${#missing_patterns[@]} -gt 0 ]; then
            log_warning ".gitignore 缺少以下模式:"
            for pattern in "${missing_patterns[@]}"; do
                echo "  - $pattern"
            done
        else
            log_success ".gitignore 配置完整"
        fi
    else
        log_error "缺少 .gitignore 文件"
        return 1
    fi
    
    # 检查 .gitattributes
    if [ -f ".gitattributes" ]; then
        log_success "找到 .gitattributes 文件"
    else
        log_warning "缺少 .gitattributes 文件"
    fi
    
    return 0
}

# 检查部署脚本
check_deployment_scripts() {
    log_info "检查部署脚本..."
    
    local deployment_scripts=(
        "scripts/deploy-aliyun-optimized.sh"
        "scripts/pre-merge-check.sh"
        "scripts/deploy-dev.sh"
        "scripts/deploy-prod.sh"
    )
    
    local missing_scripts=()
    local not_executable=()
    
    for script in "${deployment_scripts[@]}"; do
        if [ ! -f "$script" ]; then
            missing_scripts+=("$script")
        elif [ ! -x "$script" ]; then
            not_executable+=("$script")
        fi
    done
    
    if [ ${#missing_scripts[@]} -gt 0 ]; then
        log_warning "缺少以下部署脚本:"
        for script in "${missing_scripts[@]}"; do
            echo "  - $script"
        done
    fi
    
    if [ ${#not_executable[@]} -gt 0 ]; then
        log_warning "以下脚本没有执行权限:"
        for script in "${not_executable[@]}"; do
            echo "  - $script"
            log_info "运行: chmod +x $script"
        done
    fi
    
    if [ ${#missing_scripts[@]} -eq 0 ] && [ ${#not_executable[@]} -eq 0 ]; then
        log_success "部署脚本检查通过"
    fi
    
    return 0
}

# 检查 CI/CD 配置
check_cicd_config() {
    log_info "检查 CI/CD 配置..."
    
    if [ -d ".github/workflows" ]; then
        local workflow_files=$(find .github/workflows -name "*.yml" -o -name "*.yaml")
        
        if [ -n "$workflow_files" ]; then
            log_success "找到 CI/CD 工作流文件"
            echo "$workflow_files" | while read -r file; do
                echo "  - $file"
            done
        else
            log_warning ".github/workflows 目录为空"
        fi
    else
        log_warning "缺少 .github/workflows 目录"
    fi
    
    if [ -f ".github/PULL_REQUEST_TEMPLATE.md" ]; then
        log_success "找到 Pull Request 模板"
    else
        log_warning "缺少 Pull Request 模板"
    fi
    
    return 0
}

# 主验证函数
validate_environment() {
    local env_type=$1
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}装修决策Agent - 配置验证${NC}"
    echo -e "${BLUE}环境类型: $env_type${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    local errors=0
    local warnings=0
    
    # 运行所有检查
    checks=(
        check_project_structure
        check_git_config
        check_deployment_scripts
        check_cicd_config
    )
    
    for check_func in "${checks[@]}"; do
        echo ""
        if $check_func; then
            : # 检查通过
        else
            if [ $? -eq 1 ]; then
                ((errors++))
            else
                ((warnings++))
            fi
        fi
    done
    
    # 检查环境特定配置
    echo ""
    if [ "$env_type" = "development" ]; then
        check_env_file ".env.dev" "开发环境"
        check_docker_compose "docker-compose.dev.yml" "开发环境"
    elif [ "$env_type" = "production" ]; then
        check_env_file ".env.prod" "生产环境"
        check_docker_compose "docker-compose.prod.yml" "生产环境"
    else
        # 检查所有环境
        if [ -f ".env.dev" ]; then
            check_env_file ".env.dev" "开发环境"
        fi
        
        if [ -f ".env.prod" ]; then
            check_env_file ".env.prod" "生产环境"
        fi
        
        if [ -f "docker-compose.dev.yml" ]; then
            check_docker_compose "docker-compose.dev.yml" "开发环境"
        fi
        
        if [ -f "docker-compose.prod.yml" ]; then
            check_docker_compose "docker-compose.prod.yml" "生产环境"
        fi
    fi
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}验证完成${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    if [ $errors -gt 0 ]; then
        echo -e "${RED}发现 $errors 个错误${NC}"
        echo ""
        echo "必须修复的问题:"
        echo "1. 缺少关键配置文件"
        echo "2. 安全配置错误"
        echo "3. 项目结构不完整"
        return 1
    elif [ $warnings -gt 0 ]; then
        echo -e "${YELLOW}发现 $warnings 个警告${NC}"
        echo ""
        echo "建议修复的问题:"
        echo "1. 配置优化建议"
        echo "2. 缺少可选文件"
        echo "3. 权限问题"
        return 0
    else
        echo -e "${GREEN}所有检查通过，配置完整且安全${NC}"
        return 0
    fi
}

# 显示帮助信息
show_help() {
    echo "装修决策Agent - 配置验证脚本"
    echo ""
    echo "使用方法: $0 [环境类型]"
    echo ""
    echo "环境类型:"
    echo "  development   验证开发环境配置"
    echo "  production    验证生产环境配置"
    echo "  all           验证所有环境配置（默认）"
    echo ""
    echo "示例:"
    echo "  $0 development  验证开发环境配置"
    echo "  $0 production   验证生产环境配置"
    echo "  $0             验证所有配置"
    echo ""
    echo "检查项目:"
    echo "  1. 项目结构完整性"
    echo "  2. Git 配置安全性"
    echo "  3. 部署脚本可用性"
    echo "  4. CI/CD 配置完整性"
    echo "  5. 环境配置文件"
    echo "  6. Docker Compose 文件"
    echo ""
}

# 主程序
main() {
    local env_type=${1:-all}
    
    case "$env_type" in
        dev|development)
            validate_environment "development"
            ;;
        prod|production)
            validate_environment "production"
            ;;
        all)
            validate_environment "all"
            ;;
        help|--help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "未知环境类型: $env_type"
            show_help
            exit 1
            ;;
    esac
}

# 添加执行权限并运行
if [ "$0" = "$BASH_SOURCE" ]; then
    # 确保脚本有执行权限
    if [ ! -x "$0" ]; then
        chmod +x "$0"
    fi
    
    main "$@"
fi

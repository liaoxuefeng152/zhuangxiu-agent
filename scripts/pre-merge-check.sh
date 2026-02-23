#!/bin/bash
# 装修决策Agent - 预合并检查脚本
# 用于在合并到 main 分支前检查代码质量和安全性

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

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "命令 '$1' 未找到，请先安装"
        exit 1
    fi
}

# ============================================
# 主检查函数
# ============================================

# 检查开发环境配置文件
check_dev_configs() {
    log_info "检查开发环境配置文件..."
    
    local found_dev_files=()
    
    # 检查 .env.dev 文件
    if find . -name "*.env.dev" -type f | grep -q .; then
        found_dev_files+=("$(find . -name "*.env.dev" -type f)")
    fi
    
    # 检查 docker-compose.dev.yml 文件
    if find . -name "docker-compose.dev.yml" -type f | grep -q .; then
        found_dev_files+=("$(find . -name "docker-compose.dev.yml" -type f)")
    fi
    
    # 检查 config/dev 目录
    if [ -d "config/dev" ]; then
        found_dev_files+=("config/dev/")
    fi
    
    if [ ${#found_dev_files[@]} -gt 0 ]; then
        log_error "发现开发环境配置文件，禁止合并到 main 分支："
        for file in "${found_dev_files[@]}"; do
            echo "  - $file"
        done
        return 1
    else
        log_success "未发现开发环境配置文件"
        return 0
    fi
}

# 检查调试模式配置
check_debug_config() {
    log_info "检查调试模式配置..."
    
    local debug_files=()
    
    # 检查 Python 文件中的 DEBUG=True
    if grep -r "DEBUG\s*=\s*True" . --include="*.py" --include="*.env" --include="*.yml" --include="*.yaml" | grep -v ".git" | grep -v "__pycache__" | grep -q .; then
        debug_files+=("DEBUG=True 配置")
    fi
    
    # 检查环境变量文件中的调试配置
    if find . -name "*.env" -type f -exec grep -l "DEBUG=True" {} \; | grep -q .; then
        debug_files+=("环境变量中的 DEBUG=True")
    fi
    
    if [ ${#debug_files[@]} -gt 0 ]; then
        log_error "发现调试模式配置，禁止合并到 main 分支："
        for config in "${debug_files[@]}"; do
            echo "  - $config"
        done
        return 1
    else
        log_success "未发现调试模式配置"
        return 0
    fi
}

# 检查硬编码的敏感信息
check_hardcoded_secrets() {
    log_info "检查硬编码的敏感信息..."
    
    local secret_patterns=(
        "password\s*=\s*['\"].*['\"]"
        "secret_key\s*=\s*['\"].*['\"]"
        "api_key\s*=\s*['\"].*['\"]"
        "access_key\s*=\s*['\"].*['\"]"
        "token\s*=\s*['\"].*['\"]"
        "decoration123"  # 默认密码
        "your-secret-key-change-in-production"  # 默认密钥
    )
    
    local found_secrets=()
    
    for pattern in "${secret_patterns[@]}"; do
        if grep -r -i "$pattern" . --include="*.py" --include="*.js" --include="*.ts" --include="*.json" --include="*.yml" --include="*.yaml" | grep -v ".git" | grep -v "__pycache__" | grep -v ".env.example" | grep -q .; then
            found_secrets+=("$pattern")
        fi
    done
    
    if [ ${#found_secrets[@]} -gt 0 ]; then
        log_warning "发现可能的硬编码敏感信息："
        for secret in "${found_secrets[@]}"; do
            echo "  - 模式: $secret"
            grep -r -i "$secret" . --include="*.py" --include="*.js" --include="*.ts" --include="*.json" --include="*.yml" --include="*.yaml" | grep -v ".git" | grep -v "__pycache__" | grep -v ".env.example" | head -3 | sed 's/^/    /'
        done
        log_warning "请确认这些不是真实的敏感信息"
        return 0  # 警告但不阻止
    else
        log_success "未发现硬编码的敏感信息"
        return 0
    fi
}

# 检查 CORS 配置
check_cors_config() {
    log_info "检查 CORS 配置..."
    
    # 检查 Python 代码中的 CORS 配置
    if grep -r "allow_origins\s*=\s*\[\s*['\"]\*['\"]" . --include="*.py" | grep -q .; then
        log_error "发现通配符 CORS 配置，生产环境禁止使用："
        grep -r "allow_origins\s*=\s*\[\s*['\"]\*['\"]" . --include="*.py" | sed 's/^/  - /'
        return 1
    fi
    
    # 检查环境变量中的 CORS 配置
    if find . -name "*.env" -type f -exec grep -l "ALLOWED_ORIGINS=.*\*" {} \; | grep -q .; then
        log_error "发现通配符 CORS 配置（环境变量），生产环境禁止使用"
        return 1
    fi
    
    log_success "CORS 配置检查通过"
    return 0
}

# 检查代码质量
check_code_quality() {
    log_info "检查代码质量..."
    
    # 检查 Python 代码格式
    check_command black
    check_command isort
    check_command flake8
    
    log_info "运行 black 检查..."
    if ! black --check backend/ > /dev/null 2>&1; then
        log_error "Python 代码格式不符合 black 规范"
        log_info "运行以下命令修复：black backend/"
        return 1
    fi
    
    log_info "运行 isort 检查..."
    if ! isort --check-only backend/ > /dev/null 2>&1; then
        log_error "Python 导入排序不符合 isort 规范"
        log_info "运行以下命令修复：isort backend/"
        return 1
    fi
    
    log_info "运行 flake8 检查..."
    if ! flake8 backend/ --max-line-length=88 --extend-ignore=E203,W503 > /dev/null 2>&1; then
        log_error "Python 代码质量检查失败"
        return 1
    fi
    
    log_success "代码质量检查通过"
    return 0
}

# 检查测试覆盖率
check_test_coverage() {
    log_info "检查测试覆盖率..."
    
    check_command pytest
    
    if [ -d "backend/tests" ]; then
        log_info "运行单元测试..."
        if ! python -m pytest backend/tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=70 > /dev/null 2>&1; then
            log_error "测试覆盖率低于 70% 或测试失败"
            return 1
        fi
        log_success "测试覆盖率检查通过"
    else
        log_warning "未找到测试目录，跳过测试覆盖率检查"
    fi
    
    return 0
}

# 检查依赖安全
check_dependency_security() {
    log_info "检查依赖安全..."
    
    check_command safety
    
    if [ -f "backend/requirements.txt" ]; then
        log_info "运行 safety 检查..."
        if ! safety check -r backend/requirements.txt --full-report > /dev/null 2>&1; then
            log_warning "发现依赖安全漏洞，请查看详细报告"
            # 警告但不阻止，因为可能是误报或低风险漏洞
        else
            log_success "依赖安全检查通过"
        fi
    fi
    
    return 0
}

# 检查 Git 状态
check_git_status() {
    log_info "检查 Git 状态..."
    
    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        log_error "有未提交的更改，请先提交"
        git status
        return 1
    fi
    
    # 检查当前分支
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" = "main" ]; then
        log_warning "当前在 main 分支，建议在功能分支运行此检查"
    fi
    
    log_success "Git 状态检查通过"
    return 0
}

# 检查分支命名
check_branch_naming() {
    log_info "检查分支命名..."
    
    CURRENT_BRANCH=$(git branch --show-current)
    
    # 允许的分支前缀
    local allowed_prefixes=("feature/" "bugfix/" "hotfix/" "release/" "chore/" "docs/" "test/" "refactor/")
    
    # 如果是 main 或 dev 分支，跳过检查
    if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "dev" ]; then
        log_success "主分支或开发分支，跳过命名检查"
        return 0
    fi
    
    local valid_branch=false
    
    for prefix in "${allowed_prefixes[@]}"; do
        if [[ "$CURRENT_BRANCH" == "$prefix"* ]]; then
            valid_branch=true
            break
        fi
    done
    
    if [ "$valid_branch" = false ]; then
        log_error "分支命名不符合规范：$CURRENT_BRANCH"
        echo "允许的分支前缀："
        for prefix in "${allowed_prefixes[@]}"; do
            echo "  - $prefix"
        done
        return 1
    fi
    
    # 检查分支命名格式
    if [[ "$CURRENT_BRANCH" =~ ^(feature|bugfix|hotfix)/[0-9]+-[a-z-]+$ ]] || \
       [[ "$CURRENT_BRANCH" =~ ^(release)/v[0-9]+\.[0-9]+\.[0-9]+$ ]] || \
       [[ "$CURRENT_BRANCH" =~ ^(chore|docs|test|refactor)/[a-z-]+$ ]]; then
        log_success "分支命名格式正确：$CURRENT_BRANCH"
    else
        log_warning "分支命名格式建议改进：$CURRENT_BRANCH"
        echo "推荐格式："
        echo "  - feature/123-description"
        echo "  - bugfix/456-fix-issue"
        echo "  - hotfix/789-critical-fix"
        echo "  - release/v1.2.3"
        echo "  - chore/update-deps"
        # 警告但不阻止
    fi
    
    return 0
}

# ============================================
# 主程序
# ============================================

main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}装修决策Agent - 预合并检查${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    local errors=0
    local warnings=0
    
    # 运行所有检查
    checks=(
        check_git_status
        check_branch_naming
        check_dev_configs
        check_debug_config
        check_hardcoded_secrets
        check_cors_config
        check_code_quality
        check_test_coverage
        check_dependency_security
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
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}检查完成${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    if [ $errors -gt 0 ]; then
        echo -e "${RED}发现 $errors 个错误，请修复后再合并${NC}"
        echo ""
        echo "需要修复的问题："
        echo "1. 开发环境配置文件必须从 main 分支中移除"
        echo "2. 调试模式配置必须设置为 False"
        echo "3. 代码质量必须符合规范"
        echo "4. 测试覆盖率必须达标"
        exit 1
    elif [ $warnings -gt 0 ]; then
        echo -e "${YELLOW}发现 $warnings 个警告，建议修复${NC}"
        echo ""
        echo "建议修复的问题："
        echo "1. 硬编码的敏感信息应该使用环境变量"
        echo "2. 分支命名应该符合规范"
        echo "3. 依赖安全漏洞应该及时修复"
        exit 0  # 警告不影响合并
    else
        echo -e "${GREEN}所有检查通过，可以安全合并到 main 分支${NC}"
        echo ""
        echo "下一步："
        echo "1. 创建 Pull Request"
        echo "2. 等待 CI/CD 流水线通过"
        echo "3. 进行代码审查"
        echo "4. 合并到 main 分支"
        exit 0
    fi
}

# 显示帮助信息
show_help() {
    echo "装修决策Agent - 预合并检查脚本"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h    显示此帮助信息"
    echo "  --quick, -q   快速检查（跳过测试和代码质量检查）"
    echo ""
    echo "检查项目:"
    echo "  1. Git 状态和分支命名"
    echo "  2. 开发环境配置文件"
    echo "  3. 调试模式配置"
    echo "  4. 硬编码敏感信息"
    echo "  5. CORS 配置"
    echo "  6. 代码质量"
    echo "  7. 测试覆盖率"
    echo "  8. 依赖安全"
    echo ""
}

# 解析命令行参数
QUICK_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --quick|-q)
            QUICK_MODE=true
            shift
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 运行主程序
main

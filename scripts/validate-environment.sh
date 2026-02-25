#!/bin/bash
# 环境验证脚本
# 使用: ./scripts/validate-environment.sh [dev|prod] [目录路径]

set -e

echo "=========================================="
echo "环境验证脚本 v1.0"
echo "=========================================="

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
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <环境> [目录路径]"
    echo "  环境: dev | prod"
    echo "  目录路径: 可选，默认为当前目录"
    echo ""
    echo "示例:"
    echo "  $0 dev                          # 验证当前目录是否为开发环境"
    echo "  $0 prod /path/to/prod           # 验证指定目录是否为生产环境"
    echo "  $0 dev --remote                 # 验证远程开发环境"
    echo "  $0 prod --remote                # 验证远程生产环境"
    exit 1
fi

ENV=$1
TARGET_DIR="."
REMOTE=false

# 解析参数
for arg in "$@"; do
    case $arg in
        --remote)
            REMOTE=true
            ;;
        --dry-run)
            # 忽略dry-run参数，仅用于兼容性
            ;;
        -*)
            # 忽略其他选项
            ;;
        *)
            if [ "$arg" != "$ENV" ]; then
                TARGET_DIR="$arg"
            fi
            ;;
    esac
done

if [ "$REMOTE" = true ]; then
    if [ "$ENV" = "dev" ]; then
        TARGET_DIR="/root/project/dev/zhuangxiu-agent"
    else
        TARGET_DIR="/root/project/prod/zhuangxiu-agent"
    fi
fi

# SSH配置
SSH_KEY="~/zhuangxiu-agent1.pem"
SSH_HOST="120.26.201.61"

info "验证 $ENV 环境..."
if [ "$REMOTE" = true ]; then
    info "远程目录: $TARGET_DIR"
    info "SSH主机: $SSH_HOST"
else
    info "本地目录: $TARGET_DIR"
fi

# 验证函数
validate_environment() {
    local dir=$1
    local env_type=$2
    
    echo ""
    info "开始验证 $env_type 环境..."
    
    # 1. 检查目录是否存在
    if [ ! -d "$dir" ]; then
        error "目录不存在: $dir"
        return 1
    fi
    success "目录存在: $dir"
    
    # 2. 检查环境特定文件
    local passed=true
    
    if [ "$env_type" = "prod" ]; then
        # 生产环境验证
        info "检查生产环境文件..."
        
        # 不应存在的文件
        FORBIDDEN_PATTERNS=("*.dev*" "docker-compose.dev*" "docker-compose.*-test*" "docker-compose.server-dev*")
        for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
            count=$(find "$dir" -name "$pattern" -type f 2>/dev/null | wc -l)
            if [ "$count" -gt 0 ]; then
                error "发现禁止的文件模式: $pattern ($count 个文件)"
                find "$dir" -name "$pattern" -type f 2>/dev/null | head -5
                passed=false
            fi
        done
        
        # 应存在的文件
        REQUIRED_FILES=("docker-compose.yml" "backend/" "config/prod/")
        for file in "${REQUIRED_FILES[@]}"; do
            if [ ! -e "$dir/$file" ]; then
                warn "缺少必要文件: $file"
                passed=false
            else
                success "存在必要文件: $file"
            fi
        done
        
        # 检查docker-compose.yml是否指向生产配置
        if [ -f "$dir/docker-compose.yml" ]; then
            if grep -q "prod" "$dir/docker-compose.yml" || grep -q "production" "$dir/docker-compose.yml"; then
                success "docker-compose.yml 包含生产环境标识"
            else
                warn "docker-compose.yml 可能不是生产环境配置"
            fi
        fi
        
    elif [ "$env_type" = "dev" ]; then
        # 开发环境验证
        info "检查开发环境文件..."
        
        # 应存在的文件
        REQUIRED_FILES=("docker-compose.dev.yml" "backend/" "config/dev/")
        for file in "${REQUIRED_FILES[@]}"; do
            if [ ! -e "$dir/$file" ]; then
                warn "缺少必要文件: $file"
                passed=false
            else
                success "存在必要文件: $file"
            fi
        done
        
        # 检查开发环境配置文件
        if [ -f "$dir/docker-compose.dev.yml" ]; then
            if grep -q "dev" "$dir/docker-compose.dev.yml" || grep -q "development" "$dir/docker-compose.dev.yml"; then
                success "docker-compose.dev.yml 包含开发环境标识"
            fi
        fi
        
        # 允许开发文件存在
        info "开发环境允许开发文件存在"
        
    else
        error "未知环境类型: $env_type"
        return 1
    fi
    
    # 3. 检查服务状态（如果可能）
    if [ -f "$dir/docker-compose.yml" ] || [ -f "$dir/docker-compose.dev.yml" ]; then
        info "检查Docker服务状态..."
        
        COMPOSE_FILE="docker-compose.yml"
        if [ "$env_type" = "dev" ] && [ -f "$dir/docker-compose.dev.yml" ]; then
            COMPOSE_FILE="docker-compose.dev.yml"
        fi
        
        if docker compose -f "$dir/$COMPOSE_FILE" ps >/dev/null 2>&1; then
            success "Docker Compose 配置有效"
            
            # 显示服务状态
            echo ""
            info "当前服务状态:"
            docker compose -f "$dir/$COMPOSE_FILE" ps
        else
            warn "Docker Compose 配置可能有问题"
        fi
    fi
    
    # 4. 总结
    echo ""
    info "验证结果汇总:"
    if [ "$passed" = true ]; then
        success "✅ $env_type 环境验证通过"
        return 0
    else
        error "❌ $env_type 环境验证失败，发现问题"
        return 1
    fi
}

# 执行验证
if [ "$REMOTE" = true ]; then
    # 远程验证
    info "执行远程验证..."
    ssh -i "$SSH_KEY" "root@$SSH_HOST" "
        cd /tmp
        cat > /tmp/validate_remote.sh << 'EOF'
#!/bin/bash
set -e
dir=\"$TARGET_DIR\"
env_type=\"$ENV\"
$(declare -f validate_environment)
$(declare -f info warn error success)
validate_environment \"\$dir\" \"\$env_type\"
EOF
        chmod +x /tmp/validate_remote.sh
        /tmp/validate_remote.sh
    "
    EXIT_CODE=$?
else
    # 本地验证
    validate_environment "$TARGET_DIR" "$ENV"
    EXIT_CODE=$?
fi

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    success "环境验证完成 - 通过"
else
    error "环境验证完成 - 失败"
fi
echo "=========================================="

exit $EXIT_CODE

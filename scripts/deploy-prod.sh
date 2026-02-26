#!/bin/bash
# 生产环境部署脚本 - 只复制必要文件，避免开发文件泄露到生产环境
# 使用: ./scripts/deploy-prod.sh

set -e

echo "=========================================="
echo "生产环境部署脚本 v1.0"
echo "=========================================="

# 配置参数
SOURCE_DIR="/Users/mac/zhuangxiu-agent"
TARGET_DIR="/root/project/prod/zhuangxiu-agent"
SSH_KEY="~/zhuangxiu-agent1.pem"
SSH_HOST="120.26.201.61"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
    echo "用法: $0 [--dry-run]"
    echo "  --dry-run: 只显示将要执行的操作，不实际执行"
    exit 0
fi

DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    info "干运行模式：只显示将要执行的操作"
fi

# 验证源目录
if [ ! -d "$SOURCE_DIR" ]; then
    error "源目录不存在: $SOURCE_DIR"
fi

info "源目录: $SOURCE_DIR"
info "目标目录: $TARGET_DIR"
info "SSH主机: $SSH_HOST"

# 1. 检查Git状态
info "检查Git状态..."
cd "$SOURCE_DIR"
if [ -n "$(git status --porcelain)" ]; then
    warn "Git工作区有未提交的更改，建议先提交更改"
    read -p "是否继续部署？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "部署已取消"
        exit 0
    fi
fi

# 2. 创建临时目录
TEMP_DIR="/tmp/zhuangxiu-agent-prod-$(date +%Y%m%d-%H%M%S)"
info "创建临时目录: $TEMP_DIR"

if [ "$DRY_RUN" = false ]; then
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
else
    info "[干运行] 创建临时目录: $TEMP_DIR"
fi

# 3. 复制核心代码（排除开发文件）
info "复制核心代码到临时目录..."

copy_file() {
    local src="$1"
    local dest="$2"
    if [ "$DRY_RUN" = false ]; then
        cp -r "$src" "$dest"
    else
        info "[干运行] 复制: $src -> $dest"
    fi
}

# 创建目录结构
if [ "$DRY_RUN" = false ]; then
    mkdir -p "$TEMP_DIR/backend"
    mkdir -p "$TEMP_DIR/frontend"
    mkdir -p "$TEMP_DIR/database"
    mkdir -p "$TEMP_DIR/nginx"
    mkdir -p "$TEMP_DIR/scripts"
    mkdir -p "$TEMP_DIR/config/prod"
else
    info "[干运行] 创建目录结构"
fi

# 复制后端代码
copy_file "$SOURCE_DIR/backend/" "$TEMP_DIR/backend/"

# 复制前端代码（排除node_modules）
if [ "$DRY_RUN" = false ]; then
    rsync -av --exclude='node_modules' --exclude='dist' \
        "$SOURCE_DIR/frontend/" "$TEMP_DIR/frontend/"
else
    info "[干运行] 复制前端代码（排除node_modules和dist）"
fi

# 复制数据库文件
copy_file "$SOURCE_DIR/database/" "$TEMP_DIR/database/"

# 复制nginx配置
copy_file "$SOURCE_DIR/nginx/" "$TEMP_DIR/nginx/"

# 复制脚本（排除git-hooks）
if [ "$DRY_RUN" = false ]; then
    cp -r "$SOURCE_DIR/scripts/" "$TEMP_DIR/scripts/"
    rm -rf "$TEMP_DIR/scripts/git-hooks"
else
    info "[干运行] 复制脚本（排除git-hooks）"
fi

# 复制文档
copy_file "$SOURCE_DIR/docs/" "$TEMP_DIR/docs/"

# 复制配置文件
copy_file "$SOURCE_DIR/config/prod/" "$TEMP_DIR/config/prod/"

# 复制根目录文件
ROOT_FILES=("README.md" ".gitignore" ".env.example")
for file in "${ROOT_FILES[@]}"; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        copy_file "$SOURCE_DIR/$file" "$TEMP_DIR/"
    fi
done

# 4. 清理开发文件
info "清理临时目录中的开发文件..."

cleanup_patterns=(
    "*.dev*"
    "docker-compose.dev*"
    "docker-compose.*-test*"
    "docker-compose.server-dev*"
    ".env.dev*"
    "*.backup"
)

for pattern in "${cleanup_patterns[@]}"; do
    if [ "$DRY_RUN" = false ]; then
        find "$TEMP_DIR" -name "$pattern" -type f -delete 2>/dev/null || true
    else
        info "[干运行] 删除匹配 $pattern 的文件"
    fi
done

# 5. 创建生产环境docker-compose.yml
info "创建生产环境docker-compose.yml..."
if [ "$DRY_RUN" = false ]; then
    if [ -f "$TEMP_DIR/config/prod/docker-compose.prod.yml" ]; then
        cp "$TEMP_DIR/config/prod/docker-compose.prod.yml" "$TEMP_DIR/docker-compose.yml"
        info "已创建 docker-compose.yml"
    else
        warn "未找到生产环境docker-compose配置文件"
    fi
else
    info "[干运行] 创建 docker-compose.yml"
fi

# 6. 验证临时目录
info "验证临时目录内容..."
if [ "$DRY_RUN" = false ]; then
    # 检查不应存在的文件
    FORBIDDEN_COUNT=$(find "$TEMP_DIR" \( -name "*.dev*" -o -name "docker-compose.dev*" -o -name "docker-compose.*-test*" \) -type f | wc -l)
    if [ "$FORBIDDEN_COUNT" -gt 0 ]; then
        error "临时目录中包含禁止的文件！请检查清理逻辑"
    fi
    
    # 检查必要的文件
    REQUIRED_FILES=("backend/" "frontend/" "docker-compose.yml" "config/prod/")
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -e "$TEMP_DIR/$file" ]; then
            warn "缺少必要文件: $file"
        fi
    done
else
    info "[干运行] 验证临时目录内容"
fi

# 7. 部署到生产环境
info "部署到生产环境..."
if [ "$DRY_RUN" = false ]; then
    # 创建部署包
    DEPLOY_PACKAGE="/tmp/deploy-prod-$(date +%Y%m%d-%H%M%S).tar.gz"
    tar -czf "$DEPLOY_PACKAGE" -C "$TEMP_DIR" .
    info "创建部署包: $DEPLOY_PACKAGE"
    
    # 传输到服务器
    info "传输到服务器..."
    scp -i "$SSH_KEY" "$DEPLOY_PACKAGE" "root@$SSH_HOST:/tmp/"
    
    # 在服务器上解压并部署
    info "在服务器上部署..."
    ssh -i "$SSH_KEY" "root@$SSH_HOST" "
        set -e
        echo '备份当前生产环境...'
        BACKUP_DIR=\"/root/project/prod/zhuangxiu-agent-backup-\$(date +%Y%m%d-%H%M%S)\"
        if [ -d \"/root/project/prod/zhuangxiu-agent\" ]; then
            cp -r \"/root/project/prod/zhuangxiu-agent\" \"\$BACKUP_DIR\"
            echo '备份完成: '\$BACKUP_DIR
        fi
        
        echo '清理目标目录...'
        rm -rf \"/root/project/prod/zhuangxiu-agent\"
        mkdir -p \"/root/project/prod/zhuangxiu-agent\"
        
        echo '解压部署包...'
        tar -xzf \"/tmp/$(basename $DEPLOY_PACKAGE)\" -C \"/root/project/prod/zhuangxiu-agent\"
        
        echo '设置权限...'
        chmod -R 755 \"/root/project/prod/zhuangxiu-agent/scripts\"
        
        echo '清理临时文件...'
        rm -f \"/tmp/$(basename $DEPLOY_PACKAGE)\"
        
        echo '验证生产环境...'
        FORBIDDEN_COUNT=\$(find \"/root/project/prod/zhuangxiu-agent\" \( -name \"*.dev*\" -o -name \"docker-compose.dev*\" -o -name \"docker-compose.*-test*\" \) -type f | wc -l)
        if [ \"\$FORBIDDEN_COUNT\" -gt 0 ]; then
            echo '错误：生产环境中发现开发文件！'
            exit 1
        fi
        
        echo '生产环境部署完成！'
        echo '目录: /root/project/prod/zhuangxiu-agent'
        echo '下一步：进入目录并启动服务：cd /root/project/prod/zhuangxiu-agent && docker compose up -d'
    "
    
    # 清理本地临时文件
    rm -rf "$TEMP_DIR"
    rm -f "$DEPLOY_PACKAGE"
    
    info "部署完成！"
    info "请登录服务器启动服务："
    info "  ssh -i $SSH_KEY root@$SSH_HOST"
    info "  cd /root/project/prod/zhuangxiu-agent"
    info "  docker compose up -d"
else
    info "[干运行] 部署到生产环境"
    info "[干运行] 创建部署包并传输到服务器"
    info "[干运行] 在服务器上解压并部署"
fi

echo "=========================================="
echo "部署脚本执行完成"
echo "=========================================="

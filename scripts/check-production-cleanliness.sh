#!/bin/bash

# 生产环境清洁度检查脚本
# 用于确保生产环境不包含开发配置文件

set -e

echo "🔍 开始检查生产环境清洁度..."

# 定义不应该出现在生产环境的文件模式
DEV_FILE_PATTERNS=(
    "*.dev*"
    "*dev.yml"
    "*dev.yaml"
    "docker-compose.*dev*"
    ".env.dev*"
    "config/dev/*"
)

# 定义不应该出现在生产环境的特定文件
DEV_FILES=(
    "docker-compose.dev.yml"
    "docker-compose.server-dev.yml"
    "docker-compose.prod-local-test.yml"
    ".env.dev"
    ".env.dev_backup"
    "config/dev/docker-compose.dev.yml"
    "config/dev/.env.dev"
)

ERRORS=0

# 检查特定文件
echo "📋 检查特定开发文件..."
for file in "${DEV_FILES[@]}"; do
    if [ -f "$file" ] || [ -d "$file" ]; then
        echo "❌ 发现开发文件: $file"
        ERRORS=$((ERRORS + 1))
    fi
done

# 检查文件模式
echo "🔎 检查开发文件模式..."
for pattern in "${DEV_FILE_PATTERNS[@]}"; do
    # 排除node_modules目录
    find . -name "$pattern" -type f ! -path "./node_modules/*" ! -path "./frontend/node_modules/*" ! -path "./.git/*" | while read -r file; do
        # 检查是否是前端开发库文件（这些是正常的）
        if [[ "$file" == *"/node_modules/"* ]] || [[ "$file" == *".development.js" ]] || [[ "$file" == *".development.cjs" ]]; then
            continue
        fi
        echo "❌ 发现开发文件模式匹配: $file"
        ERRORS=$((ERRORS + 1))
    done
done

# 检查Git仓库中的开发文件
echo "📦 检查Git仓库中的开发文件..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    for file in "${DEV_FILES[@]}"; do
        if git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
            echo "❌ Git仓库中包含开发文件: $file"
            ERRORS=$((ERRORS + 1))
        fi
    done
fi

# 总结
if [ $ERRORS -eq 0 ]; then
    echo "✅ 生产环境清洁度检查通过！"
    exit 0
else
    echo "⚠️  发现 $ERRORS 个问题需要处理"
    echo ""
    echo "建议操作："
    echo "1. 从生产环境删除这些开发文件"
    echo "2. 从Git仓库中移除这些文件：git rm --cached <文件>"
    echo "3. 确保.gitignore配置正确"
    echo "4. 重新部署生产环境"
    exit 1
fi

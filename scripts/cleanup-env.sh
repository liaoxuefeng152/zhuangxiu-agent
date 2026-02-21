#!/bin/bash

# 环境清理脚本
# 用于清理环境混合问题，确保开发和生产环境隔离
# 使用方法: ./scripts/cleanup-env.sh [dev|prod]

set -e

ENV_TYPE="${1:-all}"

echo "🧹 开始清理环境..."

cleanup_dev() {
    echo "🧹 清理开发环境..."
    
    # 删除开发环境中的生产配置文件
    if [ -f "docker-compose.prod.yml" ]; then
        echo "🗑️  删除开发环境中的 docker-compose.prod.yml"
        rm -f docker-compose.prod.yml
    fi
    
    if [ -f ".env.prod" ]; then
        echo "🗑️  删除开发环境中的 .env.prod"
        rm -f .env.prod
    fi
    
    # 确保只有开发环境配置文件
    echo "📋 确保只有开发环境配置文件..."
    if [ ! -f "docker-compose.dev.yml" ]; then
        echo "⚠️  警告：缺少 docker-compose.dev.yml，请从 config/dev/ 复制"
    fi
    
    if [ ! -f ".env.dev" ]; then
        echo "⚠️  警告：缺少 .env.dev，请从 config/dev/ 复制"
    fi
    
    echo "✅ 开发环境清理完成"
}

cleanup_prod() {
    echo "🧹 清理生产环境..."
    
    # 删除生产环境中的开发配置文件
    if [ -f "docker-compose.dev.yml" ]; then
        echo "🗑️  删除生产环境中的 docker-compose.dev.yml"
        rm -f docker-compose.dev.yml
    fi
    
    if [ -f "docker-compose.server-dev.yml" ]; then
        echo "🗑️  删除生产环境中的 docker-compose.server-dev.yml"
        rm -f docker-compose.server-dev.yml
    fi
    
    if [ -f ".env.dev" ]; then
        echo "🗑️  删除生产环境中的 .env.dev"
        rm -f .env.dev
    fi
    
    # 删除生产环境中的测试目录
    if [ -d "test-results" ]; then
        echo "🗑️  删除生产环境中的 test-results 目录"
        rm -rf test-results
    fi
    
    if [ -d "tests" ]; then
        echo "🗑️  删除生产环境中的 tests 目录"
        rm -rf tests
    fi
    
    # 确保只有生产环境配置文件
    echo "📋 确保只有生产环境配置文件..."
    if [ ! -f "docker-compose.prod.yml" ]; then
        echo "⚠️  警告：缺少 docker-compose.prod.yml，请从 config/prod/ 复制"
    fi
    
    if [ ! -f ".env.prod" ]; then
        echo "⚠️  警告：缺少 .env.prod，请从 config/prod/ 复制"
    fi
    
    echo "✅ 生产环境清理完成"
}

case "$ENV_TYPE" in
    "dev")
        cleanup_dev
        ;;
    "prod")
        cleanup_prod
        ;;
    "all")
        cleanup_dev
        cleanup_prod
        ;;
    *)
        echo "❌ 错误：无效的环境类型 '$ENV_TYPE'"
        echo "使用方法: $0 [dev|prod|all]"
        exit 1
        ;;
esac

echo ""
echo "📋 环境清理总结："
echo "   - 开发环境只包含开发配置文件"
echo "   - 生产环境只包含生产配置文件"
echo "   - 测试文件只存在于开发环境"
echo ""
echo "✅ 环境隔离完成！"

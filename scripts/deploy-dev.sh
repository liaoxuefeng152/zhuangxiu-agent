#!/bin/bash

# 开发环境部署脚本
# 使用方法: ./scripts/deploy-dev.sh

set -e

echo "🚀 开始部署开发环境..."

# 检查当前目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 复制开发环境配置文件
echo "📋 复制开发环境配置文件..."
cp -f config/dev/.env.dev .env.dev
cp -f config/dev/docker-compose.dev.yml docker-compose.dev.yml

# 检查并创建必要的目录
mkdir -p logs
mkdir -p database

# 停止并删除现有容器
echo "🛑 停止现有开发容器..."
docker-compose -f docker-compose.dev.yml down || true

# 构建并启动开发环境
echo "🔨 构建并启动开发环境..."
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    echo "✅ 开发环境部署成功！"
    echo "📊 服务状态："
    docker-compose -f docker-compose.dev.yml ps
    
    echo ""
    echo "🌐 访问地址："
    echo "   - API文档: http://localhost:8001/api/docs"
    echo "   - 健康检查: http://localhost:8001/health"
    echo "   - 数据库: localhost:5432 (zhuangxiu_dev)"
    echo "   - Redis: localhost:6379"
else
    echo "❌ 开发环境部署失败，请检查日志："
    docker-compose -f docker-compose.dev.yml logs
    exit 1
fi

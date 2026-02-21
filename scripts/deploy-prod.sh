#!/bin/bash

# 生产环境部署脚本
# 使用方法: ./scripts/deploy-prod.sh

set -e

echo "🚀 开始部署生产环境..."

# 检查当前目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 复制生产环境配置文件
echo "📋 复制生产环境配置文件..."
cp -f config/prod/.env.prod .env.prod
cp -f config/prod/docker-compose.prod.yml docker-compose.prod.yml

# 检查并创建必要的目录
mkdir -p logs

# 检查生产环境网络是否存在
echo "🔍 检查生产环境网络..."
if ! docker network ls | grep -q "zhuangxiu-agent_zhuangxiu-prod-network"; then
    echo "📡 创建生产环境网络..."
    docker network create zhuangxiu-agent_zhuangxiu-prod-network
else
    echo "✅ 生产环境网络已存在"
fi

# 停止并删除现有生产容器
echo "🛑 停止现有生产容器..."
docker-compose -f docker-compose.prod.yml down || true

# 构建并启动生产环境
echo "🔨 构建并启动生产环境..."
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "🔍 检查服务状态..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "✅ 生产环境部署成功！"
    echo "📊 服务状态："
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    echo "🌐 访问地址："
    echo "   - API文档: http://localhost:8000/api/docs"
    echo "   - 健康检查: http://localhost:8000/health"
    echo ""
    echo "⚠️  注意：生产环境需要独立部署 PostgreSQL 和 Redis"
    echo "   - PostgreSQL: 需要手动部署 postgres-prod 容器"
    echo "   - Redis: 需要手动部署 redis-prod 容器"
    echo "   - 确保网络连接正确"
else
    echo "❌ 生产环境部署失败，请检查日志："
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

#!/bin/bash
# AI设计师聊天机器人功能部署脚本

set -e  # 遇到错误立即退出

echo "🚀 开始部署AI设计师聊天机器人功能"
echo "=========================================="

# 1. 检查当前目录
if [ ! -f "docker-compose.dev.yml" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 2. 提交代码到Git
echo "📦 步骤1: 提交代码到Git"
git add .
git commit -m "修复AI设计师聊天机器人，支持多轮对话" || {
    echo "⚠️ 警告：Git提交失败，可能没有更改或已提交"
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

# 3. 推送到远程仓库
echo "📤 步骤2: 推送到远程仓库"
git push || {
    echo "⚠️ 警告：Git推送失败"
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

# 4. 连接到阿里云服务器
echo "🔗 步骤3: 连接到阿里云服务器 (120.26.201.61)"
echo "正在执行SSH连接..."

# 使用SSH密钥连接到服务器
ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 << 'EOF'
set -e

echo "✅ 已连接到阿里云服务器"
echo "📁 步骤4: 进入项目目录"
cd /root/project/dev/zhuangxiu-agent || {
    echo "❌ 错误：项目目录不存在"
    exit 1
}

echo "🔄 步骤5: 拉取最新代码"
git pull || {
    echo "⚠️ 警告：Git拉取失败，尝试stash后重试"
    git stash
    git pull
}

echo "🐳 步骤6: 重新构建后端容器"
docker compose -f docker-compose.dev.yml build backend --no-cache || {
    echo "❌ 错误：容器构建失败"
    exit 1
}

echo "🚀 步骤7: 重启后端服务"
docker compose -f docker-compose.dev.yml up -d backend || {
    echo "❌ 错误：服务启动失败"
    exit 1
}

echo "✅ 步骤8: 检查服务状态"
docker ps | grep decoration-backend-dev || {
    echo "⚠️ 警告：后端容器可能未运行"
}

echo "📊 步骤9: 查看容器日志（最近10行）"
docker logs --tail 10 decoration-backend-dev

echo "🎉 AI设计师聊天机器人功能部署完成！"
echo "=========================================="
echo "功能说明："
echo "1. ✅ 真正的聊天机器人界面（不再是单次问答）"
echo "2. ✅ 支持多轮对话，维护对话历史"
echo "3. ✅ 支持session管理，每个用户独立对话"
echo "4. ✅ 支持清空对话、快速问题等功能"
echo "5. ✅ 后端API已支持对话历史传递"
echo ""
echo "🔍 问题归属: 这是后台问题"
echo "   已重构后端API支持多轮对话session"
echo "   已优化AI智能体调用支持对话历史"
echo "   已部署到阿里云服务器生效"
echo ""
echo "💡 测试建议："
echo "1. 打开微信小程序"
echo "2. 进入首页，点击悬浮AI设计师头像"
echo "3. 测试多轮对话功能"
echo "4. 测试清空对话、快速问题等功能"
EOF

if [ $? -eq 0 ]; then
    echo "🎉 部署脚本执行成功！"
    echo ""
    echo "📋 部署总结："
    echo "✅ 本地代码已提交并推送"
    echo "✅ 阿里云服务器已更新代码"
    echo "✅ 后端容器已重新构建"
    echo "✅ 后端服务已重启"
    echo ""
    echo "🚀 AI设计师聊天机器人功能已部署完成！"
else
    echo "❌ 部署脚本执行失败，请检查错误信息"
    exit 1
fi

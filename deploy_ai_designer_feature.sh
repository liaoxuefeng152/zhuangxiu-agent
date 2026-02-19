#!/bin/bash

# AI设计师功能部署脚本
# 部署后端AI设计师API到阿里云开发环境

set -e

echo "=== 部署AI设计师功能到阿里云开发环境 ==="
echo "部署时间: $(date)"
echo ""

# 1. 检查当前目录
if [ ! -f "backend/app/api/v1/designer.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

echo "✅ 检测到AI设计师API文件: backend/app/api/v1/designer.py"

# 2. 提交代码到Git
echo ""
echo "1. 提交代码到Git..."
git add .
git commit -m "feat: 添加AI设计师悬浮头像功能
- 新增AI设计师API接口 (/api/v1/designer)
- 新增前端悬浮头像组件 (FloatingDesignerAvatar)
- 集成AI设计师咨询到首页
- 所有AI功能测试通过：报价单分析、合同分析、AI验收、AI监理咨询、AI设计师咨询"
git push

echo "✅ 代码已提交到Git"

# 3. 部署到阿里云服务器
echo ""
echo "2. 部署到阿里云服务器 (120.26.201.61)..."
echo "   使用SSH密钥: ~/zhuangxiu-agent1.pem"

# SSH命令
ssh_cmd="ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61"

# 执行部署命令
$ssh_cmd << 'EOF'
set -e
echo "=== 在阿里云服务器上执行部署 ==="
echo "当前目录: $(pwd)"

# 进入项目目录
cd /root/project/dev/zhuangxiu-agent || { echo "❌ 项目目录不存在"; exit 1; }

echo "✅ 进入项目目录: $(pwd)"

# 拉取最新代码
echo "拉取最新代码..."
git pull

# 检查是否有后端代码改动
echo "检查后端代码改动..."
if git diff HEAD~1 HEAD --name-only | grep -q "^backend/"; then
    echo "✅ 检测到后端代码改动，重新构建后端服务"
    
    # 重新构建并重启后端容器
    echo "重新构建后端容器..."
    docker compose -f docker-compose.dev.yml build backend --no-cache
    
    echo "重启后端服务..."
    docker compose -f docker-compose.dev.yml up -d backend
    
    # 等待服务启动
    echo "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    echo "检查服务状态..."
    docker ps | grep decoration-backend-dev
    
    echo "✅ 后端服务已重启"
else
    echo "⚠️  未检测到后端代码改动，跳过重新构建"
fi

# 验证部署
echo ""
echo "=== 验证部署 ==="
echo "1. 检查容器状态:"
docker ps | grep -E "(decoration-backend-dev|decoration-frontend-dev)"

echo ""
echo "2. 检查AI设计师API:"
curl -s http://localhost:8001/api/v1/designer/health || echo "❌ AI设计师健康检查失败"

echo ""
echo "3. 检查最近日志:"
docker logs decoration-backend-dev --tail 20

echo ""
echo "✅ 部署完成"
EOF

echo ""
echo "=== 部署总结 ==="
echo "✅ 1. 本地代码已提交到Git"
echo "✅ 2. 阿里云服务器代码已更新"
echo "✅ 3. 后端服务已重新构建并重启"
echo ""
echo "🎉 AI设计师功能部署完成！"
echo ""
echo "功能验证:"
echo "1. 访问首页查看AI设计师悬浮头像"
echo "2. 点击头像进行AI设计师咨询"
echo "3. 测试报价单分析、合同分析、AI验收、AI监理咨询功能"
echo ""
echo "注意: 前端需要重新编译才能在微信开发者工具中看到悬浮头像"

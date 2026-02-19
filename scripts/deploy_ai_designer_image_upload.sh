#!/bin/bash
# AI设计师图片上传功能部署脚本
# 部署到阿里云开发环境

set -e

echo "=== 开始部署AI设计师图片上传功能 ==="

# 1. 提交到Git
echo "1. 提交代码到Git..."
git add .
git commit -m "feat: 实现AI设计师图片上传功能，支持户型图分析和漫游视频生成器" || echo "没有新更改或提交失败，继续..."
git push

echo "✅ 代码已提交到Git"

# 2. 更新阿里云开发环境
echo "2. 更新阿里云开发环境..."
echo "SSH连接到阿里云服务器..."

ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 << 'EOF'
set -e
echo "登录成功，开始更新..."

# 进入项目目录
cd /root/project/dev/zhuangxiu-agent

# 拉取最新代码
echo "拉取最新代码..."
git pull

# 检查是否有冲突
if git status | grep -q "both modified"; then
    echo "⚠️ 检测到冲突，尝试解决..."
    git stash
    git pull
    git stash pop || echo "stash pop失败，继续..."
fi

# 重新构建并重启后端服务
echo "重新构建后端服务..."
docker compose -f docker-compose.dev.yml build backend --no-cache
docker compose -f docker-compose.dev.yml up -d backend

# 检查服务状态
echo "检查服务状态..."
sleep 5
docker ps | grep decoration-backend-dev

echo "✅ 阿里云部署完成"
EOF

echo "3. 验证部署..."
echo "等待服务启动..."
sleep 10

# 测试健康检查
echo "测试AI设计师健康检查..."
curl -s http://120.26.201.61:8001/api/v1/designer/health || echo "健康检查失败，请手动检查"

echo "=== 部署完成 ==="
echo "请访问：http://120.26.201.61:8001/api/v1/designer/health 验证服务状态"
echo "前端需要重新编译以使用新的图片上传功能"

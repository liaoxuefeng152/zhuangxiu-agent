#!/bin/bash

# 部署聚合数据API集成（去掉天眼查，只用聚合数据）

echo "=== 部署聚合数据API集成 ==="
echo ""

# 1. 检查当前目录
echo "1. 检查当前目录..."
if [ ! -f "backend/app/api/v1/companies.py" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi
echo "✓ 当前目录正确"

# 2. 检查Git状态
echo ""
echo "2. 检查Git状态..."
git status --short
echo ""

# 3. 提交代码到Git
echo "3. 提交代码到Git..."
read -p "是否提交代码到Git? (y/n): " confirm
if [ "$confirm" = "y" ]; then
    git add .
    git commit -m "feat: 去掉天眼查，集成聚合数据企业工商信息和法律案件API"
    git push
    echo "✓ 代码已提交到Git"
else
    echo "⚠ 跳过Git提交"
fi

# 4. 部署到阿里云
echo ""
echo "4. 部署到阿里云服务器..."
echo "这是后台问题，需要部署到阿里云服务器并重启后端服务"
echo ""
echo "请执行以下步骤:"
echo "1. SSH登录到阿里云服务器:"
echo "   ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61"
echo ""
echo "2. 进入项目目录:"
echo "   cd /root/project/dev/zhuangxiu-agent"
echo ""
echo "3. 拉取最新代码:"
echo "   git pull"
echo ""
echo "4. 重新构建并重启后端服务:"
echo "   docker compose -f docker-compose.dev.yml build backend --no-cache"
echo "   docker compose -f docker-compose.dev.yml up -d backend"
echo ""
echo "5. 验证部署:"
echo "   docker logs decoration-backend-dev --tail 20"

# 5. 测试API
echo ""
echo "5. 测试API..."
echo "部署完成后，可以测试以下API端点:"
echo ""
echo "a) 公司搜索API:"
echo "   GET /api/v1/companies/search?q=装饰&limit=5"
echo ""
echo "b) 公司扫描API:"
echo "   POST /api/v1/companies/scan"
echo "   Body: {\"company_name\": \"广州轩怡装饰设计工程有限公司\"}"
echo ""
echo "c) 获取扫描结果:"
echo "   GET /api/v1/companies/scan/{scan_id}"

echo ""
echo "=== 部署说明完成 ==="
echo ""
echo "总结:"
echo "1. 已移除天眼查API依赖"
echo "2. 已集成聚合数据两个API:"
echo "   - 企业工商信息API (SIMPLE_LIST_TOKEN)"
echo "   - 司法企业查询API (JUHECHA_TOKEN)"
echo "3. 公司搜索现在使用聚合数据企业工商信息API"
echo "4. 风险分析基于法律案件信息，不基于企业成立时间"
echo "5. 综合分析返回企业信息 + 法律风险分析"

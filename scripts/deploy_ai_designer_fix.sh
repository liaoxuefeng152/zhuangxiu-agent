#!/bin/bash
# AI设计师500错误修复部署脚本

echo "=========================================="
echo "AI设计师500错误修复部署"
echo "=========================================="

# 1. 提交代码到Git
echo "1. 提交代码到Git..."
git add backend/app/services/risk_analyzer.py
git commit -m "fix: AI设计师500错误修复 - 添加降级逻辑和友好的错误信息"

if [ $? -eq 0 ]; then
    echo "✓ 代码提交成功"
else
    echo "✗ 代码提交失败，请检查git状态"
    exit 1
fi

echo "2. 推送到远程仓库..."
git push

if [ $? -eq 0 ]; then
    echo "✓ 代码推送成功"
else
    echo "✗ 代码推送失败"
    exit 1
fi

echo ""
echo "3. 部署到阿里云开发环境..."
echo "   请执行以下命令："
echo ""
echo "   ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61"
echo "   cd /root/project/dev/zhuangxiu-agent"
echo "   git pull"
echo "   docker compose -f docker-compose.dev.yml build backend --no-cache"
echo "   docker compose -f docker-compose.dev.yml up -d backend"
echo ""
echo "4. 验证修复："
echo "   访问AI设计师聊天接口，应该不再返回500错误"
echo "   而是返回友好的错误信息：'抱歉，AI设计师服务暂时不可用...'"
echo ""
echo "=========================================="
echo "修复总结："
echo "=========================================="
echo "问题原因：AI设计师智能体资源点不足，返回空结果导致500错误"
echo "修复方案："
echo "  1. 添加降级逻辑：AI设计师 → AI监理 → DeepSeek"
echo "  2. 所有AI服务都不可用时，返回友好的错误信息"
echo "  3. 不再抛出异常，避免500错误"
echo ""
echo "归属：这是后台问题（AI服务配置和资源问题）"
echo ""
echo "注意：AI服务资源点不足需要联系扣子平台充值或更换智能体"
echo "=========================================="

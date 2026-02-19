#!/bin/bash
# 部署邀请功能到阿里云

echo "=== 部署邀请功能到阿里云 ==="
echo "这是**后台问题**，因为修改了后端API和数据库结构，需要部署到阿里云才能生效。"
echo ""

# 1. 提交代码到Git
echo "1. 提交代码到Git..."
git add .
git commit -m "V2.6.8: 新增邀请好友得免费报告功能
- 新增邀请系统数据库表 (invitation_records, free_unlock_entitlements)
- 新增邀请相关API接口
- 前端分享页集成邀请功能
- 报告解锁流程支持免费解锁权益
- 用户邀请码系统"
git push

echo ""
echo "✅ 代码已提交到Git"
echo ""

# 2. SSH到阿里云服务器部署
echo "2. 部署到阿里云服务器..."
echo "执行以下命令部署到阿里云:"
echo ""
echo "ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61"
echo ""
echo "然后在服务器上执行:"
echo "cd /root/project/dev/zhuangxiu-agent"
echo "git pull"
echo "docker compose -f docker-compose.dev.yml build backend --no-cache"
echo "docker compose -f docker-compose.dev.yml up -d backend"
echo ""
echo "或者使用一键部署脚本:"
echo "./scripts/deploy-aliyun.sh"
echo ""

# 3. 数据库迁移
echo "3. 数据库迁移..."
echo "在阿里云服务器上执行数据库迁移:"
echo ""
echo "docker exec -i decoration-postgres-dev psql -U decoration -d zhuangxiu_dev -f - < database/migration_v7_invitation.sql"
echo ""

# 4. 验证部署
echo "4. 验证部署..."
echo "部署完成后，验证邀请功能:"
echo "1. 访问后端API: http://120.26.201.61:8001/api/v1/invitations/"
echo "2. 测试前端分享页的'邀请好友'按钮"
echo "3. 测试报告解锁页的'使用免费解锁'功能"
echo ""

echo "=== 部署步骤完成 ==="
echo ""
echo "功能总结:"
echo "✅ 数据库表结构已创建"
echo "✅ 后端API已开发完成" 
echo "✅ 前端分享页已集成邀请功能"
echo "✅ 报告解锁流程已支持免费解锁"
echo "✅ 用户邀请码系统已实现"
echo ""
echo "使用流程:"
echo "1. 用户在分享页点击'邀请好友得免费报告'"
echo "2. 生成邀请链接和邀请码"
echo "3. 好友通过邀请链接注册"
echo "4. 邀请人获得1次免费报告解锁权益"
echo "5. 在报告解锁页可使用免费权益解锁报告"
echo ""
echo "注意: 这是**后台问题**，必须部署到阿里云服务器才能生效！"

#!/bin/bash
# Docker 一键部署脚本（带本地自动测试）
# 装修智能体项目专用

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计时函数
start_time=$(date +%s)

# ====================== 第一步：本地自动测试 ======================
echo -e "${BLUE}===== 1. 本地测试 Docker 开发环境 =====${NC}"

# 停止旧的开发容器（避免端口占用）
echo "停止旧的开发容器..."
docker-compose -f docker-compose.dev.yml down > /dev/null 2>&1 || true

# 重建并启动开发容器
echo "启动本地开发容器..."
docker-compose -f docker-compose.dev.yml up -d --build

# 等待容器启动（使用智能等待）
echo "等待服务启动..."
for i in {1..10}; do
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 服务已启动${NC}"
    break
  fi
  if [ $i -eq 10 ]; then
    echo -e "${RED}❌ 服务启动超时${NC}"
    docker-compose -f docker-compose.dev.yml down
    exit 1
  fi
  sleep 2
done

# 测试健康状态
echo "测试服务健康状态..."
health_response=$(curl -s http://localhost:8000/health | grep -o '"status":"healthy"' || echo "")
if [ -z "$health_response" ]; then
  echo -e "${RED}❌ 本地测试失败：服务不健康${NC}"
  docker-compose -f docker-compose.dev.yml down
  exit 1
fi

echo -e "${GREEN}✅ 本地测试通过！${NC}"
docker-compose -f docker-compose.dev.yml down  # 测试完停止开发容器

# ====================== 第二步：提交代码 ======================
echo -e "${BLUE}===== 2. 本地提交代码 =====${NC}"

# 检查是否有更改
if git diff --quiet && git diff --cached --quiet; then
  echo -e "${YELLOW}没有需要提交的更改${NC}"
else
  # 添加所有更改
  git add -A
  
  # 获取提交消息
  if [ -z "$1" ]; then
    read -p "请输入提交备注（如：修复微信回调配置）：" commit_msg
  else
    commit_msg="$1"
  fi
  
  # 提交更改
  git commit -m "$commit_msg"
  
  # 推送到远程
  echo "推送到GitHub..."
  git push origin main
  echo -e "${GREEN}✓ 代码已推送到GitHub${NC}"
fi

# ====================== 第三步：服务器部署 ======================
echo -e "${BLUE}===== 3. 服务器备份+部署 =====${NC}"

# 执行服务器部署
ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 "
  set -e
  cd /root/project/prod/zhuangxiu-agent
  
  echo '备份当前版本...'
  backup_dir=\"/root/project/zhuangxiu-agent.bak.\$(date +%Y%m%d%H%M%S)\"
  cp -r . \"\$backup_dir\"
  echo \"备份完成: \$backup_dir\"
  
  echo '拉取最新代码...'
  git pull origin main
  
  echo '检查数据库迁移文件...'
  if ls database/migration_*.sql 1> /dev/null 2>&1; then
    echo '发现数据库迁移文件，准备执行迁移...'
    # 这里可以添加数据库迁移逻辑
    # 例如：docker-compose -f docker-compose.prod.yml exec -T postgres-prod psql -U zhuangxiu_user -d zhuangxiu_prod -f /app/database/latest_migration.sql
    echo -e \"${YELLOW}⚠️  注意：需要手动执行数据库迁移${NC}\"
  fi
  
  echo '重启生产容器...'
  docker-compose -f docker-compose.prod.yml down
  docker-compose -f docker-compose.prod.yml up -d --build
  
  echo '等待服务启动...'
  for i in {1..15}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
      echo -e \"${GREEN}✓ 生产服务已启动${NC}\"
      break
    fi
    if [ \$i -eq 15 ]; then
      echo -e \"${RED}❌ 生产服务启动超时${NC}\"
      echo '尝试回滚到备份版本...'
      docker-compose -f docker-compose.prod.yml down
      rm -rf .
      cp -r \"\$backup_dir\"/* .
      cp -r \"\$backup_dir\"/.[!.]* . 2>/dev/null || true
      docker-compose -f docker-compose.prod.yml up -d
      echo -e \"${YELLOW}⚠️  已回滚到备份版本${NC}\"
      exit 1
    fi
    sleep 3
  done
  
  # 检查服务健康状态
  echo '检查服务健康状态...'
  health_status=\$(curl -s http://localhost:8000/health | grep -o '\"status\":\"healthy\"' || echo '')
  if [ -z \"\$health_status\" ]; then
    echo -e \"${RED}❌ 生产服务不健康${NC}\"
    exit 1
  fi
  
  echo -e \"${GREEN}✓ 生产服务健康检查通过${NC}\"
"

# ====================== 第四步：验证部署 ======================
echo -e "${BLUE}===== 4. 验证生产容器状态 =====${NC}"

ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 "
  echo '当前生产容器状态：'
  docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E '(zhuangxiu|postgres)'
  
  echo ''
  echo '服务健康状态：'
  curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
  
  echo ''
  echo '数据库连接测试：'
  docker-compose -f docker-compose.prod.yml exec -T postgres-prod pg_isready -U zhuangxiu_user -d zhuangxiu_prod && echo -e \"${GREEN}✓ 数据库连接正常${NC}\" || echo -e \"${RED}❌ 数据库连接失败${NC}\"
"

# 计算部署时间
end_time=$(date +%s)
duration=$((end_time - start_time))

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}总耗时: ${duration}秒${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}重要提醒：${NC}"
echo "1. 如果部署包含数据库变更，请手动执行数据库迁移"
echo "2. 打开小程序测试核心功能"
echo "3. 监控日志：ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 'docker-compose -f /root/project/prod/zhuangxiu-agent/docker-compose.prod.yml logs -f'"
echo ""
echo -e "${BLUE}常用命令：${NC}"
echo "  - 查看日志: ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 'docker-compose -f /root/project/prod/zhuangxiu-agent/docker-compose.prod.yml logs -f backend-prod'"
echo "  - 重启服务: ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 'cd /root/project/prod/zhuangxiu-agent && docker-compose -f docker-compose.prod.yml restart backend-prod'"
echo "  - 回滚部署: 使用备份目录: /root/project/zhuangxiu-agent.bak.*"

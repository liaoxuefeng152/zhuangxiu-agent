#!/bin/bash
set -e

echo "===== 开始生产环境部署 ====="

ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61 "
  set -e
  cd /root/project/prod/zhuangxiu-agent
  
  echo '备份当前版本...'
  backup_dir=\"/root/project/zhuangxiu-agent.bak.\$(date +%Y%m%d%H%M%S)\"
  cp -r . \"\$backup_dir\"
  echo \"备份完成: \$backup_dir\"
  
  echo '拉取最新代码...'
  git pull origin main
  
  echo '重启生产容器...'
  docker-compose -f docker-compose.prod.yml down
  docker-compose -f docker-compose.prod.yml up -d --build
  
  echo '等待服务启动...'
  for i in {1..15}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
      echo '✓ 生产服务已启动'
      break
    fi
    if [ \$i -eq 15 ]; then
      echo '❌ 生产服务启动超时'
      exit 1
    fi
    sleep 3
  done
  
  echo '检查服务健康状态...'
  curl -f http://localhost:8000/health > /dev/null 2>&1 || {
    echo '❌ 生产服务不健康'
    exit 1
  }
  
  echo '✓ 生产服务健康检查通过'
"

echo "===== 部署完成 ====="

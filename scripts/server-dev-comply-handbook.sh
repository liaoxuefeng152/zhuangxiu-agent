#!/bin/bash
# 使阿里云服务器开发环境完全符合《装修决策Agent API 访问手册》
# 在服务器上执行: bash server-dev-comply-handbook.sh
# 或: ssh root@120.26.201.61 'bash -s' < scripts/server-dev-comply-handbook.sh

set -e

echo "=== 1. 开发后端改为 8001:8000 ==="
ENV_FILE=""
if docker ps -a --format '{{.Names}}' | grep -qx zhuangxiu-backend-dev; then
  docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' zhuangxiu-backend-dev > /tmp/backend-env.txt 2>/dev/null || true
  [ -s /tmp/backend-env.txt ] && ENV_FILE="/tmp/backend-env.txt"
  docker stop zhuangxiu-backend-dev 2>/dev/null || true
  docker rm zhuangxiu-backend-dev 2>/dev/null || true
fi

NETWORK="zhuangxiu-agent_default"
if ! docker network inspect "$NETWORK" &>/dev/null; then
  NETWORK="bridge"
fi

RUN_ARGS=(-d --name zhuangxiu-backend-dev --network "$NETWORK" -p 8001:8000 --restart unless-stopped)
[ -n "$ENV_FILE" ] && RUN_ARGS+=(--env-file "$ENV_FILE")
docker run "${RUN_ARGS[@]}" zhuangxiu-agent-backend:latest
rm -f /tmp/backend-env.txt

echo "=== 2. 更新 Nginx dev.conf ==="
echo "若 Nginx 挂载宿主机目录，请将本仓库 nginx/conf.d/dev.conf 复制到服务器挂载路径（如 /root/project/dev/zhuangxiu-agent/nginx/conf.d/dev.conf）后执行:"
echo "  docker exec nginx-zhuangxiu nginx -t && docker exec nginx-zhuangxiu nginx -s reload"
echo "若未挂载，可从本机执行: cat nginx/conf.d/dev.conf | ssh root@服务器 'cat > 宿主机conf.d路径/dev.conf' 后重载。"
docker exec nginx-zhuangxiu nginx -t 2>/dev/null && docker exec nginx-zhuangxiu nginx -s reload 2>/dev/null && echo "Nginx 已重载" || true

echo "=== 3. 验证 ==="
sleep 2
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E "NAMES|backend-dev|nginx"
curl -s -o /dev/null -w "8001/health: %{http_code}\n" http://127.0.0.1:8001/health || true
curl -s -o /dev/null -w "Host dev /docs -> %{http_code}\n" -H "Host: dev.lakeli.top" http://127.0.0.1/docs || true
echo "完成。手册要求：直连 http://120.26.201.61:8001，Swagger http://dev.lakeli.top/docs"

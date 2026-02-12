#!/bin/bash
# 开发环境可用性测试（与《装修决策Agent API 访问手册》一致）
# 使用前请配置 hosts: 120.26.201.61 dev.lakeli.top
# 或使用 IP + Host 头（脚本内已用 Host 头，无需改 hosts）

set -e
BASE="${DEV_BASE_URL:-http://120.26.201.61}"
H="Host: dev.lakeli.top"
PASS=0
FAIL=0

check() {
  local name="$1"
  local want="$2"
  local code=$(curl -s -o /dev/null -w "%{http_code}" -H "$H" "$3")
  if [ "$code" = "$want" ]; then
    echo "  [OK] $name (HTTP $code)"
    ((PASS++)) || true
    return 0
  else
    echo "  [FAIL] $name (expected $want, got $code)"
    ((FAIL++)) || true
    return 1
  fi
}

echo "=== 开发环境测试 $BASE (Host: dev.lakeli.top) ==="
echo ""

echo "1. 健康检查与文档"
check "健康检查 /health" "200" "$BASE/health"
check "API 文档 /api/docs" "200" "$BASE/api/docs"
CODE=$(curl -sI -H "$H" "$BASE/docs" | grep -o "HTTP/1.1 [0-9]*" | awk '{print $2}')
if [ "$CODE" = "302" ]; then
  echo "  [OK] /docs 重定向 (HTTP 302)"
  ((PASS++)) || true
else
  echo "  [FAIL] /docs 重定向 (expected 302, got $CODE)"
  ((FAIL++)) || true
fi

echo ""
echo "2. 直连开发后端 8001"
check "8001 健康检查" "200" "$BASE:8001/health"
check "8001 /api/docs" "200" "$BASE:8001/api/docs"

echo ""
echo "3. API 路由（手册约定路径）"
# 登录：路由通即可，401 为微信配置
RES=$(curl -s -X POST -H "$H" -H "Content-Type: application/json" -d '{"code":"dev_h5_mock"}' "$BASE/api/v1/users/login")
if echo "$RES" | grep -q '"code":'; then
  echo "  [OK] POST /api/v1/users/login 可达 (返回 body 含 code)"
  ((PASS++)) || true
else
  echo "  [FAIL] POST /api/v1/users/login 无有效响应"
  ((FAIL++)) || true
fi

echo ""
echo "=== 结果: $PASS 通过, $FAIL 失败 ==="
[ "$FAIL" -eq 0 ]

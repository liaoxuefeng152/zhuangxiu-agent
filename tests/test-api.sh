#!/bin/bash
# 前后端连调测试脚本

echo "=========================================="
echo "前后端连调测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试配置
API_BASE="http://localhost:8000"
API_V1="${API_BASE}/api/v1"

# 测试计数器
PASSED=0
FAILED=0

# 测试函数
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local headers=$5
    
    echo -n "测试: $name ... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" $headers "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method $headers -H "Content-Type: application/json" -d "$data" "$url")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✓ 通过 (HTTP $http_code)${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ 失败 (HTTP $http_code)${NC}"
        echo "  响应: $body" | head -c 200
        echo ""
        ((FAILED++))
        return 1
    fi
}

# 1. 健康检查
echo "1. 后端健康检查"
test_endpoint "健康检查" "GET" "${API_BASE}/health"
echo ""

# 2. 登录测试
echo "2. 用户登录"
LOGIN_RESPONSE=$(curl -s -X POST "${API_V1}/users/login" \
    -H "Content-Type: application/json" \
    -d '{"code":"dev_h5_mock"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', ''))" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✓ 登录成功${NC}"
    echo "  Token: ${TOKEN:0:50}..."
    ((PASSED++))
else
    echo -e "${RED}✗ 登录失败${NC}"
    echo "  响应: $LOGIN_RESPONSE"
    ((FAILED++))
fi
echo ""

# 3. 报告列表测试（需要token）
if [ -n "$TOKEN" ]; then
    echo "3. 报告列表接口"
    echo -n "测试: 获取报告列表 ... "
    response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "${API_V1}/contracts/list?page=1&page_size=10")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ 通过 (HTTP $http_code)${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ 失败 (HTTP $http_code)${NC}"
        echo "  响应: $body" | head -c 200
        echo ""
        ((FAILED++))
    fi
    echo ""
fi

# 4. 用户信息测试
if [ -n "$TOKEN" ]; then
    echo "4. 用户信息接口"
    echo -n "测试: 获取用户信息 ... "
    response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "${API_V1}/users/profile")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ 通过 (HTTP $http_code)${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ 失败 (HTTP $http_code)${NC}"
        echo "  响应: $body" | head -c 200
        echo ""
        ((FAILED++))
    fi
    echo ""
fi

# 总结
echo "=========================================="
echo "测试总结"
echo "=========================================="
echo -e "${GREEN}通过: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}失败: $FAILED${NC}"
else
    echo -e "${GREEN}失败: $FAILED${NC}"
fi
echo ""

# 检查前端配置
echo "=========================================="
echo "前端配置检查"
echo "=========================================="
if [ -f "frontend/.env.development" ]; then
    API_URL=$(grep "TARO_APP_API_BASE_URL" frontend/.env.development | cut -d'=' -f2)
    echo "当前配置的API地址: $API_URL"
    
    if echo "$API_URL" | grep -q "localhost"; then
        echo -e "${YELLOW}⚠ 注意: 使用 localhost，真机预览时需要改为局域网IP${NC}"
    elif echo "$API_URL" | grep -q "192.168\|10\."; then
        echo -e "${GREEN}✓ 已配置局域网IP，可用于真机预览${NC}"
    fi
else
    echo -e "${RED}✗ 未找到 frontend/.env.development${NC}"
fi
echo ""

# 服务状态检查
echo "=========================================="
echo "服务状态"
echo "=========================================="
if lsof -i :8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务运行中 (端口 8000)${NC}"
else
    echo -e "${RED}✗ 后端服务未运行${NC}"
    echo "  启动命令: cd backend && python main.py"
fi

echo ""
echo "测试完成！"

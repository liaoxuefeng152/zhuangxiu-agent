#!/bin/bash
echo "🧪 实际API功能测试"

BASE_URL="http://localhost:8000"

echo "1. 查看API文档:"
echo "Swagger UI: http://localhost:8000/docs"
echo "ReDoc:      http://localhost:8000/redoc"

echo -e "\n2. 测试用户相关API（如果存在）:"
# 尝试常见的API端点
ENDPOINTS=("/api/v1/auth/login" "/api/v1/auth/register" "/api/v1/users/me" "/api/v1/wechat/login")

for endpoint in "${ENDPOINTS[@]}"; do
    echo -n "测试 $endpoint: "
    curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint" 2>/dev/null
    echo " 状态码"
done

echo -e "\n3. 测试装修相关API:"
ENDPOINTS=("/api/v1/reports" "/api/v1/companies" "/api/v1/materials")

for endpoint in "${ENDPOINTS[@]}"; do
    echo -n "测试 $endpoint: "
    curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint" 2>/dev/null
    echo " 状态码"
done

echo -e "\n✅ 测试完成"

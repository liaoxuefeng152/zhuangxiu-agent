#!/bin/bash
echo "🧪 API功能测试"

BASE_URL="http://localhost:8000"

echo "1. 根路径测试:"
curl -s "$BASE_URL/" | head -2

echo -e "\n2. 健康检查:"
curl -s "$BASE_URL/health" | head -2

echo -e "\n3. OpenAPI文档:"
curl -s "$BASE_URL/openapi.json" | grep -o '"title":"[^"]*"' | head -1

echo -e "\n4. 数据库状态（如果有这个端点）:"
curl -s "$BASE_URL/api/v1/health/db" 2>/dev/null | head -2 || echo "无数据库状态端点"

echo -e "\n✅ 基本测试完成"

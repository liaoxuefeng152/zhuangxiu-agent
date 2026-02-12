#!/bin/bash
# 功能测试脚本 - 基于功能测试用例V2.6.1

BASE_URL="http://120.26.201.61/api/v1"
TEST_RESULTS=()
PASSED=0
FAILED=0

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 测试结果记录函数
record_test() {
    local test_id=$1
    local test_name=$2
    local result=$3
    local note=$4
    
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $test_id: $test_name"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $test_id: $test_name - $note"
        ((FAILED++))
    fi
    
    TEST_RESULTS+=("$test_id|$test_name|$result|$note")
}

# 获取Token
echo "=========================================="
echo "功能测试 - 基于测试用例V2.6.1"
echo "=========================================="
echo ""

echo "1. 获取认证Token..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/users/login" \
    -H "Content-Type: application/json" \
    -d '{"code":"dev_weapp_mock"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
USER_ID=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('user_id', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ 登录失败，无法继续测试${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} 登录成功，Token已获取"
echo ""

# ========== 2.1 用户认证模块测试 ==========
echo "=========================================="
echo "2.1 用户认证模块测试"
echo "=========================================="

# TC-AUTH-06: 开发环境模拟登录
if [ -n "$TOKEN" ]; then
    record_test "TC-AUTH-06" "开发环境模拟登录" "PASS" ""
else
    record_test "TC-AUTH-06" "开发环境模拟登录" "FAIL" "未获取到Token"
fi

# TC-AUTH-07: 用户信息获取
PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/users/profile" \
    -H "Authorization: Bearer $TOKEN")

if echo "$PROFILE_RESPONSE" | grep -q "user_id"; then
    record_test "TC-AUTH-07" "用户信息获取" "PASS" ""
else
    record_test "TC-AUTH-07" "用户信息获取" "FAIL" "响应: $PROFILE_RESPONSE"
fi

echo ""

# ========== 2.2 公司风险检测模块测试 ==========
echo "=========================================="
echo "2.2 公司风险检测模块测试"
echo "=========================================="

# TC-COMPANY-02: 公司名称模糊搜索
SEARCH_RESPONSE=$(curl -s -X GET "$BASE_URL/companies/search?q=装修" \
    -H "Authorization: Bearer $TOKEN")

if echo "$SEARCH_RESPONSE" | grep -q "list"; then
    record_test "TC-COMPANY-02" "公司名称模糊搜索" "PASS" ""
else
    record_test "TC-COMPANY-02" "公司名称模糊搜索" "FAIL" "响应: $SEARCH_RESPONSE"
fi

# TC-COMPANY-03: 提交公司检测
SCAN_RESPONSE=$(curl -s -X POST "$BASE_URL/companies/scan" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"company_name":"测试装修公司"}')

SCAN_ID=$(echo $SCAN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('scan_id', ''))" 2>/dev/null)

if [ -n "$SCAN_ID" ]; then
    record_test "TC-COMPANY-03" "提交公司检测" "PASS" "scan_id: $SCAN_ID"
    
    # TC-COMPANY-05: 检测结果查询
    sleep 2
    SCAN_DETAIL_RESPONSE=$(curl -s -X GET "$BASE_URL/companies/scan/$SCAN_ID" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$SCAN_DETAIL_RESPONSE" | grep -q "status\|scan_id"; then
        record_test "TC-COMPANY-05" "检测结果查询" "PASS" ""
    else
        record_test "TC-COMPANY-05" "检测结果查询" "FAIL" "响应: $SCAN_DETAIL_RESPONSE"
    fi
else
    record_test "TC-COMPANY-03" "提交公司检测" "FAIL" "响应: $SCAN_RESPONSE"
fi

# TC-COMPANY-06: 检测记录列表
SCANS_LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/companies/scans?page=1&page_size=10" \
    -H "Authorization: Bearer $TOKEN")

if echo "$SCANS_LIST_RESPONSE" | grep -q "list\|total"; then
    record_test "TC-COMPANY-06" "检测记录列表" "PASS" ""
else
    record_test "TC-COMPANY-06" "检测记录列表" "FAIL" "响应: $SCANS_LIST_RESPONSE"
fi

echo ""

# ========== 2.3 报价单分析模块测试 ==========
echo "=========================================="
echo "2.3 报价单分析模块测试"
echo "=========================================="

# TC-QUOTE-07: 报价单列表
QUOTES_LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/quotes/list?page=1&page_size=10" \
    -H "Authorization: Bearer $TOKEN")

if echo "$QUOTES_LIST_RESPONSE" | grep -q "list\|total"; then
    record_test "TC-QUOTE-07" "报价单列表" "PASS" ""
else
    record_test "TC-QUOTE-07" "报价单列表" "FAIL" "响应: $QUOTES_LIST_RESPONSE"
fi

# TC-QUOTE-03: 文件格式校验（测试无效格式）
# 注意：这里我们无法实际上传文件，但可以测试接口是否存在
record_test "TC-QUOTE-03" "文件格式校验" "SKIP" "需要实际上传文件测试"

# TC-QUOTE-04: 文件大小校验
record_test "TC-QUOTE-04" "文件大小校验" "SKIP" "需要实际上传文件测试"

echo ""

# ========== 2.4 合同审核模块测试 ==========
echo "=========================================="
echo "2.4 合同审核模块测试"
echo "=========================================="

# TC-CONTRACT-04: 合同列表
CONTRACTS_LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/contracts/list?page=1&page_size=10" \
    -H "Authorization: Bearer $TOKEN")

if echo "$CONTRACTS_LIST_RESPONSE" | grep -q "list\|total"; then
    record_test "TC-CONTRACT-04" "合同列表" "PASS" ""
else
    record_test "TC-CONTRACT-04" "合同列表" "FAIL" "响应: $CONTRACTS_LIST_RESPONSE"
fi

echo ""

# ========== 2.5 施工进度管理模块测试 ==========
echo "=========================================="
echo "2.5 施工进度管理模块测试"
echo "=========================================="

# TC-CONSTRUCTION-01: 设置开工日期
START_DATE=$(date -v+7d +%Y-%m-%d 2>/dev/null || date -d "+7 days" +%Y-%m-%d)
CONSTRUCTION_RESPONSE=$(curl -s -X POST "$BASE_URL/constructions/start-date" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"start_date\":\"$START_DATE\"}")

if echo "$CONSTRUCTION_RESPONSE" | grep -q "success\|start_date"; then
    record_test "TC-CONSTRUCTION-01" "设置开工日期" "PASS" ""
    
    # TC-CONSTRUCTION-03: 进度计划查询
    SCHEDULE_RESPONSE=$(curl -s -X GET "$BASE_URL/constructions/schedule" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$SCHEDULE_RESPONSE" | grep -q "stages\|schedule"; then
        record_test "TC-CONSTRUCTION-03" "进度计划查询" "PASS" ""
    else
        record_test "TC-CONSTRUCTION-03" "进度计划查询" "FAIL" "响应: $SCHEDULE_RESPONSE"
    fi
else
    # 可能已经设置过，尝试查询
    SCHEDULE_RESPONSE=$(curl -s -X GET "$BASE_URL/constructions/schedule" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$SCHEDULE_RESPONSE" | grep -q "stages\|schedule\|404"; then
        if echo "$SCHEDULE_RESPONSE" | grep -q "404"; then
            record_test "TC-CONSTRUCTION-01" "设置开工日期" "FAIL" "需要先设置开工日期"
        else
            record_test "TC-CONSTRUCTION-01" "设置开工日期" "SKIP" "已存在开工日期"
            record_test "TC-CONSTRUCTION-03" "进度计划查询" "PASS" ""
        fi
    else
        record_test "TC-CONSTRUCTION-01" "设置开工日期" "FAIL" "响应: $CONSTRUCTION_RESPONSE"
    fi
fi

echo ""

# ========== 2.6 报告中心模块测试 ==========
echo "=========================================="
echo "2.6 报告中心模块测试"
echo "=========================================="

# TC-REPORT-01: 报告列表查询（合同报告）
if echo "$CONTRACTS_LIST_RESPONSE" | grep -q "list\|total"; then
    record_test "TC-REPORT-01" "报告列表查询" "PASS" ""
else
    record_test "TC-REPORT-01" "报告列表查询" "FAIL" ""
fi

# TC-REPORT-02: 报告列表分页
if echo "$CONTRACTS_LIST_RESPONSE" | grep -q "page\|page_size\|total"; then
    record_test "TC-REPORT-02" "报告列表分页" "PASS" ""
else
    record_test "TC-REPORT-02" "报告列表分页" "FAIL" ""
fi

echo ""

# ========== 2.7 非功能测试 ==========
echo "=========================================="
echo "2.7 非功能测试"
echo "=========================================="

# TC-NF-01: 健康检查响应时间
START_TIME=$(date +%s%N)
HEALTH_RESPONSE=$(curl -s -X GET "http://120.26.201.61/health")
END_TIME=$(date +%s%N)
DURATION=$((($END_TIME - $START_TIME) / 1000000))

if [ $DURATION -le 500 ]; then
    record_test "TC-NF-01" "健康检查响应时间" "PASS" "${DURATION}ms"
else
    record_test "TC-NF-01" "健康检查响应时间" "FAIL" "${DURATION}ms (超过500ms)"
fi

# TC-NF-04: Token认证校验
NO_TOKEN_RESPONSE=$(curl -s -X GET "$BASE_URL/users/profile" \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$NO_TOKEN_RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    record_test "TC-NF-04" "Token认证校验" "PASS" "HTTP $HTTP_CODE"
else
    record_test "TC-NF-04" "Token认证校验" "FAIL" "HTTP $HTTP_CODE"
fi

echo ""

# ========== 测试结果汇总 ==========
echo "=========================================="
echo "测试结果汇总"
echo "=========================================="
echo "总测试数: $((PASSED + FAILED))"
echo -e "${GREEN}通过: $PASSED${NC}"
echo -e "${RED}失败: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}✗ 部分测试失败${NC}"
    exit 1
fi

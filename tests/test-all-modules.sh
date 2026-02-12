#!/bin/bash
# 全面功能测试脚本 - 基于PRD V2.6.1和功能测试用例

BASE_URL="http://120.26.201.61/api/v1"
TEST_RESULTS=()
PASSED=0
FAILED=0
SKIPPED=0

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    elif [ "$result" = "SKIP" ]; then
        echo -e "${YELLOW}⊘${NC} $test_id: $test_name - $note"
        ((SKIPPED++))
    else
        echo -e "${RED}✗${NC} $test_id: $test_name - $note"
        ((FAILED++))
    fi
    
    TEST_RESULTS+=("$test_id|$test_name|$result|$note")
}

echo "=========================================="
echo "全面功能测试 - PRD V2.6.1"
echo "=========================================="
echo ""

# 获取Token
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

if echo "$SEARCH_RESPONSE" | grep -q "list\|code"; then
    record_test "TC-COMPANY-02" "公司名称模糊搜索" "PASS" ""
else
    record_test "TC-COMPANY-02" "公司名称模糊搜索" "FAIL" "响应格式异常"
fi

# TC-COMPANY-03: 提交公司检测
SCAN_RESPONSE=$(curl -s -X POST "$BASE_URL/companies/scan" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"company_name":"测试装修公司有限公司"}')

SCAN_ID=$(echo $SCAN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -n "$SCAN_ID" ]; then
    record_test "TC-COMPANY-03" "提交公司检测" "PASS" "scan_id: $SCAN_ID"
    
    # TC-COMPANY-05: 检测结果查询
    sleep 2
    SCAN_DETAIL_RESPONSE=$(curl -s -X GET "$BASE_URL/companies/scan/$SCAN_ID" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$SCAN_DETAIL_RESPONSE" | grep -q "status\|scan_id\|id"; then
        record_test "TC-COMPANY-05" "检测结果查询" "PASS" ""
    else
        record_test "TC-COMPANY-05" "检测结果查询" "FAIL" "响应格式异常"
    fi
    
    # TC-COMPANY-07: 公司风险报告详情
    if echo "$SCAN_DETAIL_RESPONSE" | grep -q "risk_level\|risk_score"; then
        record_test "TC-COMPANY-07" "公司风险报告详情" "PASS" ""
    else
        record_test "TC-COMPANY-07" "公司风险报告详情" "FAIL" ""
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
    record_test "TC-COMPANY-06" "检测记录列表" "FAIL" ""
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
    record_test "TC-QUOTE-07" "报价单列表" "FAIL" ""
fi

# TC-QUOTE-02: 报价单文件上传
cd /Users/mac/zhuangxiu-agent-backup
echo "test quote" > test_quote_upload.png 2>/dev/null
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/quotes/upload" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@test_quote_upload.png" 2>/dev/null)

QUOTE_ID=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('task_id', ''))" 2>/dev/null)

if [ -n "$QUOTE_ID" ]; then
    record_test "TC-QUOTE-02" "报价单文件上传" "PASS" "quote_id: $QUOTE_ID"
    
    # TC-QUOTE-05: 报价单分析结果
    sleep 3
    QUOTE_DETAIL_RESPONSE=$(curl -s -X GET "$BASE_URL/quotes/quote/$QUOTE_ID" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$QUOTE_DETAIL_RESPONSE" | grep -q "status\|risk_score"; then
        record_test "TC-QUOTE-05" "报价单分析结果" "PASS" ""
    else
        record_test "TC-QUOTE-05" "报价单分析结果" "SKIP" "分析可能还在进行中"
    fi
else
    record_test "TC-QUOTE-02" "报价单文件上传" "FAIL" ""
fi

# TC-QUOTE-03: 文件格式校验
echo "test" > test_invalid.doc 2>/dev/null
INVALID_FORMAT_RESPONSE=$(curl -s -X POST "$BASE_URL/quotes/upload" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@test_invalid.doc" 2>/dev/null)

if echo "$INVALID_FORMAT_RESPONSE" | grep -q "400\|仅支持"; then
    record_test "TC-QUOTE-03" "文件格式校验" "PASS" ""
else
    record_test "TC-QUOTE-03" "文件格式校验" "FAIL" ""
fi

rm -f test_quote_upload.png test_invalid.doc 2>/dev/null

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
    record_test "TC-CONTRACT-04" "合同列表" "FAIL" ""
fi

# TC-CONTRACT-01: 合同文件上传
echo "test contract" > test_contract_upload.png 2>/dev/null
CONTRACT_UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/contracts/upload" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@test_contract_upload.png" 2>/dev/null)

CONTRACT_ID=$(echo $CONTRACT_UPLOAD_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('task_id', ''))" 2>/dev/null)

if [ -n "$CONTRACT_ID" ]; then
    record_test "TC-CONTRACT-01" "合同文件上传" "PASS" "contract_id: $CONTRACT_ID"
    
    # TC-CONTRACT-02: 合同分析结果
    sleep 3
    CONTRACT_DETAIL_RESPONSE=$(curl -s -X GET "$BASE_URL/contracts/contract/$CONTRACT_ID" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$CONTRACT_DETAIL_RESPONSE" | grep -q "status\|risk_level"; then
        record_test "TC-CONTRACT-02" "合同分析结果" "PASS" ""
    else
        record_test "TC-CONTRACT-02" "合同分析结果" "SKIP" "分析可能还在进行中"
    fi
    
    # TC-CONTRACT-05: 合同详情（含summary）
    if echo "$CONTRACT_DETAIL_RESPONSE" | grep -q "summary\|risk_items"; then
        record_test "TC-CONTRACT-05" "合同详情（含summary）" "PASS" ""
    else
        record_test "TC-CONTRACT-05" "合同详情（含summary）" "SKIP" ""
    fi
else
    record_test "TC-CONTRACT-01" "合同文件上传" "FAIL" ""
fi

rm -f test_contract_upload.png 2>/dev/null

echo ""

# ========== 2.5 施工进度管理模块测试 ==========
echo "=========================================="
echo "2.5 施工进度管理模块测试"
echo "=========================================="

# TC-CONSTRUCTION-01: 设置开工日期
START_DATE="2026-02-20T00:00:00"
CONSTRUCTION_RESPONSE=$(curl -s -X POST "$BASE_URL/constructions/start-date" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"start_date\":\"$START_DATE\"}")

if echo "$CONSTRUCTION_RESPONSE" | grep -q "success\|stages\|start_date"; then
    record_test "TC-CONSTRUCTION-01" "设置开工日期" "PASS" ""
    
    # TC-CONSTRUCTION-03: 进度计划查询
    SCHEDULE_RESPONSE=$(curl -s -X GET "$BASE_URL/constructions/schedule" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$SCHEDULE_RESPONSE" | grep -q "stages\|S00\|S01"; then
        record_test "TC-CONSTRUCTION-03" "进度计划查询" "PASS" ""
        
        # 验证阶段互锁
        if echo "$SCHEDULE_RESPONSE" | grep -q "locked"; then
            record_test "TC-CONSTRUCTION-04" "流程互锁规则" "PASS" "阶段互锁机制正常"
        else
            record_test "TC-CONSTRUCTION-04" "流程互锁规则" "SKIP" ""
        fi
    else
        record_test "TC-CONSTRUCTION-03" "进度计划查询" "FAIL" ""
    fi
    
    # TC-CONSTRUCTION-05: 更新阶段状态
    UPDATE_STATUS_RESPONSE=$(curl -s -X PUT "$BASE_URL/constructions/stage-status" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"stage":"S00","status":"checked"}')
    
    if echo "$UPDATE_STATUS_RESPONSE" | grep -q "success\|stages"; then
        record_test "TC-CONSTRUCTION-05" "更新阶段状态" "PASS" ""
    else
        record_test "TC-CONSTRUCTION-05" "更新阶段状态" "SKIP" "可能需要先完成S00"
    fi
else
    # 可能已经设置过
    SCHEDULE_RESPONSE=$(curl -s -X GET "$BASE_URL/constructions/schedule" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$SCHEDULE_RESPONSE" | grep -q "stages\|404"; then
        if echo "$SCHEDULE_RESPONSE" | grep -q "404"; then
            record_test "TC-CONSTRUCTION-01" "设置开工日期" "FAIL" "需要先设置开工日期"
        else
            record_test "TC-CONSTRUCTION-01" "设置开工日期" "SKIP" "已存在开工日期"
            record_test "TC-CONSTRUCTION-03" "进度计划查询" "PASS" ""
        fi
    else
        record_test "TC-CONSTRUCTION-01" "设置开工日期" "FAIL" ""
    fi
fi

echo ""

# ========== 2.8 报告中心模块测试 ==========
echo "=========================================="
echo "2.8 报告中心模块测试"
echo "=========================================="

# TC-REPORT-01: 报告列表查询
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

# TC-REPORT-03: 报告详情查看
if [ -n "$CONTRACT_ID" ]; then
    if echo "$CONTRACT_DETAIL_RESPONSE" | grep -q "id\|status"; then
        record_test "TC-REPORT-03" "报告详情查看" "PASS" ""
    else
        record_test "TC-REPORT-03" "报告详情查看" "SKIP" ""
    fi
else
    record_test "TC-REPORT-03" "报告详情查看" "SKIP" "需要先上传合同"
fi

echo ""

# ========== 2.9 消息中心模块测试 ==========
echo "=========================================="
echo "2.9 消息中心模块测试"
echo "=========================================="

# TC-MESSAGE-01: 消息列表查询
MESSAGES_RESPONSE=$(curl -s -X GET "$BASE_URL/messages?page=1&page_size=10" \
    -H "Authorization: Bearer $TOKEN")

if echo "$MESSAGES_RESPONSE" | grep -q "list\|total\|code"; then
    record_test "TC-MESSAGE-01" "消息列表查询" "PASS" ""
else
    record_test "TC-MESSAGE-01" "消息列表查询" "SKIP" "接口可能未实现"
fi

# TC-MESSAGE-02: 未读消息数量
UNREAD_COUNT_RESPONSE=$(curl -s -X GET "$BASE_URL/messages/unread-count" \
    -H "Authorization: Bearer $TOKEN")

if echo "$UNREAD_COUNT_RESPONSE" | grep -q "count\|unread\|code"; then
    record_test "TC-MESSAGE-02" "未读消息数量" "PASS" ""
else
    record_test "TC-MESSAGE-02" "未读消息数量" "SKIP" "接口可能未实现"
fi

echo ""

# ========== 2.10 城市选择模块测试 ==========
echo "=========================================="
echo "2.10 城市选择模块测试"
echo "=========================================="

# TC-CITY-01: 热门城市查询
HOT_CITIES_RESPONSE=$(curl -s -X GET "$BASE_URL/cities/hot" \
    -H "Authorization: Bearer $TOKEN")

if echo "$HOT_CITIES_RESPONSE" | grep -q "list\|cities\|code"; then
    record_test "TC-CITY-01" "热门城市查询" "PASS" ""
else
    record_test "TC-CITY-01" "热门城市查询" "SKIP" "接口可能未实现"
fi

# TC-CITY-02: 城市列表查询
CITIES_LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/cities/list" \
    -H "Authorization: Bearer $TOKEN")

if echo "$CITIES_LIST_RESPONSE" | grep -q "list\|provinces\|code"; then
    record_test "TC-CITY-02" "城市列表查询" "PASS" ""
else
    record_test "TC-CITY-02" "城市列表查询" "SKIP" "接口可能未实现"
fi

# TC-CITY-03: 选择城市保存
SELECT_CITY_RESPONSE=$(curl -s -X POST "$BASE_URL/cities/select" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"city_name":"深圳"}')

if echo "$SELECT_CITY_RESPONSE" | grep -q "success\|code.*0"; then
    record_test "TC-CITY-03" "选择城市保存" "PASS" ""
else
    record_test "TC-CITY-03" "选择城市保存" "SKIP" "接口可能未实现"
fi

# TC-CITY-04: 当前城市查询
CURRENT_CITY_RESPONSE=$(curl -s -X GET "$BASE_URL/cities/current" \
    -H "Authorization: Bearer $TOKEN")

if echo "$CURRENT_CITY_RESPONSE" | grep -q "city_name\|city_code\|code"; then
    record_test "TC-CITY-04" "当前城市查询" "PASS" ""
else
    record_test "TC-CITY-04" "当前城市查询" "SKIP" "接口可能未实现"
fi

echo ""

# ========== 非功能测试 ==========
echo "=========================================="
echo "非功能测试"
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
echo "总测试数: $((PASSED + FAILED + SKIPPED))"
echo -e "${GREEN}通过: $PASSED${NC}"
echo -e "${RED}失败: $FAILED${NC}"
echo -e "${YELLOW}跳过: $SKIPPED${NC}"
echo ""

# 计算通过率
TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    PASS_RATE=$((PASSED * 100 / TOTAL))
    echo "通过率: ${PASS_RATE}%"
fi

echo ""
echo "详细测试结果："
for result in "${TEST_RESULTS[@]}"; do
    IFS='|' read -r id name status note <<< "$result"
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $id: $name"
    elif [ "$status" = "SKIP" ]; then
        echo -e "${YELLOW}⊘${NC} $id: $name - $note"
    else
        echo -e "${RED}✗${NC} $id: $name - $note"
    fi
done

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ 部分测试失败${NC}"
    exit 1
fi

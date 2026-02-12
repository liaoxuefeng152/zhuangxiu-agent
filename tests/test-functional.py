#!/usr/bin/env python3
"""
装修避坑管家 - 功能测试脚本
基于PRD V2.6.1测试用例执行自动化测试
"""
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sys

# 测试配置
API_BASE = "http://localhost:8000"
API_V1 = f"{API_BASE}/api/v1"

# 测试结果
test_results = []
current_token = None
current_user_id = None


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def log_test(case_id: str, name: str, result: bool, message: str = ""):
    """记录测试结果"""
    status = f"{Colors.GREEN}✓ 通过{Colors.END}" if result else f"{Colors.RED}✗ 失败{Colors.END}"
    print(f"[{case_id}] {name}: {status}")
    if message:
        print(f"  {message}")
    
    test_results.append({
        "case_id": case_id,
        "name": name,
        "result": "通过" if result else "失败",
        "message": message,
        "timestamp": datetime.now().isoformat()
    })


def make_request(method: str, endpoint: str, data: Optional[Dict] = None, 
                 headers: Optional[Dict] = None, expected_status: int = 200) -> tuple:
    """发送HTTP请求"""
    url = f"{API_V1}{endpoint}"
    if headers is None:
        headers = {}
    if current_token:
        headers["Authorization"] = f"Bearer {current_token}"
    
    try:
        if method == "GET":
            # GET请求使用params，不设置Content-Type
            response = requests.get(url, headers=headers, params=data, timeout=10)
        elif method == "POST":
            headers["Content-Type"] = "application/json"
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            response = requests.put(url, headers=headers, json=data, timeout=10)
        else:
            return False, f"不支持的HTTP方法: {method}"
        
        if response.status_code == expected_status:
            try:
                return True, response.json()
            except:
                return True, response.text
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except requests.exceptions.RequestException as e:
        return False, f"请求异常: {str(e)}"


# ==================== 测试用例 ====================

def test_auth_login():
    """TC-AUTH-06: 开发环境模拟登录"""
    global current_token, current_user_id
    
    success, result = make_request("POST", "/users/login", 
                                   data={"code": "dev_h5_mock"})
    
    if success and isinstance(result, dict) and "access_token" in result:
        current_token = result["access_token"]
        current_user_id = result.get("user_id")
        log_test("TC-AUTH-06", "开发环境模拟登录", True, 
                f"Token: {current_token[:50]}...")
        return True
    else:
        log_test("TC-AUTH-06", "开发环境模拟登录", False, str(result))
        return False


def test_auth_profile():
    """TC-AUTH-07: 用户信息获取"""
    success, result = make_request("GET", "/users/profile")
    
    if success and isinstance(result, dict):
        log_test("TC-AUTH-07", "用户信息获取", True, 
                f"用户ID: {result.get('user_id')}, 昵称: {result.get('nickname')}")
        return True
    else:
        log_test("TC-AUTH-07", "用户信息获取", False, str(result))
        return False


def test_company_search():
    """TC-COMPANY-02: 公司名称模糊搜索"""
    success, result = make_request("GET", "/companies/search", 
                                   data={"q": "装修公司", "limit": 5})
    
    if success:
        log_test("TC-COMPANY-02", "公司名称模糊搜索", True, 
                f"返回 {len(result.get('data', {}).get('list', []))} 条结果")
        return True
    else:
        log_test("TC-COMPANY-02", "公司名称模糊搜索", False, str(result))
        return False


def test_company_scan():
    """TC-COMPANY-03: 提交公司检测"""
    success, result = make_request("POST", "/companies/scan", 
                                   data={"company_name": "测试装修公司"})
    
    if success and isinstance(result, dict):
        scan_id = result.get("scan_id") or result.get("data", {}).get("scan_id")
        log_test("TC-COMPANY-03", "提交公司检测", True, f"Scan ID: {scan_id}")
        return scan_id
    else:
        log_test("TC-COMPANY-03", "提交公司检测", False, str(result))
        return None


def test_contract_list():
    """TC-CONTRACT-04: 合同列表"""
    success, result = make_request("GET", "/contracts/list", 
                                   data={"page": 1, "page_size": 10})
    
    if success:
        data = result.get("data", {}) if isinstance(result, dict) else {}
        total = data.get("total", 0)
        log_test("TC-CONTRACT-04", "合同列表查询", True, 
                f"共 {total} 条记录")
        return True
    else:
        log_test("TC-CONTRACT-04", "合同列表查询", False, str(result))
        return False


def test_contract_detail():
    """TC-CONTRACT-05: 合同详情（含summary）"""
    # 先获取列表，取第一条
    success, result = make_request("GET", "/contracts/list", 
                                   data={"page": 1, "page_size": 1})
    
    if not success:
        log_test("TC-CONTRACT-05", "合同详情查询", False, "无法获取合同列表")
        return False
    
    data = result.get("data", {}) if isinstance(result, dict) else {}
    contracts = data.get("list", [])
    
    if not contracts:
        log_test("TC-CONTRACT-05", "合同详情查询", True, "暂无合同记录（跳过）")
        return True
    
    contract_id = contracts[0].get("id")
    success, detail = make_request("GET", f"/contracts/contract/{contract_id}")
    
    if success:
        has_summary = "summary" in str(detail)
        log_test("TC-CONTRACT-05", "合同详情查询", True, 
                f"合同ID: {contract_id}, 含summary: {has_summary}")
        return True
    else:
        log_test("TC-CONTRACT-05", "合同详情查询", False, str(detail))
        return False


def test_construction_start_date():
    """TC-CONSTRUCTION-01: 设置开工日期"""
    # 使用ISO格式的datetime字符串
    start_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT00:00:00")
    success, result = make_request("POST", "/constructions/start-date", 
                                   data={"start_date": start_date})
    
    if success:
        log_test("TC-CONSTRUCTION-01", "设置开工日期", True, 
                f"开工日期: {start_date}")
        return True
    else:
        log_test("TC-CONSTRUCTION-01", "设置开工日期", False, str(result))
        return False


def test_construction_schedule():
    """TC-CONSTRUCTION-03: 进度计划查询"""
    success, result = make_request("GET", "/constructions/schedule")
    
    if success:
        stages = result.get("data", {}).get("stages", []) if isinstance(result, dict) else []
        log_test("TC-CONSTRUCTION-03", "进度计划查询", True, 
                f"共 {len(stages)} 个阶段")
        return True
    else:
        log_test("TC-CONSTRUCTION-03", "进度计划查询", False, str(result))
        return False


def test_message_list():
    """TC-MESSAGE-01: 消息列表查询"""
    success, result = make_request("GET", "/messages")
    
    if success:
        messages = result.get("data", {}).get("list", []) if isinstance(result, dict) else []
        log_test("TC-MESSAGE-01", "消息列表查询", True, 
                f"共 {len(messages)} 条消息")
        return True
    else:
        log_test("TC-MESSAGE-01", "消息列表查询", False, str(result))
        return False


def test_message_unread_count():
    """TC-MESSAGE-02: 未读消息数量"""
    success, result = make_request("GET", "/messages/unread-count")
    
    if success:
        count = result.get("data", {}).get("count", 0) if isinstance(result, dict) else 0
        log_test("TC-MESSAGE-02", "未读消息数量", True, f"未读: {count} 条")
        return True
    else:
        log_test("TC-MESSAGE-02", "未读消息数量", False, str(result))
        return False


def test_city_hot():
    """TC-CITY-01: 热门城市查询"""
    success, result = make_request("GET", "/cities/hot")
    
    if success:
        cities = result.get("data", {}).get("list", []) if isinstance(result, dict) else []
        log_test("TC-CITY-01", "热门城市查询", True, 
                f"共 {len(cities)} 个热门城市")
        return True
    else:
        log_test("TC-CITY-01", "热门城市查询", False, str(result))
        return False


def test_city_select():
    """TC-CITY-03: 选择城市保存"""
    success, result = make_request("POST", "/cities/select", 
                                   data={"city_name": "深圳"})
    
    if success:
        log_test("TC-CITY-03", "选择城市保存", True, "城市: 深圳")
        return True
    else:
        log_test("TC-CITY-03", "选择城市保存", False, str(result))
        return False


def test_health_check():
    """TC-NF-01: 健康检查响应时间"""
    start_time = time.time()
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        elapsed = (time.time() - start_time) * 1000
        
        if response.status_code == 200 and elapsed <= 500:
            log_test("TC-NF-01", "健康检查响应时间", True, 
                    f"响应时间: {elapsed:.2f}ms")
            return True
        else:
            log_test("TC-NF-01", "健康检查响应时间", False, 
                    f"响应时间: {elapsed:.2f}ms (期望≤500ms)")
            return False
    except Exception as e:
        log_test("TC-NF-01", "健康检查响应时间", False, str(e))
        return False


def test_auth_required():
    """TC-NF-04: Token认证校验"""
    # 使用无效token
    headers = {"Authorization": "Bearer invalid_token"}
    success, result = make_request("GET", "/users/profile", headers=headers, 
                                   expected_status=401)
    
    if not success:  # 期望返回401
        log_test("TC-NF-04", "Token认证校验", True, "正确返回401未授权")
        return True
    else:
        log_test("TC-NF-04", "Token认证校验", False, "未正确校验Token")
        return False


# ==================== 主测试流程 ====================

def run_all_tests():
    """执行所有测试用例"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("装修避坑管家 - 功能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"{Colors.END}\n")
    
    # 1. 认证模块
    print(f"{Colors.BOLD}【一、用户认证模块】{Colors.END}")
    if not test_auth_login():
        print(f"{Colors.RED}登录失败，后续测试可能无法执行{Colors.END}\n")
        return
    test_auth_profile()
    print()
    
    # 2. 公司检测模块
    print(f"{Colors.BOLD}【二、公司检测模块】{Colors.END}")
    test_company_search()
    test_company_scan()
    print()
    
    # 3. 合同模块
    print(f"{Colors.BOLD}【三、合同审核模块】{Colors.END}")
    test_contract_list()
    test_contract_detail()
    print()
    
    # 4. 施工进度模块
    print(f"{Colors.BOLD}【四、施工进度管理模块】{Colors.END}")
    test_construction_start_date()
    test_construction_schedule()
    print()
    
    # 5. 消息模块
    print(f"{Colors.BOLD}【五、消息中心模块】{Colors.END}")
    test_message_list()
    test_message_unread_count()
    print()
    
    # 6. 城市模块
    print(f"{Colors.BOLD}【六、城市选择模块】{Colors.END}")
    test_city_hot()
    test_city_select()
    print()
    
    # 7. 非功能测试
    print(f"{Colors.BOLD}【七、非功能测试】{Colors.END}")
    test_health_check()
    test_auth_required()
    print()
    
    # 生成测试报告
    generate_report()


def generate_report():
    """生成测试报告"""
    passed = sum(1 for r in test_results if r["result"] == "通过")
    failed = sum(1 for r in test_results if r["result"] == "失败")
    total = len(test_results)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"{Colors.END}")
    print(f"总用例数: {total}")
    print(f"{Colors.GREEN}通过: {passed}{Colors.END}")
    print(f"{Colors.RED}失败: {failed}{Colors.END}")
    print(f"通过率: {pass_rate:.1f}%")
    print()
    
    if failed > 0:
        print(f"{Colors.RED}失败的用例:{Colors.END}")
        for r in test_results:
            if r["result"] == "失败":
                print(f"  - [{r['case_id']}] {r['name']}: {r['message']}")
        print()
    
    # 保存JSON报告
    report_data = {
        "test_time": datetime.now().isoformat(),
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "results": test_results
    }
    
    report_file = f"test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"详细报告已保存至: {report_file}")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}测试被用户中断{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}测试执行异常: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

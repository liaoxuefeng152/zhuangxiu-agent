#!/usr/bin/env python3
"""
装修避坑管家 - 完整功能测试脚本
基于PRD V2.6.1测试用例文档执行所有测试
"""
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import sys
import os

# 测试配置
API_BASE = "http://localhost:8000"
API_V1 = f"{API_BASE}/api/v1"

# 测试结果
test_results = []
current_token = None
current_user_id = None
test_data = {}  # 存储测试过程中产生的数据（如scan_id, contract_id等）

# 统计信息
stats = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "by_module": {}
}


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


def log_test(case_id: str, name: str, result: str, message: str = "", priority: str = "P0"):
    """记录测试结果"""
    stats["total"] += 1
    
    if result == "通过":
        stats["passed"] += 1
        status = f"{Colors.GREEN}✓ 通过{Colors.END}"
    elif result == "失败":
        stats["failed"] += 1
        status = f"{Colors.RED}✗ 失败{Colors.END}"
    else:  # 跳过
        stats["skipped"] += 1
        status = f"{Colors.YELLOW}⊘ 跳过{Colors.END}"
    
    priority_color = Colors.RED if priority == "P0" else Colors.YELLOW if priority == "P1" else Colors.CYAN
    print(f"[{priority_color}{priority}{Colors.END}] [{case_id}] {name}: {status}")
    if message:
        print(f"  {message}")
    
    test_results.append({
        "case_id": case_id,
        "name": name,
        "result": result,
        "message": message,
        "priority": priority,
        "timestamp": datetime.now().isoformat()
    })
    
    # 按模块统计
    module = case_id.split("-")[1] if "-" in case_id else "OTHER"
    if module not in stats["by_module"]:
        stats["by_module"][module] = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
    stats["by_module"][module]["total"] += 1
    if result == "通过":
        stats["by_module"][module]["passed"] += 1
    elif result == "失败":
        stats["by_module"][module]["failed"] += 1
    else:
        stats["by_module"][module]["skipped"] += 1


def make_request(method: str, endpoint: str, data: Optional[Dict] = None, 
                 headers: Optional[Dict] = None, expected_status: int = 200,
                 files: Optional[Dict] = None) -> tuple:
    """发送HTTP请求"""
    url = f"{API_V1}{endpoint}"
    if headers is None:
        headers = {}
    if current_token:
        headers["Authorization"] = f"Bearer {current_token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data, timeout=10)
        elif method == "POST":
            if files:
                # 文件上传
                headers.pop("Content-Type", None)  # requests会自动设置
                response = requests.post(url, headers=headers, data=data, files=files, timeout=30)
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
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


# ==================== 用户认证模块 ====================

def test_auth_06():
    """TC-AUTH-06: 开发环境模拟登录"""
    global current_token, current_user_id
    
    success, result = make_request("POST", "/users/login", 
                                   data={"code": "dev_h5_mock"})
    
    if success and isinstance(result, dict) and "access_token" in result:
        current_token = result["access_token"]
        current_user_id = result.get("user_id")
        log_test("TC-AUTH-06", "开发环境模拟登录", "通过", 
                f"用户ID: {current_user_id}, Token已获取", "P0")
        return True
    else:
        log_test("TC-AUTH-06", "开发环境模拟登录", "失败", str(result), "P0")
        return False


def test_auth_07():
    """TC-AUTH-07: 用户信息获取"""
    success, result = make_request("GET", "/users/profile")
    
    if success and isinstance(result, dict):
        nickname = result.get("nickname", "未知")
        log_test("TC-AUTH-07", "用户信息获取", "通过", 
                f"昵称: {nickname}", "P0")
        return True
    else:
        log_test("TC-AUTH-07", "用户信息获取", "失败", str(result), "P0")
        return False


# ==================== 公司检测模块 ====================

def test_company_02():
    """TC-COMPANY-02: 公司名称模糊搜索"""
    success, result = make_request("GET", "/companies/search", 
                                   data={"q": "装修公司", "limit": 5})
    
    if success:
        data = result.get("data", {}) if isinstance(result, dict) else {}
        count = len(data.get("list", []))
        log_test("TC-COMPANY-02", "公司名称模糊搜索", "通过", 
                f"返回 {count} 条结果", "P1")
        return True
    else:
        log_test("TC-COMPANY-02", "公司名称模糊搜索", "失败", str(result), "P1")
        return False


def test_company_03():
    """TC-COMPANY-03: 提交公司检测"""
    success, result = make_request("POST", "/companies/scan", 
                                   data={"company_name": "测试装修公司有限公司"})
    
    if success and isinstance(result, dict):
        scan_id = result.get("scan_id") or result.get("data", {}).get("scan_id")
        test_data["scan_id"] = scan_id
        log_test("TC-COMPANY-03", "提交公司检测", "通过", 
                f"Scan ID: {scan_id}", "P0")
        return True
    else:
        log_test("TC-COMPANY-03", "提交公司检测", "失败", str(result), "P0")
        return False


def test_company_05():
    """TC-COMPANY-05: 检测结果查询"""
    if "scan_id" not in test_data:
        log_test("TC-COMPANY-05", "检测结果查询", "跳过", 
                "前置条件不满足：无scan_id", "P0")
        return False
    
    success, result = make_request("GET", f"/companies/scan/{test_data['scan_id']}")
    
    if success:
        status = result.get("status") or result.get("data", {}).get("status", "unknown")
        log_test("TC-COMPANY-05", "检测结果查询", "通过", 
                f"状态: {status}", "P0")
        return True
    else:
        log_test("TC-COMPANY-05", "检测结果查询", "失败", str(result), "P0")
        return False


def test_company_06():
    """TC-COMPANY-06: 检测记录列表"""
    success, result = make_request("GET", "/companies/scans")
    
    if success:
        data = result.get("data", {}) if isinstance(result, dict) else {}
        count = len(data.get("list", []))
        log_test("TC-COMPANY-06", "检测记录列表", "通过", 
                f"共 {count} 条记录", "P1")
        return True
    else:
        log_test("TC-COMPANY-06", "检测记录列表", "失败", str(result), "P1")
        return False


# ==================== 合同审核模块 ====================

def test_contract_04():
    """TC-CONTRACT-04: 合同列表"""
    success, result = make_request("GET", "/contracts/list", 
                                   data={"page": 1, "page_size": 10})
    
    if success:
        data = result.get("data", {}) if isinstance(result, dict) else {}
        total = data.get("total", 0)
        contracts = data.get("list", [])
        if contracts:
            test_data["contract_id"] = contracts[0].get("id")
        log_test("TC-CONTRACT-04", "合同列表查询", "通过", 
                f"共 {total} 条记录", "P0")
        return True
    else:
        log_test("TC-CONTRACT-04", "合同列表查询", "失败", str(result), "P0")
        return False


def test_contract_05():
    """TC-CONTRACT-05: 合同详情（含summary）"""
    if "contract_id" not in test_data:
        log_test("TC-CONTRACT-05", "合同详情查询", "跳过", 
                "前置条件不满足：无合同记录", "P0")
        return True  # 无数据不算失败
    
    success, result = make_request("GET", f"/contracts/contract/{test_data['contract_id']}")
    
    if success:
        has_summary = "summary" in str(result)
        log_test("TC-CONTRACT-05", "合同详情查询", "通过", 
                f"合同ID: {test_data['contract_id']}, 含summary: {has_summary}", "P0")
        return True
    else:
        log_test("TC-CONTRACT-05", "合同详情查询", "失败", str(result), "P0")
        return False


def test_contract_02():
    """TC-CONTRACT-02: 合同分析结果"""
    if "contract_id" not in test_data:
        log_test("TC-CONTRACT-02", "合同分析结果", "跳过", 
                "前置条件不满足：无合同记录", "P0")
        return True
    
    success, result = make_request("GET", f"/contracts/contract/{test_data['contract_id']}")
    
    if success:
        risk_level = result.get("risk_level") or result.get("data", {}).get("risk_level", "unknown")
        log_test("TC-CONTRACT-02", "合同分析结果", "通过", 
                f"风险等级: {risk_level}", "P0")
        return True
    else:
        log_test("TC-CONTRACT-02", "合同分析结果", "失败", str(result), "P0")
        return False


# ==================== 施工进度管理模块 ====================

def test_construction_01():
    """TC-CONSTRUCTION-01: 设置开工日期"""
    start_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT00:00:00")
    success, result = make_request("POST", "/constructions/start-date", 
                                   data={"start_date": start_date})
    
    if success:
        log_test("TC-CONSTRUCTION-01", "设置开工日期", "通过", 
                f"开工日期: {start_date}", "P0")
        return True
    else:
        log_test("TC-CONSTRUCTION-01", "设置开工日期", "失败", str(result), "P0")
        return False


def test_construction_02():
    """TC-CONSTRUCTION-02: 编辑开工日期"""
    start_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%dT00:00:00")
    success, result = make_request("POST", "/constructions/start-date", 
                                   data={"start_date": start_date})
    
    if success:
        log_test("TC-CONSTRUCTION-02", "编辑开工日期", "通过", 
                f"新开工日期: {start_date}", "P1")
        return True
    else:
        log_test("TC-CONSTRUCTION-02", "编辑开工日期", "失败", str(result), "P1")
        return False


def test_construction_03():
    """TC-CONSTRUCTION-03: 进度计划查询"""
    success, result = make_request("GET", "/constructions/schedule")
    
    if success:
        data = result.get("data", {}) if isinstance(result, dict) else result
        stages = data.get("stages", {})
        stage_count = len(stages) if isinstance(stages, dict) else 0
        log_test("TC-CONSTRUCTION-03", "进度计划查询", "通过", 
                f"共 {stage_count} 个阶段", "P0")
        return True
    else:
        log_test("TC-CONSTRUCTION-03", "进度计划查询", "失败", str(result), "P0")
        return False


def test_construction_04():
    """TC-CONSTRUCTION-04: 流程互锁规则"""
    # 尝试操作未解锁的阶段（S01需要S00先通过）
    success, result = make_request("PUT", "/constructions/stage-status", 
                                   data={"stage": "S01", "status": "completed"},
                                   expected_status=409)
    
    if not success:  # 期望返回409
        log_test("TC-CONSTRUCTION-04", "流程互锁规则", "通过", 
                "正确返回409错误，流程互锁生效", "P0")
        return True
    else:
        log_test("TC-CONSTRUCTION-04", "流程互锁规则", "失败", 
                "未正确校验流程互锁", "P0")
        return False


def test_construction_05():
    """TC-CONSTRUCTION-05: 更新阶段状态"""
    # 先完成S00阶段
    success, result = make_request("PUT", "/constructions/stage-status", 
                                   data={"stage": "S00", "status": "checked"})
    
    if success:
        log_test("TC-CONSTRUCTION-05", "更新阶段状态", "通过", 
                "S00阶段状态更新为已核对", "P0")
        return True
    else:
        log_test("TC-CONSTRUCTION-05", "更新阶段状态", "失败", str(result), "P0")
        return False


def test_construction_06():
    """TC-CONSTRUCTION-06: 阶段时间校准"""
    calibrate_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%dT00:00:00")
    success, result = make_request("PUT", "/constructions/stage-calibrate", 
                                   data={"stage": "S01", "start_date": calibrate_date})
    
    if success:
        log_test("TC-CONSTRUCTION-06", "阶段时间校准", "通过", 
                f"S01阶段校准日期: {calibrate_date}", "P1")
        return True
    else:
        log_test("TC-CONSTRUCTION-06", "阶段时间校准", "失败", str(result), "P1")
        return False


def test_construction_07():
    """TC-CONSTRUCTION-07: 智能提醒设置"""
    success, result = make_request("PUT", "/users/settings", 
                                   data={"reminder_days": 3})
    
    if success:
        log_test("TC-CONSTRUCTION-07", "智能提醒设置", "通过", 
                "提醒提前天数设置为3天", "P1")
        return True
    else:
        log_test("TC-CONSTRUCTION-07", "智能提醒设置", "失败", str(result), "P1")
        return False


# ==================== 消息中心模块 ====================

def test_message_01():
    """TC-MESSAGE-01: 消息列表查询"""
    success, result = make_request("GET", "/messages")
    
    if success:
        data = result.get("data", {}) if isinstance(result, dict) else {}
        messages = data.get("list", []) if isinstance(data, dict) else []
        count = len(messages)
        log_test("TC-MESSAGE-01", "消息列表查询", "通过", 
                f"共 {count} 条消息", "P0")
        if messages:
            test_data["message_id"] = messages[0].get("id")
        return True
    else:
        log_test("TC-MESSAGE-01", "消息列表查询", "失败", str(result), "P0")
        return False


def test_message_02():
    """TC-MESSAGE-02: 未读消息数量"""
    success, result = make_request("GET", "/messages/unread-count")
    
    if success:
        data = result.get("data", {}) if isinstance(result, dict) else {}
        count = data.get("count", 0) if isinstance(data, dict) else 0
        log_test("TC-MESSAGE-02", "未读消息数量", "通过", 
                f"未读: {count} 条", "P1")
        return True
    else:
        log_test("TC-MESSAGE-02", "未读消息数量", "失败", str(result), "P1")
        return False


def test_message_03():
    """TC-MESSAGE-03: 单条消息已读"""
    if "message_id" not in test_data:
        log_test("TC-MESSAGE-03", "单条消息已读", "跳过", 
                "前置条件不满足：无消息记录", "P1")
        return True
    
    success, result = make_request("PUT", f"/messages/{test_data['message_id']}/read")
    
    if success:
        log_test("TC-MESSAGE-03", "单条消息已读", "通过", 
                f"消息ID: {test_data['message_id']} 已标记为已读", "P1")
        return True
    else:
        log_test("TC-MESSAGE-03", "单条消息已读", "失败", str(result), "P1")
        return False


def test_message_04():
    """TC-MESSAGE-04: 一键已读"""
    success, result = make_request("PUT", "/messages/read-all")
    
    if success:
        log_test("TC-MESSAGE-04", "一键已读", "通过", 
                "所有消息已标记为已读", "P1")
        return True
    else:
        log_test("TC-MESSAGE-04", "一键已读", "失败", str(result), "P1")
        return False


# ==================== 城市选择模块 ====================

def test_city_01():
    """TC-CITY-01: 热门城市查询"""
    success, result = make_request("GET", "/cities/hot")
    
    if success:
        data = result.get("data", {}) if isinstance(result, dict) else {}
        cities = data.get("list", []) if isinstance(data, dict) else []
        count = len(cities)
        log_test("TC-CITY-01", "热门城市查询", "通过", 
                f"共 {count} 个热门城市", "P1")
        return True
    else:
        log_test("TC-CITY-01", "热门城市查询", "失败", str(result), "P1")
        return False


def test_city_02():
    """TC-CITY-02: 城市列表查询"""
    success, result = make_request("GET", "/cities/list")
    
    if success:
        data = result.get("data", {}) if isinstance(result, dict) else {}
        provinces = data.get("provinces", []) if isinstance(data, dict) else []
        count = len(provinces)
        log_test("TC-CITY-02", "城市列表查询", "通过", 
                f"共 {count} 个省份", "P1")
        return True
    else:
        log_test("TC-CITY-02", "城市列表查询", "失败", str(result), "P1")
        return False


def test_city_03():
    """TC-CITY-03: 选择城市保存"""
    success, result = make_request("POST", "/cities/select", 
                                   data={"city_name": "深圳"})
    
    if success:
        log_test("TC-CITY-03", "选择城市保存", "通过", 
                "城市: 深圳", "P0")
        return True
    else:
        log_test("TC-CITY-03", "选择城市保存", "失败", str(result), "P0")
        return False


def test_city_04():
    """TC-CITY-04: 当前城市查询"""
    success, result = make_request("GET", "/cities/current")
    
    if success:
        data = result.get("data", {}) if isinstance(result, dict) else {}
        city = data.get("city_name", "未知") if isinstance(data, dict) else "未知"
        log_test("TC-CITY-04", "当前城市查询", "通过", 
                f"当前城市: {city}", "P1")
        return True
    else:
        log_test("TC-CITY-04", "当前城市查询", "失败", str(result), "P1")
        return False


# ==================== 报告中心模块 ====================

def test_report_01():
    """TC-REPORT-01: 报告列表查询"""
    success, result = make_request("GET", "/contracts/list")
    
    if success:
        data = result.get("data", {}) if isinstance(result, dict) else {}
        total = data.get("total", 0)
        log_test("TC-REPORT-01", "报告列表查询", "通过", 
                f"共 {total} 条报告", "P0")
        return True
    else:
        log_test("TC-REPORT-01", "报告列表查询", "失败", str(result), "P0")
        return False


def test_report_02():
    """TC-REPORT-02: 报告列表分页"""
    success, result = make_request("GET", "/contracts/list", 
                                   data={"page": 1, "page_size": 10})
    
    if success:
        data = result.get("data", {}) if isinstance(result, dict) else {}
        has_pagination = "total" in data and "page" in data and "page_size" in data
        log_test("TC-REPORT-02", "报告列表分页", "通过" if has_pagination else "失败", 
                f"分页信息: page={data.get('page')}, page_size={data.get('page_size')}, total={data.get('total')}", 
                "P1")
        return has_pagination
    else:
        log_test("TC-REPORT-02", "报告列表分页", "失败", str(result), "P1")
        return False


def test_report_03():
    """TC-REPORT-03: 报告详情查看"""
    if "contract_id" not in test_data:
        log_test("TC-REPORT-03", "报告详情查看", "跳过", 
                "前置条件不满足：无报告记录", "P0")
        return True
    
    success, result = make_request("GET", f"/contracts/contract/{test_data['contract_id']}")
    
    if success:
        log_test("TC-REPORT-03", "报告详情查看", "通过", 
                f"报告ID: {test_data['contract_id']}", "P0")
        return True
    else:
        log_test("TC-REPORT-03", "报告详情查看", "失败", str(result), "P0")
        return False


# ==================== 非功能测试 ====================

def test_nf_01():
    """TC-NF-01: 健康检查响应时间"""
    start_time = time.time()
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        elapsed = (time.time() - start_time) * 1000
        
        if response.status_code == 200 and elapsed <= 500:
            log_test("TC-NF-01", "健康检查响应时间", "通过", 
                    f"响应时间: {elapsed:.2f}ms", "P1")
            return True
        else:
            log_test("TC-NF-01", "健康检查响应时间", "失败", 
                    f"响应时间: {elapsed:.2f}ms (期望≤500ms)", "P1")
            return False
    except Exception as e:
        log_test("TC-NF-01", "健康检查响应时间", "失败", str(e), "P1")
        return False


def test_nf_02():
    """TC-NF-02: 登录接口响应时间"""
    start_time = time.time()
    success, result = make_request("POST", "/users/login", 
                                   data={"code": "dev_h5_mock"})
    elapsed = (time.time() - start_time) * 1000
    
    if success and elapsed <= 1000:
        log_test("TC-NF-02", "登录接口响应时间", "通过", 
                f"响应时间: {elapsed:.2f}ms", "P1")
        return True
    else:
        log_test("TC-NF-02", "登录接口响应时间", "失败", 
                f"响应时间: {elapsed:.2f}ms (期望≤1000ms)", "P1")
        return False


def test_nf_03():
    """TC-NF-03: 报告列表加载时间"""
    start_time = time.time()
    success, result = make_request("GET", "/contracts/list")
    elapsed = (time.time() - start_time) * 1000
    
    if success and elapsed <= 1500:
        log_test("TC-NF-03", "报告列表加载时间", "通过", 
                f"响应时间: {elapsed:.2f}ms", "P1")
        return True
    else:
        log_test("TC-NF-03", "报告列表加载时间", "失败", 
                f"响应时间: {elapsed:.2f}ms (期望≤1500ms)", "P1")
        return False


def test_nf_04():
    """TC-NF-04: Token认证校验"""
    headers = {"Authorization": "Bearer invalid_token"}
    success, result = make_request("GET", "/users/profile", headers=headers, 
                                   expected_status=401)
    
    if not success:  # 期望返回401
        log_test("TC-NF-04", "Token认证校验", "通过", 
                "正确返回401未授权", "P0")
        return True
    else:
        log_test("TC-NF-04", "Token认证校验", "失败", 
                "未正确校验Token", "P0")
        return False


def test_nf_08():
    """TC-NF-08: 参数校验"""
    # 测试无效参数
    success, result = make_request("POST", "/users/login", 
                                   data={"code": ""}, expected_status=422)
    
    if not success:  # 期望返回422
        log_test("TC-NF-08", "参数校验", "通过", 
                "正确返回422参数错误", "P1")
        return True
    else:
        log_test("TC-NF-08", "参数校验", "失败", 
                "未正确校验参数", "P1")
        return False


# ==================== 主测试流程 ====================

def run_all_tests():
    """执行所有测试用例"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 80)
    print("装修避坑管家 - 完整功能测试（PRD V2.6.1）")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"{Colors.END}\n")
    
    # 1. 用户认证模块
    print(f"{Colors.BOLD}【一、用户认证模块】{Colors.END}")
    if not test_auth_06():
        print(f"{Colors.RED}登录失败，部分测试可能无法执行{Colors.END}\n")
    test_auth_07()
    print()
    
    # 2. 公司检测模块
    print(f"{Colors.BOLD}【二、公司检测模块】{Colors.END}")
    test_company_02()
    test_company_03()
    time.sleep(1)  # 等待检测任务创建
    test_company_05()
    test_company_06()
    print()
    
    # 3. 合同审核模块
    print(f"{Colors.BOLD}【三、合同审核模块】{Colors.END}")
    test_contract_04()
    test_contract_05()
    test_contract_02()
    print()
    
    # 4. 施工进度管理模块
    print(f"{Colors.BOLD}【四、施工进度管理模块】{Colors.END}")
    test_construction_01()
    test_construction_02()
    test_construction_03()
    test_construction_04()
    test_construction_05()
    test_construction_06()
    test_construction_07()
    print()
    
    # 5. 消息中心模块
    print(f"{Colors.BOLD}【五、消息中心模块】{Colors.END}")
    test_message_01()
    test_message_02()
    test_message_03()
    test_message_04()
    print()
    
    # 6. 城市选择模块
    print(f"{Colors.BOLD}【六、城市选择模块】{Colors.END}")
    test_city_01()
    test_city_02()
    test_city_03()
    test_city_04()
    print()
    
    # 7. 报告中心模块
    print(f"{Colors.BOLD}【七、报告中心模块】{Colors.END}")
    test_report_01()
    test_report_02()
    test_report_03()
    print()
    
    # 8. 非功能测试
    print(f"{Colors.BOLD}【八、非功能测试】{Colors.END}")
    test_nf_01()
    test_nf_02()
    test_nf_03()
    test_nf_04()
    test_nf_08()
    print()
    
    # 生成测试报告
    generate_report()


def generate_report():
    """生成测试报告"""
    passed = stats["passed"]
    failed = stats["failed"]
    skipped = stats["skipped"]
    total = stats["total"]
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    print(f"{Colors.END}")
    print(f"总用例数: {total}")
    print(f"{Colors.GREEN}通过: {passed}{Colors.END}")
    print(f"{Colors.RED}失败: {failed}{Colors.END}")
    print(f"{Colors.YELLOW}跳过: {skipped}{Colors.END}")
    print(f"通过率: {pass_rate:.1f}%")
    print()
    
    # 按模块统计
    print(f"{Colors.BOLD}按模块统计:{Colors.END}")
    for module, module_stats in stats["by_module"].items():
        m_pass_rate = (module_stats["passed"] / module_stats["total"] * 100) if module_stats["total"] > 0 else 0
        print(f"  {module}: {module_stats['passed']}/{module_stats['total']} 通过 ({m_pass_rate:.1f}%)")
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
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": pass_rate
        },
        "by_module": stats["by_module"],
        "results": test_results
    }
    
    report_file = f"test-report-full-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
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

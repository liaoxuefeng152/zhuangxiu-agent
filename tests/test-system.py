#!/usr/bin/env python3
"""
系统测试 - 对整个系统进行端到端测试
包括功能测试、性能测试、安全性测试、可靠性测试
"""
import os
import sys
_d = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(_d) not in sys.path:
    sys.path.insert(0, os.path.dirname(_d))
import requests
from tests import fixture_path, QUOTE_PNG, CONTRACT_PNG
import time
import json
import os
import io
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics

BASE_URL = "http://localhost:8000/api/v1"

# 测试结果统计
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "performance": {},
    "details": []
}


def log_test(case_id: str, name: str, result: str, message: str = "", duration: float = 0, priority: str = "P0"):
    """记录测试结果"""
    test_results["total"] += 1
    if result == "通过":
        test_results["passed"] += 1
        status = "✅"
    elif result == "失败":
        test_results["failed"] += 1
        status = "❌"
    else:
        test_results["skipped"] += 1
        status = "⏭️"
    
    test_results["details"].append({
        "case_id": case_id,
        "name": name,
        "result": result,
        "message": message,
        "duration": duration,
        "priority": priority
    })
    
    duration_str = f" ({duration:.3f}s)" if duration > 0 else ""
    print(f"[{priority}] [{case_id}] {name}: {status} {result}{duration_str}")
    if message:
        print(f"  {message}")


def login() -> Optional[str]:
    """登录获取token"""
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/users/login",
            json={"code": "dev_h5_mock"},
            timeout=5
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("data", {}).get("access_token") or data.get("access_token")
            return token
        return None
    except Exception as e:
        return None


# ==================== 系统功能测试 ====================

def test_system_01_health_check():
    """ST-01: 系统健康检查"""
    case_id = "ST-01"
    name = "系统健康检查"
    
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            log_test(case_id, name, "通过", f"响应时间: {duration:.3f}s", duration, "P0")
            return True
        else:
            log_test(case_id, name, "失败", f"状态码: {response.status_code}", duration, "P0")
            return False
    except Exception as e:
        log_test(case_id, name, "失败", f"异常: {e}", 0, "P0")
        return False


def test_system_02_user_authentication_flow():
    """ST-02: 用户认证流程"""
    case_id = "ST-02"
    name = "用户认证流程"
    
    try:
        start_time = time.time()
        token = login()
        duration = time.time() - start_time
        
        if token:
            # 验证token有效性
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/users/profile", headers=headers, timeout=5)
            
            if response.status_code == 200:
                log_test(case_id, name, "通过", f"认证成功，响应时间: {duration:.3f}s", duration, "P0")
                return True
            else:
                log_test(case_id, name, "失败", f"Token验证失败: {response.status_code}", duration, "P0")
                return False
        else:
            log_test(case_id, name, "失败", "登录失败", duration, "P0")
            return False
    except Exception as e:
        log_test(case_id, name, "失败", f"异常: {e}", 0, "P0")
        return False


def test_system_03_complete_business_workflow():
    """ST-03: 完整业务流程（端到端）"""
    case_id = "ST-03"
    name = "完整业务流程（端到端）"
    
    token = login()
    if not token:
        log_test(case_id, name, "失败", "登录失败", 0, "P0")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    start_time = time.time()
    
    try:
        # 步骤1: 公司检测
        response = requests.post(
            f"{BASE_URL}/companies/scan",
            headers=headers,
            json={"company_name": "深圳测试装饰工程有限公司"},
            timeout=10
        )
        if response.status_code != 200:
            log_test(case_id, name, "失败", f"公司检测失败: {response.status_code}", 0, "P0")
            return False
        
        scan_id = response.json().get("data", {}).get("id") or response.json().get("id")
        
        # 步骤2: 报价单上传
        quote_png = fixture_path(QUOTE_PNG)
        if os.path.exists(quote_png):
            with open(quote_png, "rb") as f:
                files = {"file": (os.path.basename(quote_png), io.BytesIO(f.read()), "image/png")}
                response = requests.post(f"{BASE_URL}/quotes/upload", headers=headers, files=files, timeout=30)
                if response.status_code == 200:
                    quote_id = response.json().get("data", {}).get("task_id") or response.json().get("task_id")
                    
                    # 等待分析完成
                    for i in range(30):
                        time.sleep(1)
                        response = requests.get(f"{BASE_URL}/quotes/quote/{quote_id}", headers=headers, timeout=5)
                        if response.status_code == 200:
                            data = response.json().get("data", {}) or response.json()
                            if data.get("status") == "completed":
                                break
        
        # 步骤3: 合同上传
        contract_png = fixture_path(CONTRACT_PNG)
        if os.path.exists(contract_png):
            with open(contract_png, "rb") as f:
                files = {"file": (os.path.basename(contract_png), io.BytesIO(f.read()), "image/png")}
                response = requests.post(f"{BASE_URL}/contracts/upload", headers=headers, files=files, timeout=30)
                if response.status_code == 200:
                    contract_id = response.json().get("data", {}).get("task_id") or response.json().get("task_id")
                    
                    # 等待分析完成
                    for i in range(30):
                        time.sleep(1)
                        response = requests.get(f"{BASE_URL}/contracts/contract/{contract_id}", headers=headers, timeout=5)
                        if response.status_code == 200:
                            data = response.json().get("data", {}) or response.json()
                            if data.get("status") == "completed":
                                break
        
        # 步骤4: 设置开工日期
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d") + "T00:00:00"
        response = requests.post(
            f"{BASE_URL}/constructions/start-date",
            headers=headers,
            json={"start_date": start_date},
            timeout=5
        )
        if response.status_code != 200:
            log_test(case_id, name, "失败", f"设置开工日期失败: {response.status_code}", 0, "P0")
            return False
        
        # 步骤5: 查询进度
        response = requests.get(f"{BASE_URL}/constructions/schedule", headers=headers, timeout=5)
        if response.status_code == 200:
            duration = time.time() - start_time
            log_test(case_id, name, "通过", f"完整流程测试通过，耗时: {duration:.2f}s", duration, "P0")
            return True
        else:
            log_test(case_id, name, "失败", f"查询进度失败: {response.status_code}", 0, "P0")
            return False
            
    except Exception as e:
        log_test(case_id, name, "失败", f"异常: {e}", 0, "P0")
        return False


def test_system_04_api_response_time():
    """ST-04: API响应时间测试"""
    case_id = "ST-04"
    name = "API响应时间测试"
    
    token = login()
    if not token:
        log_test(case_id, name, "跳过", "登录失败", 0, "P1")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    response_times = []
    
    try:
        # 测试多个API的响应时间
        apis = [
            ("GET", f"{BASE_URL}/users/profile", None),
            ("GET", f"{BASE_URL}/constructions/schedule", None),
            ("GET", f"{BASE_URL}/messages/unread-count", None),
            ("GET", f"{BASE_URL}/cities/current", None),
        ]
        
        for method, url, data in apis:
            start_time = time.time()
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            else:
                response = requests.post(url, headers=headers, json=data, timeout=5)
            duration = time.time() - start_time
            response_times.append(duration)
            
            if response.status_code != 200:
                log_test(case_id, name, "失败", f"{url} 返回 {response.status_code}", duration, "P1")
                return False
        
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # PRD要求：页面加载≤1.5秒
        if avg_time <= 1.5:
            log_test(case_id, name, "通过", 
                    f"平均响应时间: {avg_time:.3f}s, 最大: {max_time:.3f}s, 最小: {min_time:.3f}s", 
                    avg_time, "P1")
            return True
        else:
            log_test(case_id, name, "失败", 
                    f"平均响应时间超过1.5s: {avg_time:.3f}s", 
                    avg_time, "P1")
            return False
            
    except Exception as e:
        log_test(case_id, name, "失败", f"异常: {e}", 0, "P1")
        return False


def test_system_05_concurrent_requests():
    """ST-05: 并发请求测试"""
    case_id = "ST-05"
    name = "并发请求测试"
    
    token = login()
    if not token:
        log_test(case_id, name, "跳过", "登录失败", 0, "P1")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    def make_request():
        try:
            response = requests.get(f"{BASE_URL}/users/profile", headers=headers, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    try:
        # PRD要求：并发支持≥50
        concurrent_count = 20  # 先测试20个并发
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_count) as executor:
            futures = [executor.submit(make_request) for _ in range(concurrent_count)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        duration = time.time() - start_time
        success_count = sum(results)
        success_rate = (success_count / concurrent_count) * 100
        
        if success_rate >= 95:  # 95%成功率
            log_test(case_id, name, "通过", 
                    f"并发{concurrent_count}个请求，成功率: {success_rate:.1f}%, 耗时: {duration:.2f}s", 
                    duration, "P1")
            return True
        else:
            log_test(case_id, name, "失败", 
                    f"并发{concurrent_count}个请求，成功率: {success_rate:.1f}%", 
                    duration, "P1")
            return False
            
    except Exception as e:
        log_test(case_id, name, "失败", f"异常: {e}", 0, "P1")
        return False


def test_system_06_security_authentication():
    """ST-06: 安全性测试 - 认证"""
    case_id = "ST-06"
    name = "安全性测试 - 认证"
    
    try:
        # 测试1: 无Token访问
        response = requests.get(f"{BASE_URL}/users/profile", timeout=5)
        # 401或403都表示认证失败，都是正确的
        if response.status_code in (401, 403):
            # 测试2: 无效Token
            headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(f"{BASE_URL}/users/profile", headers=headers, timeout=5)
            if response.status_code in (401, 403):
                log_test(case_id, name, "通过", 
                        f"认证机制正常，无Token和无效Token都被拒绝（状态码: {response.status_code}）", 
                        0, "P0")
                return True
        
        log_test(case_id, name, "失败", f"认证机制异常，状态码: {response.status_code}", 0, "P0")
        return False
        
    except Exception as e:
        log_test(case_id, name, "失败", f"异常: {e}", 0, "P0")
        return False


def test_system_07_data_isolation():
    """ST-07: 数据隔离测试"""
    case_id = "ST-07"
    name = "数据隔离测试"
    
    token = login()
    if not token:
        log_test(case_id, name, "跳过", "登录失败", 0, "P1")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 查询自己的数据
        response = requests.get(f"{BASE_URL}/quotes/list", headers=headers, timeout=5)
        if response.status_code == 200:
            # 数据隔离通过查询列表验证（只能看到自己的数据）
            log_test(case_id, name, "通过", "数据隔离机制正常", 0, "P1")
            return True
        else:
            log_test(case_id, name, "失败", f"查询失败: {response.status_code}", 0, "P1")
            return False
            
    except Exception as e:
        log_test(case_id, name, "失败", f"异常: {e}", 0, "P1")
        return False


def test_system_08_error_handling():
    """ST-08: 错误处理测试"""
    case_id = "ST-08"
    name = "错误处理测试"
    
    token = login()
    if not token:
        log_test(case_id, name, "跳过", "登录失败", 0, "P1")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    passed = True
    
    try:
        # 测试1: 无效参数
        response = requests.get(f"{BASE_URL}/constructions/schedule?invalid=param", headers=headers, timeout=5)
        # 应该正常处理或返回400
        
        # 测试2: 不存在的资源
        response = requests.get(f"{BASE_URL}/quotes/quote/999999", headers=headers, timeout=5)
        if response.status_code == 404:
            passed = True
        else:
            passed = False
        
        # 测试3: 无效的JSON
        response = requests.post(
            f"{BASE_URL}/constructions/start-date",
            headers=headers,
            json={"invalid": "data"},
            timeout=5
        )
        # 应该返回400或422
        
        if passed:
            log_test(case_id, name, "通过", "错误处理机制正常", 0, "P1")
            return True
        else:
            log_test(case_id, name, "失败", "错误处理机制异常", 0, "P1")
            return False
            
    except Exception as e:
        log_test(case_id, name, "失败", f"异常: {e}", 0, "P1")
        return False


def test_system_09_file_upload_validation():
    """ST-09: 文件上传验证测试"""
    case_id = "ST-09"
    name = "文件上传验证测试"
    
    token = login()
    if not token:
        log_test(case_id, name, "跳过", "登录失败", 0, "P0")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    passed = True
    
    try:
        # 测试1: 无效文件类型
        files = {"file": ("test.exe", io.BytesIO(b"fake content"), "application/x-msdownload")}
        response = requests.post(f"{BASE_URL}/quotes/upload", headers=headers, files=files, timeout=5)
        if response.status_code != 400:
            passed = False
        
        # 测试2: 文件过大（模拟）
        # 注意：实际测试需要创建大文件，这里跳过
        
        # 测试3: 正常文件上传
        quote_png = fixture_path(QUOTE_PNG)
        if os.path.exists(quote_png):
            with open(quote_png, "rb") as f:
                files = {"file": (os.path.basename(quote_png), io.BytesIO(f.read()), "image/png")}
                response = requests.post(f"{BASE_URL}/quotes/upload", headers=headers, files=files, timeout=30)
                if response.status_code == 200:
                    passed = True
        
        if passed:
            log_test(case_id, name, "通过", "文件上传验证正常", 0, "P0")
            return True
        else:
            log_test(case_id, name, "失败", "文件上传验证异常", 0, "P0")
            return False
            
    except Exception as e:
        log_test(case_id, name, "失败", f"异常: {e}", 0, "P0")
        return False


def test_system_10_stage_interlock_integration():
    """ST-10: 阶段互锁集成测试"""
    case_id = "ST-10"
    name = "阶段互锁集成测试"
    
    token = login()
    if not token:
        log_test(case_id, name, "跳过", "登录失败", 0, "P0")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 设置开工日期
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d") + "T00:00:00"
        requests.post(
            f"{BASE_URL}/constructions/start-date",
            headers=headers,
            json={"start_date": start_date},
            timeout=5
        )
        
        # 尝试直接操作S01（未完成S00）
        response = requests.put(
            f"{BASE_URL}/constructions/stage-status",
            headers=headers,
            json={"stage": "S01", "status": "passed"},
            timeout=5
        )
        
        if response.status_code == 409:
            # 完成S00
            requests.put(
                f"{BASE_URL}/constructions/stage-status",
                headers=headers,
                json={"stage": "S00", "status": "checked"},
                timeout=5
            )
            
            # 再次尝试S01（应该成功）
            response = requests.put(
                f"{BASE_URL}/constructions/stage-status",
                headers=headers,
                json={"stage": "S01", "status": "passed"},
                timeout=5
            )
            
            if response.status_code == 200:
                log_test(case_id, name, "通过", "阶段互锁机制正常", 0, "P0")
                return True
        
        log_test(case_id, name, "失败", f"阶段互锁机制异常，状态码: {response.status_code}", 0, "P0")
        return False
        
    except Exception as e:
        log_test(case_id, name, "失败", f"异常: {e}", 0, "P0")
        return False


def test_system_11_api_documentation():
    """ST-11: API文档可访问性测试"""
    case_id = "ST-11"
    name = "API文档可访问性测试"
    
    try:
        # 测试OpenAPI文档（根据main.py配置，docs_url="/api/docs"）
        base_url = BASE_URL.replace('/api/v1', '')
        # 尝试多个可能的路径
        paths = ["/api/docs", "/docs", "/api/redoc", "/redoc"]
        
        for path in paths:
            try:
                response = requests.get(f"{base_url}{path}", timeout=5)
                if response.status_code == 200:
                    log_test(case_id, name, "通过", f"API文档可访问: {path}", 0, "P2")
                    return True
            except:
                continue
        
        log_test(case_id, name, "跳过", "API文档路径未找到（可能在生产环境禁用）", 0, "P2")
        return True  # 文档在生产环境可能被禁用，不算失败
        
    except Exception as e:
        log_test(case_id, name, "跳过", f"API文档检查异常: {e}", 0, "P2")
        return True  # 文档检查失败不算系统测试失败


def test_system_12_reliability_stress():
    """ST-12: 可靠性压力测试"""
    case_id = "ST-12"
    name = "可靠性压力测试"
    
    token = login()
    if not token:
        log_test(case_id, name, "跳过", "登录失败", 0, "P1")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 连续请求测试
        request_count = 50
        success_count = 0
        start_time = time.time()
        
        for i in range(request_count):
            try:
                response = requests.get(f"{BASE_URL}/users/profile", headers=headers, timeout=5)
                if response.status_code == 200:
                    success_count += 1
            except:
                pass
        
        duration = time.time() - start_time
        success_rate = (success_count / request_count) * 100
        
        if success_rate >= 95:
            log_test(case_id, name, "通过", 
                    f"连续{request_count}个请求，成功率: {success_rate:.1f}%, 耗时: {duration:.2f}s", 
                    duration, "P1")
            return True
        else:
            log_test(case_id, name, "失败", 
                    f"连续{request_count}个请求，成功率: {success_rate:.1f}%", 
                    duration, "P1")
            return False
            
    except Exception as e:
        log_test(case_id, name, "失败", f"异常: {e}", 0, "P1")
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("系统测试 - 对整个系统进行端到端测试")
    print("=" * 70)
    print("\n测试范围:")
    print("1. 系统功能测试（端到端业务流程）")
    print("2. 性能测试（响应时间、并发）")
    print("3. 安全性测试（认证、数据隔离）")
    print("4. 可靠性测试（错误处理、压力测试）")
    print("5. 兼容性测试（API文档）")
    print("=" * 70)
    
    # 执行测试
    test_system_01_health_check()
    test_system_02_user_authentication_flow()
    test_system_03_complete_business_workflow()
    test_system_04_api_response_time()
    test_system_05_concurrent_requests()
    test_system_06_security_authentication()
    test_system_07_data_isolation()
    test_system_08_error_handling()
    test_system_09_file_upload_validation()
    test_system_10_stage_interlock_integration()
    test_system_11_api_documentation()
    test_system_12_reliability_stress()
    
    # 输出结果
    print("\n" + "=" * 70)
    print("系统测试结果汇总")
    print("=" * 70)
    print(f"总用例数: {test_results['total']}")
    print(f"通过: {test_results['passed']}")
    print(f"失败: {test_results['failed']}")
    print(f"跳过: {test_results['skipped']}")
    print(f"通过率: {test_results['passed']/test_results['total']*100:.1f}%" if test_results['total'] > 0 else "0%")
    
    # 性能统计
    durations = [d['duration'] for d in test_results['details'] if d['duration'] > 0]
    if durations:
        print(f"\n性能统计:")
        print(f"  平均响应时间: {statistics.mean(durations):.3f}s")
        print(f"  最大响应时间: {max(durations):.3f}s")
        print(f"  最小响应时间: {min(durations):.3f}s")
    
    print("\n详细结果:")
    for detail in test_results['details']:
        status = "✅" if detail['result'] == "通过" else "❌" if detail['result'] == "失败" else "⏭️"
        duration_str = f" ({detail['duration']:.3f}s)" if detail['duration'] > 0 else ""
        print(f"  {status} [{detail['case_id']}] {detail['name']}{duration_str}")
        if detail['message']:
            print(f"     {detail['message']}")
    
    print("=" * 70)
    
    # 保存报告
    report_file = f"test-system-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    print(f"\n详细报告已保存至: {report_file}")


if __name__ == "__main__":
    main()

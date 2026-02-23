#!/usr/bin/env python3
"""
生产环境所有API接口测试脚本
使用测试数据在 tests/fixtures 目录下
"""

import os
import sys
import json
import requests
import time
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 生产环境配置
PRODUCTION_API_BASE = "https://lakeli.top"
API_V1 = f"{PRODUCTION_API_BASE}/api/v1"

# 测试计数器
passed_tests = 0
failed_tests = 0
test_results = []

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def test_endpoint(name: str, method: str, url: str, 
                  data: Optional[Dict] = None, 
                  headers: Optional[Dict] = None,
                  expected_status: int = 200,
                  auth_token: Optional[str] = None) -> Tuple[bool, Dict]:
    """测试API端点"""
    global passed_tests, failed_tests
    
    # 添加认证头
    final_headers = headers or {}
    if auth_token:
        final_headers["Authorization"] = f"Bearer {auth_token}"
    
    if "Content-Type" not in final_headers and method in ["POST", "PUT", "PATCH"]:
        final_headers["Content-Type"] = "application/json"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=final_headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=final_headers, json=data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, headers=final_headers, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=final_headers, timeout=30)
        else:
            return False, {"error": f"Unsupported method: {method}"}
        
        success = response.status_code == expected_status
        result = {
            "status_code": response.status_code,
            "success": success,
            "response": response.json() if response.text else {}
        }
        
        if success:
            passed_tests += 1
            print_success(f"{name} - HTTP {response.status_code}")
        else:
            failed_tests += 1
            print_error(f"{name} - HTTP {response.status_code} (expected {expected_status})")
            if response.text:
                print(f"  Response: {response.text[:200]}")
        
        test_results.append({
            "name": name,
            "url": url,
            "method": method,
            "success": success,
            "status_code": response.status_code
        })
        
        return success, result
        
    except Exception as e:
        failed_tests += 1
        print_error(f"{name} - Exception: {str(e)}")
        test_results.append({
            "name": name,
            "url": url,
            "method": method,
            "success": False,
            "error": str(e)
        })
        return False, {"error": str(e)}

def test_health_check():
    """测试健康检查接口"""
    print_info("1. 健康检查接口测试")
    success, result = test_endpoint(
        "健康检查",
        "GET",
        f"{PRODUCTION_API_BASE}/health"
    )
    return success

def test_user_login() -> Optional[str]:
    """测试用户登录，返回token"""
    print_info("2. 用户登录测试")
    success, result = test_endpoint(
        "用户登录",
        "POST",
        f"{API_V1}/users/login",
        data={"code": "dev_h5_mock"}
    )
    
    if success and "access_token" in result.get("response", {}):
        token = result["response"]["access_token"]
        print_success(f"登录成功，Token: {token[:50]}...")
        return token
    else:
        print_error("登录失败")
        return None

def test_user_profile(token: str):
    """测试用户信息接口"""
    print_info("3. 用户信息接口测试")
    test_endpoint(
        "获取用户信息",
        "GET",
        f"{API_V1}/users/profile",
        auth_token=token
    )

def test_quotes_apis(token: str):
    """测试报价单相关接口"""
    print_info("4. 报价单接口测试")
    
    # 获取报价单列表
    test_endpoint(
        "获取报价单列表",
        "GET",
        f"{API_V1}/quotes/list?page=1&page_size=10",
        auth_token=token
    )
    
    # 测试报价单上传（使用测试数据）
    test_quote_upload(token)

def test_quote_upload(token: str):
    """测试报价单上传"""
    global passed_tests, failed_tests
    print_info("  4.1 报价单上传测试")
    
    # 使用测试数据中的报价单图片
    fixture_path = Path("tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png")
    if not fixture_path.exists():
        print_warning(f"测试文件不存在: {fixture_path}")
        return
    
    try:
        with open(fixture_path, "rb") as f:
            files = {"file": ("quote.png", f, "image/png")}
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.post(
                f"{API_V1}/quotes/upload",
                files=files,
                headers=headers,
                timeout=60
            )
            
            success = response.status_code in [200, 201]
            if success:
                passed_tests += 1
                print_success(f"报价单上传 - HTTP {response.status_code}")
                result = response.json()
                quote_id = result.get("task_id")
                if quote_id:
                    print_info(f"  报价单ID: {quote_id}")
                    # 等待分析完成
                    test_quote_analysis_result(token, quote_id)
            else:
                failed_tests += 1
                print_error(f"报价单上传 - HTTP {response.status_code}")
                if response.text:
                    print(f"  Response: {response.text[:200]}")
                    
    except Exception as e:
        failed_tests += 1
        print_error(f"报价单上传 - Exception: {str(e)}")

def test_quote_analysis_result(token: str, quote_id: int):
    """测试获取报价单分析结果"""
    print_info(f"  4.2 获取报价单分析结果 (ID: {quote_id})")
    
    # 等待分析完成（最多等待30秒）
    max_wait = 30
    wait_interval = 2
    
    for i in range(max_wait // wait_interval):
        success, result = test_endpoint(
            f"获取报价单分析结果 (尝试 {i+1})",
            "GET",
            f"{API_V1}/quotes/quote/{quote_id}",
            auth_token=token
        )
        
        if success:
            quote_status = result.get("response", {}).get("status")
            if quote_status == "completed":
                print_success(f"报价单分析完成，状态: {quote_status}")
                # 检查分析结果
                analysis_result = result.get("response", {}).get("result_json")
                if analysis_result:
                    risk_score = analysis_result.get("risk_score", 0)
                    print_info(f"  风险评分: {risk_score}")
                break
            elif quote_status == "failed":
                print_error(f"报价单分析失败，状态: {quote_status}")
                break
            else:
                print_info(f"  分析中，状态: {quote_status}，等待 {wait_interval} 秒...")
                time.sleep(wait_interval)
        else:
            break

def test_contracts_apis(token: str):
    """测试合同相关接口"""
    print_info("5. 合同接口测试")
    
    # 获取合同列表
    test_endpoint(
        "获取合同列表",
        "GET",
        f"{API_V1}/contracts/list?page=1&page_size=10",
        auth_token=token
    )
    
    # 测试合同上传（使用测试数据）
    test_contract_upload(token)

def test_contract_upload(token: str):
    """测试合同上传"""
    global passed_tests, failed_tests
    print_info("  5.1 合同上传测试")
    
    # 使用测试数据中的合同图片
    fixture_path = Path("tests/fixtures/深圳市住宅装饰装修工程施工合同（半包装修版）.png")
    if not fixture_path.exists():
        print_warning(f"测试文件不存在: {fixture_path}")
        return
    
    try:
        with open(fixture_path, "rb") as f:
            files = {"file": ("contract.png", f, "image/png")}
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.post(
                f"{API_V1}/contracts/upload",
                files=files,
                headers=headers,
                timeout=60
            )
            
            success = response.status_code in [200, 201]
            if success:
                passed_tests += 1
                print_success(f"合同上传 - HTTP {response.status_code}")
                result = response.json()
                contract_id = result.get("task_id")
                if contract_id:
                    print_info(f"  合同ID: {contract_id}")
            else:
                failed_tests += 1
                print_error(f"合同上传 - HTTP {response.status_code}")
                if response.text:
                    print(f"  Response: {response.text[:200]}")
                    
    except Exception as e:
        failed_tests += 1
        print_error(f"合同上传 - Exception: {str(e)}")

def test_acceptance_apis(token: str):
    """测试验收报告接口"""
    print_info("6. 验收报告接口测试")
    
    # 获取验收报告列表
    test_endpoint(
        "获取验收报告列表",
        "GET",
        f"{API_V1}/acceptance/list?page=1&page_size=10",
        auth_token=token
    )

def test_constructions_apis(token: str):
    """测试施工陪伴接口"""
    print_info("7. 施工陪伴接口测试")
    
    # 获取施工项目列表
    test_endpoint(
        "获取施工项目列表",
        "GET",
        f"{API_V1}/constructions/list?page=1&page_size=10",
        auth_token=token
    )

def test_companies_apis(token: str):
    """测试公司检测接口"""
    print_info("8. 公司检测接口测试")
    
    # 搜索公司
    test_endpoint(
        "搜索装修公司",
        "GET",
        f"{API_V1}/companies/search?keyword=装修&page=1&page_size=10",
        auth_token=token
    )

def test_material_checks_apis(token: str):
    """测试材料清单接口"""
    print_info("9. 材料清单接口测试")
    
    # 获取材料清单列表
    test_endpoint(
        "获取材料清单列表",
        "GET",
        f"{API_V1}/material_checks/list?page=1&page_size=10",
        auth_token=token
    )

def test_messages_apis(token: str):
    """测试消息中心接口"""
    print_info("10. 消息中心接口测试")
    
    # 获取消息列表
    test_endpoint(
        "获取消息列表",
        "GET",
        f"{API_V1}/messages/list?page=1&page_size=10",
        auth_token=token
    )

def test_points_apis(token: str):
    """测试积分接口"""
    print_info("11. 积分接口测试")
    
    # 获取积分信息
    test_endpoint(
        "获取积分信息",
        "GET",
        f"{API_V1}/points/info",
        auth_token=token
    )

def test_monitor_apis(token: str):
    """测试监控接口"""
    print_info("12. 监控接口测试")
    
    # 获取系统状态
    test_endpoint(
        "获取系统状态",
        "GET",
        f"{API_V1}/monitor/status",
        auth_token=token
    )

def test_oss_apis(token: str):
    """测试OSS接口"""
    print_info("13. OSS接口测试")
    
    # 获取OSS上传策略
    test_endpoint(
        "获取OSS上传策略",
        "GET",
        f"{API_V1}/oss/policy",
        auth_token=token
    )

def test_designer_apis(token: str):
    """测试AI设计师接口"""
    print_info("14. AI设计师接口测试")
    
    # AI设计师咨询
    test_endpoint(
        "AI设计师咨询",
        "POST",
        f"{API_V1}/designer/chat",
        data={
            "question": "我想装修一个80平米的房子，预算15万，有什么建议？",
            "context": ""
        },
        auth_token=token
    )

def test_consultation_apis(token: str):
    """测试AI监理咨询接口"""
    print_info("15. AI监理咨询接口测试")
    
    # AI监理咨询
    test_endpoint(
        "AI监理咨询",
        "POST",
        f"{API_V1}/consultation/chat",
        data={
            "question": "水电验收需要注意什么？",
            "stage": "plumbing"
        },
        auth_token=token
    )

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("生产环境所有API接口测试")
    print(f"API地址: {PRODUCTION_API_BASE}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 健康检查
    if not test_health_check():
        print_error("健康检查失败，生产环境可能不可用")
        return
    
    # 2. 用户登录获取token
    token = test_user_login()
    if not token:
        print_error("用户登录失败，无法继续测试需要认证的接口")
        # 继续测试不需要认证的接口
        token = None
    
    # 3. 测试需要认证的接口
    if token:
        test_user_profile(token)
        test_quotes_apis(token)
        test_contracts_apis(token)
        test_acceptance_apis(token)
        test_constructions_apis(token)
        test_companies_apis(token)
        test_material_checks_apis(token)
        test_messages_apis(token)
        test_points_apis(token)
        test_monitor_apis(token)
        test_oss_apis(token)
        test_designer_apis(token)
        test_consultation_apis(token)
    
    # 打印测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试数: {passed_tests + failed_tests}")
    print(f"{Colors.GREEN}通过: {passed_tests}{Colors.END}")
    
    if failed_tests > 0:
        print(f"{Colors.RED}失败: {failed_tests}{Colors.END}")
        print("\n失败的测试:")
        for result in test_results:
            if not result.get("success", False):
                print(f"  - {result.get('name')}: {result.get('error', f'HTTP {result.get("status_code")}')}")
    else:
        print(f"{Colors.GREEN}失败: {failed_tests}{Colors.END}")
    
    print(f"\n结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 保存测试结果到文件
    save_test_results()
    
    return failed_tests == 0

def save_test_results():
    """保存测试结果到文件"""
    results_file = "tests/production-api-test-results.json"
    try:
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "api_base": PRODUCTION_API_BASE,
                "total_tests": passed_tests + failed_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "results": test_results
            }, f, indent=2, ensure_ascii=False)
        print_info(f"测试结果已保存到: {results_file}")
    except Exception as e:
        print_error(f"保存测试结果失败: {str(e)}")

if __name__ == "__main__":
    print("开始生产环境API测试...")
    success = run_all_tests()
    sys.exit(0 if success else 1)

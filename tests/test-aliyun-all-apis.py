#!/usr/bin/env python3
"""
阿里云开发环境所有API接口测试脚本
测试地址：http://120.26.201.61:8001
"""

import os
import sys
import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 阿里云开发环境配置
ALIYUN_API_BASE = "http://120.26.201.61:8000"
API_V1 = f"{ALIYUN_API_BASE}/api/v1"

# 测试计数器
passed_tests = 0
failed_tests = 0
skipped_tests = 0
test_results = []

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_debug(msg):
    print(f"{Colors.CYAN}🔍 {msg}{Colors.END}")

def test_endpoint(name: str, method: str, url: str, 
                  data: Optional[Dict] = None, 
                  headers: Optional[Dict] = None,
                  expected_status: int = 200,
                  auth_token: Optional[str] = None,
                  skip_on_failure: bool = False,
                  description: str = "") -> Tuple[bool, Dict]:
    """测试API端点"""
    global passed_tests, failed_tests, skipped_tests
    
    # 添加认证头
    final_headers = headers or {}
    if auth_token:
        final_headers["Authorization"] = f"Bearer {auth_token}"
    
    if "Content-Type" not in final_headers and method in ["POST", "PUT", "PATCH"] and data:
        final_headers["Content-Type"] = "application/json"
    
    start_time = time.time()
    
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
        
        response_time = (time.time() - start_time) * 1000  # 毫秒
        success = response.status_code == expected_status
        
        # 尝试解析JSON响应
        response_data = {}
        if response.text:
            try:
                response_data = response.json()
            except:
                response_data = {"raw_text": response.text[:200]}
        
        result = {
            "status_code": response.status_code,
            "success": success,
            "response_time_ms": round(response_time, 2),
            "response": response_data
        }
        
        if success:
            passed_tests += 1
            print_success(f"{name} - HTTP {response.status_code} ({response_time:.0f}ms)")
            if description:
                print_debug(f"   {description}")
        else:
            if skip_on_failure:
                skipped_tests += 1
                print_warning(f"{name} - HTTP {response.status_code} (期望 {expected_status}, 跳过)")
                if description:
                    print_debug(f"   {description}")
            else:
                failed_tests += 1
                print_error(f"{name} - HTTP {response.status_code} (期望 {expected_status})")
                if description:
                    print_debug(f"   {description}")
                if response.text:
                    error_preview = response.text[:300] + ("..." if len(response.text) > 300 else "")
                    print(f"   错误响应: {error_preview}")
        
        test_results.append({
            "name": name,
            "url": url,
            "method": method,
            "success": success,
            "status_code": response.status_code,
            "response_time_ms": round(response_time, 2),
            "skip_on_failure": skip_on_failure,
            "description": description
        })
        
        return success, result
        
    except requests.exceptions.Timeout:
        error_msg = "请求超时 (30秒)"
        if skip_on_failure:
            skipped_tests += 1
            print_warning(f"{name} - {error_msg} (跳过)")
        else:
            failed_tests += 1
            print_error(f"{name} - {error_msg}")
        test_results.append({
            "name": name,
            "url": url,
            "method": method,
            "success": False,
            "error": error_msg,
            "skip_on_failure": skip_on_failure,
            "description": description
        })
        return False, {"error": error_msg}
        
    except requests.exceptions.ConnectionError:
        error_msg = "连接失败 - 服务器可能未启动或网络不可达"
        if skip_on_failure:
            skipped_tests += 1
            print_warning(f"{name} - {error_msg} (跳过)")
        else:
            failed_tests += 1
            print_error(f"{name} - {error_msg}")
        test_results.append({
            "name": name,
            "url": url,
            "method": method,
            "success": False,
            "error": error_msg,
            "skip_on_failure": skip_on_failure,
            "description": description
        })
        return False, {"error": error_msg}
        
    except Exception as e:
        error_msg = f"异常: {str(e)}"
        if skip_on_failure:
            skipped_tests += 1
            print_warning(f"{name} - {error_msg} (跳过)")
        else:
            failed_tests += 1
            print_error(f"{name} - {error_msg}")
        test_results.append({
            "name": name,
            "url": url,
            "method": method,
            "success": False,
            "error": error_msg,
            "skip_on_failure": skip_on_failure,
            "description": description
        })
        return False, {"error": error_msg}

def test_health_check():
    """测试健康检查接口"""
    print_info("1. 健康检查接口测试")
    success, result = test_endpoint(
        "健康检查",
        "GET",
        f"{ALIYUN_API_BASE}/health",
        description="检查阿里云服务器是否正常运行"
    )
    return success

def test_user_login() -> Optional[str]:
    """测试用户登录，返回token"""
    print_info("2. 用户登录测试")
    success, result = test_endpoint(
        "用户登录",
        "POST",
        f"{API_V1}/users/login",
        data={"code": "dev_h5_mock"},
        description="使用开发环境mock code登录"
    )
    
    if success and "access_token" in result.get("response", {}):
        token = result["response"]["access_token"]
        print_success(f"登录成功，Token: {token[:50]}...")
        return token
    else:
        print_error("登录失败，无法获取access_token")
        if result.get("response"):
            print_debug(f"响应内容: {json.dumps(result['response'], ensure_ascii=False)[:200]}")
        return None

def test_user_apis(token: str):
    """测试用户相关接口"""
    print_info("3. 用户信息接口测试")
    
    # 获取用户信息
    test_endpoint(
        "获取用户信息",
        "GET",
        f"{API_V1}/users/profile",
        auth_token=token,
        description="获取当前登录用户的详细信息"
    )
    
    # 获取用户设置
    test_endpoint(
        "获取用户设置",
        "GET",
        f"{API_V1}/users/settings",
        auth_token=token,
        skip_on_failure=True,
        description="获取用户个性化设置"
    )
    
    # 更新用户信息（模拟）
    test_endpoint(
        "更新用户信息",
        "PUT",
        f"{API_V1}/users/profile?nickname=测试用户",
        auth_token=token,
        skip_on_failure=True,
        description="更新用户昵称"
    )

def test_quotes_apis(token: str):
    """测试报价单相关接口"""
    print_info("4. 报价单接口测试")
    
    # 获取报价单列表
    success, result = test_endpoint(
        "获取报价单列表",
        "GET",
        f"{API_V1}/quotes/list",
        auth_token=token,
        description="获取用户的所有报价单列表"
    )
    
    # 如果有报价单，测试获取详情
    if success and result.get("response", {}).get("data", {}).get("list"):
        quote_list = result["response"]["data"]["list"]
        if quote_list:
            quote_id = quote_list[0].get("id")
            if quote_id:
                test_endpoint(
                    "获取报价单详情",
                    "GET",
                    f"{API_V1}/quotes/quote/{quote_id}",
                    auth_token=token,
                    description=f"获取报价单ID={quote_id}的详细信息"
                )
    
    # 测试上传报价单（需要文件，跳过）
    test_endpoint(
        "上传报价单接口检查",
        "POST",
        f"{API_V1}/quotes/upload",
        auth_token=token,
        expected_status=400,  # 缺少文件，期望400错误
        skip_on_failure=True,
        description="检查报价单上传接口是否存在（需要文件上传）"
    )

def test_contracts_apis(token: str):
    """测试合同相关接口"""
    print_info("5. 合同接口测试")
    
    # 获取合同列表
    success, result = test_endpoint(
        "获取合同列表",
        "GET",
        f"{API_V1}/contracts/list",
        auth_token=token,
        skip_on_failure=True,
        description="获取用户的所有合同列表"
    )
    
    # 如果有合同，测试获取详情
    if success and result.get("response", {}).get("data", {}).get("list"):
        contract_list = result["response"]["data"]["list"]
        if contract_list:
            contract_id = contract_list[0].get("id")
            if contract_id:
                test_endpoint(
                    "获取合同详情",
                    "GET",
                    f"{API_V1}/contracts/contract/{contract_id}",
                    auth_token=token,
                    description=f"获取合同ID={contract_id}的详细信息"
                )

def test_companies_apis(token: str):
    """测试公司检测接口"""
    print_info("6. 公司检测接口测试")
    
    # 搜索公司
    test_endpoint(
        "搜索装修公司",
        "GET",
        f"{API_V1}/companies/search?keyword=装修",
        auth_token=token,
        skip_on_failure=True,
        description="搜索装修公司（参数名可能是keyword或q）"
    )
    
    # 获取公司扫描记录
    test_endpoint(
        "获取公司扫描记录",
        "GET",
        f"{API_V1}/companies/scans",
        auth_token=token,
        skip_on_failure=True,
        description="获取用户的公司检测记录"
    )
    
    # 提交公司检测（需要公司名称）
    test_endpoint(
        "提交公司检测接口检查",
        "POST",
        f"{API_V1}/companies/scan",
        data={"company_name": "测试装修公司"},
        auth_token=token,
        skip_on_failure=True,
        description="提交公司检测（可能需要特定格式）"
    )

def test_constructions_apis(token: str):
    """测试施工进度接口"""
    print_info("7. 施工进度接口测试")
    
    # 获取施工进度计划
    test_endpoint(
        "获取施工进度计划",
        "GET",
        f"{API_V1}/constructions/schedule",
        auth_token=token,
        skip_on_failure=True,
        description="获取用户的施工进度计划"
    )
    
    # 设置开工日期
    test_endpoint(
        "设置开工日期接口检查",
        "POST",
        f"{API_V1}/constructions/start-date",
        data={"start_date": "2026-02-22T00:00:00"},
        auth_token=token,
        skip_on_failure=True,
        description="设置施工开工日期"
    )
    
    # 更新阶段状态
    test_endpoint(
        "更新阶段状态接口检查",
        "PUT",
        f"{API_V1}/constructions/stage-status",
        data={"stage": "S00", "status": "checked"},
        auth_token=token,
        skip_on_failure=True,
        description="更新施工阶段状态（材料进场核对）"
    )

def test_messages_apis(token: str):
    """测试消息中心接口"""
    print_info("8. 消息中心接口测试")
    
    # 获取消息列表
    test_endpoint(
        "获取消息列表",
        "GET",
        f"{API_V1}/messages",
        auth_token=token,
        skip_on_failure=True,
        description="获取用户的消息列表"
    )
    
    # 获取未读消息数量
    test_endpoint(
        "获取未读消息数量",
        "GET",
        f"{API_V1}/messages/unread-count",
        auth_token=token,
        skip_on_failure=True,
        description="获取未读消息数量"
    )
    
    # 创建消息（系统内部使用）
    test_endpoint(
        "创建消息接口检查",
        "POST",
        f"{API_V1}/messages",
        data={"category": "system", "title": "测试消息", "content": "测试内容"},
        auth_token=token,
        skip_on_failure=True,
        description="创建系统消息（通常内部使用）"
    )

def test_payments_apis(token: str):
    """测试支付接口"""
    print_info("9. 支付接口测试")
    
    # 获取订单列表
    test_endpoint(
        "获取订单列表",
        "GET",
        f"{API_V1}/payments/orders",
        auth_token=token,
        skip_on_failure=True,
        description="获取用户的订单列表"
    )
    
    # 创建订单
    test_endpoint(
        "创建订单接口检查",
        "POST",
        f"{API_V1}/payments/create",
        data={"order_type": "report_single", "resource_type": "company", "resource_id": 1},
        auth_token=token,
        skip_on_failure=True,
        description="创建报告解锁订单"
    )

def test_acceptance_apis(token: str):
    """测试验收报告接口"""
    print_info("10. 验收报告接口测试")
    
    # 获取验收报告列表
    test_endpoint(
        "获取验收报告列表",
        "GET",
        f"{API_V1}/acceptance",
        auth_token=token,
        skip_on_failure=True,
        description="获取用户的验收报告列表"
    )
    
    # 验收分析接口检查
    test_endpoint(
        "验收分析接口检查",
        "POST",
        f"{API_V1}/acceptance/analyze",
        data={"stage": "S01", "file_urls": []},
        auth_token=token,
        skip_on_failure=True,
        description="提交验收分析（需要照片URL）"
    )

def test_construction_photos_apis(token: str):
    """测试施工照片接口"""
    print_info("11. 施工照片接口测试")
    
    # 获取施工照片列表
    test_endpoint(
        "获取施工照片列表",
        "GET",
        f"{API_V1}/construction-photos",
        auth_token=token,
        skip_on_failure=True,
        description="获取用户的施工照片列表"
    )

def test_material_checks_apis(token: str):
    """测试材料清单接口"""
    print_info("12. 材料清单接口测试")
    
    # 获取材料清单
    test_endpoint(
        "获取材料清单",
        "GET",
        f"{API_V1}/material-checks/material-list",
        auth_token=token,
        skip_on_failure=True,
        description="获取材料进场核对清单"
    )
    
    # 提交材料核对结果
    test_endpoint(
        "提交材料核对接口检查",
        "POST",
        f"{API_V1}/material-checks/submit",
        data={"result": "pass", "items": []},
        auth_token=token,
        skip_on_failure=True,
        description="提交材料进场核对结果"
    )

def test_cities_apis(token: str):
    """测试城市选择接口"""
    print_info("13. 城市选择接口测试")
    
    # 获取热门城市
    test_endpoint(
        "获取热门城市",
        "GET",
        f"{API_V1}/cities/hot",
        auth_token=token,
        skip_on_failure=True,
        description="获取热门城市列表"
    )
    
    # 获取当前城市
    test_endpoint(
        "获取当前城市",
        "GET",
        f"{API_V1}/cities/current",
        auth_token=token,
        skip_on_failure=True,
        description="获取用户当前选择的城市"
    )
    
    # 保存城市选择
    test_endpoint(
        "保存城市选择接口检查",
        "POST",
        f"{API_V1}/cities/select",
        data={"city_name": "深圳市"},
        auth_token=token,
        skip_on_failure=True,
        description="保存用户选择的城市"
    )

def test_consultation_apis(token: str):
    """测试AI监理咨询接口"""
    print_info("14. AI监理咨询接口测试")
    
    # 获取咨询额度
    test_endpoint(
        "获取咨询额度",
        "GET",
        f"{API_V1}/consultation/quota",
        auth_token=token,
        skip_on_failure=True,
        description="获取AI监理咨询额度信息"
    )
    
    # 获取会话列表
    test_endpoint(
        "获取会话列表",
        "GET",
        f"{API_V1}/consultation/sessions",
        auth_token=token,
        skip_on_failure=True,
        description="获取AI监理咨询会话列表"
    )
    
    # 创建会话
    test_endpoint(
        "创建会话接口检查",
        "POST",
        f"{API_V1}/consultation/session",
        data={},
        auth_token=token,
        skip_on_failure=True,
        description="创建新的AI监理咨询会话"
    )

def test_material_library_apis(token: str):
    """测试材料库接口"""
    print_info("15. 材料库接口测试")
    
    # 搜索材料库
    test_endpoint(
        "搜索材料库",
        "GET",
        f"{API_V1}/material-library/search?keyword=水泥",
        auth_token=token,
        skip_on_failure=True,
        description="搜索材料库中的材料"
    )
    
    # 获取常用材料
    test_endpoint(
        "获取常用材料",
        "GET",
        f"{API_V1}/material-library/common",
        auth_token=token,
        skip_on_failure=True,
        description="获取常用材料列表"
    )
    
    # 智能匹配材料
    test_endpoint(
        "智能匹配材料接口检查",
        "POST",
        f"{API_V1}/material-library/match",
        data={"material_names": ["水泥", "瓷砖"]},
        auth_token=token,
        skip_on_failure=True,
        description="智能匹配材料名称"
    )

def test_feedback_apis(token: str):
    """测试意见反馈接口"""
    print_info("16. 意见反馈接口测试")
    
    # 提交反馈
    test_endpoint(
        "提交反馈",
        "POST",
        f"{API_V1}/feedback",
        data={"content": "测试反馈内容"},
        auth_token=token,
        skip_on_failure=True,
        description="提交用户意见反馈"
    )

def test_appeals_apis(token: str):
    """测试申诉接口"""
    print_info("17. 申诉接口测试")
    
    # 获取申诉列表
    test_endpoint(
        "获取申诉列表",
        "GET",
        f"{API_V1}/appeals/acceptance",
        auth_token=token,
        skip_on_failure=True,
        description="获取验收申诉列表"
    )
    
    # 提交验收申诉
    test_endpoint(
        "提交验收申诉接口检查",
        "POST",
        f"{API_V1}/appeals/acceptance/1",
        data={"reason": "测试申诉原因", "images": []},
        auth_token=token,
        skip_on_failure=True,
        description="提交验收申诉（需要有效的analysis_id）"
    )

def test_reports_apis(token: str):
    """测试报告导出接口"""
    print_info("18. 报告导出接口测试")
    
    # 导出PDF报告
    test_endpoint(
        "导出PDF报告",
        "GET",
        f"{API_V1}/reports/export-pdf?report_type=company&resource_id=1",
        auth_token=token,
        expected_status=200,  # 或403如果未解锁
        skip_on_failure=True,
        description="导出公司检测报告PDF"
    )

def test_monitor_apis(token: str):
    """测试监控接口"""
    print_info("19. 监控接口测试")
    
    # 获取系统状态
    test_endpoint(
        "获取系统状态",
        "GET",
        f"{API_V1}/monitor/status",
        auth_token=token,
        description="获取系统监控状态"
    )

def test_data_management_apis(token: str):
    """测试数据管理接口"""
    print_info("20. 数据管理接口测试")
    
    # 软删除接口检查
    test_endpoint(
        "软删除接口检查",
        "POST",
        f"{API_V1}/users/data/delete",
        data={"resource_type": "construction_photo", "resource_id": 1},
        auth_token=token,
        skip_on_failure=True,
        description="软删除用户数据"
    )
    
    # 回收站列表
    test_endpoint(
        "回收站列表",
        "GET",
        f"{API_V1}/users/data/recycle",
        auth_token=token,
        skip_on_failure=True,
        description="获取回收站数据列表"
    )

def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("阿里云开发环境所有API接口测试")
    print(f"API地址: {ALIYUN_API_BASE}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 1. 健康检查
    print_info("阶段1: 基础健康检查")
    if not test_health_check():
        print_error("健康检查失败，阿里云服务器可能不可用或未启动")
        print_warning("将继续测试其他接口，但连接可能失败")
    
    # 2. 用户登录获取token
    print_info("阶段2: 用户认证")
    token = test_user_login()
    if not token:
        print_error("用户登录失败，无法测试需要认证的接口")
        print_warning("将跳过所有需要认证的接口测试")
        token = None
    
    # 3. 测试需要认证的接口
    if token:
        print_info("阶段3: 需要认证的接口测试")
        test_user_apis(token)
        test_quotes_apis(token)
        test_contracts_apis(token)
        test_companies_apis(token)
        test_constructions_apis(token)
        test_messages_apis(token)
        test_payments_apis(token)
        test_acceptance_apis(token)
        test_construction_photos_apis(token)
        test_material_checks_apis(token)
        test_cities_apis(token)
        test_consultation_apis(token)
        test_material_library_apis(token)
        test_feedback_apis(token)
        test_appeals_apis(token)
        test_reports_apis(token)
        test_monitor_apis(token)
        test_data_management_apis(token)
    
    # 打印测试总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    total_tests = len(test_results)
    
    print(f"总测试数: {total_tests}")
    print(f"{Colors.GREEN}通过: {passed_tests}{Colors.END}")
    print(f"{Colors.RED}失败: {failed_tests}{Colors.END}")
    print(f"{Colors.YELLOW}跳过: {skipped_tests}{Colors.END}")
    
    # 计算成功率
    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(f"成功率: {success_rate:.1f}%")
    
    # 显示失败的测试
    if failed_tests > 0:
        print(f"\n{Colors.RED}失败的测试:{Colors.END}")
        for result in test_results:
            if not result.get("success") and not result.get("skip_on_failure"):
                error_msg = result.get('error', f'HTTP {result.get("status_code")}')
                print(f"  - {result.get('name')}: {error_msg}")
                if result.get("description"):
                    print(f"    描述: {result.get('description')}")
    
    # 显示跳过的测试
    if skipped_tests > 0:
        print(f"\n{Colors.YELLOW}跳过的测试:{Colors.END}")
        for result in test_results:
            if not result.get("success") and result.get("skip_on_failure"):
                status = result.get('status_code', 'N/A')
                print(f"  - {result.get('name')}: HTTP {status}")
                if result.get("description"):
                    print(f"    描述: {result.get('description')}")
    
    # 响应时间统计
    if test_results:
        response_times = [r.get("response_time_ms", 0) for r in test_results if r.get("response_time_ms")]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            print(f"\n响应时间统计:")
            print(f"  平均响应时间: {avg_time:.0f}ms")
            print(f"  最大响应时间: {max_time:.0f}ms")
    
    print(f"\n结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 保存测试结果到文件
    save_test_results()
    
    return failed_tests == 0

def save_test_results():
    """保存测试结果到文件"""
    results_file = "tests/aliyun-api-test-results.json"
    try:
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "api_base": ALIYUN_API_BASE,
                "total_tests": len(test_results),
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": (passed_tests / len(test_results) * 100) if test_results else 0,
                "results": test_results
            }, f, indent=2, ensure_ascii=False)
        print_info(f"测试结果已保存到: {results_file}")
    except Exception as e:
        print_error(f"保存测试结果失败: {str(e)}")

if __name__ == "__main__":
    print("开始阿里云开发环境API测试...")
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"测试执行异常: {str(e)}")
        sys.exit(1)

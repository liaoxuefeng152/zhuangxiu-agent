#!/usr/bin/env python3
"""
核心AI接口功能测试脚本
测试公司风险扫描、报价单分析、合同分析、AI验收四个核心接口
"""

import os
import sys
import json
import requests
import time
import asyncio
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 阿里云生产环境配置
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
                  description: str = "",
                  problem_attribution: str = "待分析") -> Tuple[bool, Dict]:
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
            "response": response_data,
            "problem_attribution": problem_attribution
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
            "description": description,
            "problem_attribution": problem_attribution
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
            "description": description,
            "problem_attribution": "环境/配置问题"
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
            "description": description,
            "problem_attribution": "环境/配置问题"
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
            "description": description,
            "problem_attribution": "后台问题"
        })
        return False, {"error": error_msg}

def test_health_check():
    """测试健康检查接口"""
    print_info("1. 健康检查接口测试")
    success, result = test_endpoint(
        "健康检查",
        "GET",
        f"{ALIYUN_API_BASE}/health",
        description="检查阿里云服务器是否正常运行",
        problem_attribution="环境/配置问题"
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
        description="使用开发环境mock code登录",
        problem_attribution="后台问题"
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

def read_file_as_base64(file_path: Path) -> str:
    """读取文件并转换为Base64字符串"""
    with open(file_path, "rb") as f:
        file_data = f.read()
        base64_str = base64.b64encode(file_data).decode("utf-8")
        return base64_str

def test_company_scan_apis(token: str):
    """测试公司风险扫描接口"""
    print_info("3. 公司风险扫描接口测试")
    
    # 搜索公司
    success, search_result = test_endpoint(
        "搜索装修公司",
        "GET",
        f"{API_V1}/companies/search?q=深圳装修",
        auth_token=token,
        description="搜索装修公司，测试参数验证",
        problem_attribution="后台问题"
    )
    
    # 提交公司检测
    company_name = "深圳XX装饰工程有限公司"
    success, scan_result = test_endpoint(
        "提交公司检测",
        "POST",
        f"{API_V1}/companies/scan",
        data={"company_name": company_name},
        auth_token=token,
        description=f"提交公司检测: {company_name}",
        problem_attribution="后台问题"
    )
    
    if success and scan_result.get("response", {}).get("id"):
        scan_id = scan_result["response"]["id"]
        print_info(f"公司检测任务已创建，ID: {scan_id}")
        
        # 等待一段时间后获取结果（后台任务需要时间）
        print_info("等待10秒让后台分析任务执行...")
        time.sleep(10)
        
        # 获取检测结果
        success, result_result = test_endpoint(
            "获取公司检测结果",
            "GET",
            f"{API_V1}/companies/scan/{scan_id}",
            auth_token=token,
            description=f"获取公司检测结果，ID: {scan_id}",
            problem_attribution="后台问题"
        )
        
        if success:
            response_data = result_result.get("response", {})
            print_debug(f"公司检测结果: {json.dumps(response_data, ensure_ascii=False, indent=2)[:500]}")
            
            # 验证返回的数据结构
            if response_data.get("company_name") == company_name:
                print_success("公司名称匹配正确")
            
            if response_data.get("legal_risks"):
                print_success("法律风险信息存在")
                
            if response_data.get("status") == "completed":
                print_success("公司检测任务已完成")
            else:
                print_warning(f"公司检测任务状态: {response_data.get('status')}")
    
    return success

def test_quote_analysis_apis(token: str):
    """测试报价单分析接口"""
    print_info("4. 报价单分析接口测试")
    
    # 读取测试文件
    fixture_path = Path("tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png")
    if not fixture_path.exists():
        print_error(f"测试文件不存在: {fixture_path}")
        return False
    
    print_info(f"使用测试文件: {fixture_path}")
    
    try:
        # 将文件转换为Base64
        base64_str = read_file_as_base64(fixture_path)
        file_size = os.path.getsize(fixture_path)
        print_info(f"文件大小: {file_size} bytes, Base64长度: {len(base64_str)}")
        
        # 模拟文件上传（使用multipart/form-data）
        import io
        from urllib3 import encode_multipart_formdata
        
        # 创建文件对象
        file_content = open(fixture_path, "rb").read()
        files = {
            'file': ('quote.png', file_content, 'image/png')
        }
        
        # 构建multipart请求
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # 使用requests直接上传文件
        print_info("上传报价单文件...")
        upload_start = time.time()
        response = requests.post(
            f"{API_V1}/quotes/upload",
            files=files,
            headers=headers,
            timeout=60
        )
        upload_time = (time.time() - upload_start) * 1000
        
        if response.status_code == 200:
            print_success(f"报价单上传成功 - HTTP {response.status_code} ({upload_time:.0f}ms)")
            upload_result = response.json()
            quote_id = upload_result.get("task_id")
            
            if quote_id:
                print_info(f"报价单分析任务已创建，ID: {quote_id}")
                
                # 等待一段时间后获取结果
                print_info("等待15秒让OCR识别和AI分析执行...")
                time.sleep(15)
                
                # 获取分析结果
                success, result_result = test_endpoint(
                    "获取报价单分析结果",
                    "GET",
                    f"{API_V1}/quotes/quote/{quote_id}",
                    auth_token=token,
                    description=f"获取报价单分析结果，ID: {quote_id}",
                    problem_attribution="后台问题"
                )
                
                if success:
                    response_data = result_result.get("response", {})
                    print_debug(f"报价单分析结果预览: {json.dumps(response_data, ensure_ascii=False, indent=2)[:500]}")
                    
                    # 验证返回的数据结构
                    if response_data.get("status") == "completed":
                        print_success("报价单分析任务已完成")
                        
                        if response_data.get("risk_score") is not None:
                            print_success(f"风险评分: {response_data.get('risk_score')}")
                            
                        if response_data.get("high_risk_items"):
                            print_success(f"高风险项数量: {len(response_data.get('high_risk_items', []))}")
                            
                        if response_data.get("total_price"):
                            print_success(f"总价: {response_data.get('total_price')}")
                            
                        if response_data.get("is_unlocked"):
                            print_success("报告已解锁")
                    else:
                        print_warning(f"报价单分析任务状态: {response_data.get('status')}")
                        print_warning(f"分析进度: {response_data.get('analysis_progress', {})}")
                else:
                    print_error("获取报价单分析结果失败")
            else:
                print_error("上传响应中未找到task_id")
                return False
        else:
            print_error(f"报价单上传失败 - HTTP {response.status_code}")
            print_error(f"错误响应: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_error(f"报价单分析测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_contract_analysis_apis(token: str):
    """测试合同分析接口"""
    print_info("5. 合同分析接口测试")
    
    # 读取测试文件
    fixture_path = Path("tests/fixtures/深圳市住宅装饰装修工程施工合同（半包装修版）.png")
    if not fixture_path.exists():
        print_error(f"测试文件不存在: {fixture_path}")
        return False
    
    print_info(f"使用测试文件: {fixture_path}")
    
    try:
        # 模拟文件上传
        file_content = open(fixture_path, "rb").read()
        files = {
            'file': ('contract.png', file_content, 'image/png')
        }
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        print_info("上传合同文件...")
        upload_start = time.time()
        response = requests.post(
            f"{API_V1}/contracts/upload",
            files=files,
            headers=headers,
            timeout=60
        )
        upload_time = (time.time() - upload_start) * 1000
        
        if response.status_code == 200:
            print_success(f"合同上传成功 - HTTP {response.status_code} ({upload_time:.0f}ms)")
            upload_result = response.json()
            contract_id = upload_result.get("task_id")
            
            if contract_id:
                print_info(f"合同分析任务已创建，ID: {contract_id}")
                
                # 等待一段时间后获取结果
                print_info("等待15秒让OCR识别和AI分析执行...")
                time.sleep(15)
                
                # 获取分析结果
                success, result_result = test_endpoint(
                    "获取合同分析结果",
                    "GET",
                    f"{API_V1}/contracts/contract/{contract_id}",
                    auth_token=token,
                    description=f"获取合同分析结果，ID: {contract_id}",
                    problem_attribution="后台问题"
                )
                
                if success:
                    response_data = result_result.get("response", {})
                    print_debug(f"合同分析结果预览: {json.dumps(response_data, ensure_ascii=False, indent=2)[:500]}")
                    
                    # 验证返回的数据结构
                    if response_data.get("status") == "completed":
                        print_success("合同分析任务已完成")
                        
                        if response_data.get("risk_level"):
                            print_success(f"风险等级: {response_data.get('risk_level')}")
                            
                        if response_data.get("risk_items"):
                            print_success(f"风险条款数量: {len(response_data.get('risk_items', []))}")
                            
                        if response_data.get("unfair_terms"):
                            print_success(f"不公平条款数量: {len(response_data.get('unfair_terms', []))}")
                            
                        if response_data.get("is_unlocked"):
                            print_success("报告已解锁")
                    else:
                        print_warning(f"合同分析任务状态: {response_data.get('status')}")
                        print_warning(f"分析进度: {response_data.get('analysis_progress', {})}")
                else:
                    print_error("获取合同分析结果失败")
            else:
                print_error("上传响应中未找到task_id")
                return False
        else:
            print_error(f"合同上传失败 - HTTP {response.status_code}")
            print_error(f"错误响应: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_error(f"合同分析测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_acceptance_analysis_apis(token: str):
    """测试AI验收接口"""
    print_info("6. AI验收接口测试")
    
    # 读取测试文件
    fixture_path = Path("tests/fixtures/瓷砖验收.png")
    if not fixture_path.exists():
        # 尝试其他验收图片
        fixture_path = Path("tests/fixtures/防水验收.png")
        if not fixture_path.exists():
            print_error("未找到验收测试图片")
            return False
    
    print_info(f"使用测试文件: {fixture_path}")
    
    try:
        # 先上传验收照片
        file_content = open(fixture_path, "rb").read()
        files = {
            'file': ('acceptance.png', file_content, 'image/png')
        }
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        print_info("上传验收照片...")
        upload_start = time.time()
        response = requests.post(
            f"{API_V1}/acceptance/upload-photo",
            files=files,
            headers=headers,
            timeout=60
        )
        upload_time = (time.time() - upload_start) * 1000
        
        if response.status_code == 200:
            print_success(f"验收照片上传成功 - HTTP {response.status_code} ({upload_time:.0f}ms)")
            upload_result = response.json()
            file_url = upload_result.get("data", {}).get("file_url")
            object_key = upload_result.get("data", {}).get("object_key")
            
            if file_url or object_key:
                photo_url = file_url or object_key
                print_info(f"验收照片URL: {photo_url[:100]}...")
                
                # 提交验收分析
                print_info("提交验收分析...")
                success, analyze_result = test_endpoint(
                    "提交验收分析",
                    "POST",
                    f"{API_V1}/acceptance/analyze",
                    data={
                        "stage": "S01",  # 水电阶段
                        "file_urls": [photo_url]
                    },
                    auth_token=token,
                    description="提交验收照片进行AI分析",
                    problem_attribution="后台问题"
                )
                
                if success:
                    response_data = analyze_result.get("response", {})
                    analysis_id = response_data.get("data", {}).get("id")
                    
                    if analysis_id:
                        print_info(f"验收分析任务已创建，ID: {analysis_id}")
                        
                        # 等待一段时间后获取结果
                        print_info("等待10秒让AI分析执行...")
                        time.sleep(10)
                        
                        # 获取分析结果
                        success, result_result = test_endpoint(
                            "获取验收分析结果",
                            "GET",
                            f"{API_V1}/acceptance/{analysis_id}",
                            auth_token=token,
                            description=f"获取验收分析结果，ID: {analysis_id}",
                            problem_attribution="后台问题"
                        )
                        
                        if success:
                            response_data = result_result.get("response", {})
                            print_debug(f"验收分析结果预览: {json.dumps(response_data, ensure_ascii=False, indent=2)[:500]}")
                            
                            # 验证返回的数据结构
                            data = response_data.get("data", {})
                            if data.get("severity"):
                                print_success(f"严重程度: {data.get('severity')}")
                                
                            if data.get("issues"):
                                print_success(f"问题数量: {len(data.get('issues', []))}")
                                
                            if data.get("suggestions"):
                                print_success(f"建议数量: {len(data.get('suggestions', []))}")
                                
                            if data.get("result_status"):
                                print_success(f"结果状态: {data.get('result_status')}")
                        else:
                            print_error("获取验收分析结果失败")
                    else:
                        print_error("分析响应中未找到analysis_id")
                else:
                    print_error("提交验收分析失败")
            else:
                print_error("上传响应中未找到file_url或object_key")
                return False
        else:
            print_error(f"验收照片上传失败 - HTTP {response.status_code}")
            print_error(f"错误响应: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_error(f"AI验收测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("核心AI接口功能测试")
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
        return False
    
    # 3. 测试公司风险扫描接口
    print_info("阶段3: 公司风险扫描接口测试")
    test_company_scan_apis(token)
    
    # 4. 测试报价单分析接口
    print_info("阶段4: 报价单分析接口测试")
    test_quote_analysis_apis(token)
    
    # 5. 测试合同分析接口
    print_info("阶段5: 合同分析接口测试")
    test_contract_analysis_apis(token)
    
    # 6. 测试AI验收接口
    print_info("阶段6: AI验收接口测试")
    test_acceptance_analysis_apis(token)
    
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
    
    # 按问题归属分类
    print(f"\n问题归属分析:")
    attributions = {}
    for result in test_results:
        if not result.get("success"):
            attribution = result.get("problem_attribution", "待分析")
            attributions[attribution] = attributions.get(attribution, 0) + 1
    
    for attribution, count in attributions.items():
        print(f"  - {attribution}: {count}个问题")
    
    # 显示失败的测试
    if failed_tests > 0:
        print(f"\n{Colors.RED}失败的测试:{Colors.END}")
        for result in test_results:
            if not result.get("success") and not result.get("skip_on_failure"):
                error_msg = result.get('error', f'HTTP {result.get("status_code")}')
                print(f"  - {result.get('name')}: {error_msg}")
                print(f"    归属: {result.get('problem_attribution')}")
                if result.get("description"):
                    print(f"    描述: {result.get('description')}")
    
    # 显示跳过的测试
    if skipped_tests > 0:
        print(f"\n{Colors.YELLOW}跳过的测试:{Colors.END}")
        for result in test_results:
            if not result.get("success") and result.get("skip_on_failure"):
                status = result.get('status_code', 'N/A')
                print(f"  - {result.get('name')}: HTTP {status}")
                print(f"    归属: {result.get('problem_attribution')}")
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
    results_file = "tests/core-ai-apis-test-results.json"
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
    print("开始核心AI接口功能测试...")
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"测试执行异常: {str(e)}")
        sys.exit(1)

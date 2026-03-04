#!/usr/bin/env python3
"""
AI功能测试脚本
测试报价单分析、合同分析、AI验收功能
"""

import requests
import json
import time
import os
from typing import Dict, Any

# 配置
BASE_URL = "https://lakeli.top/api/v1"
TEST_USER_ID = 1  # 测试用户ID
TEST_COMPANY_ID = 1  # 测试公司ID

def test_health():
    """测试API健康状态"""
    print("=== 测试API健康状态 ===")
    try:
        response = requests.get(f"{BASE_URL}/health", verify=False, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_quote_analysis():
    """测试报价单分析功能"""
    print("\n=== 测试报价单分析功能 ===")
    
    # 1. 上传测试报价单文件
    print("1. 测试报价单上传...")
    test_file_path = "test_quote_pdf.pdf"
    
    if not os.path.exists(test_file_path):
        print(f"⚠️ 测试文件不存在: {test_file_path}")
        print("创建模拟测试文件...")
        # 创建简单的PDF文件（仅用于测试）
        pdf_content = b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<<>>>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer\n<</Size 4/Root 1 0 R>>\nstartxref\n149\n%%EOF"
        with open(test_file_path, "wb") as f:
            f.write(pdf_content)
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f, "application/pdf")}
            data = {
                "company_id": TEST_COMPANY_ID,
                "user_id": TEST_USER_ID,
                "file_type": "quote"
            }
            response = requests.post(
                f"{BASE_URL}/quotes/upload",
                files=files,
                data=data,
                verify=False,
                timeout=30
            )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"上传成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
            quote_id = result.get("data", {}).get("quote_id")
            return quote_id
        else:
            print(f"上传失败: {response.text}")
            return None
    except Exception as e:
        print(f"报价单上传测试失败: {e}")
        return None

def test_contract_analysis():
    """测试合同分析功能"""
    print("\n=== 测试合同分析功能 ===")
    
    # 1. 上传测试合同文件
    print("1. 测试合同上传...")
    test_file_path = "test_contract_pdf.pdf"
    
    if not os.path.exists(test_file_path):
        print(f"⚠️ 测试文件不存在: {test_file_path}")
        print("创建模拟测试文件...")
        # 创建简单的PDF文件（仅用于测试）
        pdf_content = b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<<>>>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer\n<</Size 4/Root 1 0 R>>\nstartxref\n149\n%%EOF"
        with open(test_file_path, "wb") as f:
            f.write(pdf_content)
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f, "application/pdf")}
            data = {
                "company_id": TEST_COMPANY_ID,
                "user_id": TEST_USER_ID,
                "file_type": "contract"
            }
            response = requests.post(
                f"{BASE_URL}/contracts/upload",
                files=files,
                data=data,
                verify=False,
                timeout=30
            )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"上传成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
            contract_id = result.get("data", {}).get("contract_id")
            return contract_id
        else:
            print(f"上传失败: {response.text}")
            return None
    except Exception as e:
        print(f"合同上传测试失败: {e}")
        return None

def test_acceptance_analysis():
    """测试AI验收功能"""
    print("\n=== 测试AI验收功能 ===")
    
    # 1. 创建测试验收任务
    print("1. 测试创建验收任务...")
    
    test_data = {
        "company_id": TEST_COMPANY_ID,
        "user_id": TEST_USER_ID,
        "project_name": "测试装修项目",
        "project_address": "测试地址",
        "construction_area": 100.5,
        "construction_type": "住宅装修",
        "budget": 150000.0,
        "start_date": "2024-01-01",
        "planned_end_date": "2024-03-01",
        "description": "这是一个测试验收项目"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/acceptance/create",
            json=test_data,
            verify=False,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"创建成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
            acceptance_id = result.get("data", {}).get("acceptance_id")
            return acceptance_id
        else:
            print(f"创建失败: {response.text}")
            return None
    except Exception as e:
        print(f"验收任务创建测试失败: {e}")
        return None

def test_ai_service_health():
    """测试AI服务健康状态"""
    print("\n=== 测试AI服务健康状态 ===")
    
    endpoints = [
        "/quotes/upload",
        "/contracts/upload", 
        "/acceptance/create"
    ]
    
    for endpoint in endpoints:
        try:
            # 使用HEAD请求检查端点是否存在
            response = requests.head(
                f"{BASE_URL}{endpoint}",
                verify=False,
                timeout=10
            )
            print(f"{endpoint}: {'可用' if response.status_code != 404 else '不可用'} (状态码: {response.status_code})")
        except Exception as e:
            print(f"{endpoint}: 检查失败 - {e}")

def generate_test_report():
    """生成测试报告"""
    print("\n" + "="*60)
    print("AI功能测试报告")
    print("="*60)
    
    report = {
        "测试时间": time.strftime("%Y-%m-%d %H:%M:%S"),
        "测试环境": BASE_URL,
        "测试结果": {}
    }
    
    # 测试API健康
    health_ok = test_health()
    report["测试结果"]["API健康状态"] = "通过" if health_ok else "失败"
    
    # 测试AI服务端点
    test_ai_service_health()
    
    # 测试报价单分析
    quote_id = test_quote_analysis()
    report["测试结果"]["报价单分析"] = "通过" if quote_id else "失败"
    
    # 测试合同分析
    contract_id = test_contract_analysis()
    report["测试结果"]["合同分析"] = "通过" if contract_id else "失败"
    
    # 测试AI验收
    acceptance_id = test_acceptance_analysis()
    report["测试结果"]["AI验收功能"] = "通过" if acceptance_id else "失败"
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    total_tests = len(report["测试结果"])
    passed_tests = sum(1 for result in report["测试结果"].values() if result == "通过")
    
    print(f"总测试项: {total_tests}")
    print(f"通过项: {passed_tests}")
    print(f"失败项: {total_tests - passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    
    # 保存报告到文件
    report_file = "ai_function_test_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细测试报告已保存到: {report_file}")
    
    return report

if __name__ == "__main__":
    print("开始AI功能测试...")
    print(f"测试环境: {BASE_URL}")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 禁用SSL警告（仅用于测试）
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    report = generate_test_report()
    
    # 输出最终结果
    if all(result == "通过" for result in report["测试结果"].values()):
        print("\n✅ 所有AI功能测试通过！")
    else:
        print("\n⚠️ 部分AI功能测试失败，请检查日志。")
    
    print("\n测试完成！")

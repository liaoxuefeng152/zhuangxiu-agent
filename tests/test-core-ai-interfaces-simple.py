#!/usr/bin/env python3
"""
简单测试核心AI接口：公司风险扫描、报价单分析、合同分析、AI验收
使用阿里云生产环境
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

# 阿里云生产环境配置
ALIYUN_API_BASE = "http://120.26.201.61:8000"
API_V1 = f"{ALIYUN_API_BASE}/api/v1"

# 测试计数器
passed = 0
failed = 0
skipped = 0

def print_result(success, test_name, message=""):
    global passed, failed, skipped
    if success == "PASS":
        passed += 1
        print(f"✓ {test_name}: 通过")
    elif success == "FAIL":
        failed += 1
        print(f"✗ {test_name}: 失败 - {message}")
    else:
        skipped += 1
        print(f"⚠ {test_name}: 跳过 - {message}")

def test_health_check():
    """测试健康检查接口"""
    try:
        url = f"{ALIYUN_API_BASE}/health"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print_result("PASS", "健康检查", f"HTTP {response.status_code}")
            return True
        else:
            print_result("FAIL", "健康检查", f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result("FAIL", "健康检查", str(e))
        return False

def test_company_scan():
    """测试公司风险扫描接口"""
    try:
        # 1. 搜索公司
        url = f"{API_V1}/companies/search?keyword=装修"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_result("PASS", "公司搜索", f"找到 {len(data.get('data', {}).get('list', []))} 条记录")
        else:
            print_result("FAIL", "公司搜索", f"HTTP {response.status_code}")
            return
        
        # 2. 提交公司检测
        url = f"{API_V1}/companies/scan"
        payload = {"company_name": "深圳市装修有限公司"}
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            scan_id = data.get('data', {}).get('id')
            print_result("PASS", "提交公司检测", f"扫描ID: {scan_id}")
            
            # 3. 获取检测结果
            if scan_id:
                url = f"{API_V1}/companies/scan/{scan_id}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print_result("PASS", "获取公司检测结果", "成功")
                else:
                    print_result("FAIL", "获取公司检测结果", f"HTTP {response.status_code}")
        else:
            print_result("FAIL", "提交公司检测", f"HTTP {response.status_code}")
            
    except Exception as e:
        print_result("FAIL", "公司风险扫描接口", str(e))

def test_quote_analysis():
    """测试报价单分析接口"""
    try:
        # 上传报价单图片
        quote_file = "fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png"
        if not os.path.exists(quote_file):
            print_result("SKIP", "报价单分析", f"测试文件不存在: {quote_file}")
            return
            
        url = f"{API_V1}/quotes/upload"
        files = {'file': open(quote_file, 'rb')}
        response = requests.post(url, files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            quote_id = data.get('data', {}).get('task_id')
            print_result("PASS", "上传报价单", f"报价单ID: {quote_id}")
            
            # 等待分析完成
            if quote_id:
                print("等待报价单分析完成...")
                time.sleep(10)
                
                # 获取分析结果
                url = f"{API_V1}/quotes/quote/{quote_id}"
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == 200:
                        print_result("PASS", "获取报价单分析结果", "成功")
                    else:
                        print_result("FAIL", "获取报价单分析结果", f"API错误: {data.get('msg')}")
                else:
                    print_result("FAIL", "获取报价单分析结果", f"HTTP {response.status_code}")
        else:
            print_result("FAIL", "上传报价单", f"HTTP {response.status_code}")
            
    except Exception as e:
        print_result("FAIL", "报价单分析接口", str(e))

def test_contract_analysis():
    """测试合同分析接口"""
    try:
        # 上传合同图片
        contract_file = "fixtures/深圳市住宅装饰装修工程施工合同（半包装修版）.png"
        if not os.path.exists(contract_file):
            print_result("SKIP", "合同分析", f"测试文件不存在: {contract_file}")
            return
            
        url = f"{API_V1}/contracts/upload"
        files = {'file': open(contract_file, 'rb')}
        response = requests.post(url, files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            contract_id = data.get('data', {}).get('task_id')
            print_result("PASS", "上传合同", f"合同ID: {contract_id}")
            
            # 等待分析完成
            if contract_id:
                print("等待合同分析完成...")
                time.sleep(10)
                
                # 获取分析结果
                url = f"{API_V1}/contracts/contract/{contract_id}"
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == 200:
                        print_result("PASS", "获取合同分析结果", "成功")
                    else:
                        print_result("FAIL", "获取合同分析结果", f"API错误: {data.get('msg')}")
                else:
                    print_result("FAIL", "获取合同分析结果", f"HTTP {response.status_code}")
        else:
            print_result("FAIL", "上传合同", f"HTTP {response.status_code}")
            
    except Exception as e:
        print_result("FAIL", "合同分析接口", str(e))

def test_acceptance_analysis():
    """测试AI验收接口"""
    try:
        # 上传验收照片
        acceptance_file = "fixtures/acceptance-photo.png"
        if not os.path.exists(acceptance_file):
            print_result("SKIP", "AI验收", f"测试文件不存在: {acceptance_file}")
            return
            
        # 1. 上传照片
        url = f"{API_V1}/acceptance/upload-photo"
        files = {'file': open(acceptance_file, 'rb')}
        response = requests.post(url, files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            file_url = data.get('data', {}).get('file_url')
            print_result("PASS", "上传验收照片", "成功")
            
            # 2. 进行分析
            if file_url:
                url = f"{API_V1}/acceptance/analyze"
                payload = {
                    "stage": "S01",  # 隐蔽工程阶段
                    "file_urls": [file_url]
                }
                response = requests.post(url, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    analysis_id = data.get('data', {}).get('id')
                    print_result("PASS", "验收分析", f"分析ID: {analysis_id}")
                else:
                    print_result("FAIL", "验收分析", f"HTTP {response.status_code}")
        else:
            print_result("FAIL", "上传验收照片", f"HTTP {response.status_code}")
            
    except Exception as e:
        print_result("FAIL", "AI验收接口", str(e))

def main():
    print("=" * 70)
    print("核心AI接口简单测试")
    print(f"API地址: {ALIYUN_API_BASE}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 测试健康检查
    print("\n1. 健康检查测试")
    if not test_health_check():
        print("健康检查失败，停止测试")
        return
    
    # 测试公司风险扫描接口
    print("\n2. 公司风险扫描接口测试")
    test_company_scan()
    
    # 测试报价单分析接口
    print("\n3. 报价单分析接口测试")
    test_quote_analysis()
    
    # 测试合同分析接口
    print("\n4. 合同分析接口测试")
    test_contract_analysis()
    
    # 测试AI验收接口
    print("\n5. AI验收接口测试")
    test_acceptance_analysis()
    
    # 打印测试总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"总测试数: {passed + failed + skipped}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"跳过: {skipped}")
    
    if failed == 0:
        print("\n✅ 所有接口测试通过！")
    else:
        print(f"\n❌ 有 {failed} 个测试失败")

if __name__ == "__main__":
    main()

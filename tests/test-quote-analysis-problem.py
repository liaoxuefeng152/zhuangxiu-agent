#!/usr/bin/env python3
"""
诊断报价单分析问题
直接测试报价单上传和分析流程
"""

import requests
import time
import json
from pathlib import Path

# 生产环境配置
PRODUCTION_API_BASE = "https://lakeli.top"
API_V1 = f"{PRODUCTION_API_BASE}/api/v1"

def test_quote_upload_direct():
    """直接测试报价单上传，不使用认证"""
    print("测试报价单上传和分析问题")
    print(f"API地址: {API_V1}")
    print("=" * 60)
    
    # 使用测试数据中的报价单图片
    fixture_path = Path("tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png")
    if not fixture_path.exists():
        print(f"错误: 测试文件不存在: {fixture_path}")
        return
    
    print(f"使用测试文件: {fixture_path}")
    
    try:
        # 首先尝试不使用认证
        with open(fixture_path, "rb") as f:
            files = {"file": ("quote.png", f, "image/png")}
            
            print("1. 尝试上传报价单（无认证）...")
            response = requests.post(
                f"{API_V1}/quotes/upload",
                files=files,
                timeout=60
            )
            
            print(f"  状态码: {response.status_code}")
            if response.text:
                print(f"  响应: {response.text[:500]}")
            
            if response.status_code == 401:
                print("  需要认证，尝试使用开发环境mock token...")
                # 尝试使用开发环境的mock token
                headers = {"Authorization": "Bearer dev_mock_token"}
                f.seek(0)  # 重置文件指针
                response2 = requests.post(
                    f"{API_V1}/quotes/upload",
                    files=files,
                    headers=headers,
                    timeout=60
                )
                print(f"  使用mock token状态码: {response2.status_code}")
                if response2.text:
                    print(f"  响应: {response2.text[:500]}")
                    
    except Exception as e:
        print(f"异常: {str(e)}")

def test_health_and_system():
    """测试系统健康状态"""
    print("\n2. 测试系统健康状态")
    
    endpoints = [
        ("健康检查", f"{PRODUCTION_API_BASE}/health"),
        ("API文档", f"{PRODUCTION_API_BASE}/docs"),
        ("OpenAPI JSON", f"{PRODUCTION_API_BASE}/openapi.json"),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            print(f"{name}: HTTP {response.status_code}")
            if response.status_code != 200:
                print(f"  响应: {response.text[:200]}")
        except Exception as e:
            print(f"{name}: 错误 - {str(e)}")

def test_ocr_service():
    """测试OCR服务配置"""
    print("\n3. 检查OCR服务配置")
    
    # 检查本地OCR服务配置
    config_path = Path("backend/app/core/config.py")
    if config_path.exists():
        print(f"找到配置文件: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "ALIYUN_OCR_ENDPOINT" in content:
                print("  OCR端点配置: 存在")
            if "ECS RAM" in content:
                print("  ECS RAM角色配置: 存在")
    
    # 检查OCR服务文件
    ocr_service_path = Path("backend/app/services/ocr_service.py")
    if ocr_service_path.exists():
        print(f"找到OCR服务文件: {ocr_service_path}")
        with open(ocr_service_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "recognize_quote" in content:
                print("  报价单识别函数: 存在")
            if "阿里云OCR服务" in content:
                print("  阿里云OCR服务: 已配置")

def check_recent_changes():
    """检查最近的代码更改"""
    print("\n4. 检查最近的代码更改")
    
    try:
        import subprocess
        # 检查git状态
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd="/Users/mac/zhuangxiu-agent"
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print("未提交的更改:")
            for line in result.stdout.strip().split("\n"):
                if line:
                    print(f"  {line}")
        else:
            print("没有未提交的更改")
            
        # 检查最近的提交
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True,
            text=True,
            cwd="/Users/mac/zhuangxiu-agent"
        )
        
        if result.returncode == 0:
            print("\n最近的提交:")
            for line in result.stdout.strip().split("\n"):
                if line:
                    print(f"  {line}")
                    
    except Exception as e:
        print(f"检查git状态失败: {str(e)}")

def main():
    print("=" * 60)
    print("报价单分析问题诊断")
    print("=" * 60)
    
    test_health_and_system()
    test_ocr_service()
    check_recent_changes()
    test_quote_upload_direct()
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

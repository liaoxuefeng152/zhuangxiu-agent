#!/usr/bin/env python3
"""
OCR识别详细测试脚本
用于诊断OCR识别问题
"""
import os
import sys
_d = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(_d) not in sys.path:
    sys.path.insert(0, os.path.dirname(_d))
import requests
from tests import fixture_path, QUOTE_PNG, CONTRACT_PNG
import json
import base64
import os
import io

API_BASE = "http://localhost:8000"
API_V1 = f"{API_BASE}/api/v1"

# 登录获取token
def login():
    # 使用与test-enhanced.py相同的登录方式
    response = requests.post(
        f"{API_V1}/users/login",
        json={"code": "dev_h5_mock"}
    )
    if response.status_code == 200:
        data = response.json()
        # 尝试多种可能的token字段名
        token = (data.get("data", {}) or {}).get("access_token") or data.get("access_token") or (data.get("data", {}) or {}).get("token")
        if token:
            print(f"✅ 登录成功，Token: {token[:20]}...")
            return token
    print(f"❌ 登录失败，状态码: {response.status_code}, 响应: {response.text[:200]}")
    return None

def test_quote_upload():
    """测试报价单上传和OCR识别"""
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 优先使用PNG图片，如果没有则使用PDF
    png_path = fixture_path(QUOTE_PNG)
    pdf_path = fixture_path("2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.pdf")
    
    file_path = png_path if os.path.exists(png_path) else (pdf_path if os.path.exists(pdf_path) else None)
    file_ext = "png" if os.path.exists(png_path) else ("pdf" if os.path.exists(pdf_path) else None)
    mime_type = "image/png" if file_ext == "png" else "application/pdf"
    
    if not file_path or not os.path.exists(file_path):
        print(f"❌ 报价单文件不存在: {png_path}")
        return
    
    print(f"📄 读取报价单: {file_path} ({file_ext})")
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    print(f"📊 文件大小: {len(file_content)} bytes ({len(file_content)/1024:.2f} KB)")
    
    files = {"file": (os.path.basename(file_path), io.BytesIO(file_content), mime_type)}
    print("📤 上传文件...")
    response = requests.post(
        f"{API_V1}/quotes/upload",
        headers=headers,
        files=files,
        timeout=60
    )
    
    print(f"📥 响应状态码: {response.status_code}")
    print(f"📥 响应内容: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 上传成功")
        print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
    else:
        print(f"❌ 上传失败")
        try:
            error_data = response.json()
            print(f"   错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"   错误文本: {response.text}")

def test_contract_upload():
    """测试合同上传和OCR识别"""
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 优先使用PNG图片，如果没有则使用PDF
    png_path = fixture_path(CONTRACT_PNG)
    pdf_path = fixture_path("深圳市住宅装饰装修工程施工合同（半包装修版）.pdf")
    
    file_path = png_path if os.path.exists(png_path) else (pdf_path if os.path.exists(pdf_path) else None)
    file_ext = "png" if os.path.exists(png_path) else ("pdf" if os.path.exists(pdf_path) else None)
    mime_type = "image/png" if file_ext == "png" else "application/pdf"
    
    if not file_path or not os.path.exists(file_path):
        print(f"❌ 合同文件不存在: {png_path}")
        return
    
    print(f"\n📄 读取合同: {file_path} ({file_ext})")
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    print(f"📊 文件大小: {len(file_content)} bytes ({len(file_content)/1024:.2f} KB)")
    
    # 上传文件
    files = {"file": (os.path.basename(file_path), io.BytesIO(file_content), mime_type)}
    
    print("📤 上传文件...")
    response = requests.post(
        f"{API_V1}/contracts/upload",
        headers=headers,
        files=files,
        timeout=60
    )
    
    print(f"📥 响应状态码: {response.status_code}")
    print(f"📥 响应内容: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 上传成功")
        print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
    else:
        print(f"❌ 上传失败")
        try:
            error_data = response.json()
            print(f"   错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"   错误文本: {response.text}")

if __name__ == "__main__":
    print("=" * 60)
    print("OCR识别详细测试")
    print("=" * 60)
    
    print("\n【测试1: 报价单上传和OCR识别】")
    test_quote_upload()
    
    print("\n【测试2: 合同上传和OCR识别】")
    test_contract_upload()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

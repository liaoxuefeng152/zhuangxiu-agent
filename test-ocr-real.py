#!/usr/bin/env python3
"""
测试真实OCR识别（不使用模拟文本）
"""
import requests
import time
import os
import io

BASE_URL = "http://localhost:8000/api/v1"

def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/users/login",
        json={"code": "dev_h5_mock"}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("access_token") or data.get("access_token")
    return None

def test_real_ocr():
    """测试真实OCR识别"""
    print("=" * 70)
    print("测试真实OCR识别（不使用模拟文本）")
    print("=" * 70)
    
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 上传报价单文件
    quote_png_path = "2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png"
    if not os.path.exists(quote_png_path):
        print(f"❌ 测试文件不存在")
        return
    
    print(f"\n📤 上传文件: {quote_png_path}")
    with open(quote_png_path, "rb") as f:
        file_content = f.read()
    
    files = {"file": (os.path.basename(quote_png_path), io.BytesIO(file_content), "image/png")}
    response = requests.post(
        f"{BASE_URL}/quotes/upload",
        headers=headers,
        files=files
    )
    
    if response.status_code != 200:
        print(f"❌ 上传失败: {response.status_code}")
        print(f"错误: {response.text}")
        return
    
    data = response.json()
    quote_id = data.get("data", {}).get("task_id") or data.get("task_id")
    print(f"✅ 上传成功，Quote ID: {quote_id}")
    
    # 等待分析完成
    print(f"\n⏳ 等待分析完成...")
    for i in range(30):
        time.sleep(2)
        response = requests.get(
            f"{BASE_URL}/quotes/quote/{quote_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            quote_data = result.get("data", {}) or result
            status = quote_data.get("status")
            
            if status == "completed":
                print(f"\n✅ 分析完成！")
                
                # 检查是否使用了真实OCR
                # 如果使用了模拟文本，总价应该是9600.0（模拟文本中的第一个价格）
                # 如果使用了真实OCR，总价应该不同
                total_price = quote_data.get('total_price')
                print(f"\n📊 分析结果:")
                print(f"   总价: {total_price} 元")
                
                # 检查OCR结果
                # 如果后端返回了ocr_result字段，说明使用了真实OCR
                # 注意：QuoteAnalysisResponse可能不包含ocr_result字段
                
                print(f"\n💡 判断方法:")
                print(f"   - 如果总价是9600.0元，可能是使用了模拟文本")
                print(f"   - 如果总价是80000元或其他值，说明使用了真实OCR")
                print(f"   - 如果后端日志显示'使用Base64编码进行OCR识别'，说明尝试了真实OCR")
                
                return True
            elif status == "failed":
                print(f"\n❌ 分析失败")
                return False
    
    print(f"\n⏰ 等待超时")
    return False

if __name__ == "__main__":
    test_real_ocr()

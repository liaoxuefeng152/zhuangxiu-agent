#!/usr/bin/env python3
"""
测试AI设计师图片上传功能
"""
import requests
import json
import os
from pathlib import Path

# 测试配置
BASE_URL = "http://localhost:8001/api/v1"
TEST_TOKEN = "test_token_123"  # 需要替换为实际有效的token
TEST_USER_ID = 1

def test_upload_image():
    """测试图片上传功能"""
    print("=== 测试AI设计师图片上传功能 ===")
    
    # 准备测试图片
    test_image_path = Path("test_image.jpg")
    if not test_image_path.exists():
        # 创建一个简单的测试图片
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(test_image_path)
        print(f"创建测试图片: {test_image_path}")
    
    # 构建请求头
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "X-User-Id": str(TEST_USER_ID)
    }
    
    # 上传图片
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test_image.jpg', f, 'image/jpeg')}
            response = requests.post(
                f"{BASE_URL}/designer/upload-image",
                headers=headers,
                files=files
            )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"上传结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print("✅ 图片上传成功!")
                print(f"图片URL: {result.get('image_url')}")
                return result.get('image_url')
            else:
                print(f"❌ 上传失败: {result.get('error_message')}")
        elif response.status_code == 401:
            print("❌ 认证失败，请检查token")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    return None

def test_chat_with_image(image_url):
    """测试带图片的聊天功能"""
    print("\n=== 测试带图片的聊天功能 ===")
    
    if not image_url:
        print("❌ 没有图片URL，跳过聊天测试")
        return
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "X-User-Id": str(TEST_USER_ID),
        "Content-Type": "application/json"
    }
    
    # 先创建聊天session
    try:
        print("创建聊天session...")
        session_response = requests.post(
            f"{BASE_URL}/designer/sessions",
            headers=headers,
            json={"initial_question": "你好，我是测试用户"}
        )
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data.get('session_id')
            print(f"✅ 创建session成功: {session_id}")
            
            # 发送带图片的消息
            print("发送带图片的聊天消息...")
            chat_data = {
                "session_id": session_id,
                "message": "请帮我分析一下这个户型图",
                "image_urls": [image_url]
            }
            
            chat_response = requests.post(
                f"{BASE_URL}/designer/chat",
                headers=headers,
                json=chat_data
            )
            
            print(f"状态码: {chat_response.status_code}")
            if chat_response.status_code == 200:
                chat_result = chat_response.json()
                print("✅ 发送消息成功!")
                print(f"AI回复: {chat_result.get('answer', '')[:200]}...")
            else:
                print(f"❌ 发送消息失败: {chat_response.text}")
        else:
            print(f"❌ 创建session失败: {session_response.text}")
            
    except Exception as e:
        print(f"❌ 聊天测试异常: {e}")

def test_health_check():
    """测试健康检查"""
    print("\n=== 测试AI设计师健康检查 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/designer/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 健康检查通过")
        else:
            print("❌ 健康检查失败")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")

def main():
    """主测试函数"""
    print("开始测试AI设计师图片上传功能...")
    
    # 测试健康检查
    test_health_check()
    
    # 测试图片上传
    image_url = test_upload_image()
    
    # 测试带图片的聊天
    if image_url:
        test_chat_with_image(image_url)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()

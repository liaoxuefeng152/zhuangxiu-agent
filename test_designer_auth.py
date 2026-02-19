#!/usr/bin/env python3
"""
测试AI设计师API认证问题
"""
import requests
import json
import sys

BASE_URL = "http://120.26.201.61:8001/api/v1"

def test_designer_api_with_token(token):
    """使用token测试设计师API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"测试token: {token[:20]}...")
    
    # 测试健康检查（不需要token）
    print("\n1. 测试健康检查（不需要token）:")
    try:
        response = requests.get(f"{BASE_URL}/designer/health", timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试创建session（需要token）
    print("\n2. 测试创建聊天session（需要token）:")
    try:
        response = requests.post(
            f"{BASE_URL}/designer/sessions",
            headers=headers,
            json={},
            timeout=10
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   成功! session_id: {data.get('session_id')}")
            print(f"   用户ID: {data.get('user_id')}")
            print(f"   消息数量: {len(data.get('messages', []))}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   错误: {e}")
    
    return response.status_code

def main():
    print("=== AI设计师API认证测试 ===\n")
    
    # 从命令行参数获取token，如果没有则提示
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = input("请输入JWT token（或按Enter使用测试token）: ").strip()
        if not token:
            # 使用之前看到的过期token作为测试
            token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJvcGVuaWQiOiJvQlRKZzNhSzE5S3lXc1lRZUNvU25NVng1aENnIiwiZXhwIjoxNzcyMDg1NTA1fQ.IWYh82-GAvqEXd8_mOEzNfM1EvoEQvw4Y2sgkTmIArM"
            print(f"使用测试token（已过期）: {token[:20]}...")
    
    status_code = test_designer_api_with_token(token)
    
    print(f"\n=== 测试完成 ===")
    if status_code == 200:
        print("✅ API调用成功！token有效")
    elif status_code == 401:
        print("❌ 401错误：token无效或已过期")
        print("   可能原因：")
        print("   1. token已过期")
        print("   2. JWT_SECRET_KEY不匹配")
        print("   3. 用户不存在")
    else:
        print(f"⚠️  其他错误：状态码 {status_code}")

if __name__ == "__main__":
    main()

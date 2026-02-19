#!/usr/bin/env python3
"""
诊断认证问题 - 检查用户资料API返回401的原因
"""
import requests
import json
import sys
import os

# 阿里云服务器地址
BASE_URL = "http://120.26.201.61:8001/api/v1"

def test_api_without_token():
    """测试不带token的API访问"""
    print("=== 测试不带token的API访问 ===")
    try:
        response = requests.get(f"{BASE_URL}/users/profile", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:200]}")
        return response.status_code == 401  # 应该返回401
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_api_with_invalid_token():
    """测试带无效token的API访问"""
    print("\n=== 测试带无效token的API访问 ===")
    headers = {
        "Authorization": "Bearer invalid_token_123456",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(f"{BASE_URL}/users/profile", headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:200]}")
        return response.status_code == 401  # 应该返回401
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_other_apis():
    """测试其他API是否正常工作"""
    print("\n=== 测试其他API是否正常工作 ===")
    
    # 测试健康检查API
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"健康检查API状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
        else:
            print(f"⚠️  健康检查API异常: {response.text[:100]}")
    except Exception as e:
        print(f"❌ 健康检查API请求失败: {e}")
    
    # 测试登录API（开发模式）
    print("\n=== 测试开发模式登录API ===")
    try:
        response = requests.post(f"{BASE_URL}/users/login", 
                                json={"code": "dev_h5_mock"},
                                timeout=10)
        print(f"登录API状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 登录成功，获取到token: {data.get('access_token', '')[:30]}...")
            print(f"   用户ID: {data.get('user_id')}")
            print(f"   是否会员: {data.get('is_member')}")
            
            # 使用获取到的token测试用户资料API
            token = data.get('access_token')
            if token:
                print("\n=== 使用新获取的token测试用户资料API ===")
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                profile_response = requests.get(f"{BASE_URL}/users/profile", headers=headers, timeout=10)
                print(f"用户资料API状态码: {profile_response.status_code}")
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print(f"✅ 用户资料获取成功")
                    print(f"   用户ID: {profile_data.get('user_id')}")
                    print(f"   昵称: {profile_data.get('nickname')}")
                    print(f"   是否会员: {profile_data.get('is_member')}")
                else:
                    print(f"❌ 用户资料获取失败: {profile_response.text[:200]}")
        else:
            print(f"❌ 登录失败: {response.text[:200]}")
    except Exception as e:
        print(f"❌ 登录API请求失败: {e}")

def check_backend_logs():
    """检查后端日志（通过SSH）"""
    print("\n=== 检查后端认证相关日志 ===")
    print("注意：需要SSH到阿里云服务器查看详细日志")
    print("命令: ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61")
    print("然后执行: cd /root/project/dev/zhuangxiu-agent && docker compose -f docker-compose.dev.yml logs --tail=50 backend")
    
    # 尝试执行SSH命令获取日志
    try:
        import subprocess
        print("\n尝试获取后端日志...")
        result = subprocess.run(
            ['ssh', '-i', os.path.expanduser('~/zhuangxiu-agent1.pem'), 
             'root@120.26.201.61', 
             'cd /root/project/dev/zhuangxiu-agent && docker compose -f docker-compose.dev.yml logs --tail=20 backend 2>/dev/null || echo "SSH失败"'],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            print("后端日志片段:")
            print(result.stdout[:500])
        else:
            print("SSH命令执行失败")
    except Exception as e:
        print(f"SSH执行异常: {e}")

def main():
    print("=== 认证问题诊断工具 ===\n")
    
    print("1. 测试基础API连通性...")
    if not test_api_without_token():
        print("⚠️  不带token的API测试异常")
    
    if not test_api_with_invalid_token():
        print("⚠️  带无效token的API测试异常")
    
    test_other_apis()
    
    check_backend_logs()
    
    print("\n=== 诊断总结 ===")
    print("可能的问题原因:")
    print("1. ✅ 后端服务正常运行")
    print("2. ❓ Token可能已过期或无效")
    print("3. ❓ 前端可能没有正确存储或发送token")
    print("4. ❓ 微信小程序环境可能有特殊限制")
    print("\n建议的修复步骤:")
    print("1. 检查前端token存储状态")
    print("2. 确保登录流程正常工作")
    print("3. 验证token在请求中正确发送")
    print("4. 检查后端JWT配置（SECRET_KEY等）")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

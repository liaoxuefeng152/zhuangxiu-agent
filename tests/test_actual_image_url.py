#!/usr/bin/env python3
"""
测试实际的图片URL可访问性
"""
import requests
import json
import time

# 阿里云服务器地址
BASE_URL = "http://120.26.201.61:8001/api/v1"

def test_upload_and_access():
    """测试上传图片并验证URL可访问性"""
    print("测试图片上传和URL可访问性...")
    
    # 首先获取一个有效的token（模拟登录）
    print("1. 获取测试token...")
    login_data = {
        "code": "test_code_123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            print(f"✓ 获取到token: {token[:20]}..., user_id: {user_id}")
            
            # 测试上传图片
            print("\n2. 测试上传图片...")
            files = {'file': ('test_image.jpg', b'fake_image_data', 'image/jpeg')}
            headers = {
                'Authorization': f'Bearer {token}',
                'X-User-Id': str(user_id)
            }
            
            # 注意：这里需要实际的图片文件，但我们先测试端点
            print("   注意：需要实际图片文件进行测试，跳过上传步骤")
            
            # 从日志中获取一个实际的图片URL进行测试
            print("\n3. 从日志中获取实际图片URL进行测试...")
            # 根据日志，图片URL格式应该是：
            # https://zhuangxiu-images-dev-photo.oss-cn-hangzhou.aliyuncs.com/designer/1/1771495823_1545.png?Expires=...
            
            # 让我们构造一个测试URL
            test_url = "https://zhuangxiu-images-dev-photo.oss-cn-hangzhou.aliyuncs.com/designer/1/1771495823_1545.png"
            
            print(f"   测试URL: {test_url}")
            
            # 测试URL可访问性
            print("\n4. 测试URL可访问性...")
            try:
                response = requests.get(test_url, timeout=10)
                print(f"   状态码: {response.status_code}")
                print(f"   响应头: {dict(response.headers)}")
                
                if response.status_code == 200:
                    print("   ✓ URL可访问，图片存在")
                    return True
                elif response.status_code == 403:
                    print("   ✗ URL返回403 Forbidden - 需要签名")
                    print("   问题分析: OSS文件是私有的，需要签名URL才能访问")
                    return False
                elif response.status_code == 404:
                    print("   ✗ URL返回404 Not Found - 文件不存在")
                    return False
                else:
                    print(f"   ✗ URL返回异常状态码: {response.status_code}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                print(f"   ✗ 访问URL失败: {e}")
                return False
                
        else:
            print(f"✗ 登录失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def check_oss_config():
    """检查OSS配置"""
    print("\n检查OSS配置...")
    
    # 检查环境变量
    print("1. 检查环境变量配置:")
    env_vars = [
        "ALIYUN_ACCESS_KEY_ID",
        "ALIYUN_ACCESS_KEY_SECRET", 
        "ALIYUN_OSS_ENDPOINT",
        "ALIYUN_OSS_BUCKET",
        "ALIYUN_OSS_BUCKET1"
    ]
    
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                masked = value[:5] + "..." + value[-5:] if len(value) > 10 else "***"
                print(f"   ✓ {var}: {masked}")
            else:
                print(f"   ✗ {var}: 未设置")
                
    except Exception as e:
        print(f"   检查环境变量失败: {e}")
    
    print("\n2. 分析问题:")
    print("   - 从日志看，图片上传成功，生成了签名URL")
    print("   - 但AI设计师智能体可能无法访问签名URL")
    print("   - 可能原因:")
    print("     1. 签名URL过期时间太短")
    print("     2. AI设计师智能体无法访问外部URL")
    print("     3. OSS配置问题（Bucket权限、跨域等）")
    
    return True

def main():
    print("=" * 70)
    print("图片URL可访问性测试")
    print("=" * 70)
    
    # 检查OSS配置
    check_oss_config()
    
    # 测试URL可访问性
    if not test_upload_and_access():
        print("\n❌ 图片URL可访问性测试失败")
        print("\n问题分析:")
        print("1. OSS文件是私有的，需要签名URL才能访问")
        print("2. 当前生成的签名URL可能有问题")
        print("3. AI设计师智能体可能无法访问签名URL")
        
        print("\n解决方案:")
        print("1. 检查OSS Service的sign_url_for_key函数")
        print("2. 确保生成的签名URL格式正确")
        print("3. 延长签名URL有效期（当前是24小时）")
        print("4. 检查AI设计师智能体是否能访问外部URL")
        
        print("\n这是一个**后台问题**，需要修复OSS签名URL的生成或AI设计师的URL访问逻辑。")
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)

if __name__ == "__main__":
    main()

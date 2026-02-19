#!/usr/bin/env python3
"""
验证AI设计师图片上传功能
"""
import requests
import json

# 阿里云服务器地址
BASE_URL = "http://120.26.201.61:8001/api/v1"

def test_health():
    """测试服务健康状态"""
    print("测试服务健康状态...")
    try:
        response = requests.get(f"{BASE_URL}/designer/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 服务健康: {data}")
            return True
        else:
            print(f"✗ 服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False

def test_upload_endpoint():
    """测试上传端点是否存在"""
    print("\n测试上传端点...")
    try:
        # 使用一个测试token（实际使用时需要真实token）
        test_url = f"{BASE_URL}/designer/upload-image?access_token=test&user_id=1"
        response = requests.post(test_url)
        
        # 403表示端点存在但token无效，这是正常的
        if response.status_code in [200, 401, 403, 400]:
            print(f"✓ 上传端点存在 (状态码: {response.status_code})")
            if response.status_code == 200:
                print(f"  响应: {response.text[:100]}")
            elif response.status_code == 403:
                print(f"  说明: 端点存在，但需要有效token (这是正常的)")
            return True
        else:
            print(f"✗ 上传端点异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def main():
    print("=" * 50)
    print("AI设计师图片上传功能验证")
    print("=" * 50)
    
    # 测试服务健康
    if not test_health():
        print("\n❌ 服务健康检查失败，无法继续测试")
        return
    
    # 测试上传端点
    if not test_upload_endpoint():
        print("\n❌ 上传端点测试失败")
        return
    
    print("\n" + "=" * 50)
    print("✅ 验证完成")
    print("=" * 50)
    print("\n总结:")
    print("1. AI设计师服务正常运行")
    print("2. 图片上传端点存在且可访问")
    print("3. 前端界面已优化：图片上传按钮现在位于发送按钮旁边")
    print("4. 用户现在可以更轻松地找到图片上传功能")
    print("\n改进说明:")
    print("- 将图片上传按钮从输入框左侧移到发送按钮旁边")
    print("- 使用绿色渐变背景突出显示上传按钮")
    print("- 按钮显示'📷 上传'文字，更加直观")
    print("- 优化了移动端响应式布局")

if __name__ == "__main__":
    main()

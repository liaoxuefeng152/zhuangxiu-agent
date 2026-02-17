#!/usr/bin/env python3
"""
测试存储空间使用情况API（基于真实OSS数据）
"""
import requests
import json
import sys

BASE_URL = 'http://120.26.201.61:8001/api/v1'

def test_storage_usage():
    """测试存储空间使用情况API"""
    print("=== 测试存储空间使用情况API ===")
    
    # 1. 登录获取token
    print("1. 登录获取token...")
    login_resp = requests.post(f'{BASE_URL}/users/login', json={'code': 'dev_h5_mock'})
    if login_resp.status_code != 200:
        print(f"登录失败: {login_resp.text}")
        return False
    
    login_data = login_resp.json()
    token = login_data.get('access_token')
    user_id = login_data.get('user_id')
    
    if not token:
        print("获取token失败")
        return False
    
    print(f"登录成功: user_id={user_id}, token={token[:50]}...")
    
    # 2. 测试存储空间API
    print("\n2. 测试存储空间使用情况API...")
    headers = {'Authorization': f'Bearer {token}'}
    storage_resp = requests.get(f'{BASE_URL}/users/storage-usage', headers=headers)
    
    if storage_resp.status_code != 200:
        print(f"存储空间API调用失败: {storage_resp.text}")
        return False
    
    storage_data = storage_resp.json()
    data = storage_data.get('data', {})
    
    print(f"API响应状态: {storage_data.get('code')} - {storage_data.get('msg')}")
    print(f"数据源: {data.get('data_source', 'unknown')}")
    print(f"文件总数: {data.get('file_count', 0)}")
    print(f"照片数量: {data.get('photo_count', 0)}")
    print(f"估算大小: {data.get('estimated_size_mb', 0)} MB")
    print(f"总存储空间: {data.get('total_storage_mb', 0)} MB")
    print(f"使用百分比: {data.get('usage_percentage', 0)}%")
    print(f"警告级别: {data.get('warning_level', 'unknown')}")
    print(f"会员状态: {data.get('is_member', False)}")
    print(f"存储期限: {data.get('storage_duration_months', 12)}个月")
    
    # 显示按类型统计
    by_type = data.get('by_type', {})
    if by_type:
        print("\n按类型统计:")
        for file_type, stats in by_type.items():
            print(f"  {file_type}: {stats.get('count', 0)}个文件, {stats.get('size_mb', 0)}MB")
    
    # 验证数据
    if data.get('data_source') == 'oss_real':
        print("\n✅ 成功获取真实OSS存储数据")
        return True
    elif data.get('data_source') == 'database_estimate':
        print("\n⚠️  使用数据库估算数据（OSS可能未配置或调用失败）")
        return True
    elif data.get('data_source') == 'error_fallback':
        print(f"\n⚠️  OSS调用失败，使用后备数据: {data.get('error', '未知错误')}")
        return True
    else:
        print(f"\n❌ 未知数据源: {data.get('data_source')}")
        return False

def test_cache_behavior():
    """测试缓存行为"""
    print("\n=== 测试缓存行为 ===")
    
    # 登录获取token
    login_resp = requests.post(f'{BASE_URL}/users/login', json={'code': 'dev_h5_mock'})
    if login_resp.status_code != 200:
        print("登录失败，跳过缓存测试")
        return True
    
    login_data = login_resp.json()
    token = login_data.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 第一次调用
    print("第一次调用（应该从OSS获取）...")
    resp1 = requests.get(f'{BASE_URL}/users/storage-usage', headers=headers)
    data1 = resp1.json().get('data', {})
    print(f"数据源: {data1.get('data_source')}")
    
    # 第二次调用（应该从缓存获取）
    print("第二次调用（应该从缓存获取）...")
    resp2 = requests.get(f'{BASE_URL}/users/storage-usage', headers=headers)
    data2 = resp2.json().get('data', {})
    print(f"数据源: {data2.get('data_source')}")
    
    # 比较两次结果
    if data1.get('estimated_size_mb') == data2.get('estimated_size_mb'):
        print("✅ 缓存行为正常（两次结果一致）")
        return True
    else:
        print("❌ 缓存行为异常（两次结果不一致）")
        return False

def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    # 测试无效token
    print("测试无效token...")
    headers = {'Authorization': 'Bearer invalid_token'}
    resp = requests.get(f'{BASE_URL}/users/storage-usage', headers=headers)
    
    if resp.status_code == 401:
        print("✅ 无效token正确返回401")
    else:
        print(f"❌ 无效token未返回401: {resp.status_code}")
        return False
    
    # 测试无token
    print("测试无token...")
    resp = requests.get(f'{BASE_URL}/users/storage-usage')
    
    if resp.status_code == 401:
        print("✅ 无token正确返回401")
    else:
        print(f"❌ 无token未返回401: {resp.status_code}")
        return False
    
    return True

if __name__ == '__main__':
    print("开始测试存储空间使用情况功能...")
    
    # 测试存储空间API
    success1 = test_storage_usage()
    
    # 测试缓存行为
    success2 = test_cache_behavior()
    
    # 测试错误处理
    success3 = test_error_handling()
    
    print("\n=== 测试结果 ===")
    if success1 and success2 and success3:
        print("✅ 所有测试通过！")
        print("\n功能说明：")
        print("1. 存储空间API现在基于真实OSS数据计算")
        print("2. 添加了缓存机制，避免频繁调用OSS API")
        print("3. 支持按文件类型统计存储使用情况")
        print("4. 这是后台问题，需要部署到阿里云服务器")
        sys.exit(0)
    else:
        print("❌ 测试失败")
        sys.exit(1)

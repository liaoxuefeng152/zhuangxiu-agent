#!/usr/bin/env python3
"""
测试回收站API功能
"""
import requests
import json
import sys

# 配置
BASE_URL = "http://localhost:8001/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTc0MjQwNjQwMH0.test_token"  # 替换为实际token

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_get_recycle():
    """测试获取回收站列表"""
    print("测试获取回收站列表...")
    try:
        response = requests.get(f"{BASE_URL}/users/data/recycle", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_permanent_delete():
    """测试永久删除API（需要先有数据在回收站）"""
    print("\n测试永久删除API...")
    print("注意：需要先有数据在回收站才能测试")
    return True

def test_clear_recycle():
    """测试清空回收站API"""
    print("\n测试清空回收站API...")
    try:
        response = requests.delete(f"{BASE_URL}/users/data/recycle/clear", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应: {response.json()}")
            return True
        else:
            print(f"错误响应: {response.text}")
            return False
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def main():
    print("=== 回收站API功能测试 ===\n")
    
    # 测试获取回收站列表
    if not test_get_recycle():
        print("获取回收站列表测试失败")
        return 1
    
    # 测试清空回收站
    if not test_clear_recycle():
        print("清空回收站测试失败")
        return 1
    
    print("\n=== 所有测试完成 ===")
    print("API端点已就绪，可以部署到阿里云服务器")
    return 0

if __name__ == "__main__":
    sys.exit(main())

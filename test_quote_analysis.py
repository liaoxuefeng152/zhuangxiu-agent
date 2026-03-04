#!/usr/bin/env python3
"""
测试报价单分析功能
"""
import json
import requests
import sys

def test_quote_analysis():
    """测试报价单分析API"""
    base_url = "http://120.26.201.61:8001"
    
    # 1. 首先登录获取token - 使用正确的登录端点
    print("1. 登录获取token...")
    login_data = {
        "phone": "13800138000",  # 测试用户
        "password": "123456"
    }
    
    try:
        # 尝试不同的登录端点
        login_endpoints = [
            "/api/v1/auth/login",
            "/auth/login",
            "/login"
        ]
        
        token = None
        for endpoint in login_endpoints:
            try:
                login_response = requests.post(f"{base_url}{endpoint}", json=login_data, timeout=5)
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    if login_result.get("code") == 0 and "access_token" in login_result.get("data", {}):
                        token = login_result["data"]["access_token"]
                        print(f"登录成功，使用端点: {endpoint}, token: {token[:20]}...")
                        break
            except Exception as e:
                print(f"尝试端点 {endpoint} 失败: {e}")
                continue
        
        if not token:
            print("所有登录端点尝试失败，跳过登录直接测试...")
            headers = {"Content-Type": "application/json"}
        else:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        
        # 2. 测试报价单上传API（模拟文件上传）
        print("\n2. 测试报价单上传API...")
        
        # 由于文件上传需要实际文件，我们测试API端点是否存在
        test_endpoints = [
            "/api/v1/quotes/upload",
            "/quotes/upload"
        ]
        
        for endpoint in test_endpoints:
            try:
                print(f"测试端点: {endpoint}")
                # 发送一个简单的GET请求检查端点是否存在
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                print(f"GET响应: {response.status_code}")
                
                # 尝试POST请求（不带文件）
                test_data = {"test": "data"}
                post_response = requests.post(f"{base_url}{endpoint}", json=test_data, headers=headers, timeout=5)
                print(f"POST响应状态码: {post_response.status_code}")
                print(f"POST响应内容: {post_response.text[:200]}...")
                
                if post_response.status_code != 405:  # 如果不是方法不允许
                    print(f"端点 {endpoint} 响应正常")
                    break
                    
            except Exception as e:
                print(f"测试端点 {endpoint} 失败: {e}")
                continue
        
        # 3. 测试报价单列表API
        print("\n3. 测试报价单列表API...")
        list_endpoints = [
            "/api/v1/quotes/list",
            "/quotes/list"
        ]
        
        for endpoint in list_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                print(f"列表端点 {endpoint} 响应: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"列表响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    return True
            except Exception as e:
                print(f"测试列表端点 {endpoint} 失败: {e}")
                continue
        
        return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quote_report():
    """测试报价单报告获取"""
    print("\n3. 测试报价单报告获取...")
    
    base_url = "http://120.26.201.61:8001"
    
    try:
        # 获取报价单报告列表
        response = requests.get(f"{base_url}/api/v1/quotes/reports")
        print(f"报告列表响应: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                reports = result.get("data", {}).get("reports", [])
                print(f"找到 {len(reports)} 个报价单报告")
                
                if reports:
                    # 获取第一个报告的详情
                    report_id = reports[0]["id"]
                    print(f"\n获取报告详情 (ID: {report_id})...")
                    
                    detail_response = requests.get(f"{base_url}/api/v1/quotes/reports/{report_id}")
                    if detail_response.status_code == 200:
                        detail_result = detail_response.json()
                        if detail_result.get("code") == 0:
                            report_data = detail_result.get("data", {})
                            print(f"报告详情: {json.dumps(report_data, ensure_ascii=False, indent=2)}")
                            return True
                        else:
                            print(f"获取报告详情失败: {detail_result.get('msg')}")
                    else:
                        print(f"获取报告详情HTTP错误: {detail_response.status_code}")
                else:
                    print("没有找到报价单报告")
            else:
                print(f"获取报告列表失败: {result.get('msg')}")
        else:
            print(f"获取报告列表HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"测试报告获取异常: {e}")
        
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("开始测试报价单分析功能")
    print("=" * 60)
    
    # 测试报价单分析
    analysis_success = test_quote_analysis()
    
    # 测试报告获取
    report_success = test_quote_report()
    
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print(f"报价单分析测试: {'✅ 成功' if analysis_success else '❌ 失败'}")
    print(f"报价单报告测试: {'✅ 成功' if report_success else '❌ 失败'}")
    print("=" * 60)
    
    if analysis_success and report_success:
        print("\n🎉 所有测试通过！报价单分析功能正常工作。")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查问题。")
        sys.exit(1)

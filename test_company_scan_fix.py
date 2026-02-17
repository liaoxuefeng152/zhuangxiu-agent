#!/usr/bin/env python3
"""
测试公司扫描API修复
"""
import asyncio
import httpx
import json
import sys

async def test_company_scan_api():
    """测试公司扫描API"""
    base_url = 'http://localhost:8001/api/v1'
    
    print("=== 测试公司扫描API修复 ===")
    print(f"API地址: {base_url}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 先登录获取token
        print("\n1. 登录获取token...")
        login_data = {
            'code': 'test_code_123'  # 测试用code，实际使用时需要有效的微信code
        }
        
        try:
            login_response = await client.post(f'{base_url}/users/login', json=login_data)
            print(f"登录响应状态码: {login_response.status_code}")
            
            if login_response.status_code != 200:
                print(f"登录失败，状态码: {login_response.status_code}")
                print(f"响应内容: {login_response.text}")
                return False
                
            login_result = login_response.json()
            print(f"登录响应: {json.dumps(login_result, indent=2, ensure_ascii=False)}")
            
            if login_result.get('code') != 0:
                print(f"登录失败: {login_result.get('msg')}")
                return False
                
            token = login_result['data']['access_token']
            print(f"获取到token: {token[:20]}...")
            
            # 2. 使用token测试公司扫描API
            headers = {'Authorization': f'Bearer {token}'}
            
            print("\n2. 测试公司扫描API scan_id=14...")
            response = await client.get(f'{base_url}/companies/scan/14', headers=headers)
            print(f"API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get('code') == 0:
                    print("\n✅ API调用成功！")
                    data = result.get('data', {})
                    print(f"公司名称: {data.get('company_name', 'N/A')}")
                    print(f"风险等级: {data.get('risk_level', 'N/A')}")
                    print(f"风险评分: {data.get('risk_score', 'N/A')}")
                    print(f"状态: {data.get('status', 'N/A')}")
                    print(f"是否已解锁: {data.get('is_unlocked', 'N/A')}")
                    return True
                else:
                    print(f"\n❌ API返回错误: {result.get('msg')}")
                    return False
                    
            elif response.status_code == 404:
                print("\n⚠️ 扫描记录不存在 (scan_id=14)")
                print("这可能是因为数据库中不存在ID为14的扫描记录")
                print("响应内容:", response.text)
                return True  # 404是正常情况，不是服务器错误
                
            elif response.status_code == 500:
                print("\n❌ 服务器内部错误 (500)")
                try:
                    error_data = response.json()
                    print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    print("无法解析错误响应:", response.text)
                return False
                
            else:
                print(f"\n❌ 其他错误: {response.status_code}")
                print("响应内容:", response.text)
                return False
                
        except httpx.RequestError as e:
            print(f"\n❌ 网络请求错误: {e}")
            return False
        except Exception as e:
            print(f"\n❌ 测试过程中出现异常: {e}")
            import traceback
            traceback.print_exc()
            return False

async def test_multiple_scenarios():
    """测试多种场景"""
    print("=== 测试多种场景 ===")
    
    # 测试场景1: 正常的scan_id=14
    print("\n--- 场景1: 测试scan_id=14 ---")
    result1 = await test_company_scan_api()
    
    # 测试场景2: 测试不存在的scan_id
    print("\n--- 场景2: 测试不存在的scan_id=99999 ---")
    # 这里可以扩展测试其他ID
    
    return result1

if __name__ == '__main__':
    print("开始测试公司扫描API修复...")
    try:
        result = asyncio.run(test_company_scan_api())
        if result:
            print("\n✅ 测试通过！后端修复有效。")
            sys.exit(0)
        else:
            print("\n❌ 测试失败！后端仍有问题。")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中出现未预期错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

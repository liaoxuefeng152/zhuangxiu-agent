#!/usr/bin/env python3
"""
调试聚合数据API问题
"""
import asyncio
import httpx
import json

async def debug_api_key():
    """调试API Key问题"""
    print("=" * 60)
    print("调试聚合数据API Key问题")
    print("=" * 60)
    
    # 从.env文件读取API Key
    api_key = None
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('JUHECHA_TOKEN='):
                    api_key = line.strip().split('=', 1)[1]
                    break
    except Exception as e:
        print(f"读取.env文件失败: {e}")
        return
    
    if not api_key:
        print("❌ 未找到聚合数据API Key")
        return
    
    print(f"API Key: {api_key}")
    print(f"API Key长度: {len(api_key)}")
    
    # 测试不同的API端点
    test_endpoints = [
        ("司法企业查询", "http://v.juhe.cn/sifa/ent"),
        ("企业工商信息", "http://v.juhe.cn/enterprise/businessInfo"),
        ("企业风险信息", "http://v.juhe.cn/enterprise/riskInfo"),
    ]
    
    test_company = "耒阳市怡馨装饰设计工程有限公司"
    
    for endpoint_name, endpoint_url in test_endpoints:
        print(f"\n测试端点: {endpoint_name}")
        print(f"URL: {endpoint_url}")
        print("-" * 40)
        
        try:
            # 构建请求参数
            params = {
                "keyword": test_company,
                "key": api_key,
                "range": 5,
                "pageno": 1
            }
            
            # 发送请求
            async with httpx.AsyncClient(timeout=10.0) as client:
                print(f"发送请求: {endpoint_url}")
                print(f"参数: keyword={test_company}, key={api_key[:10]}..., range=5, pageno=1")
                
                response = await client.get(endpoint_url, params=params)
                
                print(f"响应状态码: {response.status_code}")
                print(f"响应头: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"响应JSON: {json.dumps(data, ensure_ascii=False, indent=2)}")
                        
                        if data.get("error_code") == 0:
                            print(f"✅ {endpoint_name} API调用成功")
                        else:
                            print(f"❌ API返回错误: {data.get('reason', '未知错误')}")
                            print(f"错误代码: {data.get('error_code')}")
                    except json.JSONDecodeError:
                        print(f"❌ 响应不是有效的JSON")
                        print(f"响应内容: {response.text[:200]}")
                else:
                    print(f"❌ HTTP请求失败: {response.status_code}")
                    print(f"响应内容: {response.text[:200]}")
                    
        except httpx.TimeoutException:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

async def test_with_user_example():
    """使用用户提供的示例进行测试"""
    print("\n" + "=" * 60)
    print("使用用户提供的示例进行测试")
    print("=" * 60)
    
    # 用户提供的示例
    user_api_key = "36de33e10af2b8882017388cbe086daa"
    user_company = "耒阳市怡馨装饰设计工程有限公司"
    user_url = "http://v.juhe.cn/sifa/ent"
    
    print(f"使用用户提供的API Key: {user_api_key}")
    print(f"测试公司: {user_company}")
    print(f"API端点: {user_url}")
    
    try:
        # 构建请求参数（按照用户示例的格式）
        params = {
            "keyword": user_company,
            "key": user_api_key,
            "dataType": "",
            "pageno": "",
            "range": ""
        }
        
        # 发送请求
        async with httpx.AsyncClient(timeout=10.0) as client:
            print(f"\n发送请求...")
            response = await client.get(user_url, params=params)
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"响应JSON: {json.dumps(data, ensure_ascii=False, indent=2)}")
                
                if data.get("error_code") == 0:
                    print("✅ 用户提供的API Key工作正常")
                    
                    # 分析结果
                    result = data.get("result", {})
                    total_count = result.get("totalCount", 0)
                    case_list = result.get("list", [])
                    
                    print(f"\n分析结果:")
                    print(f"总案件数: {total_count}")
                    
                    if case_list:
                        print(f"找到 {len(case_list)} 条法律案件:")
                        for i, case in enumerate(case_list[:3], 1):
                            title = case.get("title", "无标题")
                            data_type = case.get("dataType", "未知")
                            date_str = case.get("sortTimeString", "未知")
                            
                            print(f"  {i}. {title}")
                            print(f"     类型: {data_type}")
                            print(f"     日期: {date_str}")
                else:
                    print(f"❌ API返回错误: {data.get('reason', '未知错误')}")
                    print(f"错误代码: {data.get('error_code')}")
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                print(f"响应内容: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def check_api_key_validity():
    """检查API Key的有效性"""
    print("\n" + "=" * 60)
    print("检查API Key有效性")
    print("=" * 60)
    
    # 可能的API Key问题
    api_keys_to_test = [
        "36de33e10af2b8882017388cbe086daa",  # 用户提供的
        "36de33e10af2b8882017388cbe086daa".upper(),  # 大写
        "36de33e10af2b8882017388cbe086daa".lower(),  # 小写
    ]
    
    test_url = "http://v.juhe.cn/sifa/ent"
    test_company = "测试公司"
    
    for api_key in api_keys_to_test:
        print(f"\n测试API Key: {api_key}")
        
        try:
            params = {
                "keyword": test_company,
                "key": api_key,
                "range": 1
            }
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(test_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    error_code = data.get("error_code")
                    reason = data.get("reason", "")
                    
                    if error_code == 0:
                        print(f"  ✅ API Key有效")
                    elif "KEY" in reason:
                        print(f"  ❌ API Key错误: {reason}")
                    elif "次数" in reason or "limit" in reason.lower():
                        print(f"  ⚠️  API调用次数限制: {reason}")
                    else:
                        print(f"  ❓ 其他错误: {reason} (错误代码: {error_code})")
                else:
                    print(f"  ❌ HTTP错误: {response.status_code}")
                    
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")

async def main():
    """主调试函数"""
    print("开始调试聚合数据API问题...")
    
    # 检查API Key有效性
    await check_api_key_validity()
    
    # 使用用户示例测试
    await test_with_user_example()
    
    # 调试API Key问题
    await debug_api_key()
    
    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
    
    print("\n建议:")
    print("1. 检查API Key是否正确")
    print("2. 检查API Key是否已激活")
    print("3. 检查API Key是否有调用次数限制")
    print("4. 联系聚合数据客服确认API Key状态")

if __name__ == "__main__":
    asyncio.run(main())

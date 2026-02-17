#!/usr/bin/env python3
"""
简单测试聚合数据API
"""
import asyncio
import httpx
import json

async def test_juhecha_api():
    """直接测试聚合数据API"""
    print("=" * 60)
    print("直接测试聚合数据API")
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
    
    print(f"✅ 找到聚合数据API Key: {api_key[:10]}...")
    
    # 测试公司名称
    test_companies = [
        "耒阳市怡馨装饰设计工程有限公司",  # 用户测试的公司
        "北京装修公司",
        "上海装饰公司"
    ]
    
    for company_name in test_companies:
        print(f"\n测试公司: {company_name}")
        print("-" * 40)
        
        try:
            # 构建请求参数
            params = {
                "keyword": company_name,
                "key": api_key,
                "range": 5,
                "pageno": 1
            }
            
            # 发送请求
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "http://v.juhe.cn/sifa/ent",
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("error_code") == 0:
                        result = data.get("result", {})
                        total_count = result.get("totalCount", 0)
                        case_list = result.get("list", [])
                        
                        print(f"✅ API调用成功")
                        print(f"   总案件数: {total_count}")
                        
                        if case_list:
                            print(f"   找到 {len(case_list)} 条法律案件:")
                            for i, case in enumerate(case_list[:3], 1):
                                title = case.get("title", "无标题")
                                data_type = case.get("dataType", "未知")
                                date_str = case.get("sortTimeString", "未知")
                                
                                # 案件类型映射
                                type_mapping = {
                                    "cpws": "裁判文书",
                                    "ajlc": "案件流程",
                                    "bgt": "执行公告",
                                    "fygg": "法院公告",
                                    "ktgg": "开庭公告",
                                    "pmgg": "拍卖公告",
                                    "shixin": "失信被执行人",
                                    "sifacdk": "司法查控",
                                    "zxgg": "限制高消费"
                                }
                                
                                data_type_zh = type_mapping.get(data_type, data_type)
                                
                                print(f"   {i}. {title}")
                                print(f"      类型: {data_type_zh}")
                                print(f"      日期: {date_str}")
                                
                                # 检查是否是装修相关
                                title_lower = title.lower()
                                decoration_keywords = ["装饰", "装修", "装潢", "家装", "工装"]
                                is_decoration = any(keyword in title_lower for keyword in decoration_keywords)
                                if is_decoration:
                                    print(f"      🔥 装修相关案件")
                        else:
                            print("   未找到法律案件")
                        
                        # 分析风险
                        if total_count > 0:
                            risk_score = 0
                            risk_reasons = []
                            
                            if total_count > 10:
                                risk_score += 50
                                risk_reasons.append(f"存在{total_count}起法律案件，风险较高")
                            elif total_count > 5:
                                risk_score += 30
                                risk_reasons.append(f"存在{total_count}起法律案件")
                            elif total_count > 0:
                                risk_score += 15
                                risk_reasons.append(f"存在{total_count}起法律案件")
                            
                            # 检查装修相关案件
                            decoration_cases = 0
                            for case in case_list:
                                title = case.get("title", "").lower()
                                if any(keyword in title for keyword in ["装饰", "装修", "装潢"]):
                                    decoration_cases += 1
                            
                            if decoration_cases > 0:
                                risk_score += 25
                                risk_reasons.append(f"存在{decoration_cases}起装修相关纠纷")
                            
                            print(f"\n   风险分析:")
                            print(f"   风险评分: {risk_score}")
                            print(f"   风险原因: {risk_reasons}")
                            
                            if risk_score >= 70:
                                risk_level = "高风险"
                            elif risk_score >= 30:
                                risk_level = "警告"
                            else:
                                risk_level = "合规"
                            
                            print(f"   风险等级: {risk_level}")
                    else:
                        print(f"❌ API返回错误: {data.get('reason', '未知错误')}")
                else:
                    print(f"❌ HTTP请求失败: {response.status_code}")
                    
        except httpx.TimeoutException:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

async def test_api_config():
    """测试API配置"""
    print("\n" + "=" * 60)
    print("测试API配置")
    print("=" * 60)
    
    # 检查.env文件中的配置
    configs = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        configs[key] = value
    except Exception as e:
        print(f"读取.env文件失败: {e}")
        return
    
    # 检查聚合数据配置
    juhecha_token = configs.get('JUHECHA_TOKEN', '')
    if juhecha_token and juhecha_token not in ("xxx", "your_token", "your_token_here"):
        print(f"✅ 聚合数据Token已配置: {juhecha_token[:10]}...")
    else:
        print("❌ 聚合数据Token未配置或无效")
    
    # 检查天眼查配置
    tianyancha_token = configs.get('TIANYANCHA_TOKEN', '')
    if tianyancha_token and tianyancha_token not in ("xxx", "your_token", "your_token_here"):
        print(f"✅ 天眼查Token已配置: {tianyancha_token[:10]}...")
    else:
        print("❌ 天眼查Token未配置或无效")
    
    # 显示其他相关配置
    print(f"\n相关配置:")
    for key in ['JUHECHA_API_BASE', 'JUHECHA_SIFA_ENDPOINT']:
        if key in configs:
            print(f"  {key}: {configs[key]}")

async def main():
    """主测试函数"""
    print("开始测试聚合数据API...")
    
    # 测试API配置
    await test_api_config()
    
    # 测试聚合数据API
    await test_juhecha_api()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

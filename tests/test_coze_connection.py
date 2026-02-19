#!/usr/bin/env python3
"""
测试扣子API连接状态
"""
import os
import sys
import json
import httpx

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))

def test_coze_api_directly():
    """直接测试扣子API连接"""
    print("=== 直接测试扣子API连接 ===")
    
    # 读取.env文件获取配置
    env_path = os.path.join(ROOT, ".env")
    if not os.path.exists(env_path):
        print(f"❌ 找不到.env文件: {env_path}")
        return False
    
    config = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    coze_token = config.get("COZE_API_TOKEN")
    coze_bot_id = config.get("COZE_SUPERVISOR_BOT_ID") or config.get("COZE_BOT_ID")
    
    if not coze_token:
        print("❌ 未配置COZE_API_TOKEN")
        return False
    
    if not coze_bot_id:
        print("❌ 未配置COZE_SUPERVISOR_BOT_ID或COZE_BOT_ID")
        return False
    
    print(f"✅ 找到扣子配置:")
    print(f"   Token: {coze_token[:20]}...")
    print(f"   Bot ID: {coze_bot_id}")
    
    # 测试扣子API v3/chat接口
    print("\n测试扣子API v3/chat接口...")
    
    headers = {
        "Authorization": f"Bearer {coze_token}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "bot_id": coze_bot_id,
        "user_id": "decoration-agent-test",
        "stream": False,
        "auto_save_history": False,
        "additional_messages": [
            {
                "role": "user",
                "content": "【系统要求】\n你是一位专业的装修报价审核专家，拥有10年以上的装修行业经验。请对用户提供的装修报价单进行分析，识别其中的风险项。\n\n【用户输入】\n请分析以下装修报价单，总价：80000元\n\n报价单内容：\n测试报价单",
                "content_type": "text"
            }
        ],
    }
    
    try:
        async def test():
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.coze.cn/v3/chat",
                    headers=headers,
                    json=payload
                )
                return response
        
        import asyncio
        response = asyncio.run(test())
        
        print(f"扣子API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"扣子API响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get("code") == 0:
                print("✅ 扣子API连接成功！")
                return True
            else:
                print(f"❌ 扣子API返回错误代码: {data.get('code')}")
                print(f"错误信息: {data.get('msg')}")
                
                # 检查常见错误代码
                if data.get("code") == 4200:
                    print("⚠️  错误4200: Bot ID不存在，请检查Bot ID是否正确")
                elif data.get("code") == 4015:
                    print("⚠️  错误4015: Bot未发布到Agent As API频道")
                elif data.get("code") == 4000:
                    print("⚠️  错误4000: 参数错误，请检查请求格式")
                elif data.get("code") == 401:
                    print("⚠️  错误401: Token无效或过期")
                
                return False
        else:
            print(f"❌ 扣子API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ 扣子API测试异常: {e}")
        return False

def check_ai_provider():
    """检查当前使用的AI服务提供商"""
    print("\n=== 检查AI服务提供商 ===")
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    
    try:
        from app.services.risk_analyzer import get_ai_provider_name
        
        provider = get_ai_provider_name()
        print(f"当前AI服务提供商: {provider}")
        
        if provider == "coze_api":
            print("✅ 使用扣子开放平台API")
        elif provider == "coze_site":
            print("✅ 使用扣子发布站点")
        elif provider == "deepseek":
            print("✅ 使用DeepSeek API")
        elif provider == "none":
            print("❌ 未配置任何AI服务")
        else:
            print(f"⚠️  未知的AI服务提供商: {provider}")
            
        return provider
        
    except Exception as e:
        print(f"❌ 检查AI服务提供商失败: {e}")
        return None

def main():
    """主函数"""
    print("扣子API连接测试")
    print("=" * 50)
    
    # 检查AI服务提供商
    provider = check_ai_provider()
    
    # 如果是扣子API，测试连接
    if provider in ["coze_api", "coze_site"]:
        success = test_coze_api_directly()
        
        if not success:
            print("\n⚠️  扣子API连接测试失败，AI分析功能可能无法正常工作")
            print("\n建议解决方案:")
            print("1. 检查扣子智能体是否已发布到'Agent As API'频道")
            print("2. 验证Bot ID是否正确")
            print("3. 检查Token是否有效")
            print("4. 配置DeepSeek作为备用方案")
        else:
            print("\n✅ 扣子API连接正常，AI分析功能应该可以正常工作")
    else:
        print(f"\n当前使用 {provider}，无需测试扣子API连接")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

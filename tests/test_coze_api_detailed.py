#!/usr/bin/env python3
"""
详细测试扣子API连接和智能体调用
"""
import os
import sys
import json
import httpx
import asyncio
import time

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))

def load_env_config():
    """加载环境配置"""
    env_path = os.path.join(ROOT, ".env")
    if not os.path.exists(env_path):
        print(f"找不到.env文件: {env_path}")
        return None
    
    config = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return config

async def test_coze_api_directly():
    """直接测试扣子API"""
    print("=== 直接测试扣子API ===")
    
    config = load_env_config()
    if not config:
        return False
    
    coze_token = config.get("COZE_API_TOKEN")
    coze_bot_id = config.get("COZE_SUPERVISOR_BOT_ID") or config.get("COZE_BOT_ID")
    coze_base = config.get("COZE_API_BASE", "https://api.coze.cn").rstrip("/")
    
    if not coze_token:
        print("❌ 未配置COZE_API_TOKEN")
        return False
    
    if not coze_bot_id:
        print("❌ 未配置COZE_SUPERVISOR_BOT_ID或COZE_BOT_ID")
        return False
    
    print(f"配置信息:")
    print(f"  API Base: {coze_base}")
    print(f"  Token: {coze_token[:20]}...")
    print(f"  Bot ID: {coze_bot_id}")
    
    # 测试简单的对话
    system_prompt = "你是一位专业的装修报价审核专家。请用JSON格式返回分析结果。"
    user_content = "请分析这个报价单：水电改造120元/米，共80米，合计9600元。"
    combined = f"【系统要求】\n{system_prompt}\n\n【用户输入】\n{user_content}"
    
    payload = {
        "bot_id": coze_bot_id,
        "user_id": "decoration-agent-test",
        "stream": False,
        "auto_save_history": False,
        "additional_messages": [
            {"role": "user", "content": combined, "content_type": "text"}
        ],
    }
    
    headers = {
        "Authorization": f"Bearer {coze_token}",
        "Content-Type": "application/json",
    }
    
    try:
        print(f"\n1. 发送请求到扣子API: {coze_base}/v3/chat")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{coze_base}/v3/chat",
                headers=headers,
                json=payload,
            )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            return False
        
        data = response.json()
        print(f"响应JSON: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        if data.get("code") != 0:
            print(f"❌ 扣子API返回错误: code={data.get('code')}, msg={data.get('msg')}")
            return False
        
        chat_id = (data.get("data") or {}).get("id")
        conversation_id = (data.get("data") or {}).get("conversation_id")
        
        if not chat_id or not conversation_id:
            print("❌ 响应中缺少chat_id或conversation_id")
            return False
        
        print(f"✅ 请求成功，chat_id: {chat_id}, conversation_id: {conversation_id}")
        
        # 轮询获取结果
        print(f"\n2. 轮询获取结果...")
        poll_interval = 2.0
        max_wait = 30
        deadline = time.monotonic() + max_wait
        
        while time.monotonic() < deadline:
            await asyncio.sleep(poll_interval)
            
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    ret = await client.get(
                        f"{coze_base}/v3/chat/retrieve",
                        params={"chat_id": chat_id, "conversation_id": conversation_id},
                        headers=headers,
                    )
                
                if ret.status_code != 200:
                    print(f"轮询请求失败: {ret.status_code}")
                    continue
                
                ret_data = ret.json()
                if ret_data.get("code") != 0:
                    print(f"轮询响应错误: code={ret_data.get('code')}")
                    continue
                
                status = (ret_data.get("data") or {}).get("status")
                print(f"当前状态: {status}")
                
                if status == "completed":
                    print("✅ 任务完成")
                    break
                elif status == "failed":
                    print("❌ 任务失败")
                    print(f"失败详情: {ret_data}")
                    return False
            
            except Exception as e:
                print(f"轮询异常: {e}")
                continue
        
        # 获取消息列表
        print(f"\n3. 获取消息列表...")
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                list_res = await client.get(
                    f"{coze_base}/v3/chat/message/list",
                    params={"chat_id": chat_id, "conversation_id": conversation_id},
                    headers=headers,
                )
            
            if list_res.status_code != 200:
                print(f"获取消息列表失败: {list_res.status_code}")
                return False
            
            list_data = list_res.json()
            print(f"消息列表响应: {json.dumps(list_data, ensure_ascii=False, indent=2)}")
            
            if list_data.get("code") != 0:
                print(f"消息列表错误: code={list_data.get('code')}")
                return False
            
            raw = list_data.get("data")
            messages = raw if isinstance(raw, list) else (raw or {}).get("messages") if isinstance(raw, dict) else []
            
            if not isinstance(messages, list):
                print(f"消息格式错误: {type(messages)}")
                return False
            
            print(f"\n消息数量: {len(messages)}")
            for i, msg in enumerate(messages):
                print(f"\n消息 {i}:")
                print(f"  角色: {msg.get('role')}")
                print(f"  内容类型: {msg.get('content_type')}")
                content = msg.get("content", "")
                if len(content) > 200:
                    print(f"  内容: {content[:200]}...")
                else:
                    print(f"  内容: {content}")
            
            # 查找助手回复
            for msg in reversed(messages):
                if msg.get("role") == "assistant":
                    content = msg.get("content", "").strip()
                    if content:
                        print(f"\n✅ 找到助手回复，长度: {len(content)} 字符")
                        print(f"前200字符: {content[:200]}")
                        return True
            
            print("❌ 未找到助手回复")
            return False
            
        except Exception as e:
            print(f"获取消息列表异常: {e}")
            return False
        
    except Exception as e:
        print(f"扣子API测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_deepseek_config():
    """测试DeepSeek配置"""
    print("\n=== 测试DeepSeek配置 ===")
    
    config = load_env_config()
    if not config:
        return False
    
    deepseek_key = config.get("DEEPSEEK_API_KEY")
    deepseek_base = config.get("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    
    if not deepseek_key:
        print("❌ 未配置DEEPSEEK_API_KEY")
        return False
    
    print(f"DeepSeek配置:")
    print(f"  API Key: {deepseek_key[:10]}...")
    print(f"  API Base: {deepseek_base}")
    
    # 测试网络连接
    try:
        response = httpx.get("https://api.deepseek.com", timeout=10.0)
        print(f"✅ DeepSeek API域名可访问，状态码: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ DeepSeek API网络连接失败: {e}")
        return False

async def test_risk_analyzer_service():
    """测试风险分析服务"""
    print("\n=== 测试风险分析服务 ===")
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    
    try:
        from app.services.risk_analyzer import RiskAnalyzerService
        
        service = RiskAnalyzerService()
        
        # 测试配置
        print(f"扣子配置检查:")
        print(f"  COZE_TOKEN配置: {'已配置' if service._coze_token else '未配置'}")
        print(f"  COZE_BOT_ID配置: {'已配置' if service._coze_bot_id else '未配置'}")
        print(f"  COZE_SUPERVISOR_BOT_ID配置: {'已配置' if service._coze_supervisor_bot_id else '未配置'}")
        print(f"  DEEPSEEK_API_KEY配置: {'已配置' if service.client.api_key else '未配置'}")
        
        # 测试报价单分析
        quote_text = "水电改造120元/米，共80米，合计9600元。"
        print(f"\n测试报价单分析...")
        print(f"报价单文本: {quote_text}")
        
        result = await service.analyze_quote(quote_text, 9600.0)
        
        print(f"\n分析结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        suggestions = result.get("suggestions", [])
        if suggestions and "AI分析服务暂时不可用" in suggestions[0]:
            print("\n❌ 风险分析服务返回兜底结果")
            return False
        
        print(f"\n✅ 风险分析服务测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 风险分析服务测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("扣子API详细诊断测试")
    print("=" * 60)
    
    # 测试DeepSeek配置
    test_deepseek_config()
    
    # 直接测试扣子API
    coze_success = await test_coze_api_directly()
    
    if not coze_success:
        print("\n⚠️  扣子API测试失败，检查以下可能原因:")
        print("1. API Token可能已过期或无效")
        print("2. Bot ID可能不正确")
        print("3. 网络连接问题")
        print("4. 扣子服务暂时不可用")
    
    # 测试风险分析服务
    print("\n" + "=" * 60)
    risk_success = await test_risk_analyzer_service()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"扣子API测试: {'✅ 成功' if coze_success else '❌ 失败'}")
    print(f"风险分析服务测试: {'✅ 成功' if risk_success else '❌ 失败'}")
    
    if not coze_success:
        print("\n建议修复步骤:")
        print("1. 检查COZE_API_TOKEN是否有效")
        print("2. 检查COZE_SUPERVISOR_BOT_ID是否正确")
        print("3. 检查网络连接是否能访问api.coze.cn")
        print("4. 考虑配置DEEPSEEK_API_KEY作为备用方案")
    
    return coze_success and risk_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

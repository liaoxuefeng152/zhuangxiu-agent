#!/usr/bin/env python3
"""
测试扣子智能体修复效果
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.coze_service import CozeService

async def test_coze_service():
    """测试扣子服务"""
    print("=== 测试扣子智能体服务 ===")
    
    # 创建服务实例
    service = CozeService()
    
    print(f"1. 服务配置检查:")
    print(f"   - 使用扣子站点API: {service.use_site_api}")
    print(f"   - 使用扣子开放平台API: {service.use_open_api}")
    print(f"   - 使用DeepSeek API: {service.use_deepseek}")
    
    if not service.use_site_api and not service.use_open_api and not service.use_deepseek:
        print("   ⚠️ 警告: 没有可用的AI分析服务配置")
    
    # 测试DeepSeek API配置
    print(f"\n2. DeepSeek API配置检查:")
    print(f"   - API密钥配置: {'已配置' if service.use_deepseek else '未配置'}")
    
    # 测试DeepSeek API调用（模拟）
    print(f"\n3. 测试DeepSeek API调用:")
    if service.use_deepseek:
        print("   - 尝试调用DeepSeek API...")
        try:
            # 模拟一个无效的图片URL
            test_image_url = "https://example.com/test.jpg"
            test_prompt = "测试提示词"
            
            result = await service._call_deepseek_api(test_image_url, test_prompt)
            if result is None:
                print("   ✅ DeepSeek API调用返回None（符合预期，因为API密钥无效）")
            else:
                print(f"   ⚠️ DeepSeek API调用返回结果: {type(result)}")
        except Exception as e:
            print(f"   ❌ DeepSeek API调用异常: {e}")
    else:
        print("   - DeepSeek API未配置，跳过测试")
    
    # 测试报价单分析（模拟）
    print(f"\n4. 测试报价单分析流程:")
    test_image_url = "https://example.com/quote.jpg"
    try:
        result = await service.analyze_quote(test_image_url, user_id=1)
        if result:
            print(f"   ✅ 报价单分析成功，返回结果类型: {type(result)}")
            print(f"   - 结果字段: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        else:
            print("   ⚠️ 报价单分析返回None（可能是配置问题）")
    except Exception as e:
        print(f"   ❌ 报价单分析异常: {e}")
    
    # 测试合同分析（模拟）
    print(f"\n5. 测试合同分析流程:")
    try:
        result = await service.analyze_contract(test_image_url, user_id=1)
        if result:
            print(f"   ✅ 合同分析成功，返回结果类型: {type(result)}")
            print(f"   - 结果字段: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        else:
            print("   ⚠️ 合同分析返回None（可能是配置问题）")
    except Exception as e:
        print(f"   ❌ 合同分析异常: {e}")
    
    print(f"\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_coze_service())

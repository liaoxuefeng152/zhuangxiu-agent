#!/usr/bin/env python3
"""
测试risk_analyzer.py中的实际逻辑
"""
import os
import sys
import asyncio

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))

async def test_risk_analyzer_logic():
    """测试risk_analyzer.py中的实际逻辑"""
    print("=== 测试risk_analyzer.py逻辑 ===")
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    
    try:
        from app.services.risk_analyzer import RiskAnalyzerService, _use_coze_site, _use_coze, get_ai_provider_name
        
        print("\n1. 检查AI服务提供商:")
        print(f"   _use_coze_site(): {_use_coze_site()}")
        print(f"   _use_coze(): {_use_coze()}")
        print(f"   get_ai_provider_name(): {get_ai_provider_name()}")
        
        print("\n2. 创建RiskAnalyzerService实例:")
        service = RiskAnalyzerService()
        print(f"   _coze_site_url: {service._coze_site_url}")
        print(f"   _coze_site_token: {'已配置' if service._coze_site_token else '未配置'}")
        print(f"   _coze_bot_id: {service._coze_bot_id}")
        print(f"   DEEPSEEK_API_KEY in client: {'已配置' if service.client.api_key else '未配置'}")
        
        print("\n3. 测试_call_coze_site()方法:")
        try:
            # 直接调用_call_coze_site方法
            system_prompt = "测试系统提示"
            user_content = "测试用户内容"
            
            print("   调用_call_coze_site()...")
            result = await service._call_coze_site(system_prompt, user_content)
            
            if result:
                print(f"   ✅ _call_coze_site()成功，返回长度: {len(result)}")
                print(f"   前200字符: {result[:200]}")
            else:
                print("   ❌ _call_coze_site()返回空")
                
                # 检查是否有DeepSeek配置
                from app.core.config import settings
                deepseek_key = getattr(settings, "DEEPSEEK_API_KEY", None) or ""
                print(f"   DeepSeek API Key配置: {'已配置' if deepseek_key.strip() else '未配置'}")
                
        except Exception as e:
            print(f"   ❌ _call_coze_site()调用失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n4. 测试完整的analyze_quote方法:")
        try:
            print("   调用analyze_quote()...")
            result = await service.analyze_quote("测试报价单", 80000.0)
            
            print(f"   analyze_quote()完成，风险评分: {result.get('risk_score', 'N/A')}")
            suggestions = result.get("suggestions", [])
            print(f"   建议数量: {len(suggestions)}")
            
            if suggestions and "AI分析服务暂时不可用" in suggestions[0]:
                print("   ⚠️  返回的是兜底结果（AI服务不可用）")
                
                # 检查兜底结果的具体内容
                print(f"   兜底结果详情:")
                print(f"     risk_score: {result.get('risk_score')}")
                print(f"     high_risk_items: {len(result.get('high_risk_items', []))}")
                print(f"     warning_items: {len(result.get('warning_items', []))}")
                print(f"     suggestions: {suggestions}")
            else:
                print("   ✅ 返回的是真实AI分析结果")
                import json
                print(f"   结果摘要: {json.dumps(result, ensure_ascii=False)[:500]}...")
                
        except Exception as e:
            print(f"   ❌ analyze_quote()调用失败: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("risk_analyzer.py逻辑测试")
    print("=" * 50)
    
    success = asyncio.run(test_risk_analyzer_logic())
    
    if success:
        print("\n✅ 逻辑测试完成")
    else:
        print("\n❌ 逻辑测试失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
详细测试AI服务提供商
"""
import os
import sys
import asyncio

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))

def test_actual_ai_provider():
    """测试实际使用的AI服务提供商"""
    print("=== 详细测试AI服务提供商 ===")
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    
    try:
        from app.core.config import settings
        from app.services.risk_analyzer import RiskAnalyzerService, _use_coze, _use_coze_site, get_ai_provider_name
        
        print("\n1. 检查配置:")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   COZE_API_TOKEN: {'已配置' if getattr(settings, 'COZE_API_TOKEN', '') else '未配置'}")
        print(f"   COZE_BOT_ID: {'已配置' if getattr(settings, 'COZE_BOT_ID', '') else '未配置'}")
        print(f"   COZE_SUPERVISOR_BOT_ID: {'已配置' if getattr(settings, 'COZE_SUPERVISOR_BOT_ID', '') else '未配置'}")
        print(f"   DEEPSEEK_API_KEY: {'已配置' if getattr(settings, 'DEEPSEEK_API_KEY', '') else '未配置'}")
        
        print("\n2. 检查AI服务提供商函数:")
        print(f"   _use_coze(): {_use_coze()}")
        print(f"   _use_coze_site(): {_use_coze_site()}")
        print(f"   get_ai_provider_name(): {get_ai_provider_name()}")
        
        print("\n3. 检查RiskAnalyzerService实例:")
        service = RiskAnalyzerService()
        print(f"   _coze_token: {'已配置' if service._coze_token else '未配置'}")
        print(f"   _coze_bot_id: {service._coze_bot_id}")
        print(f"   DEEPSEEK_API_KEY in client: {'已配置' if service.client.api_key else '未配置'}")
        
        # 测试实际分析
        print("\n4. 测试实际AI分析:")
        async def analyze():
            try:
                result = await service.analyze_quote("测试报价单", 80000.0)
                print(f"   AI分析成功: 风险评分={result.get('risk_score', 'N/A')}")
                print(f"   建议数量: {len(result.get('suggestions', []))}")
                
                # 检查是否是兜底结果
                suggestions = result.get("suggestions", [])
                if suggestions and "AI分析服务暂时不可用" in suggestions[0]:
                    print("   ⚠️  返回的是兜底结果（AI服务不可用）")
                    return "default"
                else:
                    print("   ✅ 返回的是真实AI分析结果")
                    return "real"
            except Exception as e:
                print(f"   ❌ AI分析失败: {e}")
                return "error"
        
        result_type = asyncio.run(analyze())
        
        print(f"\n5. 结论:")
        if result_type == "real":
            print("   ✅ AI分析功能正常工作，返回真实分析结果")
            print("   ⚠️  但配置有问题：COZE_BOT_ID未配置，COZE_SUPERVISOR_BOT_ID已配置")
            print("   💡 建议：修复配置，将COZE_SUPERVISOR_BOT_ID映射到COZE_BOT_ID")
        elif result_type == "default":
            print("   ⚠️  AI分析返回兜底结果，AI服务不可用")
            print("   💡 建议：修复扣子API配置或配置DeepSeek")
        else:
            print("   ❌ AI分析失败")
            print("   💡 建议：检查AI服务配置")
        
        return result_type == "real"
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_config_mapping():
    """检查配置映射问题"""
    print("\n=== 检查配置映射问题 ===")
    
    # 读取.env文件
    env_path = os.path.join(ROOT, ".env")
    if not os.path.exists(env_path):
        print(f"❌ 找不到.env文件: {env_path}")
        return
    
    config = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    print("当前.env文件中的扣子配置:")
    for key in ["COZE_API_TOKEN", "COZE_BOT_ID", "COZE_SUPERVISOR_BOT_ID", "COZE_DESIGNER_BOT_ID"]:
        if key in config:
            value = config[key]
            masked = value[:20] + "..." if len(value) > 20 else value
            print(f"   {key}: {masked}")
        else:
            print(f"   {key}: 未配置")
    
    print("\n问题分析:")
    print("1. 代码期望: COZE_BOT_ID")
    print("2. 实际配置: COZE_SUPERVISOR_BOT_ID")
    print("3. 导致: _use_coze()返回False，get_ai_provider_name()返回'none'")
    print("\n解决方案:")
    print("1. 在.env中添加: COZE_BOT_ID=7603691852046368804")
    print("2. 或修改代码，支持COZE_SUPERVISOR_BOT_ID")
    print("3. 或修改代码，将COZE_SUPERVISOR_BOT_ID映射到COZE_BOT_ID")

def main():
    """主函数"""
    print("AI服务提供商详细测试")
    print("=" * 50)
    
    # 检查配置映射问题
    check_config_mapping()
    
    # 测试实际AI服务提供商
    print("\n" + "=" * 50)
    success = test_actual_ai_provider()
    
    if success:
        print("\n✅ AI分析功能正常工作")
        print("\n⚠️  但配置有问题，需要修复：")
        print("   1. COZE_BOT_ID未配置，但COZE_SUPERVISOR_BOT_ID已配置")
        print("   2. 这可能导致生产环境出现问题")
    else:
        print("\n❌ AI分析功能有问题")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

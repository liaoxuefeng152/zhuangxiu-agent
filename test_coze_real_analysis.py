#!/usr/bin/env python3
"""
测试扣子API真实分析能力
验证报价单和合同分析是否能返回真实数据
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.coze_service import coze_service
from app.core.config import settings

async def test_quote_analysis():
    """测试报价单分析"""
    print("\n" + "="*80)
    print("测试报价单分析")
    print("="*80)
    
    # 使用一个测试图片URL
    test_image_url = "https://zhuangxiu-images-photo.oss-cn-shenzhen.aliyuncs.com/quote/test.jpg"
    
    print(f"\n1. 测试图片URL: {test_image_url[:100]}...")
    print(f"2. 扣子配置:")
    print(f"   - COZE_SITE_URL: {settings.COZE_SITE_URL}")
    print(f"   - COZE_PROJECT_ID: {settings.COZE_PROJECT_ID}")
    print(f"   - 使用站点API: {coze_service.use_site_api}")
    
    print(f"\n3. 开始调用扣子API分析报价单...")
    result = await coze_service.analyze_quote(test_image_url, user_id=1)
    
    print(f"\n4. 分析结果:")
    if result:
        print(f"   ✅ 返回了结果")
        print(f"   - 结果类型: {type(result)}")
        print(f"   - 包含字段: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        
        # 检查是否是兜底数据
        is_fallback = result.get("is_fallback", False)
        error_code = result.get("error_code")
        analysis_note = result.get("analysis_note")
        
        if is_fallback or error_code or analysis_note:
            print(f"   ⚠️  这是兜底数据:")
            print(f"      - is_fallback: {is_fallback}")
            print(f"      - error_code: {error_code}")
            print(f"      - analysis_note: {analysis_note}")
        else:
            print(f"   ✅ 这是真实的AI分析数据")
            print(f"   - risk_score: {result.get('risk_score')}")
            print(f"   - total_price: {result.get('total_price')}")
            print(f"   - high_risk_items: {len(result.get('high_risk_items', []))}个")
            print(f"   - suggestions: {len(result.get('suggestions', []))}条")
    else:
        print(f"   ❌ 返回了None")
    
    return result

async def test_contract_analysis():
    """测试合同分析"""
    print("\n" + "="*80)
    print("测试合同分析")
    print("="*80)
    
    # 使用一个测试图片URL
    test_image_url = "https://zhuangxiu-images-photo.oss-cn-shenzhen.aliyuncs.com/contract/test.jpg"
    
    print(f"\n1. 测试图片URL: {test_image_url[:100]}...")
    print(f"2. 扣子配置:")
    print(f"   - COZE_SITE_URL: {settings.COZE_SITE_URL}")
    print(f"   - COZE_PROJECT_ID: {settings.COZE_PROJECT_ID}")
    print(f"   - 使用站点API: {coze_service.use_site_api}")
    
    print(f"\n3. 开始调用扣子API分析合同...")
    result = await coze_service.analyze_contract(test_image_url, user_id=1)
    
    print(f"\n4. 分析结果:")
    if result:
        print(f"   ✅ 返回了结果")
        print(f"   - 结果类型: {type(result)}")
        print(f"   - 包含字段: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        
        # 检查是否是兜底数据
        is_fallback = result.get("is_fallback", False)
        error_code = result.get("error_code")
        analysis_note = result.get("analysis_note")
        
        if is_fallback or error_code or analysis_note:
            print(f"   ⚠️  这是兜底数据:")
            print(f"      - is_fallback: {is_fallback}")
            print(f"      - error_code: {error_code}")
            print(f"      - analysis_note: {analysis_note}")
        else:
            print(f"   ✅ 这是真实的AI分析数据")
            print(f"   - contract_type: {result.get('contract_type')}")
            print(f"   - risk_score: {result.get('risk_score')}")
            print(f"   - risk_level: {result.get('risk_level')}")
            print(f"   - high_risk_clauses: {len(result.get('high_risk_clauses', []))}个")
            print(f"   - suggestions: {len(result.get('suggestions', []))}条")
    else:
        print(f"   ❌ 返回了None")
    
    return result

async def main():
    """主函数"""
    print("\n" + "="*80)
    print("扣子API真实分析能力测试")
    print("="*80)
    
    # 测试报价单分析
    quote_result = await test_quote_analysis()
    
    # 测试合同分析
    contract_result = await test_contract_analysis()
    
    # 总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    quote_is_real = quote_result and not quote_result.get("is_fallback") and not quote_result.get("error_code")
    contract_is_real = contract_result and not contract_result.get("is_fallback") and not contract_result.get("error_code")
    
    print(f"\n报价单分析: {'✅ 返回真实数据' if quote_is_real else '❌ 返回兜底数据或失败'}")
    print(f"合同分析: {'✅ 返回真实数据' if contract_is_real else '❌ 返回兜底数据或失败'}")
    
    if not quote_is_real or not contract_is_real:
        print(f"\n⚠️  问题诊断:")
        print(f"   1. 扣子API可能无法访问测试图片URL")
        print(f"   2. 扣子智能体可能返回了工具调用说明而非分析结果")
        print(f"   3. 扣子API响应格式可能与代码解析逻辑不匹配")
        print(f"   4. 需要检查扣子站点的工作流配置")

if __name__ == "__main__":
    asyncio.run(main())

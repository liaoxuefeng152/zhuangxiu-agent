#!/usr/bin/env python3
"""
测试AI分析服务返回数据格式
"""
import json
import sys
import os

# 设置环境变量避免配置验证
os.environ['ENVIRONMENT'] = 'development'
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://test:test@localhost/test'
os.environ['WECHAT_APP_ID'] = 'test'
os.environ['WECHAT_APP_SECRET'] = 'test'
os.environ['JWT_SECRET_KEY'] = 'test'
os.environ['REDIS_URL'] = 'redis://localhost:6379'

sys.path.append('/Users/mac/zhuangxiu-agent/backend')

from app.services.risk_analyzer import RiskAnalyzerService

async def test_ai_data_format():
    """测试AI分析服务返回数据格式"""
    service = RiskAnalyzerService()
    
    # 测试报价单分析
    print("=== 测试报价单分析返回格式 ===")
    
    # 模拟OCR文本
    ocr_text = """
    装修报价单
    
    项目名称：深圳XX小区装修
    面积：89平方米
    户型：三室一厅
    
    项目明细：
    1. 水电改造：120元/米，预计80米，合计9600元
    2. 墙面处理：45元/平方米，预计200平方米，合计9000元
    3. 地面铺砖：120元/平方米，预计60平方米，合计7200元
    4. 吊顶工程：180元/平方米，预计30平方米，合计5400元
    5. 厨卫防水：85元/平方米，预计25平方米，合计2125元
    
    总计：33325元
    """
    
    try:
        result = await service.analyze_quote(ocr_text, total_price=33325)
        print(f"分析结果类型: {type(result)}")
        print(f"分析结果键: {list(result.keys())}")
        print(f"风险评分: {result.get('risk_score')}")
        print(f"高风险项: {len(result.get('high_risk_items', []))} 个")
        print(f"警告项: {len(result.get('warning_items', []))} 个")
        print(f"缺失项: {len(result.get('missing_items', []))} 个")
        print(f"虚高价项: {len(result.get('overpriced_items', []))} 个")
        print(f"建议: {result.get('suggestions', [])}")
        print(f"市场参考价: {result.get('market_ref_price')}")
        
        # 检查是否有兜底数据
        suggestions = result.get("suggestions") or []
        if suggestions and suggestions[0] == "AI分析服务暂时不可用，请稍后重试":
            print("⚠️ 警告: 返回的是兜底数据，AI服务可能未配置")
        else:
            print("✅ AI分析服务返回了真实数据")
            
        # 输出完整JSON格式
        print("\n=== 完整JSON格式 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ai_data_format())

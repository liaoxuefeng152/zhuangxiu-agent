import asyncio
import sys
sys.path.append('backend')
from app.services.risk_analyzer import risk_analyzer_service

async def test_ai_analysis():
    print("测试阿里云服务器AI分析服务...")
    
    # 测试报价单分析
    quote_text = """
装修报价单
项目名称：深圳89㎡三室一厅半包装修

1. 水电改造
   - 单价：120元/米
   - 工程量：150米
   - 总价：18000元

2. 泥工铺贴
   - 单价：80元/㎡
   - 工程量：120㎡
   - 总价：9600元

3. 木工制作
   - 单价：200元/米
   - 工程量：80米
   - 总价：16000元

4. 油漆工程
   - 单价：60元/㎡
   - 工程量：300㎡
   - 总价：18000元

5. 管理费
   - 总价：5000元

合计总价：80000元
"""
    
    print("调用AI分析服务...")
    try:
        result = await risk_analyzer_service.analyze_quote(quote_text, 80000)
        print(f"AI分析结果: {result}")
        
        if result.get("suggestions") and result["suggestions"][0] == "AI分析服务暂时不可用，请稍后重试":
            print("❌ AI分析返回兜底结果，服务不可用")
            return False
        else:
            print(f"✅ AI分析成功，风险评分: {result.get('risk_score')}")
            print(f"   高风险项目: {len(result.get('high_risk_items', []))}")
            print(f"   警告项目: {len(result.get('warning_items', []))}")
            print(f"   建议: {result.get('suggestions', [])}")
            return True
    except Exception as e:
        print(f"❌ AI分析失败: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_ai_analysis())
    sys.exit(0 if result else 1)

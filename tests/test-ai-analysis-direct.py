#!/usr/bin/env python3
"""
直接测试AI分析功能（绕过OCR识别）
"""
import asyncio
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.risk_analyzer import risk_analyzer_service

# 模拟OCR识别的文本
MOCK_QUOTE_TEXT = """
装修报价单

项目名称：深圳住宅装修（89㎡三室一厅）
装修类型：半包装修
品质等级：中档品质

项目明细：
1. 水电改造工程
   - 强电改造：120元/米，共80米，合计：9600元
   - 弱电改造：80元/米，共50米，合计：4000元
   - 水路改造：150元/米，共60米，合计：9000元
   小计：22600元

2. 泥工工程
   - 地面找平：45元/㎡，共89㎡，合计：4005元
   - 墙砖铺贴：65元/㎡，共120㎡，合计：7800元
   - 地砖铺贴：55元/㎡，共89㎡，合计：4895元
   小计：16700元

3. 木工工程
   - 吊顶：120元/㎡，共60㎡，合计：7200元
   - 定制柜体：800元/延米，共15延米，合计：12000元
   小计：19200元

4. 油漆工程
   - 墙面乳胶漆：35元/㎡，共280㎡，合计：9800元
   - 木器漆：80元/㎡，共40㎡，合计：3200元
   小计：13000元

5. 其他费用
   - 垃圾清运费：2000元
   - 材料运输费：1500元
   - 管理费：5000元
   小计：8500元

总计：80000元

备注：以上价格不含主材，主材由业主自行采购。
"""

MOCK_CONTRACT_TEXT = """
深圳市住宅装饰装修工程施工合同

甲方（委托方）：张三
乙方（承包方）：深圳XX装饰工程有限公司

第一条 工程概况
1.1 工程地点：深圳市南山区XX小区XX栋XX室
1.2 工程内容：住宅室内装修
1.3 工程承包方式：半包
1.4 工程期限：90天

第二条 工程价款
2.1 工程总价款：80000元（人民币捌万元整）
2.2 付款方式：
   - 合同签订时支付30%：24000元
   - 水电验收后支付30%：24000元
   - 泥木验收后支付30%：24000元
   - 竣工验收后支付10%：8000元

第三条 材料供应
3.1 主材由甲方采购
3.2 辅材由乙方提供

第四条 工程质量
4.1 工程质量标准：符合国家相关标准
4.2 保修期：2年

第五条 违约责任
5.1 如乙方延期完工，每延期一天支付违约金500元
5.2 如甲方延期付款，每延期一天支付违约金500元

第六条 其他条款
6.1 本合同一式两份，甲乙双方各执一份
6.2 本合同自双方签字之日起生效

甲方签字：张三
乙方签字：XX装饰公司
日期：2026年1月1日
"""


async def test_quote_analysis():
    """测试报价单AI分析功能"""
    print("=" * 60)
    print("【测试1: 装修报价AI分析功能】")
    print("=" * 60)
    
    print(f"📝 输入文本长度: {len(MOCK_QUOTE_TEXT)} 字符")
    print(f"📝 前200字符预览:\n{MOCK_QUOTE_TEXT[:200]}...\n")
    
    try:
        print("🤖 调用AI分析服务...")
        # 提取总价（模拟代码中的逻辑）
        import re
        total_price = None
        price_match = re.search(r'[总合]计[^\d]*(\d+(?:\.\d+)?)', MOCK_QUOTE_TEXT)
        if price_match:
            total_price = float(price_match.group(1))
            print(f"💰 提取到的总价: {total_price} 元")
        
        # 调用AI分析
        result = await risk_analyzer_service.analyze_quote(MOCK_QUOTE_TEXT, total_price)
        
        if result:
            print("\n✅ AI分析成功！")
            print("\n📊 分析结果:")
            print(f"   风险评分: {result.get('risk_score', 'N/A')}")
            print(f"   总价: {result.get('total_price', 'N/A')} 元")
            print(f"   市场参考价: {result.get('market_ref_price', 'N/A')} 元")
            
            high_risk = result.get('high_risk_items', [])
            if high_risk:
                print(f"\n   ⚠️  高风险项目 ({len(high_risk)}项):")
                for i, item in enumerate(high_risk[:5], 1):
                    print(f"      {i}. {item}")
            
            warning = result.get('warning_items', [])
            if warning:
                print(f"\n   ⚠️  警告项目 ({len(warning)}项):")
                for i, item in enumerate(warning[:5], 1):
                    print(f"      {i}. {item}")
            
            missing = result.get('missing_items', [])
            if missing:
                print(f"\n   📋 缺失项目 ({len(missing)}项):")
                for i, item in enumerate(missing[:5], 1):
                    print(f"      {i}. {item}")
            
            overpriced = result.get('overpriced_items', [])
            if overpriced:
                print(f"\n   💰 价格偏高项目 ({len(overpriced)}项):")
                for i, item in enumerate(overpriced[:5], 1):
                    print(f"      {i}. {item}")
            
            # 显示完整结果（JSON格式）
            print(f"\n📄 完整分析结果（JSON）:")
            import json
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            return True
        else:
            print("❌ AI分析返回None")
            return False
            
    except Exception as e:
        print(f"❌ AI分析异常: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_contract_analysis():
    """测试合同AI审核功能"""
    print("\n" + "=" * 60)
    print("【测试2: 装修合同AI审核功能】")
    print("=" * 60)
    
    print(f"📝 输入文本长度: {len(MOCK_CONTRACT_TEXT)} 字符")
    print(f"📝 前200字符预览:\n{MOCK_CONTRACT_TEXT[:200]}...\n")
    
    try:
        print("🤖 调用AI审核服务...")
        
        # 调用AI分析
        result = await risk_analyzer_service.analyze_contract(MOCK_CONTRACT_TEXT)
        
        if result:
            print("\n✅ AI审核成功！")
            print("\n📊 审核结果:")
            print(f"   风险等级: {result.get('risk_level', 'N/A')}")
            
            risk_items = result.get('risk_items', [])
            if risk_items:
                print(f"\n   ⚠️  风险条款 ({len(risk_items)}项):")
                for i, item in enumerate(risk_items[:5], 1):
                    print(f"      {i}. {item}")
            
            unfair = result.get('unfair_terms', [])
            if unfair:
                print(f"\n   ⚠️  不公平条款 ({len(unfair)}项):")
                for i, item in enumerate(unfair[:5], 1):
                    print(f"      {i}. {item}")
            
            missing = result.get('missing_terms', [])
            if missing:
                print(f"\n   📋 缺失条款 ({len(missing)}项):")
                for i, item in enumerate(missing[:5], 1):
                    print(f"      {i}. {item}")
            
            suggestions = result.get('suggested_modifications', [])
            if suggestions:
                print(f"\n   💡 建议修改 ({len(suggestions)}项):")
                for i, item in enumerate(suggestions[:5], 1):
                    print(f"      {i}. {item}")
            
            # 显示完整结果（JSON格式）
            print(f"\n📄 完整审核结果（JSON）:")
            import json
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            return True
        else:
            print("❌ AI审核返回None")
            return False
            
    except Exception as e:
        print(f"❌ AI审核异常: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("=" * 60)
    print("AI分析功能直接测试（绕过OCR）")
    print("=" * 60)
    
    # 检查AI服务配置
    from app.services.risk_analyzer import get_ai_provider_name
    provider = get_ai_provider_name()
    print(f"🤖 AI服务提供商: {provider}")
    
    if provider == "none":
        print("⚠️  警告: 未配置AI服务（DeepSeek或Coze），测试可能失败")
    
    print()
    
    # 测试报价单分析
    quote_result = await test_quote_analysis()
    
    # 测试合同审核
    contract_result = await test_contract_analysis()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"报价单AI分析功能: {'✅ 通过' if quote_result else '❌ 失败'}")
    print(f"合同AI审核功能: {'✅ 通过' if contract_result else '❌ 失败'}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

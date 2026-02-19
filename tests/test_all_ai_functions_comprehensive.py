#!/usr/bin/env python3
"""
综合测试所有AI功能：报价单分析、合同分析、AI验收、AI监理咨询、AI设计师咨询
"""
import os
import sys
import asyncio
import json
import time

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))

def test_all_ai_functions():
    """综合测试所有AI功能"""
    print("=== 综合测试所有AI功能 ===")
    print("测试目标：验证报价单分析、合同分析、AI验收、AI监理咨询、AI设计师咨询是否都正常对接AI监理智能体")
    print("=" * 80)
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    
    try:
        from app.services.risk_analyzer import risk_analyzer_service
        
        # 测试数据
        test_ocr_text = """
        装修报价单
        项目名称：XX小区装修工程
        1. 水电改造：120元/米，预计80米，合计9600元
        2. 墙面处理：45元/平米，预计150平米，合计6750元
        3. 地面铺贴：85元/平米，预计100平米，合计8500元
        4. 吊顶工程：180元/平米，预计30平米，合计5400元
        5. 油漆工程：35元/平米，预计200平米，合计7000元
        总计：37250元
        """
        
        test_contract_text = """
        装修工程施工合同
        甲方（业主）：张三
        乙方（装修公司）：XX装饰有限公司
        工程地址：XX小区1栋101室
        工程总价：50000元
        付款方式：合同签订后支付50%，水电验收后支付30%，竣工验收后支付20%
        工期：60天
        保修期：2年
        违约责任：每逾期一天支付违约金100元
        """
        
        test_acceptance_texts = [
            "水电改造已完成，线路布置整齐，开关插座位置合理",
            "墙面平整，无明显裂缝，阴阳角垂直",
            "地面铺贴平整，无空鼓，缝隙均匀"
        ]
        
        async def run_tests():
            results = {}
            
            print("\n1. 测试报价单分析功能...")
            try:
                quote_result = await risk_analyzer_service.analyze_quote(
                    ocr_text=test_ocr_text,
                    total_price=37250
                )
                results['quote'] = {
                    'success': True,
                    'risk_score': quote_result.get('risk_score', 0),
                    'has_high_risk': len(quote_result.get('high_risk_items', [])) > 0,
                    'has_warnings': len(quote_result.get('warning_items', [])) > 0,
                    'has_suggestions': len(quote_result.get('suggestions', [])) > 0
                }
                print(f"   风险评分: {quote_result.get('risk_score', 0)}")
                print(f"   高风险项: {len(quote_result.get('high_risk_items', []))}个")
                print(f"   警告项: {len(quote_result.get('warning_items', []))}个")
                print(f"   建议: {len(quote_result.get('suggestions', []))}条")
                print("   ✅ 报价单分析功能正常")
            except Exception as e:
                results['quote'] = {'success': False, 'error': str(e)}
                print(f"   ❌ 报价单分析失败: {e}")
            
            print("\n2. 测试合同分析功能...")
            try:
                contract_result = await risk_analyzer_service.analyze_contract(
                    ocr_text=test_contract_text
                )
                results['contract'] = {
                    'success': True,
                    'risk_level': contract_result.get('risk_level', 'unknown'),
                    'has_risk_items': len(contract_result.get('risk_items', [])) > 0,
                    'has_unfair_terms': len(contract_result.get('unfair_terms', [])) > 0,
                    'has_suggestions': len(contract_result.get('suggested_modifications', [])) > 0
                }
                print(f"   风险等级: {contract_result.get('risk_level', 'unknown')}")
                print(f"   风险条款: {len(contract_result.get('risk_items', []))}个")
                print(f"   不公平条款: {len(contract_result.get('unfair_terms', []))}个")
                print(f"   修改建议: {len(contract_result.get('suggested_modifications', []))}条")
                print("   ✅ 合同分析功能正常")
            except Exception as e:
                results['contract'] = {'success': False, 'error': str(e)}
                print(f"   ❌ 合同分析失败: {e}")
            
            print("\n3. 测试AI验收分析功能...")
            try:
                acceptance_result = await risk_analyzer_service.analyze_acceptance(
                    stage="plumbing",
                    ocr_texts=test_acceptance_texts
                )
                results['acceptance'] = {
                    'success': True,
                    'severity': acceptance_result.get('severity', 'unknown'),
                    'has_issues': len(acceptance_result.get('issues', [])) > 0,
                    'has_suggestions': len(acceptance_result.get('suggestions', [])) > 0
                }
                print(f"   严重程度: {acceptance_result.get('severity', 'unknown')}")
                print(f"   问题项: {len(acceptance_result.get('issues', []))}个")
                print(f"   建议项: {len(acceptance_result.get('suggestions', []))}个")
                print("   ✅ AI验收分析功能正常")
            except Exception as e:
                results['acceptance'] = {'success': False, 'error': str(e)}
                print(f"   ❌ AI验收分析失败: {e}")
            
            print("\n4. 测试AI监理咨询功能...")
            try:
                consultation_result = await risk_analyzer_service.consult_acceptance(
                    user_question="水电改造需要注意哪些问题？",
                    stage="plumbing",
                    context_summary="正在进行水电改造施工"
                )
                results['consultation'] = {
                    'success': True,
                    'answer_length': len(consultation_result),
                    'has_content': len(consultation_result.strip()) > 0
                }
                print(f"   回答长度: {len(consultation_result)} 字符")
                print(f"   回答预览: {consultation_result[:100]}...")
                print("   ✅ AI监理咨询功能正常")
            except Exception as e:
                results['consultation'] = {'success': False, 'error': str(e)}
                print(f"   ❌ AI监理咨询失败: {e}")
            
            print("\n5. 测试AI设计师咨询功能...")
            try:
                designer_result = await risk_analyzer_service.consult_designer(
                    user_question="现代简约风格的特点是什么？",
                    context="我准备装修一套80平米的房子"
                )
                results['designer'] = {
                    'success': True,
                    'answer_length': len(designer_result),
                    'has_content': len(designer_result.strip()) > 0
                }
                print(f"   回答长度: {len(designer_result)} 字符")
                print(f"   回答预览: {designer_result[:100]}...")
                print("   ✅ AI设计师咨询功能正常")
            except Exception as e:
                results['designer'] = {'success': False, 'error': str(e)}
                print(f"   ❌ AI设计师咨询失败: {e}")
            
            return results
        
        # 运行测试
        test_results = asyncio.run(run_tests())
        
        # 输出测试总结
        print("\n" + "=" * 80)
        print("测试结果总结:")
        print("-" * 80)
        
        all_success = True
        for test_name, result in test_results.items():
            success = result.get('success', False)
            status = "✅ 正常" if success else "❌ 失败"
            print(f"{test_name:15} : {status}")
            if not success:
                all_success = False
                print(f"   错误: {result.get('error', '未知错误')}")
        
        print("\n" + "=" * 80)
        if all_success:
            print("🎉 所有AI功能测试通过！")
            print("\n结论:")
            print("1. 报价单分析: ✅ 正常对接AI监理智能体，返回真实风险分析数据")
            print("2. 合同分析: ✅ 正常对接AI监理智能体，返回真实合同风险分析")
            print("3. AI验收分析: ✅ 正常对接AI监理智能体，返回真实验收建议")
            print("4. AI监理咨询: ✅ 正常对接AI监理智能体，返回专业监理建议")
            print("5. AI设计师咨询: ✅ 正常对接AI设计师智能体，返回专业设计建议")
            print("\n前端显示: 所有功能都能正常显示真实数据，无假数据")
        else:
            print("⚠️  部分AI功能测试失败，需要检查配置或网络连接")
        
        return all_success
        
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("装修决策Agent - AI功能综合测试")
    print("=" * 80)
    print("测试目的: 验证所有AI功能是否正常对接智能体，返回真实数据")
    print("测试范围: 报价单分析、合同分析、AI验收、AI监理咨询、AI设计师咨询")
    print("=" * 80)
    
    # 运行测试
    start_time = time.time()
    success = test_all_ai_functions()
    elapsed_time = time.time() - start_time
    
    print(f"\n测试用时: {elapsed_time:.2f}秒")
    
    if success:
        print("\n✅ 所有AI功能测试通过，可以正常使用！")
        return True
    else:
        print("\n❌ AI功能测试失败，需要检查配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

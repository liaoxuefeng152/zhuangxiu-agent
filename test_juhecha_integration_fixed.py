#!/usr/bin/env python3
"""
测试聚合数据API集成（去掉天眼查，只用聚合数据）
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 设置环境变量
os.environ.setdefault("ENV", "development")

from backend.app.services.juhecha_service import juhecha_service


async def test_enterprise_search():
    """测试企业工商信息搜索"""
    print("=== 测试企业工商信息搜索 ===")
    
    # 测试搜索关键词
    test_keywords = ["装饰", "装修", "设计", "建筑"]
    
    for keyword in test_keywords:
        print(f"\n搜索关键词: {keyword}")
        try:
            results = await juhecha_service.search_enterprise_info(keyword, limit=3)
            if results:
                print(f"找到 {len(results)} 个企业:")
                for i, enterprise in enumerate(results, 1):
                    print(f"  {i}. {enterprise.get('name')}")
                    print(f"     统一社会信用代码: {enterprise.get('credit_no', 'N/A')}")
                    print(f"     法人: {enterprise.get('oper_name', 'N/A')}")
                    print(f"     成立日期: {enterprise.get('start_date', 'N/A')}")
            else:
                print("未找到相关企业")
        except Exception as e:
            print(f"搜索失败: {e}")


async def test_enterprise_detail():
    """测试企业详细信息获取"""
    print("\n=== 测试企业详细信息获取 ===")
    
    # 测试企业名称
    test_companies = ["耒阳市怡馨装饰设计工程有限公司", "装饰", "装修"]
    
    for company_name in test_companies:
        print(f"\n查询企业: {company_name}")
        try:
            detail = await juhecha_service.get_enterprise_detail(company_name)
            if detail:
                print(f"企业名称: {detail.get('name')}")
                print(f"统一社会信用代码: {detail.get('credit_no', 'N/A')}")
                print(f"注册号: {detail.get('reg_no', 'N/A')}")
                print(f"法人: {detail.get('oper_name', 'N/A')}")
                print(f"成立日期: {detail.get('start_date', 'N/A')}")
                print(f"企业年龄: {detail.get('enterprise_age', 'N/A')} 年")
            else:
                print("未找到企业详细信息")
        except Exception as e:
            print(f"查询失败: {e}")


async def test_legal_cases():
    """测试法律案件查询"""
    print("\n=== 测试法律案件查询 ===")
    
    # 测试企业名称
    test_companies = ["装饰", "装修", "建筑"]
    
    for company_name in test_companies:
        print(f"\n查询企业法律案件: {company_name}")
        try:
            cases = await juhecha_service.search_company_legal_cases(company_name, limit=5)
            if cases:
                print(f"找到 {len(cases)} 个法律案件:")
                for i, case in enumerate(cases, 1):
                    print(f"  {i}. {case.get('title', 'N/A')}")
                    print(f"     类型: {case.get('data_type_zh', 'N/A')}")
                    print(f"     日期: {case.get('date', 'N/A')}")
                    print(f"     内容摘要: {case.get('content', 'N/A')[:50]}...")
            else:
                print("未找到法律案件")
        except Exception as e:
            print(f"查询失败: {e}")


async def test_legal_risk_analysis():
    """测试法律风险分析"""
    print("\n=== 测试法律风险分析 ===")
    
    # 测试企业名称
    test_companies = ["装饰", "装修", "建筑"]
    
    for company_name in test_companies:
        print(f"\n分析企业法律风险: {company_name}")
        try:
            analysis = await juhecha_service.analyze_company_legal_risk(company_name)
            if analysis:
                print(f"法律案件数量: {analysis.get('legal_case_count', 0)}")
                print(f"装修相关案件: {analysis.get('decoration_related_cases', 0)}")
                print(f"风险评分调整: {analysis.get('risk_score_adjustment', 0)}")
                print(f"风险原因: {analysis.get('risk_reasons', [])}")
                print(f"案件类型: {analysis.get('case_types', [])}")
            else:
                print("分析失败")
        except Exception as e:
            print(f"分析失败: {e}")


async def test_comprehensive_analysis():
    """测试综合分析"""
    print("\n=== 测试综合分析 ===")
    
    # 测试企业名称
    test_companies = ["耒阳市怡馨装饰设计工程有限公司", "装饰", "装修"]
    
    for company_name in test_companies:
        print(f"\n综合分析企业: {company_name}")
        try:
            analysis = await juhecha_service.analyze_company_comprehensive(company_name)
            if analysis:
                # 企业信息
                enterprise_info = analysis.get('enterprise_info')
                if enterprise_info:
                    print("企业信息:")
                    print(f"  名称: {enterprise_info.get('name', 'N/A')}")
                    print(f"  法人: {enterprise_info.get('oper_name', 'N/A')}")
                    print(f"  成立日期: {enterprise_info.get('start_date', 'N/A')}")
                    print(f"  企业年龄: {enterprise_info.get('enterprise_age', 'N/A')} 年")
                
                # 法律分析
                legal_analysis = analysis.get('legal_analysis')
                if legal_analysis:
                    print("法律分析:")
                    print(f"  案件数量: {legal_analysis.get('legal_case_count', 0)}")
                    print(f"  装修相关案件: {legal_analysis.get('decoration_related_cases', 0)}")
                    print(f"  风险原因: {legal_analysis.get('risk_reasons', [])}")
                
                # 风险摘要
                risk_summary = analysis.get('risk_summary')
                if risk_summary:
                    print("风险摘要:")
                    print(f"  风险等级: {risk_summary.get('risk_level', 'N/A')}")
                    print(f"  风险评分: {risk_summary.get('risk_score', 0)}")
                    print(f"  建议: {risk_summary.get('recommendation', 'N/A')}")
            else:
                print("综合分析失败")
        except Exception as e:
            print(f"综合分析失败: {e}")


async def test_api_configuration():
    """测试API配置"""
    print("\n=== 测试API配置 ===")
    
    # 检查Token配置
    print("检查聚合数据API配置:")
    print(f"司法企业查询Token: {'已配置' if juhecha_service._has_valid_sifa_token() else '未配置'}")
    print(f"企业工商信息Token: {'已配置' if juhecha_service._has_valid_enterprise_token() else '未配置'}")
    
    if not juhecha_service._has_valid_sifa_token():
        print("警告: 司法企业查询Token未配置，法律案件查询功能将不可用")
    
    if not juhecha_service._has_valid_enterprise_token():
        print("警告: 企业工商信息Token未配置，企业信息查询功能将不可用")


async def main():
    """主测试函数"""
    print("聚合数据API集成测试")
    print("=" * 50)
    
    # 测试API配置
    await test_api_configuration()
    
    # 测试企业搜索
    await test_enterprise_search()
    
    # 测试企业详情
    await test_enterprise_detail()
    
    # 测试法律案件
    await test_legal_cases()
    
    # 测试法律风险分析
    await test_legal_risk_analysis()
    
    # 测试综合分析
    await test_comprehensive_analysis()
    
    print("\n" + "=" * 50)
    print("测试完成")


if __name__ == "__main__":
    asyncio.run(main())

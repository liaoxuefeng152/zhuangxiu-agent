#!/usr/bin/env python3
"""
简单测试聚合数据API集成
"""
import asyncio
import sys
import os

# 设置环境变量
os.environ.setdefault("ENV", "development")

# 添加backend目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")
sys.path.insert(0, backend_dir)

# 直接导入配置和juhecha_service
try:
    # 先导入配置
    from app.core.config import settings
    print(f"配置加载成功: APP_NAME={settings.APP_NAME}")
    
    # 创建JuhechaService实例
    from app.services.juhecha_service import JuhechaService
    juhecha_service = JuhechaService()
    
    print("聚合数据服务初始化成功")
    
except Exception as e:
    print(f"初始化失败: {e}")
    sys.exit(1)


async def test_basic_functionality():
    """测试基本功能"""
    print("\n=== 测试基本功能 ===")
    
    # 测试Token配置
    print("检查Token配置:")
    print(f"司法企业查询Token: {'已配置' if juhecha_service._has_valid_sifa_token() else '未配置'}")
    print(f"企业工商信息Token: {'已配置' if juhecha_service._has_valid_enterprise_token() else '未配置'}")
    
    # 测试企业搜索
    print("\n测试企业搜索:")
    try:
        results = await juhecha_service.search_enterprise_info("装饰", limit=2)
        if results:
            print(f"找到 {len(results)} 个企业:")
            for i, enterprise in enumerate(results, 1):
                print(f"  {i}. {enterprise.get('name', 'N/A')}")
        else:
            print("未找到相关企业")
    except Exception as e:
        print(f"企业搜索失败: {e}")
    
    # 测试法律案件查询
    print("\n测试法律案件查询:")
    try:
        cases = await juhecha_service.search_company_legal_cases("装饰", limit=2)
        if cases:
            print(f"找到 {len(cases)} 个法律案件:")
            for i, case in enumerate(cases, 1):
                print(f"  {i}. {case.get('title', 'N/A')[:30]}...")
        else:
            print("未找到法律案件")
    except Exception as e:
        print(f"法律案件查询失败: {e}")
    
    # 测试综合分析
    print("\n测试综合分析:")
    try:
        analysis = await juhecha_service.analyze_company_comprehensive("装饰")
        if analysis:
            print("综合分析成功:")
            
            enterprise_info = analysis.get('enterprise_info')
            if enterprise_info:
                print(f"  企业名称: {enterprise_info.get('name', 'N/A')}")
            
            legal_analysis = analysis.get('legal_analysis')
            if legal_analysis:
                print(f"  法律案件数量: {legal_analysis.get('legal_case_count', 0)}")
            
            risk_summary = analysis.get('risk_summary')
            if risk_summary:
                print(f"  风险等级: {risk_summary.get('risk_level', 'N/A')}")
                print(f"  风险评分: {risk_summary.get('risk_score', 0)}")
        else:
            print("综合分析失败")
    except Exception as e:
        print(f"综合分析失败: {e}")


async def main():
    """主测试函数"""
    print("聚合数据API集成测试")
    print("=" * 50)
    
    await test_basic_functionality()
    
    print("\n" + "=" * 50)
    print("测试完成")


if __name__ == "__main__":
    asyncio.run(main())

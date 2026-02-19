#!/usr/bin/env python3
"""
测试聚合数据API集成
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

# 设置环境变量
os.environ["ENV"] = "development"

# 导入服务
try:
    from app.services.juhecha_service import juhecha_service
    from app.services.tianyancha_service import tianyancha_service
    print("✅ 服务导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("尝试直接导入...")
    # 尝试直接导入
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "juhecha_service", 
        os.path.join(os.path.dirname(__file__), "backend/app/services/juhecha_service.py")
    )
    juhecha_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(juhecha_module)
    juhecha_service = juhecha_module.juhecha_service
    
    spec = importlib.util.spec_from_file_location(
        "tianyancha_service", 
        os.path.join(os.path.dirname(__file__), "backend/app/services/tianyancha_service.py")
    )
    tianyancha_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tianyancha_module)
    tianyancha_service = tianyancha_module.tianyancha_service
    print("✅ 直接导入成功")


async def test_juhecha_service():
    """测试聚合数据服务"""
    print("=" * 60)
    print("测试聚合数据API集成")
    print("=" * 60)
    
    # 测试公司名称
    test_companies = [
        "耒阳市怡馨装饰设计工程有限公司",  # 用户测试的公司
        "北京装修公司",
        "上海装饰公司"
    ]
    
    for company_name in test_companies:
        print(f"\n测试公司: {company_name}")
        print("-" * 40)
        
        try:
            # 测试聚合数据API
            print("1. 测试聚合数据法律案件查询...")
            legal_cases = await juhecha_service.search_company_legal_cases(company_name, limit=5)
            
            if legal_cases:
                print(f"   找到 {len(legal_cases)} 条法律案件:")
                for i, case in enumerate(legal_cases[:3], 1):
                    print(f"   {i}. {case.get('title', '无标题')}")
                    print(f"      类型: {case.get('data_type_zh', '未知')}")
                    print(f"      日期: {case.get('date', '未知')}")
                    print(f"      内容摘要: {case.get('content', '')[:50]}...")
            else:
                print("   未找到法律案件")
            
            # 测试法律风险分析
            print("\n2. 测试法律风险分析...")
            legal_analysis = await juhecha_service.analyze_company_legal_risk(company_name)
            
            print(f"   法律案件数量: {legal_analysis.get('legal_case_count', 0)}")
            print(f"   装修相关案件: {legal_analysis.get('decoration_related_cases', 0)}")
            print(f"   风险评分调整: {legal_analysis.get('risk_score_adjustment', 0)}")
            print(f"   风险原因: {legal_analysis.get('risk_reasons', [])}")
            
            # 测试天眼查服务（对比）
            print("\n3. 测试天眼查服务（对比）...")
            try:
                tyc_analysis = await tianyancha_service.analyze_company_risk(company_name)
                print(f"   天眼查风险等级: {tyc_analysis.get('risk_level', '未知')}")
                print(f"   天眼查风险评分: {tyc_analysis.get('risk_score', 0)}")
                print(f"   天眼查投诉数量: {tyc_analysis.get('complaint_count', 0)}")
            except Exception as e:
                print(f"   天眼查测试失败: {e}")
            
            # 计算合并风险评分
            tyc_score = tyc_analysis.get('risk_score', 0) if 'tyc_analysis' in locals() else 0
            juhe_adjustment = legal_analysis.get('risk_score_adjustment', 0)
            combined_score = min(tyc_score + juhe_adjustment, 100)
            
            print(f"\n4. 合并风险分析:")
            print(f"   天眼查基础评分: {tyc_score}")
            print(f"   聚合数据调整: {juhe_adjustment}")
            print(f"   合并风险评分: {combined_score}")
            
            if combined_score >= 70:
                risk_level = "高风险"
            elif combined_score >= 30:
                risk_level = "警告"
            else:
                risk_level = "合规"
            
            print(f"   最终风险等级: {risk_level}")
            
        except Exception as e:
            print(f"   测试失败: {e}")
            import traceback
            traceback.print_exc()


async def test_api_config():
    """测试API配置"""
    print("\n" + "=" * 60)
    print("测试API配置")
    print("=" * 60)
    
    # 检查聚合数据Token
    token = juhecha_service.token
    if token and token not in ("xxx", "your_token", "your_token_here"):
        print(f"✅ 聚合数据Token已配置: {token[:10]}...")
    else:
        print("❌ 聚合数据Token未配置或无效")
    
    # 检查天眼查Token
    tyc_token = tianyancha_service.token
    if tyc_token and tyc_token not in ("xxx", "your_token", "your_token_here"):
        print(f"✅ 天眼查Token已配置: {tyc_token[:10]}...")
    else:
        print("❌ 天眼查Token未配置或无效")
    
    # 检查API基础URL
    print(f"聚合数据API基础URL: {juhecha_service.base_url}")
    print(f"聚合数据司法端点: {juhecha_service.sifa_endpoint}")


async def test_specific_company():
    """测试特定公司（用户测试的公司）"""
    print("\n" + "=" * 60)
    print("测试用户提供的公司")
    print("=" * 60)
    
    company_name = "耒阳市怡馨装饰设计工程有限公司"
    print(f"测试公司: {company_name}")
    
    try:
        # 测试聚合数据API
        print("\n1. 聚合数据API测试:")
        legal_cases = await juhecha_service.search_company_legal_cases(company_name, limit=10)
        
        if legal_cases:
            print(f"   找到 {len(legal_cases)} 条法律案件:")
            for i, case in enumerate(legal_cases, 1):
                print(f"   {i}. {case.get('title', '无标题')}")
                print(f"      类型: {case.get('data_type_zh', '未知')}")
                print(f"      日期: {case.get('date', '未知')}")
                
                # 检查是否是装修相关
                title = case.get('title', '').lower()
                content = case.get('content', '').lower()
                decoration_keywords = ["装饰", "装修", "装潢", "家装", "工装"]
                is_decoration = any(keyword in title or keyword in content for keyword in decoration_keywords)
                if is_decoration:
                    print(f"      🔥 装修相关案件")
        else:
            print("   未找到法律案件")
        
        # 测试法律风险分析
        print("\n2. 法律风险分析:")
        legal_analysis = await juhecha_service.analyze_company_legal_risk(company_name)
        
        print(f"   法律案件总数: {legal_analysis.get('legal_case_count', 0)}")
        print(f"   装修相关案件: {legal_analysis.get('decoration_related_cases', 0)}")
        print(f"   案件类型: {legal_analysis.get('case_types', [])}")
        print(f"   风险原因: {legal_analysis.get('risk_reasons', [])}")
        print(f"   风险评分调整: {legal_analysis.get('risk_score_adjustment', 0)}")
        
        # 显示最近案件
        recent_cases = legal_analysis.get('recent_cases', [])
        if recent_cases:
            print(f"\n3. 最近案件（最多5条）:")
            for i, case in enumerate(recent_cases, 1):
                print(f"   {i}. {case.get('title', '无标题')}")
        
    except Exception as e:
        print(f"   测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主测试函数"""
    print("开始测试聚合数据API集成...")
    
    # 测试API配置
    await test_api_config()
    
    # 测试聚合数据服务
    await test_juhecha_service()
    
    # 测试特定公司
    await test_specific_company()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

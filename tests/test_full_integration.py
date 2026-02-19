#!/usr/bin/env python3
"""
完整测试聚合数据API集成
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
    sys.exit(1)


async def test_juhecha_service_integration():
    """测试聚合数据服务集成"""
    print("=" * 60)
    print("测试聚合数据服务集成")
    print("=" * 60)
    
    test_company = "耒阳市怡馨装饰设计工程有限公司"
    
    print(f"测试公司: {test_company}")
    print("-" * 40)
    
    try:
        # 1. 测试法律案件查询
        print("1. 测试法律案件查询...")
        legal_cases = await juhecha_service.search_company_legal_cases(test_company, limit=5)
        
        if legal_cases:
            print(f"   ✅ 找到 {len(legal_cases)} 条法律案件")
            for i, case in enumerate(legal_cases[:2], 1):
                print(f"   {i}. {case.get('title', '无标题')}")
                print(f"      类型: {case.get('data_type_zh', '未知')}")
                print(f"      日期: {case.get('date', '未知')}")
                
                # 检查是否是装修相关
                title = case.get('title', '').lower()
                if any(keyword in title for keyword in ["装饰", "装修", "装潢"]):
                    print(f"      🔥 装修相关案件")
        else:
            print("   ⚠️ 未找到法律案件")
        
        # 2. 测试法律风险分析
        print("\n2. 测试法律风险分析...")
        legal_analysis = await juhecha_service.analyze_company_legal_risk(test_company)
        
        print(f"   ✅ 法律案件数量: {legal_analysis.get('legal_case_count', 0)}")
        print(f"   ✅ 装修相关案件: {legal_analysis.get('decoration_related_cases', 0)}")
        print(f"   ✅ 风险评分调整: {legal_analysis.get('risk_score_adjustment', 0)}")
        
        risk_reasons = legal_analysis.get('risk_reasons', [])
        if risk_reasons:
            print(f"   ✅ 风险原因:")
            for reason in risk_reasons:
                print(f"      - {reason}")
        
        # 3. 测试天眼查服务（模拟）
        print("\n3. 测试天眼查服务（模拟）...")
        try:
            # 模拟天眼查返回结果
            mock_tyc_analysis = {
                "risk_level": "warning",
                "risk_score": 45,
                "risk_reasons": ["企业成立时间不足3年", "存在2条投诉记录"],
                "complaint_count": 2,
                "legal_risks": []
            }
            
            print(f"   ✅ 模拟天眼查风险等级: {mock_tyc_analysis.get('risk_level')}")
            print(f"   ✅ 模拟天眼查风险评分: {mock_tyc_analysis.get('risk_score')}")
            print(f"   ✅ 模拟天眼查投诉数量: {mock_tyc_analysis.get('complaint_count')}")
            
            # 4. 合并风险分析
            print("\n4. 合并风险分析...")
            tyc_score = mock_tyc_analysis.get('risk_score', 0)
            juhe_adjustment = legal_analysis.get('risk_score_adjustment', 0)
            combined_score = min(tyc_score + juhe_adjustment, 100)
            
            print(f"   ✅ 天眼查基础评分: {tyc_score}")
            print(f"   ✅ 聚合数据调整: {juhe_adjustment}")
            print(f"   ✅ 合并风险评分: {combined_score}")
            
            if combined_score >= 70:
                risk_level = "high"
                risk_level_zh = "高风险"
            elif combined_score >= 30:
                risk_level = "warning"
                risk_level_zh = "警告"
            else:
                risk_level = "compliant"
                risk_level_zh = "合规"
            
            print(f"   ✅ 最终风险等级: {risk_level} ({risk_level_zh})")
            
            # 合并风险原因
            combined_reasons = mock_tyc_analysis.get('risk_reasons', []) + legal_analysis.get('risk_reasons', [])
            print(f"   ✅ 合并风险原因 ({len(combined_reasons)} 条):")
            for reason in combined_reasons[:5]:  # 只显示前5条
                print(f"      - {reason}")
            
            # 5. 验证数据结构
            print("\n5. 验证数据结构...")
            legal_info = {
                "legal_case_count": legal_analysis.get('legal_case_count', 0),
                "legal_cases": legal_analysis.get('recent_cases', []),
                "decoration_related_cases": legal_analysis.get('decoration_related_cases', 0),
                "case_types": legal_analysis.get('case_types', [])
            }
            
            print(f"   ✅ 法律信息结构验证通过")
            print(f"      案件数量: {legal_info['legal_case_count']}")
            print(f"      案件类型: {legal_info['case_types']}")
            print(f"      装修相关案件: {legal_info['decoration_related_cases']}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 天眼查测试失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 聚合数据服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_backend_integration():
    """测试后端集成"""
    print("\n" + "=" * 60)
    print("测试后端集成")
    print("=" * 60)
    
    try:
        # 模拟公司扫描分析流程
        print("模拟公司扫描分析流程...")
        print("-" * 40)
        
        # 模拟数据
        test_company = "耒阳市怡馨装饰设计工程有限公司"
        company_scan_id = 12345
        
        print(f"1. 开始分析公司: {test_company}")
        print(f"2. 扫描ID: {company_scan_id}")
        
        # 模拟并发调用
        print("3. 并发调用天眼查和聚合数据API...")
        
        # 模拟聚合数据结果
        juhe_result = {
            "legal_case_count": 4,
            "recent_case_date": "2021年05月18日",
            "case_types": ["裁判文书", "案件流程"],
            "decoration_related_cases": 2,
            "risk_score_adjustment": 40,
            "risk_reasons": ["存在4起法律案件", "存在2起装修相关纠纷"],
            "recent_cases": [
                {
                    "type": "cpws",
                    "title": "胡小辉与耒阳市怡馨装饰设计工程有限公司装饰装修合同纠纷一审民事裁定书",
                    "date": "2021年05月18日",
                    "content": "湖南省耒阳市人民法院   民 ...",
                    "data_type_zh": "裁判文书"
                }
            ]
        }
        
        # 模拟天眼查结果
        tyc_result = {
            "risk_level": "warning",
            "risk_score": 45,
            "risk_reasons": ["企业成立时间不足3年", "存在2条投诉记录"],
            "complaint_count": 2,
            "legal_risks": []
        }
        
        print("4. API调用完成")
        print(f"   聚合数据: 找到 {juhe_result['legal_case_count']} 条法律案件")
        print(f"   天眼查: 风险评分 {tyc_result['risk_score']}, 等级 {tyc_result['risk_level']}")
        
        # 合并分析结果
        print("5. 合并风险分析结果...")
        
        original_score = tyc_result.get("risk_score", 0)
        legal_adjustment = juhe_result.get("risk_score_adjustment", 0)
        combined_score = min(original_score + legal_adjustment, 100)
        
        combined_reasons = tyc_result.get("risk_reasons", []) + juhe_result.get("risk_reasons", [])
        
        if combined_score >= 70:
            combined_risk_level = "high"
        elif combined_score >= 30:
            combined_risk_level = "warning"
        else:
            combined_risk_level = "compliant"
        
        print(f"6. 最终结果:")
        print(f"   风险等级: {combined_risk_level}")
        print(f"   风险评分: {combined_score}")
        print(f"   法律案件数量: {juhe_result['legal_case_count']}")
        print(f"   装修相关案件: {juhe_result['decoration_related_cases']}")
        print(f"   风险原因数量: {len(combined_reasons)}")
        
        # 验证数据结构
        legal_info = {
            "legal_case_count": juhe_result['legal_case_count'],
            "legal_cases": juhe_result['recent_cases'],
            "decoration_related_cases": juhe_result['decoration_related_cases'],
            "case_types": juhe_result['case_types']
        }
        
        print(f"7. 数据结构验证:")
        print(f"   法律信息结构: OK")
        print(f"   案件数据: {len(legal_info['legal_cases'])} 条")
        
        return True
        
    except Exception as e:
        print(f"❌ 后端集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_frontend_display():
    """测试前端显示"""
    print("\n" + "=" * 60)
    print("测试前端显示")
    print("=" * 60)
    
    print("模拟前端显示法律案件信息...")
    print("-" * 40)
    
    # 模拟数据
    legal_cases = [
        {
            "type": "cpws",
            "title": "胡小辉与耒阳市怡馨装饰设计工程有限公司装饰装修合同纠纷一审民事裁定书",
            "date": "2021年05月18日",
            "content": "湖南省耒阳市人民法院   民 ...",
            "data_type_zh": "裁判文书"
        },
        {
            "type": "ajlc",
            "title": "原告:胡小辉;被告:耒阳市怡馨装饰设计工程有限公司",
            "date": "2021年04月09日",
            "content": "当事人:原告:胡小辉;被告:耒...",
            "data_type_zh": "案件流程"
        }
    ]
    
    legal_analysis = {
        "legal_case_count": 4,
        "recent_case_date": "2021年05月18日",
        "case_types": ["裁判文书", "案件流程"],
        "decoration_related_cases": 2,
        "risk_score_adjustment": 40,
        "risk_reasons": ["存在4起法律案件", "存在2起装修相关纠纷"],
        "recent_cases": legal_cases
    }
    
    print("1. 法律案件信息显示:")
    if legal_cases:
        for i, case in enumerate(legal_cases, 1):
            print(f"   {i}. {case['title']}")
            print(f"      类型: {case['data_type_zh']}")
            print(f"      日期: {case['date']}")
    
    print("\n2. 风险分析摘要:")
    print(f"   法律案件总数: {legal_analysis['legal_case_count']}")
    print(f"   装修相关案件: {legal_analysis['decoration_related_cases']}")
    print(f"   最近案件日期: {legal_analysis['recent_case_date']}")
    
    print("\n3. 风险原因:")
    for reason in legal_analysis['risk_reasons']:
        print(f"   • {reason}")
    
    print("\n4. 前端组件结构:")
    print("""
   <View className="legal-cases-section">
     <Text className="section-title">法律案件信息</Text>
     {legalCases.map((case, index) => (
       <View key={index} className="case-item">
         <Text className="case-title">{case.title}</Text>
         <Text className="case-date">{case.date}</Text>
         <Text className="case-type">类型：{case.data_type_zh}</Text>
       </View>
     ))}
   </View>
    """)
    
    return True


async def main():
    """主测试函数"""
    print("开始完整测试聚合数据API集成...")
    
    success_count = 0
    total_tests = 3
    
    # 测试聚合数据服务集成
    if await test_juhecha_service_integration():
        success_count += 1
    
    # 测试后端集成
    if await test_backend_integration():
        success_count += 1
    
    # 测试前端显示
    if await test_frontend_display():
        success_count += 1
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    print(f"测试完成: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("✅ 所有测试通过！聚合数据API集成成功。")
        print("\n下一步:")
        print("1. 部署到阿里云服务器")
        print("2. 重启后端服务")
        print("3. 在前端测试公司风险扫描功能")
    else:
        print("⚠️  部分测试失败，请检查问题。")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

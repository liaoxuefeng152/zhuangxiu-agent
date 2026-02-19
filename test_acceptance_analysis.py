#!/usr/bin/env python3
"""
测试AI验收功能
直接调用风险分析服务测试验收分析
"""
import os
import sys
import json
import asyncio

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))

def test_acceptance_analysis():
    """测试验收分析功能"""
    print("=== 测试AI验收功能 ===")
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    
    try:
        from app.services.risk_analyzer import risk_analyzer_service
        
        # 创建模拟的验收OCR文本
        ocr_texts = [
            "水电改造完成，线路整齐，符合规范",
            "水管压力测试合格，无渗漏",
            "开关插座位置正确，安装牢固"
        ]
        
        # 测试水电阶段验收
        stage = "plumbing"
        
        print(f"\n测试施工阶段: {stage}")
        print(f"OCR文本: {ocr_texts}")
        
        # 直接调用风险分析服务
        print("\n直接调用验收分析服务...")
        
        async def analyze():
            return await risk_analyzer_service.analyze_acceptance(stage, ocr_texts)
        
        result = asyncio.run(analyze())
        
        print("\n验收分析结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 检查是否返回了兜底结果
        summary = result.get("summary", "")
        if "分析服务暂时不可用" in summary:
            print("\n⚠️  验收分析返回了兜底结果，服务可能不可用")
            return False
            
        print(f"\n✅ 验收分析成功，严重程度: {result.get('severity', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"直接调用验收分析服务异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_acceptance_consult():
    """测试AI监理咨询功能"""
    print("\n=== 测试AI监理咨询功能 ===")
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    
    try:
        from app.services.risk_analyzer import risk_analyzer_service
        
        # 创建模拟的用户问题
        user_question = "水电改造完成后，如何验收水管是否合格？"
        stage = "plumbing"
        
        print(f"\n用户问题: {user_question}")
        print(f"施工阶段: {stage}")
        
        # 直接调用风险分析服务
        print("\n直接调用AI监理咨询...")
        
        async def consult():
            return await risk_analyzer_service.consult_acceptance(
                user_question=user_question,
                stage=stage,
                context_summary="水电改造已完成，需要进行验收",
                context_issues=[
                    {"category": "水管压力", "description": "需要测试水管压力是否达标"},
                    {"category": "线路安全", "description": "检查线路是否安全规范"}
                ]
            )
        
        result = asyncio.run(consult())
        
        print("\nAI监理咨询结果:")
        print(result)
        
        if not result or "AI分析服务暂时不可用" in result:
            print("\n⚠️  AI监理咨询返回了兜底结果，服务可能不可用")
            return False
            
        print(f"\n✅ AI监理咨询成功，回答长度: {len(result)} 字符")
        return True
        
    except Exception as e:
        print(f"直接调用AI监理咨询异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("AI验收与监理咨询功能测试")
    print("=" * 50)
    
    # 测试验收分析
    success1 = test_acceptance_analysis()
    
    # 测试AI监理咨询
    success2 = test_acceptance_consult()
    
    if success1 and success2:
        print("\n✅ AI验收与监理咨询功能测试通过")
    else:
        print("\n❌ AI验收与监理咨询功能测试失败")
    
    return success1 and success2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
测试AI设计师API功能
"""
import os
import sys
import asyncio
import json

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))

def test_designer_api():
    """测试AI设计师API功能"""
    print("=== 测试AI设计师API功能 ===")
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    
    try:
        from app.services.risk_analyzer import risk_analyzer_service
        
        # 测试AI设计师咨询
        print("\n1. 测试AI设计师咨询功能...")
        
        async def test_designer():
            return await risk_analyzer_service.consult_designer(
                user_question="现代简约风格的特点是什么？",
                context="我准备装修一套80平米的房子"
            )
        
        designer_result = asyncio.run(test_designer())
        print(f"AI设计师回答长度: {len(designer_result)} 字符")
        print(f"AI设计师回答预览: {designer_result[:200]}...")
        
        if not designer_result or "AI分析服务暂时不可用" in designer_result:
            print("❌ AI设计师咨询返回了兜底结果")
            return False
        else:
            print("✅ AI设计师咨询成功")
        
        # 测试更多问题
        print("\n2. 测试更多装修设计问题...")
        
        test_questions = [
            "小户型如何设计显得空间更大？",
            "装修预算怎么分配比较合理？",
            "选择地板还是瓷砖比较好？",
            "客厅灯光设计有什么建议？"
        ]
        
        for i, question in enumerate(test_questions):
            async def test_question(q):
                return await risk_analyzer_service.consult_designer(q)
            
            result = asyncio.run(test_question(question))
            print(f"问题{i+1}: {question[:30]}...")
            print(f"  回答长度: {len(result)} 字符")
            print(f"  回答预览: {result[:100]}...")
            
            if not result or "AI分析服务暂时不可用" in result:
                print(f"  ❌ 问题{i+1}返回了兜底结果")
                return False
            else:
                print(f"  ✅ 问题{i+1}成功")
        
        return True
        
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("AI设计师API功能测试")
    print("=" * 50)
    
    # 测试AI设计师功能
    success = test_designer_api()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ AI设计师API功能测试通过")
        print("\n测试结果总结:")
        print("1. AI设计师咨询功能: ✅ 正常（返回真实AI分析结果）")
        print("2. 多种装修设计问题: ✅ 正常（返回专业设计建议）")
        print("\n结论: AI设计师智能体已成功对接，可以正常返回专业设计建议")
    else:
        print("\n❌ AI设计师API功能测试失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

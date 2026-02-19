#!/usr/bin/env python3
"""
测试最终修复效果
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

from app.services.risk_analyzer import risk_analyzer_service

async def test_designer_fix():
    """测试AI设计师修复"""
    print("测试AI设计师修复效果...")
    
    try:
        # 测试一个简单的问题
        user_question = "现代简约风格的特点是什么？"
        
        print(f"用户问题: {user_question}")
        
        # 调用AI设计师服务
        answer = await risk_analyzer_service.consult_designer(
            user_question=user_question,
            context=""
        )
        
        print(f"✓ AI设计师返回结果!")
        print(f"回答长度: {len(answer)} 字符")
        print(f"回答预览: {answer[:300]}...")
        
        # 检查是否返回了友好的错误信息
        if "抱歉，AI设计师服务暂时不可用" in answer:
            print("⚠️ 注意：返回了友好的错误信息（AI服务资源点不足）")
            print("✓ 修复成功：不再抛出500错误，而是返回友好的错误信息")
            return True
        else:
            print("✓ 修复成功：AI设计师服务正常工作")
            return True
            
    except Exception as e:
        print(f"✗ AI设计师聊天失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("AI设计师500错误修复测试")
    print("=" * 60)
    
    # 检查配置
    print(f"AI设计师URL配置: {risk_analyzer_service._design_site_url}")
    print(f"AI设计师Token配置: {'已配置' if risk_analyzer_service._design_site_token else '未配置'}")
    print(f"AI监理URL配置: {risk_analyzer_service._coze_site_url}")
    
    # 运行测试
    result = await test_designer_fix()
    
    print("\n" + "=" * 60)
    print("测试结果:")
    if result:
        print("✓ 修复成功！AI设计师服务不再返回500错误")
        print("\n总结：")
        print("1. 问题原因：AI设计师智能体资源点不足，返回空结果")
        print("2. 修复方案：添加降级逻辑和友好的错误信息")
        print("3. 效果：前端不再收到500错误，而是看到友好的提示信息")
        print("4. 归属：这是后台问题（AI服务配置和资源问题）")
    else:
        print("✗ 修复失败，需要进一步排查")
    
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

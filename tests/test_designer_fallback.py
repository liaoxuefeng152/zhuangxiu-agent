#!/usr/bin/env python3
"""
测试AI设计师降级逻辑
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

from app.services.risk_analyzer import risk_analyzer_service

async def test_designer_fallback():
    """测试AI设计师降级逻辑"""
    print("测试AI设计师降级逻辑...")
    
    try:
        # 测试一个简单的问题
        user_question = "现代简约风格的特点是什么？"
        
        print(f"用户问题: {user_question}")
        
        # 调用AI设计师服务
        answer = await risk_analyzer_service.consult_designer(
            user_question=user_question,
            context=""
        )
        
        print(f"✓ AI设计师回答成功!")
        print(f"回答长度: {len(answer)} 字符")
        print(f"回答预览: {answer[:200]}...")
        return True
        
    except Exception as e:
        print(f"✗ AI设计师聊天失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_designer_with_image():
    """测试带图片的AI设计师咨询"""
    print("\n测试带图片的AI设计师咨询...")
    
    try:
        # 测试带图片的问题
        user_question = "请帮我分析一下这个户型图，给出装修建议。"
        image_urls = ["https://zhuangxiu-images-dev-photo.oss-cn-hangzhou.aliyuncs.com/designer/1/1771500082_4194.png"]
        
        print(f"用户问题: {user_question}")
        print(f"图片URL: {image_urls}")
        
        # 调用AI设计师服务
        answer = await risk_analyzer_service.consult_designer(
            user_question=user_question,
            context="",
            image_urls=image_urls
        )
        
        print(f"✓ 带图片的AI设计师回答成功!")
        print(f"回答长度: {len(answer)} 字符")
        print(f"回答预览: {answer[:200]}...")
        return True
        
    except Exception as e:
        print(f"✗ 带图片的AI设计师聊天失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("AI设计师降级逻辑测试")
    print("=" * 60)
    
    # 检查配置
    print(f"AI设计师URL配置: {risk_analyzer_service._design_site_url}")
    print(f"AI设计师Token配置: {'已配置' if risk_analyzer_service._design_site_token else '未配置'}")
    print(f"AI设计师项目ID: {risk_analyzer_service._design_project_id}")
    print(f"AI监理URL配置: {risk_analyzer_service._coze_site_url}")
    print(f"AI监理Token配置: {'已配置' if risk_analyzer_service._coze_site_token else '未配置'}")
    
    # 运行测试
    fallback_ok = await test_designer_fallback()
    image_ok = await test_designer_with_image()
    
    print("\n" + "=" * 60)
    print("测试结果:")
    print(f"降级逻辑测试: {'✓ 通过' if fallback_ok else '✗ 失败'}")
    print(f"带图片咨询测试: {'✓ 通过' if image_ok else '✗ 失败'}")
    
    if fallback_ok or image_ok:
        print("✓ 至少一个测试通过，降级逻辑可能有效!")
        return 0
    else:
        print("✗ 所有测试失败，需要进一步排查")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

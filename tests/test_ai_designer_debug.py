#!/usr/bin/env python3
"""
测试AI设计师智能体，查看返回的具体内容
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.risk_analyzer import risk_analyzer_service

async def test_ai_designer():
    """测试AI设计师智能体"""
    print("=== 测试AI设计师智能体 ===")
    
    # 测试问题
    user_question = "请帮我设计一个现代简约风格的客厅，面积约30平米，预算5万元左右。"
    context = ""
    image_urls = []
    
    try:
        print(f"发送问题: {user_question}")
        print("正在调用AI设计师智能体...")
        
        response = await risk_analyzer_service.consult_designer(
            user_question=user_question,
            context=context,
            image_urls=image_urls
        )
        
        print("\n=== AI设计师返回内容 ===")
        print(response)
        print(f"\n返回内容长度: {len(response)} 字符")
        
        # 检查返回内容的质量
        if len(response) < 100:
            print("\n⚠️ 警告: 返回内容可能过短，可能AI设计师智能体资源点不足")
        elif "抱歉" in response or "暂时不可用" in response:
            print("\n⚠️ 警告: AI设计师智能体可能返回了错误信息")
        else:
            print("\n✅ AI设计师智能体返回了详细内容")
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_ai_designer_with_image():
    """测试带图片的AI设计师智能体"""
    print("\n=== 测试带图片的AI设计师智能体 ===")
    
    # 测试问题
    user_question = "请分析这张户型图，给出装修建议。"
    context = ""
    
    # 使用之前上传的图片URL
    image_urls = ["https://zhuangxiu-images-dev-photo.oss-cn-hangzhou.aliyuncs.com/designer/1/1771502110_3416.png"]
    
    try:
        print(f"发送问题: {user_question}")
        print(f"使用图片: {image_urls[0]}")
        print("正在调用AI设计师智能体...")
        
        response = await risk_analyzer_service.consult_designer(
            user_question=user_question,
            context=context,
            image_urls=image_urls
        )
        
        print("\n=== AI设计师返回内容 ===")
        print(response[:500] + "..." if len(response) > 500 else response)
        print(f"\n返回内容长度: {len(response)} 字符")
        
        # 检查返回内容的质量
        if len(response) < 100:
            print("\n⚠️ 警告: 返回内容可能过短，可能AI设计师智能体资源点不足")
        elif "抱歉" in response or "暂时不可用" in response:
            print("\n⚠️ 警告: AI设计师智能体可能返回了错误信息")
        else:
            print("\n✅ AI设计师智能体返回了详细内容")
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主函数"""
    print("AI设计师智能体调试测试")
    print("=" * 50)
    
    # 测试1: 纯文本问题
    await test_ai_designer()
    
    print("\n" + "=" * 50 + "\n")
    
    # 测试2: 带图片的问题
    await test_ai_designer_with_image()
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    # 设置环境变量
    os.environ["ENV"] = "development"
    
    # 运行测试
    asyncio.run(main())

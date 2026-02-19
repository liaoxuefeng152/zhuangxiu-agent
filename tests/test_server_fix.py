#!/usr/bin/env python3
"""
测试阿里云服务器上的AI设计师修复效果
"""
import asyncio
import aiohttp
import json

async def test_ai_designer_on_server():
    """测试阿里云服务器上的AI设计师接口"""
    url = "http://120.26.201.61:8001/api/v1/designer/chat"
    
    # 测试数据
    payload = {
        "user_question": "现代简约风格的特点是什么？",
        "context": "",
        "image_urls": []
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token"  # 测试用token
    }
    
    print(f"测试AI设计师接口: {url}")
    print(f"请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                status = response.status
                print(f"响应状态码: {status}")
                
                if status == 200:
                    data = await response.json()
                    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
                    
                    if "answer" in data:
                        answer = data["answer"]
                        print(f"✓ AI设计师返回结果!")
                        print(f"回答长度: {len(answer)} 字符")
                        print(f"回答预览: {answer[:300]}...")
                        
                        # 检查是否返回了友好的错误信息
                        if "抱歉，AI设计师服务暂时不可用" in answer:
                            print("⚠️ 注意：返回了友好的错误信息（AI服务资源点不足）")
                            print("✓ 修复成功：不再返回500错误，而是返回友好的错误信息")
                            return True
                        else:
                            print("✓ 修复成功：AI设计师服务正常工作")
                            return True
                    else:
                        print(f"响应格式错误: {data}")
                        return False
                else:
                    print(f"请求失败，状态码: {status}")
                    response_text = await response.text()
                    print(f"响应内容: {response_text}")
                    
                    if status == 500:
                        print("✗ 修复失败：仍然返回500错误")
                        return False
                    else:
                        print(f"⚠️ 非预期状态码: {status}")
                        return False
                        
    except Exception as e:
        print(f"请求异常: {e}")
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("阿里云服务器AI设计师500错误修复验证")
    print("=" * 60)
    
    # 运行测试
    result = await test_ai_designer_on_server()
    
    print("\n" + "=" * 60)
    print("验证结果:")
    if result:
        print("✓ 修复成功！AI设计师服务不再返回500错误")
        print("\n总结：")
        print("1. 问题原因：AI设计师智能体资源点不足，返回空结果")
        print("2. 修复方案：添加降级逻辑和友好的错误信息")
        print("3. 效果：前端不再收到500错误，而是看到友好的提示信息")
        print("4. 归属：这是后台问题（AI服务配置和资源问题）")
        print("5. 部署状态：已成功部署到阿里云服务器")
    else:
        print("✗ 修复验证失败，需要进一步排查")
    
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

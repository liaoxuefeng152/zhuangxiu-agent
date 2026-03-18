import asyncio
import aiohttp
import json

async def test_quote_analysis():
    """测试报价单分析功能"""
    url = "http://120.26.201.61:8001/api/v1/quotes/analyze"
    
    # 使用一个测试图片URL（可以是任何有效的图片URL）
    test_data = {
        "image_url": "https://via.placeholder.com/300x400.png?text=Test+Quote",
        "user_id": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=test_data, headers=headers) as response:
                print(f"状态码: {response.status}")
                print(f"响应头: {dict(response.headers)}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                else:
                    text = await response.text()
                    print(f"错误响应: {text}")
                    
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    asyncio.run(test_quote_analysis())

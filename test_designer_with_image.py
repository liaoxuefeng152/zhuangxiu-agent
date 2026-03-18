#!/usr/bin/env python3
"""
测试AI设计师智能体处理图片URL
"""
import httpx
import json

def test_designer_with_image():
    """测试AI设计师智能体处理图片URL"""
    print("=== 测试AI设计师智能体处理图片URL ===")
    
    # AI设计师智能体配置
    site_url = "https://66g9ffxgrz.coze.site/stream_run"
    site_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImQwODAzZmJiLTQ0NTItNGFmOS1hOWU5LTM1NTA5YjgyMDNmMSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIklURW5kbExSdmFGaHloWVl1ZTNVUVZEazhpWEl3OVBEIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzcxMzg2NDA5LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjA3Nzg0NTMxMjE4NjYxNDExIiwic3JjIjoiaW5ib3VuZF9hdXhoX2FjY2Vzc190b2tlbl9pZDo3NjA4MDQ2Njk3OTQ3NTk0Nzc5In0.Fa84UBed4StmvscbUSpe7NQ1IXNbTmQfj7f7xMtxCcV3fIOa4Ht4SYbB8yyCFbwLIi0XNKNnM-D-yEIlQbJ4OBGxiABaS2stARLoT6xyBhFKUZXoFwBaR7TcfGBMgb1RysArXmroYe_mOXb99Xs3Aj73CvS8NgoQiRU4rmxYO3zVsJ7fox29x13o6nGG4M8__Eu1yS0D_3nvXj7y7OC60zalVy-8oA0TMSZqPQ831ZY8DIqRFW07bjbehGtMca1gmn-rW9OxNf7ZRMnuvdKFXg3JD_280DtRLKn4WLLOCEWo-GkW-v8PhbAu9RXkPPRg8-ql58nKY4S3DdRP3swu2w"
    project_id = "7607751084224069672"
    
    # 测试不同的请求类型
    test_cases = [
        ("简单文本请求", "请给我一些现代简约风格的装修建议"),
        ("带图片URL的请求", "请分析这张户型图，给出装修建议"),
        ("报价单分析格式请求", "请分析这份装修报价单图片，返回JSON格式的结构化数据")
    ]
    
    # 使用简单的公开图片URL
    image_url = "https://img.alicdn.com/imgextra/i4/O1CN01Z5p5LZ1M1J5Q6X8q5_!!6000000001378-2-tps-800-600.png"
    
    headers = {
        "Authorization": f"Bearer {site_token}",
        "Content-Type": "application/json"
    }
    
    for test_name, prompt in test_cases:
        print(f"\n--- 测试: {test_name} ---")
        
        # 构建请求数据
        api_url = site_url
        
        if "图片" in prompt or "户型图" in prompt or "报价单" in prompt:
            combined_prompt = f"{prompt}\n\n图片URL: {image_url}"
        else:
            combined_prompt = prompt
        
        data = {
            "content": {
                "query": {
                    "prompt": [
                        {
                            "type": "text",
                            "content": {
                                "text": combined_prompt
                            }
                        }
                    ]
                }
            },
            "type": "query",
            "session_id": "test_session_123",
            "project_id": project_id
        }
        
        try:
            response = httpx.post(
                api_url,
                json=data,
                headers=headers,
                timeout=30.0
            )
            
            print(f"  响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ 成功!")
                print(f"  响应前100字符: {response.text[:100]}...")
                
                # 检查响应内容
                if "event: message" in response.text:
                    print("  ✅ 响应包含流式事件")
                elif "data:" in response.text:
                    print("  ✅ 响应包含流式数据")
                else:
                    print("  ⚠️ 响应格式不明确")
            else:
                print(f"  ❌ 失败!")
                print(f"  错误信息: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")

if __name__ == "__main__":
    test_designer_with_image()

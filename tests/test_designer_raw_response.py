#!/usr/bin/env python3
"""
测试AI设计师原始响应格式
"""
import asyncio
import sys
import os
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

from app.core.config import settings

async def test_raw_response():
    """测试原始响应格式"""
    print("测试AI设计师原始响应格式...")
    
    # 直接从配置获取参数
    design_site_url = (getattr(settings, "DESIGN_SITE_URL", None) or "").rstrip("/")
    design_site_token = getattr(settings, "DESIGN_SITE_TOKEN", None) or ""
    design_project_id = str(getattr(settings, "DESIGN_PROJECT_ID", None) or "").strip()
    
    print(f"AI设计师URL: {design_site_url}")
    print(f"AI设计师Token: {'已配置' if design_site_token else '未配置'}")
    print(f"AI设计师项目ID: {design_project_id}")
    
    # 确保URL以/stream_run结尾
    base_url = design_site_url.rstrip("/")
    if not base_url.endswith("/stream_run"):
        url = f"{base_url}/stream_run"
    else:
        url = base_url
    
    print(f"最终请求URL: {url}")
    
    # 构建请求
    import httpx
    import time
    
    system_prompt = "你是一位专业的AI装修设计师。请回答用户的问题。"
    user_content = "现代简约风格的特点是什么？"
    combined = f"【系统要求】\n{system_prompt}\n\n【用户输入】\n{user_content}"
    
    session_id = f"test-{int(time.time() * 1000)}"
    payload = {
        "content": {
            "query": {
                "prompt": [
                    {"type": "text", "content": {"text": combined}}
                ]
            }
        },
        "type": "query",
        "session_id": session_id,
    }
    if design_project_id:
        payload["project_id"] = int(design_project_id) if design_project_id.isdigit() else design_project_id
    
    headers = {
        "Authorization": f"Bearer {design_site_token}",
        "Content-Type": "application/json",
    }
    
    print(f"\n发送请求到: {url}")
    print(f"请求头: Authorization: Bearer ...")
    print(f"请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as resp:
                print(f"\n响应状态码: {resp.status_code}")
                print(f"响应头: {dict(resp.headers)}")
                
                raw_lines = []
                async for line in resp.aiter_lines():
                    line = (line or "").strip()
                    raw_lines.append(line)
                    if line and not line.startswith("event:"):
                        print(f"原始行: {line[:200]}...")
                    
                    # 尝试解析JSON
                    if line.startswith("data:"):
                        json_str = line[5:].strip()
                        try:
                            data = json.loads(json_str)
                            print(f"解析的JSON: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")
                            
                            # 特别检查content字段
                            if "content" in data:
                                content = data["content"]
                                print(f"content字段类型: {type(content)}")
                                if isinstance(content, dict):
                                    print(f"content字段内容: {json.dumps(content, ensure_ascii=False, indent=2)[:300]}...")
                                    if "answer" in content:
                                        answer = content["answer"]
                                        print(f"answer字段类型: {type(answer)}")
                                        if isinstance(answer, str):
                                            print(f"answer字段值: {answer[:200]}...")
                                        else:
                                            print(f"answer字段值: {answer}")
                        except json.JSONDecodeError as e:
                            print(f"JSON解析错误: {e}")
                            print(f"原始JSON字符串: {json_str[:200]}...")
                
                print(f"\n总共收到 {len(raw_lines)} 行数据")
                print(f"前5行示例:")
                for i, line in enumerate(raw_lines[:5]):
                    print(f"  {i+1}: {line[:100]}...")
                
    except Exception as e:
        print(f"请求失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    print("=" * 60)
    print("AI设计师原始响应格式测试")
    print("=" * 60)
    
    await test_raw_response()

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
调试扣子API响应
"""
import sys
sys.path.insert(0, 'backend')
import asyncio
import json
import httpx
import time
from app.core.config import settings

async def debug_coze_response():
    """调试扣子API响应"""
    print('=== 调试扣子API响应 ===')
    
    site_url = settings.COZE_SITE_URL
    site_token = settings.COZE_SITE_TOKEN
    project_id = settings.COZE_PROJECT_ID
    
    print(f'Site URL: {site_url}')
    print(f'Project ID: {project_id}')
    print(f'Token: {site_token[:20]}...')
    
    # 测试图片URL
    test_image_url = 'https://zhuangxiu-images-photo.oss-cn-shenzhen.aliyuncs.com/quote/test.jpg'
    
    # 构建提示词 - 使用更简单的提示词
    prompt = """请分析这份装修报价单图片，返回JSON格式的分析结果。"""
    
    combined_prompt = f'{prompt}\n\n图片URL: {test_image_url}'
    
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
        "session_id": f"session_debug_{int(time.time())}",
        "project_id": project_id,
        "config": {"recursion_limit": 25},
    }
    
    headers = {
        "Authorization": f"Bearer {site_token}",
        "Content-Type": "application/json"
    }
    
    api_url = f"{site_url.rstrip('/')}/stream_run"
    print(f'\n调用API: {api_url}')
    
    try:
        timeout = httpx.Timeout(60.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", api_url, json=data, headers=headers) as response:
                print(f'响应状态: {response.status_code}')
                print(f'响应头: {dict(response.headers)}')
                
                all_chunks = []
                answer_chunks = []
                tool_request_chunks = []
                tool_response_chunks = []
                
                async for line in response.aiter_lines():
                    line = (line or "").strip()
                    if not line or line == "data: [DONE]":
                        continue
                    
                    all_chunks.append(line[:200])
                    
                    if not line.startswith("data:"):
                        continue
                    
                    json_str = line[5:].strip()
                    try:
                        data_chunk = json.loads(json_str)
                        chunk_type = data_chunk.get("type", "unknown")
                        
                        if chunk_type == "answer":
                            answer_chunks.append(data_chunk)
                            print(f'[ANSWER] 收到answer数据块: {json.dumps(data_chunk, ensure_ascii=False)[:200]}...')
                        elif chunk_type == "tool_request":
                            tool_request_chunks.append(data_chunk)
                            print(f'[TOOL_REQUEST] 收到工具请求: {json.dumps(data_chunk, ensure_ascii=False)[:200]}...')
                        elif chunk_type == "tool_response":
                            tool_response_chunks.append(data_chunk)
                            print(f'[TOOL_RESPONSE] 收到工具响应: {json.dumps(data_chunk, ensure_ascii=False)[:200]}...')
                        elif chunk_type == "message_start":
                            print(f'[MESSAGE_START] 消息开始')
                        elif chunk_type == "message_end":
                            print(f'[MESSAGE_END] 消息结束')
                        else:
                            print(f'[{chunk_type.upper()}] 收到数据块')
                            
                    except json.JSONDecodeError as e:
                        print(f'[ERROR] JSON解析失败: {e}')
                        print(f'原始行: {line[:100]}...')
                
                print(f'\n=== 统计信息 ===')
                print(f'总数据块数: {len(all_chunks)}')
                print(f'answer数据块数: {len(answer_chunks)}')
                print(f'tool_request数据块数: {len(tool_request_chunks)}')
                print(f'tool_response数据块数: {len(tool_response_chunks)}')
                
                # 分析answer数据块
                if answer_chunks:
                    print(f'\n=== 分析answer数据块 ===')
                    for i, chunk in enumerate(answer_chunks):
                        print(f'\nAnswer #{i+1}:')
                        content = chunk.get("content", {})
                        if isinstance(content, dict):
                            print(f'  类型: dict')
                            print(f'  键: {list(content.keys())}')
                            if "text" in content:
                                text = content["text"]
                                print(f'  文本长度: {len(text)}')
                                print(f'  文本前100字符: {text[:100]}...')
                        elif isinstance(content, str):
                            print(f'  类型: str')
                            print(f'  长度: {len(content)}')
                            print(f'  内容前100字符: {content[:100]}...')
                        else:
                            print(f'  类型: {type(content)}')
                            print(f'  内容: {content}')
                
                # 分析tool_request数据块
                if tool_request_chunks:
                    print(f'\n=== 分析tool_request数据块 ===')
                    for i, chunk in enumerate(tool_request_chunks):
                        print(f'\nTool Request #{i+1}:')
                        tool_call = chunk.get("tool_call", {})
                        if tool_call:
                            print(f'  工具调用: {json.dumps(tool_call, ensure_ascii=False)[:200]}...')
                
                # 分析tool_response数据块
                if tool_response_chunks:
                    print(f'\n=== 分析tool_response数据块 ===')
                    for i, chunk in enumerate(tool_response_chunks):
                        print(f'\nTool Response #{i+1}:')
                        tool_response = chunk.get("tool_response", {})
                        if tool_response:
                            print(f'  工具响应: {json.dumps(tool_response, ensure_ascii=False)[:200]}...')
                
                # 尝试提取所有文本内容
                print(f'\n=== 提取所有文本内容 ===')
                all_text = []
                for chunk in answer_chunks:
                    content = chunk.get("content", {})
                    if isinstance(content, dict) and "text" in content:
                        all_text.append(content["text"])
                    elif isinstance(content, str):
                        all_text.append(content)
                
                full_text = "".join(all_text)
                if full_text:
                    print(f'提取到文本内容 ({len(full_text)} 字符):')
                    print(full_text[:500] + "..." if len(full_text) > 500 else full_text)
                    
                    # 尝试解析为JSON
                    try:
                        cleaned = full_text.strip()
                        if cleaned.startswith("```json"):
                            cleaned = cleaned[7:].strip()
                        if cleaned.startswith("```"):
                            cleaned = cleaned[3:].strip()
                        if cleaned.endswith("```"):
                            cleaned = cleaned[:-3].strip()
                        
                        result = json.loads(cleaned)
                        print(f'\n✅ 成功解析为JSON:')
                        print(f'   包含字段: {list(result.keys())}')
                    except json.JSONDecodeError as e:
                        print(f'\n❌ 无法解析为JSON: {e}')
                else:
                    print('没有提取到文本内容')
                
                return len(answer_chunks) > 0
    
    except Exception as e:
        print(f'请求异常: {e}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    success = await debug_coze_response()
    
    print(f'\n\n=== 调试总结 ===')
    if success:
        print('✅ 扣子API响应正常，收到了answer数据块')
    else:
        print('❌ 扣子API响应异常，没有收到answer数据块')
        print('\n可能的问题:')
        print('1. 扣子智能体配置错误')
        print('2. 扣子站点可能已失效')
        print('3. 图片URL无法访问')
        print('4. 扣子智能体工作流配置有问题')

if __name__ == "__main__":
    asyncio.run(main())

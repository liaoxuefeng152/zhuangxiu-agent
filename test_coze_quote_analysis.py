#!/usr/bin/env python3
"""
测试扣子报价单分析功能
"""
import sys
sys.path.insert(0, 'backend')
import asyncio
import json
import httpx
import time
from app.core.config import settings

async def test_coze_quote_analysis():
    """测试扣子报价单分析"""
    print('=== 测试扣子报价单分析功能 ===')
    
    site_url = settings.COZE_SITE_URL
    site_token = settings.COZE_SITE_TOKEN
    project_id = settings.COZE_PROJECT_ID
    
    print(f'Site URL: {site_url}')
    print(f'Project ID: {project_id}')
    print(f'Token: {site_token[:20]}...')
    
    # 测试图片URL
    test_image_url = 'https://zhuangxiu-images-photo.oss-cn-shenzhen.aliyuncs.com/quote/test.jpg'
    
    # 构建提示词 - 简化版本，避免触发工具调用
    prompt = """请分析这份装修报价单图片，直接返回JSON格式的分析结果，不要调用任何工具。

返回格式：
{
  "total_price": 总价,
  "risk_score": 风险评分,
  "high_risk_items": [],
  "warning_items": [],
  "missing_items": [],
  "overpriced_items": [],
  "market_ref_price": 市场参考价,
  "suggestions": [],
  "summary": "分析总结"
}

请直接返回JSON，不要包含其他文本，不要调用工具。"""
    
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
        "session_id": f"session_test_{int(time.time())}",
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
                
                answer_content = []
                async for line in response.aiter_lines():
                    line = (line or "").strip()
                    if not line or line == "data: [DONE]":
                        continue
                    if not line.startswith("data:"):
                        continue
                    json_str = line[5:].strip()
                    try:
                        data_chunk = json.loads(json_str)
                        # 提取answer类型的内容
                        if data_chunk.get("type") == "answer" and "content" in data_chunk:
                            content = data_chunk.get("content", {})
                            if isinstance(content, dict) and "text" in content:
                                answer_content.append(content["text"])
                            elif isinstance(content, str):
                                answer_content.append(content)
                    except json.JSONDecodeError:
                        continue
                
                full_answer = "".join(answer_content)
                print(f'\n提取的answer内容 ({len(full_answer)} 字符):')
                if full_answer:
                    print(full_answer[:500] + "..." if len(full_answer) > 500 else full_answer)
                else:
                    print('没有提取到内容')
                
                # 尝试解析为JSON
                if full_answer:
                    try:
                        # 清理可能的markdown代码块
                        cleaned = full_answer.strip()
                        if cleaned.startswith("```json"):
                            cleaned = cleaned[7:].strip()
                        if cleaned.startswith("```"):
                            cleaned = cleaned[3:].strip()
                        if cleaned.endswith("```"):
                            cleaned = cleaned[:-3].strip()
                        
                        result = json.loads(cleaned)
                        print(f'\n✅ 成功解析为JSON:')
                        print(f'   包含字段: {list(result.keys())}')
                        if "risk_score" in result:
                            print(f'   风险评分: {result["risk_score"]}')
                        if "total_price" in result:
                            print(f'   总价: {result["total_price"]}')
                        return True
                    except json.JSONDecodeError as e:
                        print(f'\n❌ 无法解析为JSON: {e}')
                        print(f'   原始内容前200字符: {full_answer[:200]}')
                        return False
                else:
                    print('\n❌ 没有提取到answer内容')
                    return False
    
    except Exception as e:
        print(f'请求异常: {e}')
        return False

async def test_coze_contract_analysis():
    """测试扣子合同分析"""
    print('\n\n=== 测试扣子合同分析功能 ===')
    
    site_url = settings.COZE_SITE_URL
    site_token = settings.COZE_SITE_TOKEN
    project_id = settings.COZE_PROJECT_ID
    
    # 测试图片URL
    test_image_url = 'https://zhuangxiu-images-photo.oss-cn-shenzhen.aliyuncs.com/contract/test.jpg'
    
    # 构建提示词
    prompt = """请分析这份装修合同图片，直接返回JSON格式的分析结果，不要调用任何工具。

返回格式：
{
  "contract_type": "装修工程合同",
  "risk_score": 风险评分,
  "risk_level": "high/medium/low",
  "high_risk_clauses": [],
  "missing_clauses": [],
  "unfair_clauses": [],
  "suggestions": [],
  "summary": "分析总结"
}

请直接返回JSON，不要包含其他文本，不要调用工具。"""
    
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
        "session_id": f"session_test_{int(time.time())}",
        "project_id": project_id,
        "config": {"recursion_limit": 25},
    }
    
    headers = {
        "Authorization": f"Bearer {site_token}",
        "Content-Type": "application/json"
    }
    
    api_url = f"{site_url.rstrip('/')}/stream_run"
    
    try:
        timeout = httpx.Timeout(60.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", api_url, json=data, headers=headers) as response:
                print(f'响应状态: {response.status_code}')
                
                answer_content = []
                async for line in response.aiter_lines():
                    line = (line or "").strip()
                    if not line or line == "data: [DONE]":
                        continue
                    if not line.startswith("data:"):
                        continue
                    json_str = line[5:].strip()
                    try:
                        data_chunk = json.loads(json_str)
                        if data_chunk.get("type") == "answer" and "content" in data_chunk:
                            content = data_chunk.get("content", {})
                            if isinstance(content, dict) and "text" in content:
                                answer_content.append(content["text"])
                            elif isinstance(content, str):
                                answer_content.append(content)
                    except json.JSONDecodeError:
                        continue
                
                full_answer = "".join(answer_content)
                print(f'\n提取的answer内容 ({len(full_answer)} 字符):')
                if full_answer:
                    print(full_answer[:500] + "..." if len(full_answer) > 500 else full_answer)
                else:
                    print('没有提取到内容')
                
                # 尝试解析为JSON
                if full_answer:
                    try:
                        cleaned = full_answer.strip()
                        if cleaned.startswith("```json"):
                            cleaned = cleaned[7:].strip()
                        if cleaned.startswith("```"):
                            cleaned = cleaned[3:].strip()
                        if cleaned.endswith("```"):
                            cleaned = cleaned[:-3].strip()
                        
                        result = json.loads(cleaned)
                        print(f'\n✅ 成功解析为JSON:')
                        print(f'   包含字段: {list(result.keys())}')
                        if "risk_score" in result:
                            print(f'   风险评分: {result["risk_score"]}')
                        if "contract_type" in result:
                            print(f'   合同类型: {result["contract_type"]}')
                        return True
                    except json.JSONDecodeError as e:
                        print(f'\n❌ 无法解析为JSON: {e}')
                        print(f'   原始内容前200字符: {full_answer[:200]}')
                        return False
                else:
                    print('\n❌ 没有提取到answer内容')
                    return False
    
    except Exception as e:
        print(f'请求异常: {e}')
        return False

async def main():
    """主函数"""
    print('开始测试扣子AI分析功能...')
    
    quote_success = await test_coze_quote_analysis()
    contract_success = await test_coze_contract_analysis()
    
    print('\n\n=== 测试总结 ===')
    print(f'报价单分析: {"✅ 成功" if quote_success else "❌ 失败"}')
    print(f'合同分析: {"✅ 成功" if contract_success else "❌ 失败"}')
    
    if not quote_success:
        print('\n⚠️ 报价单分析失败的可能原因:')
        print('1. 扣子智能体配置可能有问题')
        print('2. 图片URL可能无法访问')
        print('3. 扣子智能体返回了工具调用说明而不是分析结果')
        print('4. 提示词可能需要优化')
    
    if not contract_success:
        print('\n⚠️ 合同分析失败的可能原因:')
        print('1. 扣子智能体配置可能有问题')
        print('2. 图片URL可能无法访问')
        print('3. 扣子智能体返回了工具调用说明而不是分析结果')
        print('4. 提示词可能需要优化')

if __name__ == "__main__":
    asyncio.run(main())

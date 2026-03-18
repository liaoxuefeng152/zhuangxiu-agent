#!/usr/bin/env python3
"""
最终测试扣子API响应
"""
import sys
sys.path.insert(0, 'backend')
import asyncio
import json
import httpx
import time
from app.core.config import settings

async def test_coze_final():
    """最终测试扣子API"""
    print('=== 最终测试扣子API ===')
    
    site_url = settings.COZE_SITE_URL
    site_token = settings.COZE_SITE_TOKEN
    project_id = settings.COZE_PROJECT_ID
    
    print(f'Site URL: {site_url}')
    print(f'Project ID: {project_id}')
    
    # 测试图片URL
    test_image_url = 'https://zhuangxiu-images-photo.oss-cn-shenzhen.aliyuncs.com/quote/test.jpg'
    
    # 构建提示词 - 使用更明确的指令
    prompt = """请分析这份装修报价单图片，返回JSON格式的分析结果。

返回格式必须严格遵循：
{
  "total_price": 总价（数字）,
  "risk_score": 风险评分（0-100整数）,
  "high_risk_items": [{"name": "项目名称", "reason": "风险原因"}],
  "warning_items": [{"name": "项目名称", "reason": "警告原因"}],
  "missing_items": [{"name": "缺失项目", "suggestion": "补充建议"}],
  "overpriced_items": [{"name": "项目名称", "current_price": "当前价格", "market_price": "市场价格", "reason": "价格过高原因"}],
  "market_ref_price": 市场参考价,
  "suggestions": ["建议1", "建议2", "建议3"],
  "summary": "分析总结"
}

请直接返回JSON，不要包含其他任何文本。"""
    
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
        "session_id": f"session_final_{int(time.time())}",
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
                
                all_answers = []
                async for line in response.aiter_lines():
                    line = (line or "").strip()
                    if not line or line == "data: [DONE]":
                        continue
                    if not line.startswith("data:"):
                        continue
                    
                    json_str = line[5:].strip()
                    try:
                        data_chunk = json.loads(json_str)
                        if data_chunk.get("type") == "answer":
                            content = data_chunk.get("content", {})
                            if isinstance(content, dict):
                                # 检查是否有answer字段
                                if "answer" in content:
                                    answer_text = content.get("answer", "")
                                    if answer_text:
                                        all_answers.append(answer_text)
                                        print(f'收到answer文本: {answer_text[:100]}...')
                                # 检查是否有text字段
                                elif "text" in content:
                                    text = content.get("text", "")
                                    if text:
                                        all_answers.append(text)
                                        print(f'收到text文本: {text[:100]}...')
                    except json.JSONDecodeError:
                        continue
                
                full_answer = "".join(all_answers)
                print(f'\n提取的完整回答 ({len(full_answer)} 字符):')
                if full_answer:
                    print(full_answer[:500] + "..." if len(full_answer) > 500 else full_answer)
                    
                    # 尝试解析为JSON
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
                        print(f'\n✅ 成功解析为JSON!')
                        print(f'   包含字段: {list(result.keys())}')
                        
                        # 检查关键字段
                        required_fields = ["risk_score", "suggestions", "summary"]
                        missing_fields = [field for field in required_fields if field not in result]
                        
                        if missing_fields:
                            print(f'   ⚠️ 缺少关键字段: {missing_fields}')
                        else:
                            print(f'   ✅ 所有关键字段都存在')
                        
                        if "risk_score" in result:
                            print(f'   风险评分: {result["risk_score"]}')
                        if "total_price" in result:
                            print(f'   总价: {result["total_price"]}')
                        if "high_risk_items" in result:
                            print(f'   高风险项目数: {len(result["high_risk_items"])}')
                        if "suggestions" in result:
                            print(f'   建议数: {len(result["suggestions"])}')
                        
                        return True, result
                    except json.JSONDecodeError as e:
                        print(f'\n❌ 无法解析为JSON: {e}')
                        print(f'   原始内容前200字符: {full_answer[:200]}')
                        return False, None
                else:
                    print('\n❌ 没有提取到回答内容')
                    return False, None
    
    except Exception as e:
        print(f'请求异常: {e}')
        import traceback
        traceback.print_exc()
        return False, None

async def test_backend_service():
    """测试后端服务中的扣子服务"""
    print('\n\n=== 测试后端扣子服务 ===')
    
    try:
        from app.services.coze_service import coze_service
        
        test_image_url = 'https://zhuangxiu-images-photo.oss-cn-shenzhen.aliyuncs.com/quote/test.jpg'
        
        print(f'测试图片URL: {test_image_url[:100]}...')
        print('调用coze_service.analyze_quote()...')
        
        result = await coze_service.analyze_quote(test_image_url, user_id=999)
        
        if result:
            print(f'✅ 后端服务返回结果')
            print(f'   结果类型: {type(result)}')
            if isinstance(result, dict):
                print(f'   包含字段: {list(result.keys())}')
                
                # 检查是否是兜底数据
                if result.get("is_fallback"):
                    print(f'   ⚠️ 这是兜底数据 (is_fallback: True)')
                    print(f'   错误代码: {result.get("error_code")}')
                    print(f'   分析说明: {result.get("analysis_note")}')
                    return False, result
                else:
                    print(f'   ✅ 这是真实的AI分析数据')
                    if "risk_score" in result:
                        print(f'   风险评分: {result["risk_score"]}')
                    if "total_price" in result:
                        print(f'   总价: {result["total_price"]}')
                    return True, result
            else:
                print(f'   ❌ 结果不是字典类型: {type(result)}')
                return False, result
        else:
            print('❌ 后端服务返回空结果')
            return False, None
            
    except Exception as e:
        print(f'后端服务测试异常: {e}')
        import traceback
        traceback.print_exc()
        return False, None

async def main():
    """主函数"""
    print('开始测试扣子AI分析功能...')
    
    # 测试直接API调用
    print('\n1. 测试直接API调用:')
    api_success, api_result = await test_coze_final()
    
    # 测试后端服务
    print('\n2. 测试后端服务:')
    backend_success, backend_result = await test_backend_service()
    
    print('\n\n=== 最终测试总结 ===')
    print(f'直接API调用: {"✅ 成功" if api_success else "❌ 失败"}')
    print(f'后端服务调用: {"✅ 成功" if backend_success else "❌ 失败"}')
    
    if not api_success:
        print('\n⚠️ 直接API调用失败的可能原因:')
        print('1. 扣子智能体配置可能有问题')
        print('2. 图片URL可能无法访问')
        print('3. 扣子智能体返回了工具调用说明而不是分析结果')
        print('4. 提示词可能需要优化')
        print('5. 扣子站点可能已失效')
    
    if not backend_success:
        print('\n⚠️ 后端服务调用失败的可能原因:')
        print('1. 扣子服务配置有问题')
        print('2. 扣子服务解析逻辑有问题')
        print('3. 扣子智能体返回了工具调用说明，触发了兜底机制')
        print('4. 需要检查coze_service.py中的解析逻辑')
    
    # 问题归属分析
    print('\n=== 问题归属分析 ===')
    print('这是**后台问题**，具体表现在：')
    print('1. 扣子智能体配置在后端')
    print('2. AI分析服务调用逻辑在后端')
    print('3. 错误处理和兜底机制在后端')
    print('4. 需要修复后端扣子服务的解析逻辑')
    
    # 建议的解决方案
    print('\n=== 建议的解决方案 ===')
    print('1. 检查扣子智能体配置是否正确')
    print('2. 优化扣子服务的提示词和解析逻辑')
    print('3. 如果扣子智能体确实返回工具调用说明，需要调整智能体配置')
    print('4. 考虑使用备用AI服务（如DeepSeek）')
    print('5. 修复coze_service.py中的解析逻辑')

if __name__ == "__main__":
    asyncio.run(main())

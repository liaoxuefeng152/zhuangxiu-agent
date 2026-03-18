#!/usr/bin/env python3
"""
修复后的扣子API测试 - 使用正确的开发环境图片URL
"""
import sys
sys.path.insert(0, 'backend')
import asyncio
import json
import httpx
import time
from app.core.config import settings
from app.services.oss_service import oss_service

async def test_coze_with_correct_url():
    """使用正确的图片URL测试扣子API"""
    print('=== 使用正确的图片URL测试扣子API ===')
    
    site_url = settings.COZE_SITE_URL
    site_token = settings.COZE_SITE_TOKEN
    project_id = settings.COZE_PROJECT_ID
    
    print(f'Site URL: {site_url}')
    print(f'Project ID: {project_id}')
    
    # 使用正确的开发环境图片URL
    # 首先检查OSS服务是否正常工作
    if not oss_service.photo_bucket:
        print('❌ OSS照片Bucket未初始化')
        return False, None
    
    # 生成测试图片的签名URL
    test_object_key = 'quote/test.jpg'
    try:
        signed_url = oss_service.sign_url_for_key(test_object_key, expires=3600)
        print(f'生成的签名URL: {signed_url[:100]}...')
        
        # 测试URL是否可访问
        import requests
        response = requests.head(signed_url, timeout=10)
        if response.status_code == 200:
            print(f'✅ 图片URL可以访问 (状态码: {response.status_code})')
            test_image_url = signed_url
        else:
            print(f'❌ 图片URL无法访问 (状态码: {response.status_code})')
            # 尝试使用公共URL
            bucket_name = settings.ALIYUN_OSS_BUCKET1
            endpoint = settings.ALIYUN_OSS_ENDPOINT
            public_url = f'https://{bucket_name}.{endpoint}/{test_object_key}'
            print(f'尝试公共URL: {public_url}')
            
            response2 = requests.head(public_url, timeout=10)
            if response2.status_code == 200:
                print(f'✅ 公共URL可以访问')
                test_image_url = public_url
            else:
                print(f'❌ 公共URL也无法访问 (状态码: {response2.status_code})')
                # 使用模拟URL
                test_image_url = 'https://via.placeholder.com/600x800?text=Test+Quote+Image'
                print(f'⚠️ 使用模拟图片URL: {test_image_url}')
                
    except Exception as e:
        print(f'❌ 生成签名URL失败: {e}')
        # 使用模拟URL
        test_image_url = 'https://via.placeholder.com/600x800?text=Test+Quote+Image'
        print(f'⚠️ 使用模拟图片URL: {test_image_url}')
    
    print(f'\n使用的图片URL: {test_image_url}')
    
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
        "session_id": f"session_fixed_{int(time.time())}",
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

async def test_backend_service_fixed():
    """测试修复后的后端服务"""
    print('\n\n=== 测试修复后的后端服务 ===')
    
    try:
        from app.services.coze_service import coze_service
        
        # 使用正确的图片URL
        test_object_key = 'quote/test.jpg'
        signed_url = oss_service.sign_url_for_key(test_object_key, expires=3600)
        
        print(f'测试图片URL: {signed_url[:100]}...')
        print('调用coze_service.analyze_quote()...')
        
        result = await coze_service.analyze_quote(signed_url, user_id=999)
        
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
                    
                    # 检查错误原因
                    if result.get("error_code") == "tool_call_detected":
                        print(f'   ❌ 扣子智能体返回了工具调用说明，而不是分析结果')
                        print(f'   需要检查扣子智能体配置')
                    elif result.get("error_code") == "image_access_failed":
                        print(f'   ❌ 图片访问失败')
                        print(f'   需要检查图片URL是否正确')
                    elif result.get("error_code") == "json_parse_failed":
                        print(f'   ❌ JSON解析失败')
                        print(f'   需要检查扣子智能体返回格式')
                    
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

async def test_contract_analysis():
    """测试合同分析功能"""
    print('\n\n=== 测试合同分析功能 ===')
    
    try:
        from app.services.coze_service import coze_service
        
        # 使用正确的图片URL
        test_object_key = 'contract/test.jpg'
        signed_url = oss_service.sign_url_for_key(test_object_key, expires=3600)
        
        print(f'测试合同图片URL: {signed_url[:100]}...')
        print('调用coze_service.analyze_contract()...')
        
        result = await coze_service.analyze_contract(signed_url, user_id=999)
        
        if result:
            print(f'✅ 合同分析返回结果')
            print(f'   结果类型: {type(result)}')
            if isinstance(result, dict):
                print(f'   包含字段: {list(result.keys())}')
                
                # 检查是否是兜底数据
                if result.get("is_fallback"):
                    print(f'   ⚠️ 这是兜底数据 (is_fallback: True)')
                    print(f'   错误代码: {result.get("error_code")}')
                    return False, result
                else:
                    print(f'   ✅ 这是真实的AI分析数据')
                    if "risk_score" in result:
                        print(f'   风险评分: {result["risk_score"]}')
                    if "key_clauses" in result:
                        print(f'   关键条款数: {len(result["key_clauses"])}')
                    return True, result
            else:
                print(f'   ❌ 结果不是字典类型: {type(result)}')
                return False, result
        else:
            print('❌ 合同分析返回空结果')
            return False, None
            
    except Exception as e:
        print(f'合同分析测试异常: {e}')
        import traceback
        traceback.print_exc()
        return False, None

async def main():
    """主函数"""
    print('开始测试修复后的扣子AI分析功能...')
    
    # 测试直接API调用
    print('\n1. 测试直接API调用（使用正确URL）:')
    api_success, api_result = await test_coze_with_correct_url()
    
    # 测试后端服务
    print('\n2. 测试后端服务（报价单分析）:')
    backend_success, backend_result = await test_backend_service_fixed()
    
    # 测试合同分析
    print('\n3. 测试合同分析功能:')
    contract_success, contract_result = await test_contract_analysis()
    
    print('\n\n=== 最终测试总结 ===')
    print(f'直接API调用: {"✅ 成功" if api_success else "❌ 失败"}')
    print(f'后端报价单分析: {"✅ 成功" if backend_success else "❌ 失败"}')
    print(f'后端合同分析: {"✅ 成功" if contract_success else "❌ 失败"}')
    
    # 问题归属分析
    print('\n=== 问题归属分析 ===')
    if not api_success or not backend_success or not contract_success:
        print('这是**后台问题**，具体表现在：')
        print('1. 扣子智能体配置在后端')
        print('2. AI分析服务调用逻辑在后端')
        print('3. 图片URL生成和访问问题在后端')
        print('4. 错误处理和兜底机制在后端')
    else:
        print('✅ 所有测试通过！这是**正常功能**')
    
    # 建议的解决方案
    print('\n=== 建议的解决方案 ===')
    if not api_success:
        print('1. 检查扣子智能体配置是否正确')
        print('2. 优化扣子服务的提示词和解析逻辑')
        print('3. 如果扣子智能体返回工具调用说明，需要调整智能体配置')
    
    if not backend_success or not contract_success:
        print('4. 检查coze_service.py中的解析逻辑')
        print('5. 确保图片URL可以正常访问')
        print('6. 考虑使用备用AI服务（如DeepSeek）')
    
    print('\n7. 修复OSS服务配置，确保生成正确的签名URL')
    print('8. 确保开发环境和生产环境的OSS桶配置一致')

if __name__ == "__main__":
    asyncio.run(main())

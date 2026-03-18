#!/usr/bin/env python3
"""
直接测试扣子智能体API - 简化版本
"""
import requests
import json
import time

def test_coze_direct():
    """直接测试扣子智能体API"""
    print('=== 直接测试扣子智能体API ===')
    
    # 扣子站点配置
    site_url = 'https://9n37hmztzw.coze.site'
    site_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImIxYmFkYTkxLTYyMjctNDAyYi1iZTMwLTU4ZTMxODQzYjJjYiJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbImhEbENJemNqZk83V1ZyTG5IblJlNjRQR05NOGJjbnUxIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzcyNjc1MzM2LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjAzNzA1MTg3MjY5NjA3NDYwIiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjEzNTgyNTk0OTEwNzE1OTEzIn0.HfN-fqpyZiVyDS_8RndLNgcmmcwhY6kGbHAeuidFOTDGhLXFVdPuf1WrEhd_zYzbjL2SXbx8Gg6acaUu8FQCJDQQQd46NeY_NoIQQti1Gh5ZXVry7K6qtxCLxkX46MzTZ_sP1PkqzgCRMFJMjLKZ3wAEBkALLxkR82uzdjYUoiRz6pFhm6Rhvwtk-3cxLFmwr5w6vfeRFCBQyBcti_Uks8JaKjp6nvqg_cseYmVrtym2Sp0bcDFUQx5F2ft6qm-4g0cT-n2DCFSyWaEVl_lvf09NQU43gU6ucDOpwDU4gduDss1en-OMfWIEfa7-u9_gXTn2AcQvwpNb7U4ZzCH7zg'
    project_id = '7603691852046368804'
    
    print(f'Site URL: {site_url}')
    print(f'Project ID: {project_id}')
    
    # 使用一个公开可访问的测试图片URL
    test_image_url = 'https://via.placeholder.com/600x800?text=Test+Quote+Image'
    print(f'测试图片URL: {test_image_url}')
    
    # 构建提示词
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
        response = requests.post(api_url, json=data, headers=headers, timeout=60)
        print(f'响应状态码: {response.status_code}')
        
        if response.status_code == 200:
            # 解析流式响应
            content = response.text
            print(f'响应内容长度: {len(content)} 字符')
            
            # 尝试提取JSON响应
            lines = content.split('\n')
            json_responses = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('data:'):
                    json_str = line[5:].strip()
                    if json_str and json_str != '[DONE]':
                        try:
                            data_chunk = json.loads(json_str)
                            if data_chunk.get('type') == 'answer':
                                content_data = data_chunk.get('content', {})
                                if isinstance(content_data, dict):
                                    if 'answer' in content_data:
                                        json_responses.append(content_data['answer'])
                                    elif 'text' in content_data:
                                        json_responses.append(content_data['text'])
                        except json.JSONDecodeError:
                            continue
            
            if json_responses:
                full_response = ''.join(json_responses)
                print(f'\n提取的完整响应 ({len(full_response)} 字符):')
                print(full_response[:500] + '...' if len(full_response) > 500 else full_response)
                
                # 尝试解析为JSON
                try:
                    # 清理可能的markdown代码块
                    cleaned = full_response.strip()
                    if cleaned.startswith('```json'):
                        cleaned = cleaned[7:].strip()
                    if cleaned.startswith('```'):
                        cleaned = cleaned[3:].strip()
                    if cleaned.endswith('```'):
                        cleaned = cleaned[:-3].strip()
                    
                    result = json.loads(cleaned)
                    print(f'\n✅ 成功解析为JSON!')
                    print(f'   包含字段: {list(result.keys())}')
                    
                    # 检查关键字段
                    required_fields = ['risk_score', 'suggestions', 'summary']
                    missing_fields = [field for field in required_fields if field not in result]
                    
                    if missing_fields:
                        print(f'   ⚠️ 缺少关键字段: {missing_fields}')
                    else:
                        print(f'   ✅ 所有关键字段都存在')
                    
                    if 'risk_score' in result:
                        print(f'   风险评分: {result["risk_score"]}')
                    if 'total_price' in result:
                        print(f'   总价: {result["total_price"]}')
                    if 'high_risk_items' in result:
                        print(f'   高风险项目数: {len(result["high_risk_items"])}')
                    if 'suggestions' in result:
                        print(f'   建议数: {len(result["suggestions"])}')
                    
                    return True, result
                except json.JSONDecodeError as e:
                    print(f'\n❌ 无法解析为JSON: {e}')
                    print(f'   原始内容前200字符: {full_response[:200]}')
                    
                    # 检查是否是工具调用说明
                    if 'tool_call' in full_response.lower() or 'function' in full_response.lower():
                        print(f'   ⚠️ 扣子智能体返回了工具调用说明，而不是分析结果')
                        print(f'   需要检查扣子智能体配置')
                    
                    return False, None
            else:
                print('\n❌ 没有提取到JSON响应')
                print(f'   原始响应: {content[:500]}...')
                return False, None
        else:
            print(f'❌ API调用失败: {response.status_code}')
            print(f'   响应内容: {response.text[:500]}')
            return False, None
            
    except Exception as e:
        print(f'❌ API调用异常: {e}')
        import traceback
        traceback.print_exc()
        return False, None

def test_contract_analysis():
    """测试合同分析"""
    print('\n\n=== 测试合同分析 ===')
    
    # 扣子站点配置
    site_url = 'https://9n37hmztzw.coze.site'
    site_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImIxYmFkYTkxLTYyMjctNDAyYi1iZTMwLTU4ZTMxODQzYjJjYiJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbImhEbENJemNqZk83V1ZyTG5IblJlNjRQR05NOGJjbnUxIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzcyNjc1MzM2LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjAzNzA1MTg3MjY5NjA3NDYwIiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjEzNTgyNTk0OTEwNzE1OTEzIn0.HfN-fqpyZiVyDS_8RndLNgcmmcwhY6kGbHAeuidFOTDGhLXFVdPuf1WrEhd_zYzbjL2SXbx8Gg6acaUu8FQCJDQQQd46NeY_NoIQQti1Gh5ZXVry7K6qtxCLxkX46MzTZ_sP1PkqzgCRMFJMjLKZ3wAEBkALLxkR82uzdjYUoiRz6pFhm6Rhvwtk-3cxLFmwr5w6vfeRFCBQyBcti_Uks8JaKjp6nvqg_cseYmVrtym2Sp0bcDFUQx5F2ft6qm-4g0cT-n2DCFSyWaEVl_lvf09NQU43gU6ucDOpwDU4gduDss1en-OMfWIEfa7-u9_gXTn2AcQvwpNb7U4ZzCH7zg'
    project_id = '7603691852046368804'
    
    # 使用一个公开可访问的测试图片URL
    test_image_url = 'https://via.placeholder.com/600x800?text=Test+Contract+Image'
    
    # 构建提示词
    prompt = """请分析这份装修合同图片，返回JSON格式的分析结果。

返回格式必须严格遵循：
{
  "risk_score": 风险评分（0-100整数）,
  "key_clauses": [{"clause": "条款内容", "risk_level": "风险等级", "suggestion": "修改建议"}],
  "missing_clauses": [{"clause": "缺失条款", "importance": "重要性", "suggestion": "补充建议"}],
  "unfair_terms": [{"term": "不公平条款", "reason": "不公平原因", "suggestion": "修改建议"}],
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
        "session_id": f"session_contract_{int(time.time())}",
        "project_id": project_id,
        "config": {"recursion_limit": 25},
    }
    
    headers = {
        "Authorization": f"Bearer {site_token}",
        "Content-Type": "application/json"
    }
    
    api_url = f"{site_url.rstrip('/')}/stream_run"
    
    try:
        response = requests.post(api_url, json=data, headers=headers, timeout=60)
        
        if response.status_code == 200:
            # 简化处理：只检查是否有响应
            print(f'✅ 合同分析API调用成功 (状态码: {response.status_code})')
            print(f'   响应长度: {len(response.text)} 字符')
            return True, None
        else:
            print(f'❌ 合同分析API调用失败: {response.status_code}')
            return False, None
            
    except Exception as e:
        print(f'❌ 合同分析API调用异常: {e}')
        return False, None

def main():
    """主函数"""
    print('开始测试扣子智能体AI分析功能...')
    
    # 测试报价单分析
    quote_success, quote_result = test_coze_direct()
    
    # 测试合同分析
    contract_success, contract_result = test_contract_analysis()
    
    print('\n\n=== 测试总结 ===')
    print(f'报价单分析: {"✅ 成功" if quote_success else "❌ 失败"}')
    print(f'合同分析: {"✅ 成功" if contract_success else "❌ 失败"}')
    
    # 问题归属分析
    print('\n=== 问题归属分析 ===')
    
    if not quote_success or not contract_success:
        print('这是**后台问题**，具体表现在：')
        print('1. 扣子智能体配置可能有问题')
        print('2. 扣子智能体可能返回工具调用说明而非分析结果')
        print('3. 扣子智能体API调用可能失败')
        print('4. 网络连接或权限问题')
        
        print('\n可能的原因：')
        print('1. 扣子智能体未正确配置为返回JSON格式')
        print('2. 扣子智能体需要工具调用才能分析图片')
        print('3. 扣子智能体令牌可能已过期')
        print('4. 扣子站点URL可能已失效')
    else:
        print('✅ 扣子智能体API可以正常调用！')
        print('   问题可能在后端服务配置或OSS图片访问')
    
    # 建议的解决方案
    print('\n=== 建议的解决方案 ===')
    if not quote_success or not contract_success:
        print('1. 检查扣子智能体配置是否正确')
        print('2. 检查扣子智能体是否配置为直接返回JSON分析结果')
        print('3. 检查扣子智能体令牌是否有效')
        print('4. 检查扣子站点URL是否可以访问')
    
    print('5. 如果扣子智能体需要工具调用，需要配置相应的工具')
    print('6. 考虑使用备用AI服务（如DeepSeek）')
    print('7. 确保OSS图片URL可以正常访问')

if __name__ == "__main__":
    main()

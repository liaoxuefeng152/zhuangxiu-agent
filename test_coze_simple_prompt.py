#!/usr/bin/env python3
"""
测试简单的提示词是否能让扣子智能体正常工作
"""
import httpx
import json

def test_simple_prompt():
    """测试简单的提示词"""
    print("=== 测试简单提示词 vs 复杂提示词 ===")
    
    # 扣子智能体配置
    site_url = "https://9n37hmztzw.coze.site/stream_run"
    site_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImIxYmFkYTkxLTYyMjctNDAyYi1iZTMwLTU4ZTMxODQzYjJjYiJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbImhEbENJemNqZk83V1ZyTG5IblJlNjRQR05NOGJjbnUxIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzcyNjc1MzM2LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjAzNzA1MTg3MjY5NjA3NDYwIiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjEzNTgyNTk0OTEwNzE1OTEzIn0.HfN-fqpyZiVyDS_8RndLNgcmmcwhY6kGbHAeuidFOTDGhLXFVdPuf1WrEhd_zYzbjL2SXbx8Gg6acaUu8FQCJDQQQd46NeY_NoIQQti1Gh5ZXVry7K6qtxCLxkX46MzTZ_sP1PkqzgCRMFJMjLKZ3wAEBkALLxkR82uzdjYUoiRz6pFhm6Rhvwtk-3cxLFmwr5w6vfeRFCBQyBcti_Uks8JaKjp6nvqg_cseYmVrtym2Sp0bcDFUQx5F2ft6qm-4g0cT-n2DCFSyWaEVl_lvf09NQU43gU6ucDOpwDU4gduDss1en-OMfWIEfa7-u9_gXTn2AcQvwpNb7U4ZzCH7zg"
    project_id = "7603691852046368804"
    
    # 使用用户提供的OSS图片URL
    image_url = "https://zhuangxiu-images-photo.oss-cn-hangzhou.aliyuncs.com/quote/2/1773712924_8150.png?Expires=1773745361&OSSAccessKeyId=TMP.3KoY7XZKoyJpxGvJCeCeLyT6GBiromCYspRdYTRN2RnKYgHzVfb8e5tcnRuXtDi8j6UBYjFrr6pEVWvTZLPE9jMU2A1VzB&Signature=pCLrnIwOarjpKXwdTzkAlR3r5Qs%3D"
    
    headers = {
        "Authorization": f"Bearer {site_token}",
        "Content-Type": "application/json"
    }
    
    # 测试1：用户的简单提示词
    print("\n--- 测试1：用户的简单提示词 ---")
    simple_prompt = f"请帮我分析一下{image_url}"
    
    data_simple = {
        "content": {
            "query": {
                "prompt": [
                    {
                        "type": "text",
                        "content": {
                            "text": simple_prompt
                        }
                    }
                ]
            }
        },
        "type": "query",
        "session_id": "uDXvy0NavDB7WXhLBrSGI",
        "project_id": project_id
    }
    
    try:
        response = httpx.post(
            site_url,
            json=data_simple,
            headers=headers,
            timeout=30.0
        )
        
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 成功!")
            print(f"响应前200字符: {response.text[:200]}...")
        else:
            print(f"❌ 失败!")
            print(f"错误信息: {response.text[:200]}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 测试2：后端的复杂提示词
    print("\n--- 测试2：后端的复杂提示词 ---")
    complex_prompt = """【重要指令】请分析这份装修报价单图片，返回JSON格式的结构化数据。

【明确要求】
1. 这是装修报价单图片，不是合同图片
2. 请分析报价单中的价格、项目、材料等信息
3. 返回纯JSON格式，不要包含其他任何文本

【必需字段】
{
  "total_price": 总价（数字，如：85000.00）,
  "risk_score": 风险评分（0-100整数）,
  "high_risk_items": [
    {"name": "项目名称", "reason": "风险原因"}
  ],
  "warning_items": [
    {"name": "项目名称", "reason": "警告原因"}
  ],
  "missing_items": [
    {"name": "缺失项目", "suggestion": "补充建议"}
  ],
  "overpriced_items": [
    {"name": "项目名称", "current_price": "当前价格", "market_price": "市场价格", "reason": "价格过高原因"}
  ],
  "market_ref_price": 市场参考价（数字或字符串）,
  "suggestions": ["建议1", "建议2", "建议3"],
  "summary": "分析总结（字符串）"
}

【特别注意】
- 不要返回工具调用说明或函数调用格式
- 不要返回合同分析格式（如risk_items、unfair_terms、missing_terms等）
- 直接返回JSON对象，不要用```json```包裹
- 如果无法识别某些信息，请使用合理的默认值或空数组

图片URL: """ + image_url
    
    data_complex = {
        "content": {
            "query": {
                "prompt": [
                    {
                        "type": "text",
                        "content": {
                            "text": complex_prompt
                        }
                    }
                ]
            }
        },
        "type": "query",
        "session_id": "test_session_123",
        "project_id": project_id,
        "config": {"recursion_limit": 25}
    }
    
    try:
        response = httpx.post(
            site_url,
            json=data_complex,
            headers=headers,
            timeout=30.0
        )
        
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 成功!")
            print(f"响应前200字符: {response.text[:200]}...")
        else:
            print(f"❌ 失败!")
            print(f"错误信息: {response.text[:200]}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 测试3：简化版提示词
    print("\n--- 测试3：简化版提示词 ---")
    simplified_prompt = f"""请分析这份装修报价单图片，返回JSON格式的结构化数据。

图片URL: {image_url}

请返回以下JSON格式：
{{
  "total_price": 总价,
  "risk_score": 风险评分,
  "high_risk_items": [{{"name": "项目", "reason": "原因"}}],
  "suggestions": ["建议"],
  "summary": "总结"
}}"""
    
    data_simplified = {
        "content": {
            "query": {
                "prompt": [
                    {
                        "type": "text",
                        "content": {
                            "text": simplified_prompt
                        }
                    }
                ]
            }
        },
        "type": "query",
        "session_id": "test_session_456",
        "project_id": project_id
    }
    
    try:
        response = httpx.post(
            site_url,
            json=data_simplified,
            headers=headers,
            timeout=30.0
        )
        
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 成功!")
            print(f"响应前200字符: {response.text[:200]}...")
        else:
            print(f"❌ 失败!")
            print(f"错误信息: {response.text[:200]}")
    except Exception as e:
        print(f"❌ 异常: {e}")

if __name__ == "__main__":
    test_simple_prompt()

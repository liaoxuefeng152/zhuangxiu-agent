#!/usr/bin/env python3
"""
测试简化提示词的扣子API调用
"""
import httpx
import json

def test_coze_simplified_prompt():
    """测试简化提示词的扣子API调用"""
    print("=== 测试简化提示词的扣子API调用 ===")
    
    site_url = "https://9n37hmztzw.coze.site"
    site_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImIxYmFkYTkxLTYyMjctNDAyYi1iZTMwLTU4ZTMxODQzYjJjYiJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbImhEbENJemNqZk83V1ZyTG5IblJlNjRQR05NOGJjbnUxIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzcyNjc1MzM2LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjAzNzA1MTg3MjY5NjA3NDYwIiwic3JjIjoiaW5ib3VuZF9hdXhoX2FjY2Vzc190b2tlbl9pZDo3NjEzNTgyNTk0OTEwNzE1OTEzIn0.HfN-fqpyZiVyDS_8RndLNgcmmcwhY6kGbHAeuidFOTDGhLXFVdPuf1WrEhd_zYzbjL2SXbx8Gg6acaUu8FQCJDQQQd46NeY_NoIQQti1Gh5ZXVry7K6qtxCLxkX46MzTZ_sP1PkqzgCRMFJMjLKZ3wAEBkALLxkR82uzdjYUoiRz6pFhm6Rhvwtk-3cxLFmwr5w6vfeRFCBQyBcti_Uks8JaKjp6nvqg_cseYmVrtym2Sp0bcDFUQx5F2ft6qm-4g0cT-n2DCFSyWaEVl_lvf09NQU43gU6ucDOpwDU4gduDss1en-OMfWIEfa7-u9_gXTn2AcQvwpNb7U4ZzCH7zg"
    project_id = "7603691852046368804"
    
    # 测试不同的提示词复杂度
    test_cases = [
        ("最简单提示词", "分析这张装修报价单图片"),
        ("中等复杂度", "请分析装修报价单图片，返回JSON格式"),
        ("完整提示词（无格式要求）", "请分析这份装修报价单图片，告诉我总价、风险评分和建议"),
        ("后端原版提示词", """【重要指令】请分析这份装修报价单图片，返回JSON格式的结构化数据。

【明确要求】
1. 这是装修报价单图片，不是合同图片
2. 请分析报价单中的价格、项目、材料等信息
3. 返回纯JSON格式，不要包含其他任何文本

【必需字段】
{
  "total_price": 85000.00,
  "risk_score": 65,
  "high_risk_items": [
    {"name": "水电改造", "reason": "单价过高，超出市场价30%"}
  ],
  "warning_items": [
    {"name": "墙面处理", "reason": "材料规格不明确"}
  ],
  "missing_items": [
    {"name": "垃圾清运费", "suggestion": "建议明确包含在总价中"}
  ],
  "overpriced_items": [
    {"name": "水电改造", "current_price": "15000", "market_price": "10000", "reason": "单价过高"}
  ],
  "market_ref_price": "80000-90000",
  "suggestions": ["建议明确材料品牌和规格", "建议增加质保条款", "建议明确付款方式"],
  "summary": "报价单存在中等风险，主要问题是水电改造单价过高和材料规格不明确。"
}

【特别注意】
- 不要返回工具调用说明或函数调用格式
- 不要返回合同分析格式
- 直接返回JSON对象，不要用```json```包裹""")
    ]
    
    # 使用简单的公开图片URL
    image_url = "https://img.alicdn.com/imgextra/i4/O1CN01Z5p5LZ1M1J5Q6X8q5_!!6000000001378-2-tps-800-600.png"
    
    headers = {
        "Authorization": f"Bearer {site_token}",
        "Content-Type": "application/json"
    }
    
    for test_name, prompt in test_cases:
        print(f"\n--- 测试: {test_name} ---")
        print(f"  提示词长度: {len(prompt)} 字符")
        
        # 构建请求数据
        api_url = f"{site_url.rstrip('/')}/stream_run"
        combined_prompt = f"{prompt}\n\n图片URL: {image_url}"
        
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
            "session_id": "uDXvy0NavDB7WXhLBrSGI",
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
                if "analyze_contract_quote" in response.text or "tool_call" in response.text:
                    print("  ⚠️ 注意: 响应包含工具调用说明")
                elif "total_price" in response.text or "risk_score" in response.text:
                    print("  ✅ 响应包含报价单分析字段")
                else:
                    print("  ⚠️ 响应不包含报价单分析字段")
            else:
                print(f"  ❌ 失败!")
                print(f"  错误信息: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")

if __name__ == "__main__":
    test_coze_simplified_prompt()

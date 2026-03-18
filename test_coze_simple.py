#!/usr/bin/env python3
"""
简单测试扣子API，模拟用户提供的curl命令
"""
import httpx
import json

def test_coze_api_simple():
    """简单测试扣子API"""
    print("=== 简单测试扣子API（模拟用户curl命令） ===")
    
    site_url = "https://9n37hmztzw.coze.site"
    site_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImIxYmFkYTkxLTYyMjctNDAyYi1iZTMwLTU4ZTMxODQzYjJjYiJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbImhEbENJemNqZk83V1ZyTG5IblJlNjRQR05NOGJjbnUxIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzcyNjc1MzM2LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjAzNzA1MTg3MjY5NjA3NDYwIiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjEzNTgyNTk0OTEwNzE1OTEzIn0.HfN-fqpyZiVyDS_8RndLNgcmmcwhY6kGbHAeuidFOTDGhLXFVdPuf1WrEhd_zYzbjL2SXbx8Gg6acaUu8FQCJDQQQd46NeY_NoIQQti1Gh5ZXVry7K6qtxCLxkX46MzTZ_sP1PkqzgCRMFJMjLKZ3wAEBkALLxkR82uzdjYUoiRz6pFhm6Rhvwtk-3cxLFmwr5w6vfeRFCBQyBcti_Uks8JaKjp6nvqg_cseYmVrtym2Sp0bcDFUQx5F2ft6qm-4g0cT-n2DCFSyWaEVl_lvf09NQU43gU6ucDOpwDU4gduDss1en-OMfWIEfa7-u9_gXTn2AcQvwpNb7U4ZzCH7zg"
    project_id = "7603691852046368804"
    
    # 使用用户提供的curl命令中的相同数据
    data = {
        "content": {
            "query": {
                "prompt": [
                    {
                        "type": "text",
                        "content": {
                            "text": "你能做什么"
                        }
                    }
                ]
            }
        },
        "type": "query",
        "session_id": "uDXvy0NavDB7WXhLBrSGI",
        "project_id": project_id
    }
    
    headers = {
        "Authorization": f"Bearer {site_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("  发送请求到扣子API...")
        print(f"  URL: {site_url}/stream_run")
        print(f"  Headers: {headers}")
        print(f"  Data: {json.dumps(data, ensure_ascii=False)}")
        
        response = httpx.post(
            f"{site_url}/stream_run",
            json=data,
            headers=headers,
            timeout=30.0
        )
        
        print(f"  响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("  ✅ 扣子API调用成功!")
            print(f"  响应内容: {response.text[:200]}...")
            return True
        else:
            print(f"  ❌ 扣子API调用失败: {response.status_code}")
            print(f"  错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ 扣子API调用异常: {e}")
        return False

if __name__ == "__main__":
    test_coze_api_simple()

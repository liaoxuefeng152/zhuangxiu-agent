#!/usr/bin/env python3
"""
直接查询数据库获取完整的报价单数据（包括result_json）
"""
import requests
import json
import sys

BASE_URL = "http://120.26.201.61:8001/api/v1"

def main():
    # 1. 登录
    resp = requests.post(
        f"{BASE_URL}/users/login",
        json={"code": "dev_weapp_mock"},
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        data = result.get("data", {})
    else:
        data = result
    
    token = data.get("access_token")
    user_id = data.get("user_id")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    # 2. 获取报价单列表
    resp = requests.get(
        f"{BASE_URL}/quotes/list",
        headers=headers,
        params={"page": 1, "page_size": 5},
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        quotes_data = result.get("data", {})
        quotes = quotes_data.get("quotes", []) or quotes_data.get("list", [])
    else:
        quotes = result.get("quotes", []) or result.get("list", [])
    
    print("=" * 80)
    print("所有报价单列表")
    print("=" * 80)
    for quote in quotes:
        print(f"\nQuote ID: {quote.get('id')}")
        print(f"  文件名: {quote.get('file_name')}")
        print(f"  状态: {quote.get('status')}")
        print(f"  风险评分: {quote.get('risk_score')}")
        print(f"  总价: {quote.get('total_price')}")
        print(f"  创建时间: {quote.get('created_at')}")
        print(f"  result_json存在: {quote.get('result_json') is not None}")
        if quote.get('result_json'):
            print(f"  result_json类型: {type(quote.get('result_json'))}")
            print(f"  result_json内容: {json.dumps(quote.get('result_json'), indent=2, ensure_ascii=False)[:500]}")
    
    # 3. 获取最新的报价单详情
    if quotes:
        latest_quote = quotes[0]
        quote_id = latest_quote.get("id")
        
        print("\n" + "=" * 80)
        print(f"报价单 {quote_id} 完整数据")
        print("=" * 80)
        print(json.dumps(latest_quote, indent=2, ensure_ascii=False))
        
        # 4. 尝试通过详情接口获取
        print("\n" + "=" * 80)
        print(f"通过详情接口获取报价单 {quote_id}")
        print("=" * 80)
        
        resp = requests.get(
            f"{BASE_URL}/quotes/quote/{quote_id}",
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        detail_result = resp.json()
        
        if detail_result.get("code") == 0:
            quote_detail = detail_result.get("data", {})
        else:
            quote_detail = detail_result
        
        print(json.dumps(quote_detail, indent=2, ensure_ascii=False))
        
        # 检查result_json
        result_json = quote_detail.get("result_json")
        if result_json:
            print("\n" + "=" * 80)
            print("result_json 完整内容")
            print("=" * 80)
            print(json.dumps(result_json, indent=2, ensure_ascii=False))
        else:
            print("\n⚠️  result_json为空或未返回")
            print(f"可用字段: {list(quote_detail.keys())}")

if __name__ == "__main__":
    main()

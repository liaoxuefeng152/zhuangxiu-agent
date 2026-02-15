#!/usr/bin/env python3
"""
获取报价单分析结果的详细信息
"""
import requests
import json
import sys
import os

BASE_URL = "http://120.26.201.61:8001/api/v1"

def main():
    # 1. 登录
    print("登录中...")
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
    
    if not token:
        print("登录失败")
        return
    
    print(f"✅ 登录成功 (User ID: {user_id})")
    
    # 2. 获取最新的报价单
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    print("\n获取报价单列表...")
    resp = requests.get(
        f"{BASE_URL}/quotes/list",
        headers=headers,
        params={"page": 1, "page_size": 1},
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        quotes_data = result.get("data", {})
        quotes = quotes_data.get("quotes", []) or quotes_data.get("list", [])
    else:
        quotes = result.get("quotes", []) or result.get("list", [])
    
    if not quotes:
        print("❌ 未找到报价单")
        return
    
    quote = quotes[0]
    quote_id = quote.get("id")
    
    print(f"✅ 找到最新报价单 (Quote ID: {quote_id})")
    
    # 3. 获取详细分析结果
    print(f"\n获取报价单 {quote_id} 的详细分析结果...")
    resp = requests.get(
        f"{BASE_URL}/quotes/quote/{quote_id}",
        headers=headers,
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        quote_data = result.get("data", {})
    else:
        quote_data = result
    
    print("\n" + "=" * 80)
    print("报价单分析结果 - 完整数据")
    print("=" * 80)
    print(json.dumps(quote_data, indent=2, ensure_ascii=False))
    
    # 4. 提取关键字段
    print("\n" + "=" * 80)
    print("关键字段提取")
    print("=" * 80)
    
    print(f"\n基本信息:")
    print(f"  ID: {quote_data.get('id')}")
    print(f"  文件名: {quote_data.get('file_name')}")
    print(f"  文件类型: {quote_data.get('file_type')}")
    print(f"  状态: {quote_data.get('status')}")
    print(f"  创建时间: {quote_data.get('created_at')}")
    
    print(f"\n价格信息:")
    print(f"  总价: {quote_data.get('total_price')}")
    print(f"  市场参考价: {quote_data.get('market_ref_price')}")
    
    print(f"\n风险分析:")
    print(f"  风险评分: {quote_data.get('risk_score')}")
    print(f"  高风险项数量: {len(quote_data.get('high_risk_items', []))}")
    print(f"  警告项数量: {len(quote_data.get('warning_items', []))}")
    print(f"  漏项数量: {len(quote_data.get('missing_items', []))}")
    print(f"  虚高项数量: {len(quote_data.get('overpriced_items', []))}")
    
    # 详细显示各项
    high_risk = quote_data.get('high_risk_items', [])
    if high_risk:
        print(f"\n高风险项详情:")
        for i, item in enumerate(high_risk[:5], 1):
            print(f"  {i}. {json.dumps(item, indent=4, ensure_ascii=False)}")
    
    warning = quote_data.get('warning_items', [])
    if warning:
        print(f"\n警告项详情:")
        for i, item in enumerate(warning[:5], 1):
            print(f"  {i}. {json.dumps(item, indent=4, ensure_ascii=False)}")
    
    missing = quote_data.get('missing_items', [])
    if missing:
        print(f"\n漏项详情:")
        for i, item in enumerate(missing[:5], 1):
            print(f"  {i}. {json.dumps(item, indent=4, ensure_ascii=False)}")
    
    overpriced = quote_data.get('overpriced_items', [])
    if overpriced:
        print(f"\n虚高项详情:")
        for i, item in enumerate(overpriced[:5], 1):
            print(f"  {i}. {json.dumps(item, indent=4, ensure_ascii=False)}")
    
    # 5. 显示result_json的完整内容
    result_json = quote_data.get('result_json', {})
    if result_json:
        print(f"\n" + "=" * 80)
        print("result_json 完整内容（AI分析原始结果）")
        print("=" * 80)
        print(json.dumps(result_json, indent=2, ensure_ascii=False))
        
        # 检查材料信息
        materials = result_json.get("materials") or result_json.get("material_list") or []
        if materials:
            print(f"\n材料清单（从result_json提取）:")
            print(f"  材料数量: {len(materials)}")
            for i, mat in enumerate(materials[:10], 1):
                print(f"  {i}. {json.dumps(mat, indent=4, ensure_ascii=False)}")
        else:
            print(f"\n⚠️  result_json中未找到材料信息")
            print(f"  可用字段: {list(result_json.keys())}")
    else:
        print(f"\n⚠️  result_json为空")
    
    # 6. 显示OCR结果（如果有）
    ocr_result = quote_data.get('ocr_result')
    if ocr_result:
        print(f"\n" + "=" * 80)
        print("OCR识别结果（前500字符）")
        print("=" * 80)
        if isinstance(ocr_result, str):
            print(ocr_result[:500])
        elif isinstance(ocr_result, dict):
            print(json.dumps(ocr_result, indent=2, ensure_ascii=False)[:500])
        else:
            print(str(ocr_result)[:500])
    
    # 7. 保存完整结果到文件
    output_file = os.path.join(
        os.path.dirname(__file__),
        f"quote_{quote_id}_analysis_result.json"
    )
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(quote_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 完整结果已保存到: {output_file}")

if __name__ == "__main__":
    main()

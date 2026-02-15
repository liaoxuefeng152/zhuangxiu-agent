#!/usr/bin/env python3
"""
获取合同AI分析结果的详细信息
"""
import requests
import json
import sys

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
    
    # 2. 获取最新的合同
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    print("\n获取合同列表...")
    resp = requests.get(
        f"{BASE_URL}/contracts/list",
        headers=headers,
        params={"page": 1, "page_size": 1},
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        contracts_data = result.get("data", {})
        contracts = contracts_data.get("contracts", []) or contracts_data.get("list", [])
    else:
        contracts = result.get("contracts", []) or result.get("list", [])
    
    if not contracts:
        print("❌ 未找到合同")
        return
    
    contract = contracts[0]
    contract_id = contract.get("id")
    
    print(f"✅ 找到最新合同 (Contract ID: {contract_id})")
    
    # 3. 获取详细分析结果
    print(f"\n获取合同 {contract_id} 的详细分析结果...")
    resp = requests.get(
        f"{BASE_URL}/contracts/contract/{contract_id}",
        headers=headers,
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        contract_data = result.get("data", {})
    else:
        contract_data = result
    
    print("\n" + "=" * 80)
    print("合同分析结果 - 完整数据")
    print("=" * 80)
    print(json.dumps(contract_data, indent=2, ensure_ascii=False))
    
    # 4. 提取关键字段
    print("\n" + "=" * 80)
    print("关键字段提取")
    print("=" * 80)
    
    print(f"\n基本信息:")
    print(f"  ID: {contract_data.get('id')}")
    print(f"  文件名: {contract_data.get('file_name')}")
    print(f"  状态: {contract_data.get('status')}")
    print(f"  创建时间: {contract_data.get('created_at')}")
    
    print(f"\n风险分析:")
    print(f"  风险等级: {contract_data.get('risk_level')}")
    print(f"  风险项数量: {len(contract_data.get('risk_items', []))}")
    print(f"  霸王条款数量: {len(contract_data.get('unfair_terms', []))}")
    print(f"  漏项数量: {len(contract_data.get('missing_terms', []))}")
    print(f"  建议修改数量: {len(contract_data.get('suggested_modifications', []))}")
    
    # 详细显示各项
    risk_items = contract_data.get('risk_items', [])
    if risk_items:
        print(f"\n风险项详情:")
        for i, item in enumerate(risk_items[:5], 1):
            print(f"  {i}. {json.dumps(item, indent=4, ensure_ascii=False)}")
    
    unfair_terms = contract_data.get('unfair_terms', [])
    if unfair_terms:
        print(f"\n霸王条款详情:")
        for i, item in enumerate(unfair_terms[:5], 1):
            print(f"  {i}. {json.dumps(item, indent=4, ensure_ascii=False)}")
    
    missing_terms = contract_data.get('missing_terms', [])
    if missing_terms:
        print(f"\n漏项详情:")
        for i, item in enumerate(missing_terms[:5], 1):
            print(f"  {i}. {json.dumps(item, indent=4, ensure_ascii=False)}")
    
    suggested_modifications = contract_data.get('suggested_modifications', [])
    if suggested_modifications:
        print(f"\n建议修改详情:")
        for i, item in enumerate(suggested_modifications[:5], 1):
            print(f"  {i}. {json.dumps(item, indent=4, ensure_ascii=False)}")
    
    # 5. 显示result_json的完整内容
    result_json = contract_data.get('result_json', {})
    if result_json:
        print(f"\n" + "=" * 80)
        print("result_json 完整内容（AI分析原始结果）")
        print("=" * 80)
        print(json.dumps(result_json, indent=2, ensure_ascii=False))
        
        # 检查摘要
        summary = result_json.get("summary")
        if summary:
            print(f"\nAI分析摘要:")
            print(f"  {summary}")
    else:
        print(f"\n⚠️  result_json为空")
        print(f"  可用字段: {list(contract_data.keys())}")
    
    # 6. 显示OCR结果（如果有）
    ocr_result = contract_data.get('ocr_result')
    if ocr_result:
        print(f"\n" + "=" * 80)
        print("OCR识别结果（前500字符）")
        print("=" * 80)
        if isinstance(ocr_result, str):
            print(ocr_result[:500])
        elif isinstance(ocr_result, dict):
            ocr_text = ocr_result.get('text', '')
            print(ocr_text[:500] if ocr_text else str(ocr_result)[:500])
        else:
            print(str(ocr_result)[:500])
    
    # 7. 保存完整结果到文件
    output_file = f"contract_{contract_id}_analysis_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(contract_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 完整结果已保存到: {output_file}")

if __name__ == "__main__":
    main()

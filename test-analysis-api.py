#!/usr/bin/env python3
"""
通过API测试装修报价分析和合同审核功能
由于OCR可能失败，我们通过查询已有记录来测试分析功能
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"


def login():
    """登录获取token"""
    try:
        response = requests.post(
            f"{BASE_URL}/users/login",
            json={"code": "dev_h5_mock"}
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("data", {}).get("access_token") or data.get("access_token")
            return token
        return None
    except Exception as e:
        print(f"登录异常: {e}")
        return None


def get_all_quotes(token):
    """获取所有报价单列表"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(
            f"{BASE_URL}/quotes/list",
            headers=headers,
            params={"page": 1, "page_size": 100}
        )
        if response.status_code == 200:
            data = response.json()
            quotes = data.get("data", {}).get("items", []) or data.get("items", [])
            return quotes
        return []
    except Exception as e:
        print(f"获取报价单列表异常: {e}")
        return []


def get_all_contracts(token):
    """获取所有合同列表"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(
            f"{BASE_URL}/contracts/list",
            headers=headers,
            params={"page": 1, "page_size": 100}
        )
        if response.status_code == 200:
            data = response.json()
            contracts = data.get("data", {}).get("items", []) or data.get("items", [])
            return contracts
        return []
    except Exception as e:
        print(f"获取合同列表异常: {e}")
        return []


def test_quote_analysis(token):
    """测试报价单分析功能"""
    print("\n" + "=" * 60)
    print("【测试1: 装修报价分析功能】")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取所有报价单
    print("📋 查询已有报价单...")
    quotes = get_all_quotes(token)
    
    if not quotes:
        print("⚠️  没有找到已存在的报价单")
        print("   提示: 由于OCR识别失败，无法创建新的报价单")
        print("   如果之前有成功上传的报价单，请检查数据库")
        return False
    
    print(f"✅ 找到 {len(quotes)} 个报价单")
    
    # 查找已完成分析的报价单
    completed_quotes = [q for q in quotes if q.get("status") == "completed"]
    
    if completed_quotes:
        print(f"✅ 找到 {len(completed_quotes)} 个已完成分析的报价单")
        quote = completed_quotes[0]
        quote_id = quote.get("id")
        
        print(f"\n📊 查看报价单分析结果 (ID: {quote_id})...")
        response = requests.get(
            f"{BASE_URL}/quotes/quote/{quote_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            quote_data = result.get("data", {}) or result
            
            print(f"\n✅ 报价单分析结果:")
            print(f"   风险评分: {quote_data.get('risk_score', 'N/A')}")
            print(f"   总价: {quote_data.get('total_price', 'N/A')} 元")
            print(f"   市场参考价: {quote_data.get('market_ref_price', 'N/A')} 元")
            
            high_risk = quote_data.get('high_risk_items', [])
            if high_risk:
                print(f"\n   ⚠️  高风险项目 ({len(high_risk)}项):")
                for i, item in enumerate(high_risk[:3], 1):
                    print(f"      {i}. {item}")
            
            warning = quote_data.get('warning_items', [])
            if warning:
                print(f"\n   ⚠️  警告项目 ({len(warning)}项):")
                for i, item in enumerate(warning[:3], 1):
                    print(f"      {i}. {item}")
            
            missing = quote_data.get('missing_items', [])
            if missing:
                print(f"\n   📋 缺失项目 ({len(missing)}项):")
                for i, item in enumerate(missing[:3], 1):
                    print(f"      {i}. {item}")
            
            overpriced = quote_data.get('overpriced_items', [])
            if overpriced:
                print(f"\n   💰 价格偏高项目 ({len(overpriced)}项):")
                for i, item in enumerate(overpriced[:3], 1):
                    print(f"      {i}. {item}")
            
            return True
        else:
            print(f"❌ 获取分析结果失败: {response.status_code}")
            return False
    else:
        # 查找分析中的报价单
        analyzing_quotes = [q for q in quotes if q.get("status") == "analyzing"]
        if analyzing_quotes:
            print(f"⏳ 找到 {len(analyzing_quotes)} 个正在分析中的报价单")
            print("   等待分析完成...")
            
            quote_id = analyzing_quotes[0].get("id")
            max_wait = 60
            waited = 0
            
            while waited < max_wait:
                time.sleep(2)
                waited += 2
                
                response = requests.get(
                    f"{BASE_URL}/quotes/quote/{quote_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    quote_data = result.get("data", {}) or result
                    status = quote_data.get("status")
                    
                    if status == "completed":
                        print(f"\n✅ 报价单分析完成！")
                        print(f"   风险评分: {quote_data.get('risk_score', 'N/A')}")
                        return True
                    elif status == "failed":
                        print(f"\n❌ 报价单分析失败")
                        return False
        else:
            print("⚠️  没有找到已完成或正在分析的报价单")
            print("   所有报价单状态:")
            for q in quotes[:5]:
                print(f"      ID: {q.get('id')}, 状态: {q.get('status')}, 文件名: {q.get('file_name', 'N/A')}")
            return False


def test_contract_analysis(token):
    """测试合同审核功能"""
    print("\n" + "=" * 60)
    print("【测试2: 装修合同审核功能】")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取所有合同
    print("📋 查询已有合同...")
    contracts = get_all_contracts(token)
    
    if not contracts:
        print("⚠️  没有找到已存在的合同")
        print("   提示: 由于OCR识别失败，无法创建新的合同")
        print("   如果之前有成功上传的合同，请检查数据库")
        return False
    
    print(f"✅ 找到 {len(contracts)} 个合同")
    
    # 查找已完成审核的合同
    completed_contracts = [c for c in contracts if c.get("status") == "completed"]
    
    if completed_contracts:
        print(f"✅ 找到 {len(completed_contracts)} 个已完成审核的合同")
        contract = completed_contracts[0]
        contract_id = contract.get("id")
        
        print(f"\n📊 查看合同审核结果 (ID: {contract_id})...")
        response = requests.get(
            f"{BASE_URL}/contracts/contract/{contract_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            contract_data = result.get("data", {}) or result
            
            print(f"\n✅ 合同审核结果:")
            print(f"   风险等级: {contract_data.get('risk_level', 'N/A')}")
            
            risk_items = contract_data.get('risk_items', [])
            if risk_items:
                print(f"\n   ⚠️  风险条款 ({len(risk_items)}项):")
                for i, item in enumerate(risk_items[:3], 1):
                    print(f"      {i}. {item}")
            
            unfair = contract_data.get('unfair_terms', [])
            if unfair:
                print(f"\n   ⚠️  不公平条款 ({len(unfair)}项):")
                for i, item in enumerate(unfair[:3], 1):
                    print(f"      {i}. {item}")
            
            missing = contract_data.get('missing_terms', [])
            if missing:
                print(f"\n   📋 缺失条款 ({len(missing)}项):")
                for i, item in enumerate(missing[:3], 1):
                    print(f"      {i}. {item}")
            
            suggestions = contract_data.get('suggested_modifications', [])
            if suggestions:
                print(f"\n   💡 建议修改 ({len(suggestions)}项):")
                for i, item in enumerate(suggestions[:3], 1):
                    print(f"      {i}. {item}")
            
            return True
        else:
            print(f"❌ 获取审核结果失败: {response.status_code}")
            return False
    else:
        # 查找审核中的合同
        analyzing_contracts = [c for c in contracts if c.get("status") == "analyzing"]
        if analyzing_contracts:
            print(f"⏳ 找到 {len(analyzing_contracts)} 个正在审核中的合同")
            print("   等待审核完成...")
            
            contract_id = analyzing_contracts[0].get("id")
            max_wait = 60
            waited = 0
            
            while waited < max_wait:
                time.sleep(2)
                waited += 2
                
                response = requests.get(
                    f"{BASE_URL}/contracts/contract/{contract_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    contract_data = result.get("data", {}) or result
                    status = contract_data.get("status")
                    
                    if status == "completed":
                        print(f"\n✅ 合同审核完成！")
                        print(f"   风险等级: {contract_data.get('risk_level', 'N/A')}")
                        return True
                    elif status == "failed":
                        print(f"\n❌ 合同审核失败")
                        return False
        else:
            print("⚠️  没有找到已完成或正在审核的合同")
            print("   所有合同状态:")
            for c in contracts[:5]:
                print(f"      ID: {c.get('id')}, 状态: {c.get('status')}, 文件名: {c.get('file_name', 'N/A')}")
            return False


def main():
    """主函数"""
    print("=" * 60)
    print("装修报价分析和合同审核功能测试")
    print("=" * 60)
    
    # 登录
    token = login()
    if not token:
        print("❌ 无法继续测试：登录失败")
        return
    
    print("✅ 登录成功")
    
    # 测试报价单分析
    quote_result = test_quote_analysis(token)
    
    # 测试合同审核
    contract_result = test_contract_analysis(token)
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"报价单分析功能: {'✅ 通过' if quote_result else '❌ 失败（可能原因：OCR识别失败或没有已完成的报价单）'}")
    print(f"合同审核功能: {'✅ 通过' if contract_result else '❌ 失败（可能原因：OCR识别失败或没有已完成的合同）'}")
    print("\n💡 提示:")
    print("   - 如果测试失败，可能是因为OCR识别失败导致无法创建新的报价单/合同")
    print("   - 请先修复OCR配置（更新有效的阿里云Access Key）")
    print("   - 或者检查数据库中是否有之前成功上传并完成分析的记录")
    print("=" * 60)


if __name__ == "__main__":
    main()

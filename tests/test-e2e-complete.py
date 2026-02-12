#!/usr/bin/env python3
"""
完整的端到端测试：从文件上传到AI分析结果
"""
import os
import sys
_d = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(_d) not in sys.path:
    sys.path.insert(0, os.path.dirname(_d))
import requests
from tests import fixture_path, QUOTE_PNG, CONTRACT_PNG
import time
import json
import os
import io
from typing import Dict, Optional

BASE_URL = "http://localhost:8000/api/v1"

def login() -> Optional[str]:
    """登录获取token"""
    try:
        response = requests.post(
            f"{BASE_URL}/users/login",
            json={"code": "dev_h5_mock"}
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("data", {}).get("access_token") or data.get("access_token")
            print(f"✅ 登录成功")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None


def test_quote_e2e(token: str) -> bool:
    """完整的报价单分析端到端测试"""
    print("\n" + "=" * 70)
    print("【端到端测试1: 报价单分析完整流程】")
    print("=" * 70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 步骤1: 上传报价单文件
    quote_png_path = fixture_path(QUOTE_PNG)
    if not os.path.exists(quote_png_path):
        print(f"❌ 测试文件不存在: {quote_png_path}")
        return False
    
    print(f"\n📤 步骤1: 上传报价单文件")
    print(f"   文件: {quote_png_path}")
    try:
        with open(quote_png_path, "rb") as f:
            file_content = f.read()
        
        print(f"   文件大小: {len(file_content)} bytes ({len(file_content)/1024:.2f} KB)")
        
        files = {"file": (os.path.basename(quote_png_path), io.BytesIO(file_content), "image/png")}
        response = requests.post(
            f"{BASE_URL}/quotes/upload",
            headers=headers,
            files=files
        )
        
        if response.status_code != 200:
            print(f"   ❌ 上传失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
        
        data = response.json()
        quote_id = data.get("data", {}).get("task_id") or data.get("task_id")
        status = data.get("data", {}).get("status") or data.get("status")
        
        print(f"   ✅ 上传成功")
        print(f"   Quote ID: {quote_id}")
        print(f"   状态: {status}")
        
        # 步骤2: 等待OCR识别和AI分析完成
        print(f"\n⏳ 步骤2: 等待OCR识别和AI分析完成（最多90秒）...")
        max_wait = 90
        wait_interval = 3
        waited = 0
        last_status = status
        
        while waited < max_wait:
            time.sleep(wait_interval)
            waited += wait_interval
            
            try:
                response = requests.get(
                    f"{BASE_URL}/quotes/quote/{quote_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    quote_data = result.get("data", {}) or result
                    current_status = quote_data.get("status")
                    
                    if current_status != last_status:
                        print(f"   📊 状态变化: {last_status} → {current_status} ({waited}秒)")
                        last_status = current_status
                    
                    if current_status == "completed":
                        print(f"\n   ✅ 分析完成！")
                        
                        # 步骤3: 验证分析结果
                        print(f"\n📊 步骤3: 验证分析结果")
                        
                        risk_score = quote_data.get('risk_score')
                        total_price = quote_data.get('total_price')
                        market_ref_price = quote_data.get('market_ref_price')
                        
                        print(f"   风险评分: {risk_score}")
                        print(f"   总价: {total_price} 元" if total_price else "   总价: 未识别")
                        print(f"   市场参考价: {market_ref_price} 元" if market_ref_price else "   市场参考价: 未提供")
                        
                        # 检查分析结果字段
                        high_risk = quote_data.get('high_risk_items', [])
                        warning = quote_data.get('warning_items', [])
                        missing = quote_data.get('missing_items', [])
                        overpriced = quote_data.get('overpriced_items', [])
                        
                        print(f"\n   分析项统计:")
                        print(f"   - 高风险项目: {len(high_risk)} 项")
                        print(f"   - 警告项目: {len(warning)} 项")
                        print(f"   - 缺失项目: {len(missing)} 项")
                        print(f"   - 价格偏高项目: {len(overpriced)} 项")
                        
                        # 显示部分结果
                        if high_risk:
                            print(f"\n   ⚠️  高风险项目示例:")
                            for i, item in enumerate(high_risk[:2], 1):
                                if isinstance(item, dict):
                                    print(f"      {i}. {item.get('item', item.get('name', str(item)))}")
                                else:
                                    print(f"      {i}. {item}")
                        
                        if warning:
                            print(f"\n   ⚠️  警告项目示例:")
                            for i, item in enumerate(warning[:2], 1):
                                if isinstance(item, dict):
                                    print(f"      {i}. {item.get('item', item.get('name', str(item)))}")
                                else:
                                    print(f"      {i}. {item}")
                        
                        # 验证OCR结果
                        ocr_result = quote_data.get('ocr_result', {})
                        if ocr_result:
                            ocr_text = ocr_result.get('text', '')
                            if ocr_text:
                                print(f"\n   ✅ OCR识别成功，文本长度: {len(ocr_text)} 字符")
                                print(f"   OCR文本预览: {ocr_text[:100]}...")
                            else:
                                print(f"\n   ⚠️  OCR结果为空")
                        else:
                            print(f"\n   ⚠️  未找到OCR结果")
                        
                        # 验证AI分析结果
                        result_json = quote_data.get('result_json', {})
                        if result_json:
                            print(f"\n   ✅ AI分析结果已保存")
                        else:
                            print(f"\n   ⚠️  未找到AI分析结果JSON")
                        
                        print(f"\n✅ 报价单分析端到端测试通过！")
                        return True
                    elif current_status == "failed":
                        print(f"\n   ❌ 分析失败")
                        error_msg = quote_data.get('error_message', '未知错误')
                        print(f"   错误信息: {error_msg}")
                        return False
                elif response.status_code == 404:
                    print(f"   ⚠️  报价单不存在 (404)")
                    return False
                else:
                    # 忽略查询错误，继续等待
                    pass
            except Exception as e:
                # 忽略查询异常，继续等待
                pass
        
        print(f"\n⏰ 等待超时（{max_wait}秒），分析可能仍在进行中")
        print(f"   最终状态: {last_status}")
        return False
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_contract_e2e(token: str) -> bool:
    """完整的合同审核端到端测试"""
    print("\n" + "=" * 70)
    print("【端到端测试2: 合同审核完整流程】")
    print("=" * 70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 步骤1: 上传合同文件
    contract_png_path = fixture_path(CONTRACT_PNG)
    if not os.path.exists(contract_png_path):
        print(f"❌ 测试文件不存在: {contract_png_path}")
        return False
    
    print(f"\n📤 步骤1: 上传合同文件")
    print(f"   文件: {contract_png_path}")
    try:
        with open(contract_png_path, "rb") as f:
            file_content = f.read()
        
        print(f"   文件大小: {len(file_content)} bytes ({len(file_content)/1024:.2f} KB)")
        
        files = {"file": (os.path.basename(contract_png_path), io.BytesIO(file_content), "image/png")}
        response = requests.post(
            f"{BASE_URL}/contracts/upload",
            headers=headers,
            files=files
        )
        
        if response.status_code != 200:
            print(f"   ❌ 上传失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
        
        data = response.json()
        contract_id = data.get("data", {}).get("task_id") or data.get("task_id")
        status = data.get("data", {}).get("status") or data.get("status")
        
        print(f"   ✅ 上传成功")
        print(f"   Contract ID: {contract_id}")
        print(f"   状态: {status}")
        
        # 步骤2: 等待OCR识别和AI审核完成
        print(f"\n⏳ 步骤2: 等待OCR识别和AI审核完成（最多90秒）...")
        max_wait = 90
        wait_interval = 3
        waited = 0
        last_status = status
        
        while waited < max_wait:
            time.sleep(wait_interval)
            waited += wait_interval
            
            try:
                response = requests.get(
                    f"{BASE_URL}/contracts/contract/{contract_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    contract_data = result.get("data", {}) or result
                    current_status = contract_data.get("status")
                    
                    if current_status != last_status:
                        print(f"   📊 状态变化: {last_status} → {current_status} ({waited}秒)")
                        last_status = current_status
                    
                    if current_status == "completed":
                        print(f"\n   ✅ 审核完成！")
                        
                        # 步骤3: 验证审核结果
                        print(f"\n📊 步骤3: 验证审核结果")
                        
                        risk_level = contract_data.get('risk_level')
                        print(f"   风险等级: {risk_level}")
                        
                        # 检查审核结果字段
                        risk_items = contract_data.get('risk_items', [])
                        unfair_terms = contract_data.get('unfair_terms', [])
                        missing_terms = contract_data.get('missing_terms', [])
                        suggestions = contract_data.get('suggested_modifications', [])
                        
                        print(f"\n   审核项统计:")
                        print(f"   - 风险条款: {len(risk_items)} 项")
                        print(f"   - 不公平条款: {len(unfair_terms)} 项")
                        print(f"   - 缺失条款: {len(missing_terms)} 项")
                        print(f"   - 建议修改: {len(suggestions)} 项")
                        
                        # 显示部分结果
                        if risk_items:
                            print(f"\n   ⚠️  风险条款示例:")
                            for i, item in enumerate(risk_items[:2], 1):
                                if isinstance(item, dict):
                                    term = item.get('term', item.get('description', str(item)))
                                    print(f"      {i}. {term}")
                                else:
                                    print(f"      {i}. {item}")
                        
                        if missing_terms:
                            print(f"\n   📋 缺失条款示例:")
                            for i, item in enumerate(missing_terms[:2], 1):
                                if isinstance(item, dict):
                                    term = item.get('term', item.get('reason', str(item)))
                                    print(f"      {i}. {term}")
                                else:
                                    print(f"      {i}. {item}")
                        
                        if suggestions:
                            print(f"\n   💡 建议修改示例:")
                            for i, item in enumerate(suggestions[:2], 1):
                                if isinstance(item, dict):
                                    reason = item.get('reason', item.get('suggestion', str(item)))
                                    print(f"      {i}. {reason}")
                                else:
                                    print(f"      {i}. {item}")
                        
                        # 验证OCR结果
                        ocr_result = contract_data.get('ocr_result', {})
                        if ocr_result:
                            ocr_text = ocr_result.get('text', '')
                            if ocr_text:
                                print(f"\n   ✅ OCR识别成功，文本长度: {len(ocr_text)} 字符")
                                print(f"   OCR文本预览: {ocr_text[:100]}...")
                            else:
                                print(f"\n   ⚠️  OCR结果为空")
                        else:
                            print(f"\n   ⚠️  未找到OCR结果")
                        
                        # 验证AI分析结果
                        result_json = contract_data.get('result_json', {})
                        if result_json:
                            print(f"\n   ✅ AI审核结果已保存")
                        else:
                            print(f"\n   ⚠️  未找到AI审核结果JSON")
                        
                        print(f"\n✅ 合同审核端到端测试通过！")
                        return True
                    elif current_status == "failed":
                        print(f"\n   ❌ 审核失败")
                        error_msg = contract_data.get('error_message', '未知错误')
                        print(f"   错误信息: {error_msg}")
                        return False
                elif response.status_code == 404:
                    print(f"   ⚠️  合同不存在 (404)")
                    return False
                else:
                    # 忽略查询错误，继续等待
                    pass
            except Exception as e:
                # 忽略查询异常，继续等待
                pass
        
        print(f"\n⏰ 等待超时（{max_wait}秒），审核可能仍在进行中")
        print(f"   最终状态: {last_status}")
        return False
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("完整的端到端测试：报价单分析和合同审核")
    print("=" * 70)
    print("\n测试流程:")
    print("1. 文件上传 → OCR识别 → AI分析 → 结果验证")
    print("2. 验证所有关键步骤和数据完整性")
    print("=" * 70)
    
    # 登录
    token = login()
    if not token:
        print("\n❌ 无法继续测试：登录失败")
        return
    
    # 测试报价单分析
    quote_result = test_quote_e2e(token)
    
    # 测试合同审核
    contract_result = test_contract_e2e(token)
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("端到端测试结果汇总")
    print("=" * 70)
    print(f"报价单分析完整流程: {'✅ 通过' if quote_result else '❌ 失败'}")
    print(f"合同审核完整流程: {'✅ 通过' if contract_result else '❌ 失败'}")
    
    if quote_result and contract_result:
        print("\n🎉 所有端到端测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查日志")
    
    print("=" * 70)


if __name__ == "__main__":
    main()

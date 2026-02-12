#!/usr/bin/env python3
"""
测试装修报价分析功能和装修合同审核功能
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
import base64
from typing import Dict, Optional

BASE_URL = "http://localhost:8000/api/v1"

# 测试用的OCR文本（模拟OCR识别结果）
MOCK_QUOTE_OCR_TEXT = """
装修报价单

项目名称：深圳住宅装修（89㎡三室一厅）
装修类型：半包装修
品质等级：中档品质

项目明细：
1. 水电改造工程
   - 强电改造：120元/米，共80米，合计：9600元
   - 弱电改造：80元/米，共50米，合计：4000元
   - 水路改造：150元/米，共60米，合计：9000元
   小计：22600元

2. 泥工工程
   - 地面找平：45元/㎡，共89㎡，合计：4005元
   - 墙砖铺贴：65元/㎡，共120㎡，合计：7800元
   - 地砖铺贴：55元/㎡，共89㎡，合计：4895元
   小计：16700元

3. 木工工程
   - 吊顶：120元/㎡，共60㎡，合计：7200元
   - 定制柜体：800元/延米，共15延米，合计：12000元
   小计：19200元

4. 油漆工程
   - 墙面乳胶漆：35元/㎡，共280㎡，合计：9800元
   - 木器漆：80元/㎡，共40㎡，合计：3200元
   小计：13000元

5. 其他费用
   - 垃圾清运费：2000元
   - 材料运输费：1500元
   - 管理费：5000元
   小计：8500元

总计：80000元

备注：以上价格不含主材，主材由业主自行采购。
"""

MOCK_CONTRACT_OCR_TEXT = """
深圳市住宅装饰装修工程施工合同

甲方（委托方）：张三
乙方（承包方）：深圳XX装饰工程有限公司

第一条 工程概况
1.1 工程地点：深圳市南山区XX小区XX栋XX室
1.2 工程内容：住宅室内装修
1.3 工程承包方式：半包
1.4 工程期限：90天

第二条 工程价款
2.1 工程总价款：80000元（人民币捌万元整）
2.2 付款方式：
   - 合同签订时支付30%：24000元
   - 水电验收后支付30%：24000元
   - 泥木验收后支付30%：24000元
   - 竣工验收后支付10%：8000元

第三条 材料供应
3.1 主材由甲方采购
3.2 辅材由乙方提供

第四条 工程质量
4.1 工程质量标准：符合国家相关标准
4.2 保修期：2年

第五条 违约责任
5.1 如乙方延期完工，每延期一天支付违约金500元
5.2 如甲方延期付款，每延期一天支付违约金500元

第六条 其他条款
6.1 本合同一式两份，甲乙双方各执一份
6.2 本合同自双方签字之日起生效

甲方签字：张三
乙方签字：XX装饰公司
日期：2026年1月1日
"""


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
            print(f"✅ 登录成功，Token: {token[:20]}...")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None


def test_quote_analysis(token: str) -> bool:
    """测试报价单分析功能"""
    print("\n" + "=" * 60)
    print("【测试1: 装修报价分析功能】")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 步骤1: 上传报价单文件（使用PNG图片）
    quote_png_path = fixture_path(QUOTE_PNG)
    if not os.path.exists(quote_png_path):
        print(f"⚠️  报价单文件不存在: {quote_png_path}")
        print("   使用模拟OCR文本进行测试...")
        # 如果文件不存在，我们无法测试完整流程，但可以测试AI分析部分
        return False
    
    print(f"📄 上传报价单文件: {quote_png_path}")
    try:
        with open(quote_png_path, "rb") as f:
            file_content = f.read()
        
        files = {"file": (os.path.basename(quote_png_path), io.BytesIO(file_content), "image/png")}
        response = requests.post(
            f"{BASE_URL}/quotes/upload",
            headers=headers,
            files=files
        )
        
        if response.status_code != 200:
            print(f"❌ 文件上传失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        
        data = response.json()
        quote_id = data.get("data", {}).get("task_id") or data.get("task_id")
        status = data.get("data", {}).get("status") or data.get("status")
        
        print(f"✅ 文件上传成功")
        print(f"   Quote ID: {quote_id}")
        print(f"   状态: {status}")
        
        # 步骤2: 等待分析完成（最多等待60秒）
        print(f"\n⏳ 等待AI分析完成（最多60秒）...")
        max_wait = 60
        wait_interval = 2
        waited = 0
        
        while waited < max_wait:
            time.sleep(wait_interval)
            waited += wait_interval
            
            response = requests.get(
                f"{BASE_URL}/quotes/quote/{quote_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                quote_data = result.get("data", {}) or result
                current_status = quote_data.get("status")
                
                print(f"   等待中... ({waited}秒) 当前状态: {current_status}")
                
                if current_status == "completed":
                    print(f"\n✅ 报价单分析完成！")
                    print(f"\n📊 分析结果:")
                    print(f"   风险评分: {quote_data.get('risk_score', 'N/A')}")
                    print(f"   总价: {quote_data.get('total_price', 'N/A')} 元")
                    print(f"   市场参考价: {quote_data.get('market_ref_price', 'N/A')} 元")
                    
                    high_risk = quote_data.get('high_risk_items', [])
                    if high_risk:
                        print(f"\n   ⚠️  高风险项目 ({len(high_risk)}项):")
                        for item in high_risk[:3]:  # 只显示前3项
                            print(f"      - {item}")
                    
                    warning = quote_data.get('warning_items', [])
                    if warning:
                        print(f"\n   ⚠️  警告项目 ({len(warning)}项):")
                        for item in warning[:3]:  # 只显示前3项
                            print(f"      - {item}")
                    
                    missing = quote_data.get('missing_items', [])
                    if missing:
                        print(f"\n   📋 缺失项目 ({len(missing)}项):")
                        for item in missing[:3]:  # 只显示前3项
                            print(f"      - {item}")
                    
                    overpriced = quote_data.get('overpriced_items', [])
                    if overpriced:
                        print(f"\n   💰 价格偏高项目 ({len(overpriced)}项):")
                        for item in overpriced[:3]:  # 只显示前3项
                            print(f"      - {item}")
                    
                    return True
                elif current_status == "failed":
                    print(f"\n❌ 报价单分析失败")
                    return False
            else:
                print(f"   ⚠️  查询状态失败: {response.status_code}")
        
        print(f"\n⏰ 等待超时（{max_wait}秒），分析可能仍在进行中")
        return False
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_contract_analysis(token: str) -> bool:
    """测试合同审核功能"""
    print("\n" + "=" * 60)
    print("【测试2: 装修合同审核功能】")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 步骤1: 上传合同文件（使用PNG图片）
    contract_png_path = fixture_path(CONTRACT_PNG)
    if not os.path.exists(contract_png_path):
        print(f"⚠️  合同文件不存在: {contract_png_path}")
        print("   使用模拟OCR文本进行测试...")
        return False
    
    print(f"📄 上传合同文件: {contract_png_path}")
    try:
        with open(contract_png_path, "rb") as f:
            file_content = f.read()
        
        files = {"file": (os.path.basename(contract_png_path), io.BytesIO(file_content), "image/png")}
        response = requests.post(
            f"{BASE_URL}/contracts/upload",
            headers=headers,
            files=files
        )
        
        if response.status_code != 200:
            print(f"❌ 文件上传失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        
        data = response.json()
        contract_id = data.get("data", {}).get("task_id") or data.get("task_id")
        status = data.get("data", {}).get("status") or data.get("status")
        
        print(f"✅ 文件上传成功")
        print(f"   Contract ID: {contract_id}")
        print(f"   状态: {status}")
        
        # 步骤2: 等待分析完成（最多等待60秒）
        print(f"\n⏳ 等待AI审核完成（最多60秒）...")
        max_wait = 60
        wait_interval = 2
        waited = 0
        
        while waited < max_wait:
            time.sleep(wait_interval)
            waited += wait_interval
            
            response = requests.get(
                f"{BASE_URL}/contracts/contract/{contract_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                contract_data = result.get("data", {}) or result
                current_status = contract_data.get("status")
                
                print(f"   等待中... ({waited}秒) 当前状态: {current_status}")
                
                if current_status == "completed":
                    print(f"\n✅ 合同审核完成！")
                    print(f"\n📊 审核结果:")
                    print(f"   风险等级: {contract_data.get('risk_level', 'N/A')}")
                    
                    risk_items = contract_data.get('risk_items', [])
                    if risk_items:
                        print(f"\n   ⚠️  风险条款 ({len(risk_items)}项):")
                        for item in risk_items[:3]:  # 只显示前3项
                            print(f"      - {item}")
                    
                    unfair = contract_data.get('unfair_terms', [])
                    if unfair:
                        print(f"\n   ⚠️  不公平条款 ({len(unfair)}项):")
                        for item in unfair[:3]:  # 只显示前3项
                            print(f"      - {item}")
                    
                    missing = contract_data.get('missing_terms', [])
                    if missing:
                        print(f"\n   📋 缺失条款 ({len(missing)}项):")
                        for item in missing[:3]:  # 只显示前3项
                            print(f"      - {item}")
                    
                    suggestions = contract_data.get('suggested_modifications', [])
                    if suggestions:
                        print(f"\n   💡 建议修改 ({len(suggestions)}项):")
                        for item in suggestions[:3]:  # 只显示前3项
                            print(f"      - {item}")
                    
                    return True
                elif current_status == "failed":
                    print(f"\n❌ 合同审核失败")
                    return False
            else:
                print(f"   ⚠️  查询状态失败: {response.status_code}")
        
        print(f"\n⏰ 等待超时（{max_wait}秒），审核可能仍在进行中")
        return False
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
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
    
    # 测试报价单分析
    quote_result = test_quote_analysis(token)
    
    # 测试合同审核
    contract_result = test_contract_analysis(token)
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"报价单分析功能: {'✅ 通过' if quote_result else '❌ 失败'}")
    print(f"合同审核功能: {'✅ 通过' if contract_result else '❌ 失败'}")
    print("=" * 60)


if __name__ == "__main__":
    main()

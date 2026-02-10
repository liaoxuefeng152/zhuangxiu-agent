#!/usr/bin/env python3
"""
绕过OCR直接测试AI分析功能
通过API创建测试记录，然后手动触发分析
"""
import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

# 模拟OCR识别的文本
MOCK_QUOTE_TEXT = """
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

MOCK_CONTRACT_TEXT = """
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


def create_test_quote_with_ocr(token, ocr_text):
    """创建测试报价单记录（绕过OCR）"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 直接调用数据库创建记录（需要后端支持）
    # 或者通过修改上传接口，允许传入OCR文本
    # 这里我们尝试通过修改后的接口
    
    # 方案：创建一个测试端点或修改现有接口
    # 由于无法修改后端代码，我们使用数据库直接插入的方式
    # 但更简单的方法是：创建一个临时的测试脚本，直接调用后台分析函数
    
    print("⚠️  无法直接创建测试记录，需要后端支持")
    print("   建议：创建一个测试端点或修改上传接口以支持模拟OCR文本")
    return None


def test_analysis_via_backend_api():
    """通过后端API测试分析功能"""
    print("=" * 60)
    print("AI分析功能测试（需要后端支持测试端点）")
    print("=" * 60)
    print("\n由于OCR失败，建议的解决方案：")
    print("1. 修复OCR Access Key（推荐）")
    print("2. 创建测试端点，允许直接传入OCR文本进行测试")
    print("3. 在数据库中手动创建测试记录")
    print("\n当前无法绕过OCR限制进行完整测试。")
    return False


def main():
    """主函数"""
    print("=" * 60)
    print("绕过OCR测试AI分析功能")
    print("=" * 60)
    
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    
    print("✅ 登录成功")
    
    # 由于无法直接创建测试记录，我们提供建议
    print("\n💡 解决方案：")
    print("   由于OCR Access Key无效，建议：")
    print("   1. 更新.env中的ALIYUN_ACCESS_KEY_ID和ALIYUN_ACCESS_KEY_SECRET")
    print("   2. 或者创建后端测试端点，允许直接传入OCR文本")
    print("   3. 或者手动在数据库中创建测试记录")
    
    # 尝试运行完整的测试流程（即使OCR失败，看看是否有其他错误）
    print("\n" + "=" * 60)
    print("尝试完整流程测试（即使OCR失败）")
    print("=" * 60)
    
    from test_analysis_functions import test_quote_analysis, test_contract_analysis
    
    try:
        quote_result = test_quote_analysis(token)
        contract_result = test_contract_analysis(token)
        
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        print(f"报价单分析功能: {'✅ 通过' if quote_result else '❌ 失败'}")
        print(f"合同审核功能: {'✅ 通过' if contract_result else '❌ 失败'}")
    except Exception as e:
        print(f"测试异常: {e}")


if __name__ == "__main__":
    # 直接运行完整测试
    import subprocess
    print("运行完整测试流程...")
    result = subprocess.run(
        ["python", "test-analysis-functions.py"],
        cwd="/Users/mac/zhuangxiu-agent-backup",
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("错误:", result.stderr)

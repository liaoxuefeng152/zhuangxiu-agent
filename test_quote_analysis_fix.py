#!/usr/bin/env python3
"""
测试报价单分析功能修复
"""

import sys
import os
import json
import requests
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试生产环境API
BASE_URL = "http://120.26.201.61:8000"
API_BASE_URL = f"{BASE_URL}/api/v1"

def test_health():
    """测试健康检查"""
    print("=== 测试健康检查 ===")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_quote_analysis():
    """测试报价单分析功能"""
    print("\n=== 测试报价单分析功能 ===")
    
    # 创建一个测试报价单数据
    test_quote_data = {
        "company_name": "测试装修公司",
        "total_amount": 150000.0,
        "items": [
            {
                "name": "水电改造",
                "quantity": 1,
                "unit": "项",
                "unit_price": 30000.0,
                "total_price": 30000.0,
                "description": "全屋水电改造"
            },
            {
                "name": "墙面处理",
                "quantity": 120,
                "unit": "平方米",
                "unit_price": 80.0,
                "total_price": 9600.0,
                "description": "墙面刮腻子刷漆"
            },
            {
                "name": "地板铺设",
                "quantity": 80,
                "unit": "平方米",
                "unit_price": 200.0,
                "total_price": 16000.0,
                "description": "实木复合地板"
            }
        ],
        "analysis_type": "quote"
    }
    
    try:
        print(f"发送报价单分析请求到: {API_BASE_URL}/quotes/analyze")
        print(f"测试数据: {json.dumps(test_quote_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            f"{API_BASE_URL}/quotes/analyze",
            json=test_quote_data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"分析成功!")
            print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 检查关键字段
            if "analysis" in result:
                analysis = result["analysis"]
                print(f"\n分析结果包含字段:")
                for key in analysis.keys():
                    print(f"  - {key}")
                
                # 检查是否有风险分析
                if "risk_analysis" in analysis:
                    print(f"\n风险分析: {analysis['risk_analysis']}")
                
                # 检查是否有建议
                if "suggestions" in analysis:
                    print(f"\n建议: {analysis['suggestions']}")
                
                return True
            else:
                print("响应中没有analysis字段")
                return False
        else:
            print(f"分析失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"报价单分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_contract_analysis():
    """测试合同分析功能"""
    print("\n=== 测试合同分析功能 ===")
    
    # 创建一个测试合同数据
    test_contract_data = {
        "company_name": "测试装修公司",
        "contract_content": """
        装修工程施工合同
        
        甲方（业主）：张三
        乙方（施工方）：测试装修公司
        
        第一条 工程概况
        1.1 工程名称：住宅装修工程
        1.2 工程地点：北京市朝阳区
        1.3 工程内容：全屋装修
        1.4 工程期限：60天
        
        第二条 工程造价
        2.1 工程总造价：人民币150,000元（大写：壹拾伍万元整）
        2.2 付款方式：合同签订后支付30%，工程过半支付40%，竣工验收后支付30%
        
        第三条 工程质量
        3.1 工程质量标准：符合国家相关标准
        3.2 保修期：工程竣工验收合格之日起24个月
        
        第四条 违约责任
        4.1 乙方逾期完工，每逾期一日按工程总造价的千分之五支付违约金
        4.2 甲方逾期付款，每逾期一日按应付未付款的千分之五支付违约金
        """,
        "analysis_type": "contract"
    }
    
    try:
        print(f"发送合同分析请求到: {API_BASE_URL}/contracts/analyze")
        
        response = requests.post(
            f"{API_BASE_URL}/contracts/analyze",
            json=test_contract_data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"分析成功!")
            print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 检查关键字段
            if "analysis" in result:
                analysis = result["analysis"]
                print(f"\n分析结果包含字段:")
                for key in analysis.keys():
                    print(f"  - {key}")
                
                # 检查是否有风险分析
                if "risk_analysis" in analysis:
                    print(f"\n风险分析: {analysis['risk_analysis']}")
                
                # 检查是否有建议
                if "suggestions" in analysis:
                    print(f"\n建议: {analysis['suggestions']}")
                
                return True
            else:
                print("响应中没有analysis字段")
                return False
        else:
            print(f"分析失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"合同分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试报价单和合同分析功能修复...")
    
    # 测试健康检查
    if not test_health():
        print("健康检查失败，无法继续测试")
        return False
    
    # 测试报价单分析
    quote_success = test_quote_analysis()
    
    # 测试合同分析
    contract_success = test_contract_analysis()
    
    # 总结
    print("\n=== 测试总结 ===")
    print(f"健康检查: {'通过' if True else '失败'}")
    print(f"报价单分析: {'通过' if quote_success else '失败'}")
    print(f"合同分析: {'通过' if contract_success else '失败'}")
    
    overall_success = quote_success and contract_success
    print(f"\n总体测试结果: {'通过' if overall_success else '失败'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

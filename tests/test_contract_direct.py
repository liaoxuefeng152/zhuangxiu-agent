#!/usr/bin/env python3
"""
直接测试合同分析功能
直接调用风险分析服务测试合同分析
"""
import os
import sys
import json
import asyncio

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))

def test_contract_analysis_direct():
    """直接测试合同分析功能"""
    print("=== 直接测试合同分析功能 ===")
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    
    try:
        from app.services.risk_analyzer import risk_analyzer_service
        
        # 创建模拟的合同文本
        contract_text = """
装修工程施工合同

甲方（业主）：张三
乙方（装修公司）：某某装饰有限公司

第一条 工程概况
1.1 工程名称：住宅装修工程
1.2 工程地点：深圳市南山区
1.3 工程内容：全屋装修
1.4 承包方式：半包
1.5 工程期限：60天

第二条 工程造价
2.1 工程总造价：人民币80000元（大写：捌万元整）
2.2 付款方式：
  第一期：合同签订后支付50%即40000元
  第二期：水电工程完成后支付30%即24000元
  第三期：工程竣工验收后支付20%即16000元

第三条 工程质量
3.1 工程质量标准：符合国家相关标准
3.2 隐蔽工程验收：乙方应提前通知甲方验收

第四条 违约责任
4.1 乙方逾期完工，每逾期一天支付违约金100元
4.2 甲方逾期付款，每逾期一天支付违约金100元

第五条 保修条款
5.1 工程保修期为2年
5.2 保修范围：施工质量问题

第六条 其他
6.1 本合同一式两份，甲乙双方各执一份
6.2 本合同自双方签字盖章之日起生效

甲方签字：张三
乙方签字：某某装饰有限公司
日期：2026年2月19日
"""
        
        # 直接调用风险分析服务
        print("\n直接调用风险分析服务...")
        
        async def analyze():
            return await risk_analyzer_service.analyze_contract(contract_text)
        
        result = asyncio.run(analyze())
        
        print("\n合同分析结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 检查是否返回了兜底结果
        summary = result.get("summary", "")
        if "AI分析服务暂时不可用" in summary:
            print("\n⚠️  合同分析返回了兜底结果，服务可能不可用")
            return False
            
        print(f"\n✅ 合同分析成功，风险等级: {result.get('risk_level', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"直接调用风险分析服务异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("装修合同AI分析功能直接测试")
    print("=" * 50)
    
    # 测试合同分析
    success = test_contract_analysis_direct()
    
    if success:
        print("\n✅ 合同分析功能测试通过")
    else:
        print("\n❌ 合同分析功能测试失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

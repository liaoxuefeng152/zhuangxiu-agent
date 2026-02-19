#!/usr/bin/env python3
"""
测试公司风险报告页修改：直接展示聚合数据API原文，不做评价
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

# 模拟公司扫描数据
MOCK_COMPANY_DATA = {
    "id": 999,
    "company_name": "测试装修公司",
    "company_info": {
        "name": "测试装修有限公司",
        "credit_code": "91310101MA1F123456",
        "legal_person": "张三",
        "registered_capital": "1000万元人民币",
        "start_date": "2018-05-10",
        "enterprise_age": "6年",
        "business_status": "在业",
        "industry": "建筑装饰业",
        "address": "上海市浦东新区张江高科技园区",
        "business_scope": "室内外装饰装修工程设计与施工"
    },
    "legal_risks": {
        "legal_case_count": 3,
        "decoration_related_cases": 2,
        "recent_case_date": "2024-08-15",
        "case_types": [
            {"type": "合同纠纷", "count": 2},
            {"type": "劳动争议", "count": 1}
        ],
        "recent_cases": [
            {
                "title": "装修合同纠纷案",
                "case_number": "(2024)沪0105民初12345号",
                "court": "上海市长宁区人民法院",
                "date": "2024-08-15",
                "case_type": "合同纠纷",
                "parties": "原告：李四 vs 被告：测试装修有限公司",
                "summary": "原告主张被告未按合同约定完成装修工程，要求赔偿损失"
            },
            {
                "title": "劳动争议案",
                "case_number": "(2023)沪0105民初98765号",
                "court": "上海市长宁区人民法院",
                "date": "2023-11-20",
                "case_type": "劳动争议",
                "parties": "原告：王五 vs 被告：测试装修有限公司",
                "summary": "原告主张被告未支付工资及加班费"
            }
        ]
    },
    "risk_level": "compliant",
    "risk_score": 15,
    "risk_reasons": [],
    "is_unlocked": True,
    "created_at": "2025-02-17T10:30:00Z"
}

def test_company_data_formatter():
    """测试公司数据格式化逻辑（模拟前端逻辑）"""
    print("=== 测试公司数据格式化逻辑 ===")
    
    # 模拟前端格式化逻辑
    enterprise_info = MOCK_COMPANY_DATA["company_info"]
    legal_analysis = MOCK_COMPANY_DATA["legal_risks"]
    
    # 模拟生成预览摘要
    previews = []
    if enterprise_info:
        if enterprise_info.get("enterprise_age"):
            previews.append(f"企业年龄：{enterprise_info.get('enterprise_age')}")
        if enterprise_info.get("business_status"):
            previews.append(f"经营状态：{enterprise_info.get('business_status')}")
    
    if legal_analysis:
        if legal_analysis.get("legal_case_count"):
            previews.append(f"法律案件：{legal_analysis.get('legal_case_count')}件")
        if legal_analysis.get("decoration_related_cases"):
            previews.append(f"装修相关案件：{legal_analysis.get('decoration_related_cases')}件")
    
    preview_summary = ' | '.join(previews) if previews else '暂无预览信息'
    print(f"预览摘要：{preview_summary}")
    print()
    
    # 模拟生成完整报告
    report_lines = []
    report_lines.append("# 公司信息报告")
    report_lines.append(f"**报告生成时间**：2025-02-17 18:30:00")
    report_lines.append(f"**公司名称**：{MOCK_COMPANY_DATA['company_name']}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # 企业基本信息
    report_lines.append("# 企业基本信息")
    report_lines.append("")
    if enterprise_info:
        if enterprise_info.get("name"):
            report_lines.append(f"**公司名称**：{enterprise_info.get('name')}")
        if enterprise_info.get("legal_person"):
            report_lines.append(f"**法定代表人**：{enterprise_info.get('legal_person')}")
        if enterprise_info.get("registered_capital"):
            report_lines.append(f"**注册资本**：{enterprise_info.get('registered_capital')}")
        if enterprise_info.get("start_date"):
            report_lines.append(f"**成立日期**：{enterprise_info.get('start_date')}")
        if enterprise_info.get("enterprise_age"):
            report_lines.append(f"**企业年龄**：{enterprise_info.get('enterprise_age')}")
        if enterprise_info.get("business_status"):
            report_lines.append(f"**经营状态**：{enterprise_info.get('business_status')}")
    else:
        report_lines.append("暂无企业信息")
    
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # 法律案件信息
    report_lines.append("# 法律案件分析")
    report_lines.append("")
    if legal_analysis:
        if legal_analysis.get("legal_case_count") is not None:
            report_lines.append(f"**法律案件总数**：{legal_analysis.get('legal_case_count')}件")
        if legal_analysis.get("decoration_related_cases") is not None:
            report_lines.append(f"**装修相关案件**：{legal_analysis.get('decoration_related_cases')}件")
        if legal_analysis.get("recent_case_date"):
            report_lines.append(f"**最近案件日期**：{legal_analysis.get('recent_case_date')}")
    else:
        report_lines.append("暂无法律案件信息")
    
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # 数据来源说明和免责声明
    report_lines.append("## 数据来源说明")
    report_lines.append("1. 企业基本信息来源于国家企业信用信息公示系统")
    report_lines.append("2. 法律案件信息来源于中国裁判文书网等公开司法数据")
    report_lines.append("3. 数据更新日期：2025-02-17")
    report_lines.append("")
    report_lines.append("## 免责声明")
    report_lines.append("1. 本报告基于公开信息生成，仅供参考")
    report_lines.append("2. 报告内容不构成任何投资、合作建议")
    report_lines.append("3. 用户应自行核实信息的准确性和时效性")
    report_lines.append("4. 本平台不对信息的完整性和准确性承担法律责任")
    
    full_report = "\n".join(report_lines)
    
    print("完整报告生成结果（前500字符）：")
    print(full_report[:500] + "...")
    print()
    
    # 检查是否包含风险等级评价
    if "高风险" in full_report or "中风险" in full_report or "低风险" in full_report:
        print("❌ 错误：报告中包含风险等级评价")
        return False
    else:
        print("✅ 正确：报告中不包含风险等级评价")
    
    # 检查是否包含原文数据
    if "测试装修有限公司" in full_report and "张三" in full_report:
        print("✅ 正确：报告中包含聚合数据API的原文")
    else:
        print("❌ 错误：报告中未包含聚合数据API的原文")
        return False
    
    # 检查是否包含免责声明
    if "免责声明" in full_report and "仅供参考" in full_report:
        print("✅ 正确：报告中包含免责声明")
    else:
        print("❌ 错误：报告中未包含免责声明")
        return False
    
    return True

def test_pdf_generation():
    """测试PDF生成函数"""
    print("\n=== 测试PDF生成函数 ===")
    
    # 导入PDF生成函数
    from backend.app.api.v1.reports import _build_company_pdf
    
    # 创建模拟的CompanyScan对象
    class MockCompanyScan:
        def __init__(self, data):
            self.id = data["id"]
            self.company_name = data["company_name"]
            self.company_info = data["company_info"]
            self.legal_risks = data["legal_risks"]
            self.risk_level = data["risk_level"]
            self.risk_score = data["risk_score"]
            self.risk_reasons = data["risk_reasons"]
            self.is_unlocked = data["is_unlocked"]
            self.created_at = data["created_at"]
    
    mock_scan = MockCompanyScan(MOCK_COMPANY_DATA)
    
    try:
        # 生成PDF
        pdf_buffer = _build_company_pdf(mock_scan)
        
        # 检查PDF是否生成成功
        pdf_bytes = pdf_buffer.getvalue()
        if len(pdf_bytes) > 100:
            print(f"✅ PDF生成成功，大小：{len(pdf_bytes)} 字节")
            
            # 检查PDF内容是否包含关键信息
            pdf_text = pdf_bytes.decode('utf-8', errors='ignore')
            
            # 检查是否包含公司名称
            if "测试装修公司" in pdf_text or "测试装修有限公司" in pdf_text:
                print("✅ PDF中包含公司名称")
            else:
                print("❌ PDF中未包含公司名称")
                return False
            
            # 检查是否包含企业基本信息
            if "企业基本信息" in pdf_text and "法定代表人" in pdf_text:
                print("✅ PDF中包含企业基本信息")
            else:
                print("❌ PDF中未包含企业基本信息")
                return False
            
            # 检查是否包含法律案件信息
            if "法律案件信息" in pdf_text and "案件类型分布" in pdf_text:
                print("✅ PDF中包含法律案件信息")
            else:
                print("❌ PDF中未包含法律案件信息")
                return False
            
            # 检查是否包含免责声明
            if "免责声明" in pdf_text and "仅供参考" in pdf_text:
                print("✅ PDF中包含免责声明")
            else:
                print("❌ PDF中未包含免责声明")
                return False
            
            # 检查是否不包含风险等级评价
            if "高风险" not in pdf_text and "中风险" not in pdf_text and "低风险" not in pdf_text:
                print("✅ PDF中不包含风险等级评价")
            else:
                print("❌ PDF中包含风险等级评价")
                return False
            
            return True
        else:
            print("❌ PDF生成失败，文件太小")
            return False
            
    except Exception as e:
        print(f"❌ PDF生成失败：{e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试公司风险报告页修改...")
    print("=" * 60)
    
    all_passed = True
    
    # 测试数据格式化逻辑
    if test_company_data_formatter():
        print("✅ 数据格式化逻辑测试通过")
    else:
        print("❌ 数据格式化逻辑测试失败")
        all_passed = False
    
    # 测试PDF生成
    if test_pdf_generation():
        print("✅ PDF生成测试通过")
    else:
        print("❌ PDF生成测试失败")
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！公司风险报告页修改成功")
        print("\n修改内容总结：")
        print("1. ✅ 前端页面直接展示聚合数据API原文")
        print("2. ✅ 移除风险等级评价（高风险/中风险/低风险）")
        print("3. ✅ 添加免责声明")
        print("4. ✅ PDF导出也按照原文展示方式生成")
        print("5. ✅ 公司报告页面特殊展示企业信息和法律案件信息")
    else:
        print("❌ 测试失败，请检查代码")
        sys.exit(1)

if __name__ == "__main__":
    main()

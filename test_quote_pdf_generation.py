#!/usr/bin/env python3
"""
测试报价单PDF生成功能
"""
import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from io import BytesIO
from datetime import datetime

# 模拟一个报价单对象
class MockQuote:
    def __init__(self):
        self.id = 123
        self.file_name = "测试报价单.pdf"
        self.created_at = datetime.now()
        self.risk_score = 75
        self.total_price = 85000
        self.market_ref_price = 75000
        self.is_unlocked = True
        self.status = "completed"
        
        # 模拟扣子智能体返回的数据
        self.result_json = {
            "risk_score": 75,
            "total_price": 85000,
            "market_ref_price": "75000-85000元",
            "high_risk_items": [
                {"name": "水电改造", "reason": "价格虚高30%", "impact": "可能多收3000元"},
                {"name": "墙面处理", "reason": "工艺描述模糊", "impact": "后期可能加价"}
            ],
            "warning_items": [
                {"item": "地板安装", "description": "辅材未明确品牌"},
                {"item": "油漆工程", "description": "涂刷遍数未注明"}
            ],
            "missing_items": [
                {"name": "垃圾清运费", "importance": "高", "suggestion": "需明确包含在总价内"},
                {"name": "成品保护", "importance": "中", "suggestion": "应包含保护膜费用"}
            ],
            "overpriced_items": [
                {"name": "瓷砖铺贴", "current_price": 120, "market_price": 85, "reason": "单价偏高40%"},
                {"name": "吊顶工程", "current_price": 180, "market_price": 135, "reason": "单价偏高33%"}
            ],
            "suggestions": [
                "建议与装修公司协商降低水电改造单价",
                "要求明确墙面处理的具体工艺和材料",
                "补充垃圾清运费和成品保护费用",
                "对比市场价重新议价瓷砖和吊顶工程"
            ]
        }
        self.high_risk_items = self.result_json["high_risk_items"]
        self.warning_items = self.result_json["warning_items"]
        self.missing_items = self.result_json["missing_items"]
        self.overpriced_items = self.result_json["overpriced_items"]

def test_quote_pdf_generation():
    """测试报价单PDF生成"""
    print("测试报价单PDF生成...")
    
    try:
        # 导入实际的PDF生成函数
        from backend.app.api.v1.reports import _build_quote_pdf, _ensure_cjk_font
        
        # 测试字体注册
        print("测试中文字体注册...")
        font_name = _ensure_cjk_font()
        print(f"✓ 使用的字体: {font_name}")
        
        # 创建模拟报价单
        quote = MockQuote()
        
        # 生成PDF
        print("生成报价单PDF...")
        buf = _build_quote_pdf(quote)
        
        # 检查结果
        pdf_bytes = buf.getvalue()
        print(f"✓ PDF生成成功，大小: {len(pdf_bytes)} 字节")
        
        # 保存文件
        output_file = "test_real_quote_pdf.pdf"
        with open(output_file, "wb") as f:
            f.write(pdf_bytes)
        print(f"✓ PDF已保存为 {output_file}")
        
        # 检查内容
        pdf_text = pdf_bytes.decode('latin-1', errors='ignore')
        
        # 检查是否包含关键信息
        checks = [
            ("报价单分析报告", "标题"),
            ("测试报价单.pdf", "文件名"),
            ("75", "风险评分"),
            ("85000", "总价"),
            ("高风险项", "风险项标题"),
            ("水电改造", "高风险项目"),
            ("建议", "建议部分")
        ]
        
        print("\n检查PDF内容:")
        all_passed = True
        for text, description in checks:
            if text in pdf_text:
                print(f"  ✓ 包含{description}: {text}")
            else:
                print(f"  ✗ 缺少{description}: {text}")
                all_passed = False
        
        if all_passed:
            print("\n✅ 报价单PDF生成测试通过")
        else:
            print("\n⚠ 报价单PDF生成测试部分失败")
            
        return all_passed
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("报价单PDF生成功能测试")
    print("=" * 60)
    
    success = test_quote_pdf_generation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试完成 - 报价单PDF生成功能正常")
    else:
        print("❌ 测试失败 - 报价单PDF生成功能有问题")
    print("=" * 60)

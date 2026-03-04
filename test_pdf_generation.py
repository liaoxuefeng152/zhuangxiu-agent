#!/usr/bin/env python3
"""
测试PDF报告生成功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

def test_basic_pdf():
    """测试基本的PDF生成功能"""
    print("测试基本PDF生成...")
    
    try:
        # 创建一个简单的PDF
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, 
                               rightMargin=2*cm, leftMargin=2*cm, 
                               topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        
        story = [
            Paragraph("测试报价单分析报告", styles["Title"]),
            Spacer(1, 0.5*cm),
            Paragraph("文件名：test_quote.pdf", styles["Normal"]),
            Paragraph("生成时间：2026-03-05 03:30:00", styles["Normal"]),
            Paragraph("报告编号：R-Q-123", styles["Normal"]),
            Spacer(1, 0.5*cm),
            Paragraph("风险评分：75分", styles["Normal"]),
            Paragraph("总价：85000元", styles["Normal"]),
            Paragraph("市场参考价：75000-85000元", styles["Normal"]),
        ]
        
        doc.build(story)
        buf.seek(0)
        
        # 检查PDF内容
        pdf_bytes = buf.getvalue()
        print(f"✓ PDF生成成功，大小: {len(pdf_bytes)} 字节")
        
        # 保存测试文件
        with open("test_generated.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("✓ 测试PDF已保存为 test_generated.pdf")
        
        # 检查是否包含中文字符
        if "报价单" in pdf_bytes.decode('latin-1', errors='ignore'):
            print("✓ PDF包含中文字符")
        else:
            print("⚠ PDF可能不包含中文字符（字体问题）")
            
        return True
        
    except Exception as e:
        print(f"✗ PDF生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reportlab_fonts():
    """测试ReportLab字体支持"""
    print("\n测试ReportLab字体支持...")
    
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # 检查可用字体
        print("可用字体:")
        for font_name in pdfmetrics.getRegisteredFontNames():
            print(f"  - {font_name}")
            
        # 尝试注册中文字体
        cjk_font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/System/Library/Fonts/STHeiti Light.ttc",  # macOS
        ]
        
        for font_path in cjk_font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont("CJKTest", font_path))
                    print(f"✓ 成功注册字体: {font_path}")
                    break
                except Exception as e:
                    print(f"✗ 注册字体失败 {font_path}: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ 字体测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PDF报告生成测试")
    print("=" * 60)
    
    # 测试字体支持
    test_reportlab_fonts()
    
    # 测试PDF生成
    success = test_basic_pdf()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试完成 - PDF生成功能正常")
    else:
        print("❌ 测试失败 - PDF生成功能有问题")
    print("=" * 60)

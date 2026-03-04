#!/usr/bin/env python3
"""
修复PDF字体问题
"""
import os
import sys
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

logger = logging.getLogger(__name__)

def fix_cjk_font():
    """修复中文字体问题"""
    print("修复中文字体问题...")
    
    try:
        # 检查当前已注册的字体
        print("当前已注册字体:")
        for font_name in pdfmetrics.getRegisteredFontNames():
            print(f"  - {font_name}")
        
        # macOS系统字体路径
        mac_fonts = [
            "/System/Library/Fonts/PingFang.ttc",  # 苹方字体
            "/System/Library/Fonts/STHeiti Light.ttc",  # 黑体
            "/System/Library/Fonts/STHeiti Medium.ttc",  # 黑体中号
            "/System/Library/Fonts/Hiragino Sans GB.ttc",  # 冬青黑体
        ]
        
        # Linux字体路径（Docker环境）
        linux_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # 文泉驿正黑
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 文泉驿微米黑
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Noto字体
        ]
        
        # 尝试所有字体路径
        all_fonts = mac_fonts + linux_fonts
        
        for font_path in all_fonts:
            if os.path.exists(font_path):
                try:
                    # 尝试注册字体
                    font_name = "CJKFont"
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"✓ 成功注册字体: {font_path} 作为 '{font_name}'")
                    
                    # 测试字体是否可用
                    from reportlab.pdfgen import canvas
                    buf = BytesIO()
                    c = canvas.Canvas(buf, pagesize=A4)
                    c.setFont(font_name, 12)
                    c.drawString(100, 700, "测试中文字体：报价单分析报告")
                    c.save()
                    
                    print(f"✓ 字体测试成功: 可以绘制中文字符")
                    return font_name
                    
                except Exception as e:
                    print(f"✗ 注册字体失败 {font_path}: {e}")
        
        print("⚠ 未能注册任何中文字体，使用默认字体")
        return "Helvetica"
        
    except Exception as e:
        print(f"✗ 字体修复失败: {e}")
        import traceback
        traceback.print_exc()
        return "Helvetica"

def create_test_pdf_with_fixed_font():
    """使用修复后的字体创建测试PDF"""
    print("\n创建测试PDF...")
    
    try:
        # 修复字体
        font_name = fix_cjk_font()
        
        # 创建PDF
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, 
                               rightMargin=2*cm, leftMargin=2*cm, 
                               topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        
        # 创建使用中文字体的样式
        cjk_title_style = ParagraphStyle(
            name="CJKTitle",
            parent=styles["Title"],
            fontName=font_name,
            fontSize=20,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=HexColor("#2c3e50")
        )
        
        cjk_normal_style = ParagraphStyle(
            name="CJKNormal",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=12,
            spaceAfter=6
        )
        
        cjk_heading_style = ParagraphStyle(
            name="CJKHeading",
            parent=styles["Heading2"],
            fontName=font_name,
            fontSize=14,
            spaceAfter=8,
            textColor=HexColor("#3498db")
        )
        
        # 添加样式
        styles.add(cjk_title_style)
        styles.add(cjk_normal_style)
        styles.add(cjk_heading_style)
        
        # 创建内容
        story = []
        
        # 标题
        story.append(Paragraph("报价单分析报告", cjk_title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 基本信息
        story.append(Paragraph(f"文件名：测试报价单.pdf", cjk_normal_style))
        story.append(Paragraph(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", cjk_normal_style))
        story.append(Paragraph(f"报告编号：R-Q-123", cjk_normal_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 风险摘要
        story.append(Paragraph("风险摘要", cjk_heading_style))
        story.append(Paragraph("风险评分：75分", cjk_normal_style))
        story.append(Paragraph("总价：85000元", cjk_normal_style))
        story.append(Paragraph("市场参考价：75000-85000元", cjk_normal_style))
        story.append(Spacer(1, 0.3*cm))
        
        # 高风险项
        story.append(Paragraph("高风险项 (2个)", cjk_heading_style))
        story.append(Paragraph("• 水电改造：价格虚高30%（影响：可能多收3000元）", cjk_normal_style))
        story.append(Paragraph("• 墙面处理：工艺描述模糊（影响：后期可能加价）", cjk_normal_style))
        story.append(Spacer(1, 0.3*cm))
        
        # 建议
        story.append(Paragraph("建议", cjk_heading_style))
        story.append(Paragraph("1. 建议与装修公司协商降低水电改造单价", cjk_normal_style))
        story.append(Paragraph("2. 要求明确墙面处理的具体工艺和材料", cjk_normal_style))
        story.append(Paragraph("3. 补充垃圾清运费和成品保护费用", cjk_normal_style))
        
        # 生成PDF
        doc.build(story)
        buf.seek(0)
        
        # 检查结果
        pdf_bytes = buf.getvalue()
        print(f"✓ PDF生成成功，大小: {len(pdf_bytes)} 字节")
        
        # 保存文件
        output_file = "fixed_chinese_pdf.pdf"
        with open(output_file, "wb") as f:
            f.write(pdf_bytes)
        print(f"✓ PDF已保存为 {output_file}")
        
        # 检查内容
        pdf_text = pdf_bytes.decode('latin-1', errors='ignore')
        
        # 检查是否包含中文字符
        chinese_chars = ["报价单", "风险", "水电", "建议", "墙面", "工艺"]
        found_chars = []
        
        print("\n检查中文字符:")
        for char in chinese_chars:
            if char in pdf_text:
                print(f"  ✓ 包含: {char}")
                found_chars.append(char)
            else:
                print(f"  ✗ 缺少: {char}")
        
        if len(found_chars) >= 3:
            print(f"\n✅ 成功生成包含中文的PDF（找到 {len(found_chars)}/{len(chinese_chars)} 个中文字符）")
            
            # 显示PDF信息
            print(f"\nPDF文件信息:")
            print(f"  大小: {len(pdf_bytes)} 字节")
            print(f"  字体: {font_name}")
            
            return True
        else:
            print(f"\n⚠ PDF可能不包含中文字符（字体问题）")
            
            # 显示PDF原始内容（前500字符）
            print(f"\nPDF原始内容预览（前500字符）:")
            print(pdf_text[:500])
            
            return False
            
    except Exception as e:
        print(f"✗ 创建PDF失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_chinese():
    """简单测试中文字体"""
    print("\n简单测试中文字体...")
    
    try:
        from reportlab.pdfgen import canvas
        
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        
        # 使用Helvetica字体（不支持中文）
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "Helvetica: 报价单分析报告")
        
        # 尝试使用注册的中文字体
        try:
            c.setFont("CJKFont", 12)
            c.drawString(100, 730, "CJKFont: 报价单分析报告")
        except:
            pass
            
        # 使用Symbol字体（肯定不支持中文）
        c.setFont("Symbol", 12)
        c.drawString(100, 710, "Symbol: 报价单分析报告")
        
        c.save()
        buf.seek(0)
        
        pdf_bytes = buf.getvalue()
        pdf_text = pdf_bytes.decode('latin-1', errors='ignore')
        
        print("PDF内容预览:")
        print(pdf_text[:300])
        
        return True
        
    except Exception as e:
        print(f"✗ 简单测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PDF字体问题修复")
    print("=" * 60)
    
    # 简单测试
    test_simple_chinese()
    
    # 修复字体并创建PDF
    success = create_test_pdf_with_fixed_font()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 修复成功 - PDF中文支持已修复")
        print("   修复方案:")
        print("   1. 确保正确注册中文字体")
        print("   2. 创建使用中文字体的ParagraphStyle")
        print("   3. 直接使用Paragraph而不是_safe_paragraph")
    else:
        print("❌ 修复失败 - 需要进一步调试")
    print("=" * 60)

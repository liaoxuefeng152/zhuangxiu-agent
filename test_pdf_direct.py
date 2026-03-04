#!/usr/bin/env python3
"""
直接测试PDF生成函数，避免数据库依赖
"""
import sys
import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor
import logging

logger = logging.getLogger(__name__)

# 复制 _ensure_cjk_font 函数
_CJK_FONT_REGISTERED = None
_CJK_FONT_PATHS = [
    # 文泉驿（优先，TTC 无需 subfontIndex）
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    # Noto（备选，需 subfontIndex=3 表示简体中文）
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]

def _ensure_cjk_font():
    """注册一个支持中文的字体，用于 PDF 导出"""
    global _CJK_FONT_REGISTERED
    if _CJK_FONT_REGISTERED is not None:
        return _CJK_FONT_REGISTERED
    
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # 1. 文泉驿字体（不需要 subfontIndex）
        wqy_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        ]
        for path in wqy_fonts:
            if os.path.isfile(path):
                try:
                    pdfmetrics.registerFont(TTFont("CJK", path))
                    _CJK_FONT_REGISTERED = "CJK"
                    logger.info("ReportLab CJK font registered: %s", path)
                    return "CJK"
                except Exception as e:
                    logger.debug("Failed to register WQY font %s: %s", path, e)
                    continue
        
        # 2. 如果文泉驿失败，尝试 Noto CJK（subfontIndex: 0=TC, 1=JP, 2=KR, 3=SC）
        for path in _CJK_FONT_PATHS:
            if os.path.isfile(path):
                try:
                    kw = {}
                    if "noto" in path.lower() and path.lower().endswith(".ttc"):
                        kw["subfontIndex"] = 3  # 3=Simplified Chinese (SC)
                    pdfmetrics.registerFont(TTFont("CJK", path, **kw))
                    _CJK_FONT_REGISTERED = "CJK"
                    logger.info("ReportLab CJK font registered: %s", path)
                    return "CJK"
                except Exception as e:
                    logger.debug("Failed to register font %s: %s", path, e)
                    continue
                    
    except Exception as e:
        logger.warning("ReportLab CJK font registration failed: %s", e)
    
    _CJK_FONT_REGISTERED = "Helvetica"
    return "Helvetica"

def _safe_paragraph(text: str, styles, style_name: str = "Normal"):
    """若当前样式字体不支持中文，则用 ASCII 占位避免崩溃"""
    s = styles[style_name]
    try:
        return Paragraph(text, s)
    except Exception:
        # 降级：仅保留 ASCII
        safe = "".join(c if ord(c) < 128 else "?" for c in (str(text or "")[:2000]))
        return Paragraph(safe or "-", s)

def _safe_strftime(dt, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """安全格式化时间"""
    if dt is None:
        return "-"
    try:
        return dt.strftime(fmt)
    except Exception:
        return str(dt)[:19] if dt else "-"

def test_pdf_with_chinese():
    """测试包含中文的PDF生成"""
    print("测试包含中文的PDF生成...")
    
    try:
        # 创建PDF
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, 
                               rightMargin=2*cm, leftMargin=2*cm, 
                               topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        
        # 注册中文字体
        font = _ensure_cjk_font()
        print(f"使用的字体: {font}")
        
        # 设置字体
        for name in ("Title", "Normal", "Heading2"):
            if name in styles:
                styles[name].fontName = font
        
        # 创建内容
        story = []
        
        # 标题
        story.append(_safe_paragraph("报价单分析报告", styles, "Title"))
        story.append(Spacer(1, 0.5*cm))
        
        # 基本信息
        story.append(_safe_paragraph(f"文件名：测试报价单.pdf", styles))
        story.append(_safe_paragraph(f"生成时间：{_safe_strftime(datetime.now())}", styles))
        story.append(_safe_paragraph(f"报告编号：R-Q-123", styles))
        story.append(Spacer(1, 0.5*cm))
        
        # 风险摘要
        story.append(_safe_paragraph("风险摘要", styles, "Heading2"))
        story.append(_safe_paragraph("风险评分：75分", styles))
        story.append(_safe_paragraph("总价：85000元", styles))
        story.append(_safe_paragraph("市场参考价：75000-85000元", styles))
        story.append(Spacer(1, 0.3*cm))
        
        # 高风险项
        story.append(_safe_paragraph("高风险项 (2个)", styles, "Heading2"))
        story.append(_safe_paragraph("• 水电改造：价格虚高30%（影响：可能多收3000元）", styles))
        story.append(_safe_paragraph("• 墙面处理：工艺描述模糊（影响：后期可能加价）", styles))
        story.append(Spacer(1, 0.3*cm))
        
        # 建议
        story.append(_safe_paragraph("建议", styles, "Heading2"))
        story.append(_safe_paragraph("1. 建议与装修公司协商降低水电改造单价", styles))
        story.append(_safe_paragraph("2. 要求明确墙面处理的具体工艺和材料", styles))
        
        # 生成PDF
        doc.build(story)
        buf.seek(0)
        
        # 检查结果
        pdf_bytes = buf.getvalue()
        print(f"✓ PDF生成成功，大小: {len(pdf_bytes)} 字节")
        
        # 保存文件
        output_file = "test_chinese_pdf.pdf"
        with open(output_file, "wb") as f:
            f.write(pdf_bytes)
        print(f"✓ PDF已保存为 {output_file}")
        
        # 检查内容
        pdf_text = pdf_bytes.decode('latin-1', errors='ignore')
        
        # 检查是否包含中文字符
        chinese_chars = ["报价单", "风险", "水电", "建议"]
        found_chars = []
        
        print("\n检查中文字符:")
        for char in chinese_chars:
            if char in pdf_text:
                print(f"  ✓ 包含: {char}")
                found_chars.append(char)
            else:
                print(f"  ✗ 缺少: {char}")
        
        if len(found_chars) >= 2:
            print(f"\n✅ 成功生成包含中文的PDF（找到 {len(found_chars)}/{len(chinese_chars)} 个中文字符）")
            return True
        else:
            print(f"\n⚠ PDF可能不包含中文字符（字体问题）")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_font_registration():
    """测试字体注册"""
    print("\n测试字体注册...")
    
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        print("当前已注册字体:")
        for font_name in pdfmetrics.getRegisteredFontNames():
            print(f"  - {font_name}")
        
        # 测试注册中文字体
        font_paths = [
            "/System/Library/Fonts/STHeiti Light.ttc",  # macOS
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont("TestCJK", path))
                    print(f"✓ 成功注册字体: {path}")
                    return True
                except Exception as e:
                    print(f"✗ 注册字体失败 {path}: {e}")
        
        print("⚠ 未能注册任何中文字体")
        return False
        
    except Exception as e:
        print(f"✗ 字体测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PDF中文支持测试")
    print("=" * 60)
    
    # 测试字体注册
    font_ok = test_font_registration()
    
    # 测试PDF生成
    pdf_ok = test_pdf_with_chinese()
    
    print("\n" + "=" * 60)
    if pdf_ok:
        print("✅ 测试完成 - PDF中文支持正常")
    else:
        print("❌ 测试失败 - PDF中文支持有问题")
        if not font_ok:
            print("   原因：中文字体注册失败")
    print("=" * 60)

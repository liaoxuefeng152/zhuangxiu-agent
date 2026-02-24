"""
装修决策Agent - 报告PDF导出API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import CompanyScan, Quote, Contract, AcceptanceAnalysis, User
from app.schemas import ApiResponse

router = APIRouter(prefix="/reports", tags=["报告导出"])
logger = logging.getLogger(__name__)

STAGE_NAMES = {
    "S00": "材料进场", "S01": "隐蔽工程", "S02": "泥瓦工", "S03": "木工", "S04": "油漆", "S05": "安装收尾",
    "material": "材料进场", "plumbing": "水电", "carpentry": "泥瓦工", "woodwork": "木工",
    "painting": "油漆", "installation": "安装收尾", "flooring": "泥瓦工", "soft_furnishing": "安装收尾",
}
RESULT_STATUS_ZH = {"passed": "已通过", "need_rectify": "未通过", "pending_recheck": "待复检", "completed": "已完成", "failed": "未通过"}
SEVERITY_ZH = {"pass": "低风险", "high": "高风险", "warning": "中风险", "low": "低风险", "mid": "中风险"}

# 中文字体路径（Docker 已安装 fonts-wqy-zenhei + fonts-noto-cjk）
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
    """注册一个支持中文的字体，用于 PDF 导出
    优先使用文泉驿字体，ReportLab 对文泉驿的 TTC 支持较好"""
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
    """安全格式化时间，将 UTC 转为北京时间后输出"""
    if dt is None:
        return "-"
    try:
        from datetime import timezone, timedelta
        # 数据库存 UTC，转为北京时间 (UTC+8)
        if getattr(dt, "tzinfo", None) is None:
            dt = dt.replace(tzinfo=timezone.utc)
        beijing = timezone(timedelta(hours=8))
        return dt.astimezone(beijing).strftime(fmt)
    except Exception:
        return str(dt)[:19] if dt else "-"


def _minimal_pdf(title: str, resource_id: int) -> BytesIO:
    """生成仅含标题和 ID 的纯 ASCII PDF，用于任何异常时的最后兜底。内部多重 fallback 确保尽量不抛错。"""
    try:
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(str(title)[:50], styles["Title"]),
            Spacer(1, 0.5*cm),
            Paragraph(f"ID: {resource_id}", styles["Normal"]),
        ]
        doc.build(story)
        buf.seek(0)
        return buf
    except Exception as e1:
        logger.debug("_minimal_pdf platypus failed: %s", e1)
    try:
        from reportlab.pdfgen import canvas as pdf_canvas
        buf = BytesIO()
        c = pdf_canvas.Canvas(buf, pagesize=A4)
        c.setFont("Helvetica", 12)
        c.drawString(100, 700, f"Report ID: {resource_id}")
        c.save()
        buf.seek(0)
        return buf
    except Exception as e2:
        logger.warning("_minimal_pdf canvas failed: %s", e2)
    # 最后兜底：内嵌最小合法 PDF（单页）
    return BytesIO(_static_minimal_pdf_bytes())


def _static_minimal_pdf_bytes() -> bytes:
    """返回最小合法单页 PDF 字节，用于 ReportLab 全部失败时的兜底。先尝试 canvas 生成并缓存。"""
    if getattr(_static_minimal_pdf_bytes, "_cached", None) is not None:
        return _static_minimal_pdf_bytes._cached  # type: ignore
    try:
        from reportlab.pdfgen import canvas as pdf_canvas
        buf = BytesIO()
        c = pdf_canvas.Canvas(buf, pagesize=A4)
        c.setFont("Helvetica", 12)
        c.drawString(100, 700, "Report")
        c.save()
        out = buf.getvalue()
        _static_minimal_pdf_bytes._cached = out  # type: ignore
        return out
    except Exception as e:
        logger.debug("_static_minimal_pdf_bytes canvas failed: %s", e)
    # 最小合法 PDF（无 xref，部分阅读器接受）
    fallback = (
        b"%PDF-1.0\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
        b"trailer<</Size 4/Root 1 0 R>>\n"
        b"startxref\n0\n%%EOF"
    )
    _static_minimal_pdf_bytes._cached = fallback  # type: ignore
    return fallback


def _safe_filename(name: str, max_len: int = 100) -> str:
    """清理 filename 用于 Content-Disposition，去掉引号与换行，仅保留 ASCII 避免 latin-1 编码报错"""
    s = (name or "report").replace('"', "").replace("\n", "").replace("\r", "")[:max_len]
    s = "".join(c if ord(c) < 128 else "_" for c in (s or "report"))
    return s or "report"


def _content_disposition_pdf(display_filename: str) -> str:
    """生成仅含 ASCII 的 Content-Disposition，避免 Starlette 在 encode('latin-1') 时报错"""
    clean = (display_filename or "report").replace('"', "").replace("\n", "").replace("\r", "")[:100]
    ascii_only = "".join(c if ord(c) < 128 else "_" for c in clean).strip() or "report"
    if not ascii_only.endswith(".pdf"):
        ascii_only += ".pdf"
    return f'attachment; filename="{ascii_only}"'


def _build_company_pdf(scan: CompanyScan) -> BytesIO:
    """公司检测PDF：与前端报告页一致，展示企业信息和法律案件详情，不做风险评价"""
    try:
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        font = _ensure_cjk_font()
        for name in ("Title", "Normal", "Heading2"):
            styles[name].fontName = font
        story = []
        
        # 标题
        story.append(_safe_paragraph("装修公司信息报告", styles, "Title"))
        story.append(Spacer(1, 0.5*cm))
        
        # 基本信息
        story.append(_safe_paragraph(f"公司名称：{scan.company_name or '未命名'}", styles))
        story.append(_safe_paragraph(f"生成时间：{_safe_strftime(scan.created_at)}", styles))
        story.append(_safe_paragraph(f"报告编号：R-C-{scan.id}", styles))
        story.append(Spacer(1, 0.5*cm))
        
        # 企业信息
        company_info = scan.company_info or {}
        legal_risks = scan.legal_risks or {}
        
        story.append(_safe_paragraph("企业基本信息", styles, "Heading2"))
        if company_info.get("name"):
            story.append(_safe_paragraph(f"• 公司名称：{company_info.get('name')}", styles))
        if company_info.get("enterprise_age") is not None:
            story.append(_safe_paragraph(f"• 企业年龄：{company_info.get('enterprise_age')}年", styles))
        if company_info.get("start_date"):
            story.append(_safe_paragraph(f"• 成立时间：{company_info.get('start_date')}", styles))
        if company_info.get("oper_name"):
            story.append(_safe_paragraph(f"• 法定代表人：{company_info.get('oper_name')}", styles))
        if company_info.get("reg_capital"):
            story.append(_safe_paragraph(f"• 注册资本：{company_info.get('reg_capital')}", styles))
        if company_info.get("reg_status"):
            story.append(_safe_paragraph(f"• 登记状态：{company_info.get('reg_status')}", styles))
        
        story.append(Spacer(1, 0.3*cm))
        
        # 法律案件统计
        story.append(_safe_paragraph("法律案件统计", styles, "Heading2"))
        if legal_risks.get("legal_case_count") is not None:
            story.append(_safe_paragraph(f"• 法律案件总数：{legal_risks.get('legal_case_count')}件", styles))
        if legal_risks.get("decoration_related_cases") is not None:
            story.append(_safe_paragraph(f"• 装修相关案件：{legal_risks.get('decoration_related_cases')}件", styles))
        if legal_risks.get("recent_case_date"):
            story.append(_safe_paragraph(f"• 最近案件日期：{legal_risks.get('recent_case_date')}", styles))
        if legal_risks.get("case_types") and isinstance(legal_risks.get("case_types"), list):
            case_types = "、".join(legal_risks.get("case_types", []))
            story.append(_safe_paragraph(f"• 案件类型：{case_types}", styles))
        
        story.append(Spacer(1, 0.3*cm))
        
        # 案件详情（展示所有案件）
        recent_cases = legal_risks.get("recent_cases") or legal_risks.get("legal_cases") or []
        if recent_cases and isinstance(recent_cases, list):
            story.append(_safe_paragraph("案件详情", styles, "Heading2"))
            for i, case_item in enumerate(recent_cases, 1):
                if isinstance(case_item, dict):
                    # 构建案件详细信息（与前端一致）
                    case_details = []
                    
                    # 案件标题和日期
                    data_type = case_item.get("data_type_zh") or "案件"
                    title = case_item.get("title") or ""
                    date = case_item.get("date") or ""
                    if title or date:
                        case_details.append(f"{data_type}：{title}（{date}）")
                    
                    # 案件类型
                    case_type = case_item.get("case_type")
                    if case_type:
                        case_details.append(f"类型：{case_type}")
                    
                    # 案由
                    cause = case_item.get("cause")
                    if cause:
                        case_details.append(f"案由：{cause}")
                    
                    # 判决结果
                    result = case_item.get("result")
                    if result:
                        case_details.append(f"结果：{result}")
                    
                    # 相关法条
                    related_laws = case_item.get("related_laws")
                    if related_laws and isinstance(related_laws, list):
                        case_details.append(f"相关法条：{'、'.join(related_laws)}")
                    
                    # 案件编号
                    case_no = case_item.get("case_no")
                    if case_no:
                        case_details.append(f"案号：{case_no}")
                    
                    # 将案件详情组合成一行
                    case_text = f"{i}. {' | '.join(case_details)}"
                    story.append(_safe_paragraph(case_text, styles))
                else:
                    # 如果是字符串格式的案件
                    story.append(_safe_paragraph(f"{i}. {str(case_item)}", styles))
        
        # 数据来源说明
        story.append(Spacer(1, 0.5*cm))
        story.append(_safe_paragraph("数据来源说明", styles, "Heading2"))
        story.append(_safe_paragraph("• 企业信息：国家企业信用信息公示系统", styles))
        story.append(_safe_paragraph("• 法律案件：中国裁判文书网等公开司法数据", styles))
        story.append(_safe_paragraph("• 数据更新：报告生成时最新数据", styles))
        story.append(Spacer(1, 0.3*cm))
        story.append(_safe_paragraph("注：本报告基于公开信息生成，仅供参考。", styles))
        
        doc.build(story)
        buf.seek(0)
        return buf
    except Exception as e:
        logger.warning("Company PDF with CJK failed, falling back to ASCII: %s", e)
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("Company Information Report", styles["Title"]),
            Spacer(1, 0.5*cm),
            Paragraph(f"Company: {scan.company_name or 'N/A'}", styles["Normal"]),
            Paragraph(f"Time: {_safe_strftime(scan.created_at)}", styles["Normal"]),
            Paragraph(f"Report No: R-C-{scan.id}", styles["Normal"]),
        ]
        doc.build(story)
        buf.seek(0)
        return buf


def _build_quote_pdf(quote: Quote) -> BytesIO:
    """报价单 PDF：专业格式，包含摘要、风险分析和详细建议"""
    rj = getattr(quote, "result_json", None) or {}
    high_risk_items = rj.get("high_risk_items") or getattr(quote, "high_risk_items", None) or []
    warning_items = rj.get("warning_items") or getattr(quote, "warning_items", None) or []
    missing_items = rj.get("missing_items") or getattr(quote, "missing_items", None) or []
    overpriced_items = rj.get("overpriced_items") or getattr(quote, "overpriced_items", None) or []
    suggestions = rj.get("suggestions") or []
    
    # 统计信息
    high_risk_count = len(high_risk_items) if isinstance(high_risk_items, list) else 0
    warning_count = len(warning_items) if isinstance(warning_items, list) else 0
    missing_count = len(missing_items) if isinstance(missing_items, list) else 0
    overpriced_count = len(overpriced_items) if isinstance(overpriced_items, list) else 0
    suggestion_count = len(suggestions) if isinstance(suggestions, list) else 0

    def item_text(parts):
        txt = " ".join(str(p) for p in parts if p)
        return (txt[:500] if txt else "—").replace("\n", " ")

    try:
        buf = BytesIO()
        
        # 创建带页眉页脚的文档模板
        from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
        from reportlab.lib.units import inch

        # 定义页眉页脚函数 - 添加深圳市拉克力国际贸易有限公司Logo
        def add_header_footer(canvas, doc):
            # 保存当前状态
            canvas.saveState()
            
            # 获取支持中文的字体
            cjk_font = _ensure_cjk_font()
            cjk_font_bold = cjk_font  # 使用相同字体，ReportLab会自动处理粗体

            # 页眉 - 公司Logo和标题
            canvas.setFont(cjk_font_bold, 16)
            canvas.setFillColor(HexColor("#2c3e50"))
            canvas.drawString(1.5*cm, A4[1] - 1.5*cm, "深圳市拉克力国际贸易有限公司")

            # 页眉 - 报告类型
            canvas.setFont(cjk_font, 10)
            canvas.setFillColor(HexColor("#7f8c8d"))
            canvas.drawString(1.5*cm, A4[1] - 2.0*cm, "装修决策Agent - 报价单分析报告")

            # 页眉 - 分隔线
            canvas.setStrokeColor(HexColor("#3498db"))
            canvas.setLineWidth(1)
            canvas.line(1.5*cm, A4[1] - 2.2*cm, A4[0] - 1.5*cm, A4[1] - 2.2*cm)

            # 页脚 - 页码和公司信息
            canvas.setFont(cjk_font, 8)
            canvas.setFillColor(HexColor("#95a5a6"))

            # 左侧：公司信息
            canvas.drawString(1.5*cm, 1.0*cm, "深圳市拉克力国际贸易有限公司")

            # 中间：免责声明
            canvas.drawCentredString(A4[0]/2, 1.0*cm, "本报告仅供参考，不构成专业法律或财务建议")

            # 右侧：页码
            page_num = canvas.getPageNumber()
            canvas.drawRightString(A4[0] - 1.5*cm, 1.0*cm, f"第 {page_num} 页")

            # 页脚分隔线
            canvas.setStrokeColor(HexColor("#bdc3c7"))
            canvas.setLineWidth(0.5)
            canvas.line(1.5*cm, 1.3*cm, A4[0] - 1.5*cm, 1.3*cm)

            # 恢复状态
            canvas.restoreState()

            # 添加水印
            canvas.saveState()
            canvas.setFont(cjk_font, 60)
            canvas.setFillColor(HexColor("#f0f0f0"))
            canvas.rotate(45)
            canvas.drawCentredString(4*inch, -3*inch, "拉克力国际")
            canvas.restoreState()
        
        # 创建文档模板
        doc = BaseDocTemplate(buf, pagesize=A4, 
                             rightMargin=1.5*cm, leftMargin=1.5*cm, 
                             topMargin=3.0*cm, bottomMargin=2.0*cm)
        
        # 创建框架
        frame = Frame(doc.leftMargin, doc.bottomMargin, 
                     doc.width, doc.height, 
                     id='normal')
        
        # 创建页面模板
        template = PageTemplate(id='test', frames=frame, onPage=add_header_footer)
        doc.addPageTemplates([template])
        
        styles = getSampleStyleSheet()
        font = _ensure_cjk_font()
        
        # 设置字体
        for name in ("Title", "Normal", "Heading1", "Heading2", "Heading3"):
            if name in styles:
                styles[name].fontName = font
        
        # 创建自定义样式
        # 报告标题样式
        styles.add(ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=HexColor("#2c3e50")
        ))
        
        # 副标题样式
        styles.add(ParagraphStyle(
            name="SubTitle",
            parent=styles["Normal"],
            fontSize=12,
            textColor=HexColor("#666666"),
            spaceAfter=6
        ))
        
        # 摘要卡片样式
        styles.add(ParagraphStyle(
            name="SummaryCard",
            parent=styles["Normal"],
            fontSize=11,
            backColor=HexColor("#f8f9fa"),
            borderColor=HexColor("#dee2e6"),
            borderWidth=1,
            borderPadding=8,
            spaceAfter=8
        ))
        
        # 风险项样式
        styles.add(ParagraphStyle(
            name="HighRiskItem",
            parent=styles["Normal"],
            fontSize=10,
            textColor=HexColor("#dc3545"),
            spaceAfter=4
        ))
        
        styles.add(ParagraphStyle(
            name="WarningItem",
            parent=styles["Normal"],
            fontSize=10,
            textColor=HexColor("#fd7e14"),
            spaceAfter=4
        ))
        
        styles.add(ParagraphStyle(
            name="MissingItem",
            parent=styles["Normal"],
            fontSize=10,
            textColor=HexColor("#ffc107"),
            spaceAfter=4
        ))
        
        styles.add(ParagraphStyle(
            name="OverpricedItem",
            parent=styles["Normal"],
            fontSize=10,
            textColor=HexColor("#0d6efd"),
            spaceAfter=4
        ))
        
        story = []
        
        # 1. 报告标题
        story.append(_safe_paragraph("报价单分析报告", styles, "ReportTitle"))
        story.append(Spacer(1, 0.3*cm))
        
        # 2. 基本信息
        story.append(_safe_paragraph(f"文件名：{quote.file_name or '未命名'}", styles, "SubTitle"))
        story.append(_safe_paragraph(f"生成时间：{_safe_strftime(quote.created_at)}", styles, "SubTitle"))
        story.append(_safe_paragraph(f"报告编号：R-Q-{quote.id}", styles, "SubTitle"))
        story.append(Spacer(1, 0.5*cm))
        
        # 3. 风险摘要卡片
        summary_text = f"""
        <b>风险评分：{quote.risk_score or 0}分</b><br/>
        总价：{quote.total_price or '未识别'}元 | 市场参考价：{quote.market_ref_price or '未提供'}元<br/>
        高风险项：{high_risk_count}个 | 警告项：{warning_count}个<br/>
        漏项：{missing_count}个 | 价格虚高项：{overpriced_count}个<br/>
        建议：{suggestion_count}条
        """
        story.append(_safe_paragraph(summary_text, styles, "SummaryCard"))
        story.append(Spacer(1, 0.8*cm))
        
        # 4. 关键建议摘要
        if suggestions and isinstance(suggestions, list):
            story.append(_safe_paragraph("关键建议摘要", styles, "Heading1"))
            story.append(Spacer(1, 0.3*cm))
            for i, s in enumerate(suggestions[:5], 1):
                suggestion_text = str(s)[:300]
                story.append(_safe_paragraph(f"{i}. {suggestion_text}", styles))
            if suggestion_count > 5:
                story.append(_safe_paragraph(f"... 还有 {suggestion_count - 5} 条建议", styles, "SubTitle"))
            story.append(Spacer(1, 0.5*cm))
        
        # 5. 详细分析
        story.append(_safe_paragraph("详细分析结果", styles, "Heading1"))
        story.append(Spacer(1, 0.3*cm))
        
        # 5.1 高风险项
        if high_risk_items and isinstance(high_risk_items, list):
            story.append(_safe_paragraph(f"高风险项 ({high_risk_count}个)", styles, "Heading2"))
            story.append(Spacer(1, 0.2*cm))
            for it in high_risk_items:
                # 字段名映射：数据库中是name和reason，代码期望item和description
                i = it.get("name", it.get("item", it.get("description", ""))) if isinstance(it, dict) else str(it)
                d = it.get("reason", it.get("description", "")) if isinstance(it, dict) else ""
                imp = it.get("impact", "") if isinstance(it, dict) else ""
                item_text = f"• {i}"
                if d:
                    item_text += f"：{d}"
                if imp:
                    item_text += f"（影响：{imp}）"
                story.append(_safe_paragraph(item_text, styles, "HighRiskItem"))
            story.append(Spacer(1, 0.3*cm))
        
        # 5.2 警告项
        if warning_items and isinstance(warning_items, list):
            story.append(_safe_paragraph(f"警告项 ({warning_count}个)", styles, "Heading2"))
            story.append(Spacer(1, 0.2*cm))
            for it in warning_items:
                i = it.get("item", "") if isinstance(it, dict) else str(it)
                d = it.get("description", "") if isinstance(it, dict) else ""
                item_text = f"• {i}"
                if d:
                    item_text += f"：{d}"
                story.append(_safe_paragraph(item_text, styles, "WarningItem"))
            story.append(Spacer(1, 0.3*cm))
        
        # 5.3 漏项
        if missing_items and isinstance(missing_items, list):
            story.append(_safe_paragraph(f"漏项 ({missing_count}个)", styles, "Heading2"))
            story.append(Spacer(1, 0.2*cm))
            for it in missing_items:
                # 字段名映射：数据库中是name和suggestion，代码期望item和reason
                i = it.get("name", it.get("item", "")) if isinstance(it, dict) else str(it)
                imp = it.get("importance", "中") if isinstance(it, dict) else "中"
                r = it.get("suggestion", it.get("reason", "")) if isinstance(it, dict) else ""
                item_text = f"• {i}（重要性：{imp}）"
                if r:
                    item_text += f"：{r}"
                story.append(_safe_paragraph(item_text, styles, "MissingItem"))
            story.append(Spacer(1, 0.3*cm))
        
        # 5.4 价格虚高项
        if overpriced_items and isinstance(overpriced_items, list):
            story.append(_safe_paragraph(f"价格虚高项 ({overpriced_count}个)", styles, "Heading2"))
            story.append(Spacer(1, 0.2*cm))
            for it in overpriced_items:
                # 字段名映射：数据库中是name、current_price、market_price、reason
                i = it.get("name", it.get("item", "")) if isinstance(it, dict) else str(it)
                qp = it.get("current_price", it.get("quoted_price", ""))
                mr = it.get("market_price", it.get("market_ref_price", ""))
                pd = it.get("reason", it.get("price_diff", ""))
                item_text = f"• {i}"
                if qp:
                    item_text += f"：报价 {qp}元"
                if mr:
                    item_text += f"，市场参考价 {mr}元"
                if pd:
                    item_text += f"（{pd}）"
                story.append(_safe_paragraph(item_text, styles, "OverpricedItem"))
            story.append(Spacer(1, 0.3*cm))
        
        # 6. 完整建议列表
        if suggestions and isinstance(suggestions, list) and suggestion_count > 5:
            story.append(_safe_paragraph("完整建议列表", styles, "Heading1"))
            story.append(Spacer(1, 0.3*cm))
            for i, s in enumerate(suggestions[5:], 6):
                suggestion_text = str(s)[:300]
                story.append(_safe_paragraph(f"{i}. {suggestion_text}", styles))
            story.append(Spacer(1, 0.3*cm))
        
        # 7. 页脚信息
        story.append(Spacer(1, 1*cm))
        story.append(_safe_paragraph("— 报告结束 —", styles, "SubTitle"))
        story.append(Spacer(1, 0.2*cm))
        footer_text = f"""
        本报告由深圳市拉克力国际贸易有限公司装修决策Agent生成，基于AI分析结果提供参考建议。<br/>
        报告生成时间：{_safe_strftime(quote.created_at)} | 报告编号：R-Q-{quote.id}<br/>
        免责声明：本报告仅供参考，不构成专业法律或财务建议。
        """
        story.append(_safe_paragraph(footer_text, styles, "SubTitle"))
        
        doc.build(story)
        buf.seek(0)
        return buf
    except Exception as e:
        logger.warning("Quote PDF build failed, fallback ASCII: %s", e)
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        safe_name = "".join(c if ord(c) < 128 else "?" for c in (str(quote.file_name or "")[:80])) or "N/A"
        story = [
            Paragraph("Quote Analysis Report", styles["Title"]),
            Spacer(1, 0.5*cm),
            Paragraph(f"File: {safe_name}", styles["Normal"]),
            Paragraph(f"Time: {_safe_strftime(quote.created_at)}", styles["Normal"]),
            Paragraph(f"Risk score: {quote.risk_score or 0}", styles["Normal"]),
        ]
        doc.build(story)
        buf.seek(0)
        return buf


def _build_contract_pdf(contract: Contract) -> BytesIO:
    """合同 PDF：专业格式，包含摘要、风险分析和详细建议，借鉴报价单报告的设计"""
    # 与前端一致：优先 result_json，否则用顶层字段
    rj = getattr(contract, "result_json", None) or {}
    risk_items = (rj.get("risk_items") or getattr(contract, "risk_items", None) or [])
    unfair_terms = (rj.get("unfair_terms") or getattr(contract, "unfair_terms", None) or [])
    missing_terms = (rj.get("missing_terms") or getattr(contract, "missing_terms", None) or [])
    suggested_modifications = (rj.get("suggested_modifications") or getattr(contract, "suggested_modifications", None) or [])
    summary = (rj.get("summary") or "").strip()
    
    # 统计信息
    risk_count = len(risk_items) if isinstance(risk_items, list) else 0
    unfair_count = len(unfair_terms) if isinstance(unfair_terms, list) else 0
    missing_count = len(missing_terms) if isinstance(missing_terms, list) else 0
    suggestion_count = len(suggested_modifications) if isinstance(suggested_modifications, list) else 0

    def item_text(parts):
        txt = " ".join(str(p) for p in parts if p)
        return (txt[:500] if txt else "—").replace("\n", " ")

    try:
        buf = BytesIO()
        
        # 创建带页眉页脚的文档模板（借鉴报价单报告设计）
        from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
        from reportlab.lib.units import inch

        # 定义页眉页脚函数 - 添加深圳市拉克力国际贸易有限公司Logo
        def add_header_footer(canvas, doc):
            # 保存当前状态
            canvas.saveState()
            
            # 获取支持中文的字体
            cjk_font = _ensure_cjk_font()
            cjk_font_bold = cjk_font  # 使用相同字体，ReportLab会自动处理粗体

            # 页眉 - 公司Logo和标题
            canvas.setFont(cjk_font_bold, 16)
            canvas.setFillColor(HexColor("#2c3e50"))
            canvas.drawString(1.5*cm, A4[1] - 1.5*cm, "深圳市拉克力国际贸易有限公司")

            # 页眉 - 报告类型
            canvas.setFont(cjk_font, 10)
            canvas.setFillColor(HexColor("#7f8c8d"))
            canvas.drawString(1.5*cm, A4[1] - 2.0*cm, "装修决策Agent - 合同审核报告")

            # 页眉 - 分隔线
            canvas.setStrokeColor(HexColor("#3498db"))
            canvas.setLineWidth(1)
            canvas.line(1.5*cm, A4[1] - 2.2*cm, A4[0] - 1.5*cm, A4[1] - 2.2*cm)

            # 页脚 - 页码和公司信息
            canvas.setFont(cjk_font, 8)
            canvas.setFillColor(HexColor("#95a5a6"))

            # 左侧：公司信息
            canvas.drawString(1.5*cm, 1.0*cm, "深圳市拉克力国际贸易有限公司")

            # 中间：免责声明
            canvas.drawCentredString(A4[0]/2, 1.0*cm, "本报告仅供参考，不构成专业法律建议")

            # 右侧：页码
            page_num = canvas.getPageNumber()
            canvas.drawRightString(A4[0] - 1.5*cm, 1.0*cm, f"第 {page_num} 页")

            # 页脚分隔线
            canvas.setStrokeColor(HexColor("#bdc3c7"))
            canvas.setLineWidth(0.5)
            canvas.line(1.5*cm, 1.3*cm, A4[0] - 1.5*cm, 1.3*cm)

            # 恢复状态
            canvas.restoreState()

            # 添加水印
            canvas.saveState()
            canvas.setFont(cjk_font, 60)
            canvas.setFillColor(HexColor("#f0f0f0"))
            canvas.rotate(45)
            canvas.drawCentredString(4*inch, -3*inch, "拉克力国际")
            canvas.restoreState()
        
        # 创建文档模板
        doc = BaseDocTemplate(buf, pagesize=A4, 
                             rightMargin=1.5*cm, leftMargin=1.5*cm, 
                             topMargin=3.0*cm, bottomMargin=2.0*cm)
        
        # 创建框架
        frame = Frame(doc.leftMargin, doc.bottomMargin, 
                     doc.width, doc.height, 
                     id='normal')
        
        # 创建页面模板
        template = PageTemplate(id='test', frames=frame, onPage=add_header_footer)
        doc.addPageTemplates([template])
        
        styles = getSampleStyleSheet()
        font = _ensure_cjk_font()
        
        # 设置字体
        for name in ("Title", "Normal", "Heading1", "Heading2", "Heading3"):
            if name in styles:
                styles[name].fontName = font
        
        # 创建自定义样式（借鉴报价单报告）
        # 报告标题样式
        styles.add(ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=HexColor("#2c3e50")
        ))
        
        # 副标题样式
        styles.add(ParagraphStyle(
            name="SubTitle",
            parent=styles["Normal"],
            fontSize=12,
            textColor=HexColor("#666666"),
            spaceAfter=6
        ))
        
        # 摘要卡片样式
        styles.add(ParagraphStyle(
            name="SummaryCard",
            parent=styles["Normal"],
            fontSize=11,
            backColor=HexColor("#f8f9fa"),
            borderColor=HexColor("#dee2e6"),
            borderWidth=1,
            borderPadding=8,
            spaceAfter=8
        ))
        
        # 风险等级样式
        styles.add(ParagraphStyle(
            name="HighRisk",
            parent=styles["Normal"],
            fontSize=10,
            textColor=HexColor("#dc3545"),  # 红色 - 高风险
            spaceAfter=4
        ))
        
        styles.add(ParagraphStyle(
            name="MediumRisk",
            parent=styles["Normal"],
            fontSize=10,
            textColor=HexColor("#fd7e14"),  # 橙色 - 中风险
            spaceAfter=4
        ))
        
        styles.add(ParagraphStyle(
            name="LowRisk",
            parent=styles["Normal"],
            fontSize=10,
            textColor=HexColor("#ffc107"),  # 黄色 - 低风险
            spaceAfter=4
        ))
        
        styles.add(ParagraphStyle(
            name="Compliant",
            parent=styles["Normal"],
            fontSize=10,
            textColor=HexColor("#28a745"),  # 绿色 - 合规
            spaceAfter=4
        ))
        
        styles.add(ParagraphStyle(
            name="Suggestion",
            parent=styles["Normal"],
            fontSize=10,
            textColor=HexColor("#0d6efd"),  # 蓝色 - 建议
            spaceAfter=4
        ))
        
        story = []
        
        # 1. 报告标题
        story.append(_safe_paragraph("合同审核报告", styles, "ReportTitle"))
        story.append(Spacer(1, 0.3*cm))
        
        # 2. 基本信息
        story.append(_safe_paragraph(f"文件名：{contract.file_name or '未命名'}", styles, "SubTitle"))
        story.append(_safe_paragraph(f"生成时间：{_safe_strftime(contract.created_at)}", styles, "SubTitle"))
        story.append(_safe_paragraph(f"报告编号：R-C-{contract.id}", styles, "SubTitle"))
        story.append(Spacer(1, 0.5*cm))
        
        # 3. 检查合同状态：如果分析失败，显示错误信息
        if contract.status == "failed":
            story.append(_safe_paragraph("分析状态：AI分析失败，请稍后再试", styles, "Heading1"))
            story.append(Spacer(1, 0.3*cm))
            story.append(_safe_paragraph("抱歉，合同分析服务暂时不可用。请稍后重试或联系客服。", styles))
            story.append(Spacer(1, 0.5*cm))
        else:
            # 4. 风险摘要卡片
            risk_level = contract.risk_level or "pending"
            risk_level_zh = {
                "high": "高风险", "warning": "中风险", "low": "低风险", 
                "compliant": "合规", "pending": "待分析"
            }.get(risk_level, risk_level)
            
            summary_text = f"""
            <b>风险等级：{risk_level_zh}</b><br/>
            风险条款：{risk_count}个 | 不公平条款：{unfair_count}个<br/>
            缺失条款：{missing_count}个 | 修改建议：{suggestion_count}条<br/>
            分析状态：{contract.status or "pending"}
            """
            story.append(_safe_paragraph(summary_text, styles, "SummaryCard"))
            story.append(Spacer(1, 0.8*cm))
            
            # 5. 摘要（如果有）
            if summary:
                story.append(_safe_paragraph("分析摘要", styles, "Heading1"))
                story.append(Spacer(1, 0.3*cm))
                story.append(_safe_paragraph(summary[:800], styles))
                story.append(Spacer(1, 0.5*cm))
            
            # 6. 详细分析结果（只有在分析成功时才显示）
            if contract.status == "completed":
                story.append(_safe_paragraph("详细分析结果", styles, "Heading1"))
                story.append(Spacer(1, 0.3*cm))
                
                # 6.1 风险条款
                if risk_items and isinstance(risk_items, list):
                    story.append(_safe_paragraph(f"风险条款 ({risk_count}个)", styles, "Heading2"))
                    story.append(Spacer(1, 0.2*cm))
                    for it in risk_items:
                        t = it.get("term", it.get("description", "")) if isinstance(it, dict) else str(it)
                        d = it.get("description", "") if isinstance(it, dict) else ""
                        item_text = f"• {t}"
                        if d:
                            item_text += f"：{d}"
                        # 根据风险等级使用不同颜色
                        risk_style = "HighRisk"
                        story.append(_safe_paragraph(item_text, styles, risk_style))
                    story.append(Spacer(1, 0.3*cm))
                
                # 6.2 不公平条款
                if unfair_terms and isinstance(unfair_terms, list):
                    story.append(_safe_paragraph(f"不公平条款 ({unfair_count}个)", styles, "Heading2"))
                    story.append(Spacer(1, 0.2*cm))
                    for it in unfair_terms:
                        t = it.get("term", "") if isinstance(it, dict) else str(it)
                        d = it.get("description", "") if isinstance(it, dict) else ""
                        item_text = f"• {t}"
                        if d:
                            item_text += f"：{d}"
                        # 不公平条款使用橙色（中风险）
                        story.append(_safe_paragraph(item_text, styles, "MediumRisk"))
                    story.append(Spacer(1, 0.3*cm))
                
                # 6.3 缺失条款
                if missing_terms and isinstance(missing_terms, list):
                    story.append(_safe_paragraph(f"缺失条款 ({missing_count}个)", styles, "Heading2"))
                    story.append(Spacer(1, 0.2*cm))
                    for it in missing_terms:
                        t = it.get("term", it.get("item", "")) if isinstance(it, dict) else str(it)
                        imp = it.get("importance", "中") if isinstance(it, dict) else "中"
                        r = it.get("reason", "") if isinstance(it, dict) else ""
                        item_text = f"• {t}（重要性：{imp}）"
                        if r:
                            item_text += f"：{r}"
                        # 缺失条款使用黄色（低风险）
                        story.append(_safe_paragraph(item_text, styles, "LowRisk"))
                    story.append(Spacer(1, 0.3*cm))
                
                # 6.4 修改建议
                if suggested_modifications and isinstance(suggested_modifications, list):
                    story.append(_safe_paragraph(f"修改建议 ({suggestion_count}条)", styles, "Heading2"))
                    story.append(Spacer(1, 0.2*cm))
                    for it in suggested_modifications:
                        m = it.get("modified", it.get("original", "")) if isinstance(it, dict) else str(it)
                        r = it.get("reason", "") if isinstance(it, dict) else ""
                        item_text = f"• {m}"
                        if r:
                            item_text += f"：{r}"
                        # 修改建议使用蓝色
                        story.append(_safe_paragraph(item_text, styles, "Suggestion"))
                    story.append(Spacer(1, 0.3*cm))
                
                # 7. 关键建议摘要（如果有修改建议）
                if suggested_modifications and isinstance(suggested_modifications, list) and suggestion_count > 3:
                    story.append(_safe_paragraph("关键修改建议摘要", styles, "Heading1"))
                    story.append(Spacer(1, 0.3*cm))
                    for i, it in enumerate(suggested_modifications[:3], 1):
                        m = it.get("modified", it.get("original", "")) if isinstance(it, dict) else str(it)
                        r = it.get("reason", "") if isinstance(it, dict) else ""
                        item_text = f"{i}. {m}"
                        if r:
                            item_text += f"：{r[:100]}"
                        story.append(_safe_paragraph(item_text, styles))
                    if suggestion_count > 3:
                        story.append(_safe_paragraph(f"... 还有 {suggestion_count - 3} 条修改建议", styles, "SubTitle"))
                    story.append(Spacer(1, 0.5*cm))
        
        # 8. 页脚信息
        story.append(Spacer(1, 1*cm))
        story.append(_safe_paragraph("— 报告结束 —", styles, "SubTitle"))
        story.append(Spacer(1, 0.2*cm))
        footer_text = f"""
        本报告由深圳市拉克力国际贸易有限公司装修决策Agent生成，基于AI分析结果提供参考建议。<br/>
        报告生成时间：{_safe_strftime(contract.created_at)} | 报告编号：R-C-{contract.id}<br/>
        免责声明：本报告仅供参考，不构成专业法律建议。具体合同条款请咨询专业律师。
        """
        story.append(_safe_paragraph(footer_text, styles, "SubTitle"))
        
        doc.build(story)
        buf.seek(0)
        return buf
    except Exception as e:
        logger.warning("Contract PDF build failed, fallback ASCII: %s", e)
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        safe_name = "".join(c if ord(c) < 128 else "?" for c in (str(getattr(contract, "file_name", None) or "")[:80])) or "N/A"
        story = [
            Paragraph("Contract Review Report", styles["Title"]),
            Spacer(1, 0.5*cm),
            Paragraph(f"File: {safe_name}", styles["Normal"]),
            Paragraph(f"Time: {_safe_strftime(getattr(contract, 'created_at', None))}", styles["Normal"]),
            Paragraph(f"Risk: {getattr(contract, 'risk_level', None) or 'pending'}", styles["Normal"]),
        ]
        doc.build(story)
        buf.seek(0)
        return buf


def _build_acceptance_pdf(analysis: AcceptanceAnalysis, user_nickname: str = "") -> BytesIO:
    """P30 FR-028 验收报告 PDF（支持中文，失败时降级 ASCII）"""
    try:
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        font = _ensure_cjk_font()
        for name in ("Title", "Normal", "Heading2"):
            styles[name].fontName = font
        story = []
        stage_name = STAGE_NAMES.get(analysis.stage or "", analysis.stage or "验收")
        story.append(_safe_paragraph(f"{stage_name}验收报告", styles, "Title"))
        story.append(Spacer(1, 0.5*cm))
        story.append(_safe_paragraph(f"用户：{user_nickname or '用户'}", styles))
        story.append(_safe_paragraph(f"生成时间：{_safe_strftime(analysis.created_at)}", styles))
        rs = (getattr(analysis, "result_status", None) or "completed") or "completed"
        story.append(_safe_paragraph(f"验收结果：{RESULT_STATUS_ZH.get(str(rs).lower(), rs)}", styles))
        sev = (analysis.severity or "-") or "-"
        story.append(_safe_paragraph(f"风险等级：{SEVERITY_ZH.get(str(sev).lower(), sev)}", styles))
        story.append(Spacer(1, 0.5*cm))
        if analysis.issues and isinstance(analysis.issues, list):
            story.append(_safe_paragraph("问题项：", styles, "Heading2"))
            for it in analysis.issues:
                txt = it.get("description", it.get("item", str(it))) if isinstance(it, dict) else str(it)
                story.append(_safe_paragraph(f"• {txt}", styles))
            story.append(Spacer(1, 0.3*cm))
        if analysis.suggestions and isinstance(analysis.suggestions, list):
            story.append(_safe_paragraph("整改建议：", styles, "Heading2"))
            for it in analysis.suggestions:
                if isinstance(it, dict):
                    item_t = it.get("item") or it.get("suggestion") or it.get("content")
                    action_t = it.get("action")
                    if item_t and action_t:
                        txt = f"{item_t}：{action_t}"
                    elif item_t:
                        txt = str(item_t)
                    else:
                        txt = it.get("suggestion") or it.get("content") or str(it)
                else:
                    txt = str(it)
                story.append(_safe_paragraph(f"• {txt}", styles))
        doc.build(story)
        buf.seek(0)
        return buf
    except Exception as e:
        logger.warning("Acceptance PDF with CJK failed, fallback ASCII: %s", e)
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("Acceptance Report", styles["Title"]),
            Spacer(1, 0.5*cm),
            Paragraph(f"Stage: {analysis.stage or 'N/A'}", styles["Normal"]),
            Paragraph(f"Time: {_safe_strftime(analysis.created_at)}", styles["Normal"]),
            Paragraph(f"Result: {getattr(analysis, 'result_status', 'completed') or 'completed'}", styles["Normal"]),
        ]
        doc.build(story)
        buf.seek(0)
        return buf


@router.get("")
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """报告列表（公司检测、报价单、合同、验收的汇总，用于数据管理/报告中心）"""
    try:
        offset = (page - 1) * page_size
        items = []

        # 公司检测
        r = await db.execute(
            select(CompanyScan)
            .where(CompanyScan.user_id == user_id)
            .order_by(CompanyScan.created_at.desc())
            .limit(page_size * 2)
        )
        for row in r.scalars().all():
            items.append({
                "type": "company",
                "id": row.id,
                "title": f"公司检测 - {row.company_name or '未命名'}",
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "is_unlocked": True,
            })

        # 报价单
        r = await db.execute(
            select(Quote)
            .where(Quote.user_id == user_id)
            .order_by(Quote.created_at.desc())
            .limit(page_size * 2)
        )
        for row in r.scalars().all():
            items.append({
                "type": "quote",
                "id": row.id,
                "title": f"报价单 - {row.file_name or str(row.id)}",
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "is_unlocked": getattr(row, "is_unlocked", False),
            })

        # 合同
        r = await db.execute(
            select(Contract)
            .where(Contract.user_id == user_id)
            .order_by(Contract.created_at.desc())
            .limit(page_size * 2)
        )
        for row in r.scalars().all():
            items.append({
                "type": "contract",
                "id": row.id,
                "title": f"合同审核 - {row.file_name or str(row.id)}",
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "is_unlocked": getattr(row, "is_unlocked", False),
            })

        # 验收分析（未删除）
        r = await db.execute(
            select(AcceptanceAnalysis)
            .where(
                AcceptanceAnalysis.user_id == user_id,
                AcceptanceAnalysis.deleted_at.is_(None),
            )
            .order_by(AcceptanceAnalysis.created_at.desc())
            .limit(page_size * 2)
        )
        for row in r.scalars().all():
            stage_name = STAGE_NAMES.get(row.stage or "", row.stage or "验收")
            items.append({
                "type": "acceptance",
                "id": row.id,
                "title": f"{stage_name}验收报告",
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "is_unlocked": getattr(row, "is_unlocked", False),
            })

        # 按创建时间倒序，再分页
        items.sort(key=lambda x: x["created_at"] or "", reverse=True)
        total = len(items)
        items = items[offset : offset + page_size]
        return ApiResponse(code=0, msg="success", data={"list": items, "total": total})
    except Exception as e:
        logger.error(f"获取报告列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取失败")


@router.get("/export-pdf")
async def export_report_pdf(
    report_type: str = Query(..., description="company|quote|contract|acceptance"),
    resource_id: int = Query(..., description="scan_id / quote_id / contract_id / acceptance_analysis_id"),
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """导出报告为PDF（仅支持已解锁报告）"""
    try:
        if report_type == "company":
            r = await db.execute(select(CompanyScan).where(
                CompanyScan.id == resource_id,
                CompanyScan.user_id == user_id
            ))
            obj = r.scalar_one_or_none()
            if not obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")
            if not getattr(obj, "is_unlocked", True):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="请先解锁报告")
            try:
                buf = _build_company_pdf(obj)
            except Exception as e:
                logger.warning("Company PDF build failed, using minimal PDF: %s", e)
                buf = BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
                styles = getSampleStyleSheet()
                safe_name = "".join(c if ord(c) < 128 else "?" for c in (str(obj.company_name or "")[:50])) or "N/A"
                story = [
                    Paragraph("Company Risk Report", styles["Title"]),
                    Spacer(1, 0.5*cm),
                    Paragraph(f"ID: {resource_id}", styles["Normal"]),
                    Paragraph(f"Company: {safe_name}", styles["Normal"]),
                ]
                doc.build(story)
                buf.seek(0)
            filename = f"company_risk_report_{resource_id}.pdf"
        elif report_type == "quote":
            r = await db.execute(select(Quote).where(
                Quote.id == resource_id,
                Quote.user_id == user_id
            ))
            obj = r.scalar_one_or_none()
            if not obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")
            
            # 检查分析状态：必须为completed才能导出
            if obj.status != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"分析尚未完成，当前状态：{obj.status}，请稍后再试"
                )
            
            if not getattr(obj, "is_unlocked", False):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="请先解锁报告")
            try:
                buf = _build_quote_pdf(obj)
                filename = f"报价单分析报告_{obj.file_name or resource_id}.pdf"
            except Exception as e:
                logger.warning("Quote PDF endpoint fallback: %s", e)
                buf = _minimal_pdf("Quote Report", resource_id)
                filename = f"quote_report_{resource_id}.pdf"
        elif report_type == "contract":
            r = await db.execute(select(Contract).where(
                Contract.id == resource_id,
                Contract.user_id == user_id
            ))
            obj = r.scalar_one_or_none()
            if not obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")
            if not getattr(obj, "is_unlocked", False):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="请先解锁报告")
            try:
                buf = _build_contract_pdf(obj)
                filename = f"合同审核报告_{getattr(obj, 'file_name', None) or resource_id}.pdf"
            except Exception as e:
                logger.warning("Contract PDF endpoint fallback: %s", e)
                try:
                    buf = _minimal_pdf("ContractReport", resource_id)
                except Exception:
                    buf = _minimal_pdf("Report", resource_id)
                filename = f"contract_report_{resource_id}.pdf"
        elif report_type == "acceptance":
            r = await db.execute(
                select(AcceptanceAnalysis).where(
                    AcceptanceAnalysis.id == resource_id,
                    AcceptanceAnalysis.user_id == user_id,
                    AcceptanceAnalysis.deleted_at.is_(None)
                )
            )
            obj = r.scalar_one_or_none()
            if not obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="验收报告不存在")
            u = await db.execute(select(User).where(User.id == user_id))
            user = u.scalar_one_or_none()
            # 会员可免费导出；已解锁可导出；已通过可导出；复检3次已用完可导出（用户已完整参与流程，各阶段一致）
            is_member = getattr(user, "is_member", False) if user else False
            is_unlocked = getattr(obj, "is_unlocked", False)
            result_status = getattr(obj, "result_status", "") or ""
            is_passed = result_status.strip().lower() == "passed"
            recheck_cnt = getattr(obj, "recheck_count", 0) or 0
            recheck_exhausted = recheck_cnt >= 3
            if not is_unlocked and not is_member and not is_passed and not recheck_exhausted:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="请先解锁报告")
            nickname = user.nickname or "用户" if user else "用户"
            buf = _build_acceptance_pdf(obj, nickname)
            date_str = _safe_strftime(obj.created_at, "%Y-%m-%d") if obj.created_at else ""
            stage_name = STAGE_NAMES.get(obj.stage or "", obj.stage or "验收")
            filename = f"{stage_name}验收报告-{nickname}-{date_str}.pdf"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的报告类型")

        # 使用 Response 返回完整 PDF 字节，避免 StreamingResponse(BytesIO) 在小程序端收不到正确内容
        # Content-Disposition 使用 RFC 5987 编码中文文件名，避免 latin-1 报错
        pdf_bytes = buf.getvalue()
        headers = {
            "Content-Disposition": _content_disposition_pdf(filename),
            "Content-Length": str(len(pdf_bytes)),
        }
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers=headers,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("导出PDF失败 report_type=%s resource_id=%s: %s", report_type, resource_id, e, exc_info=True)
        try:
            buf = _minimal_pdf("Report", resource_id)
            pdf_bytes = buf.getvalue()
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": _content_disposition_pdf(f"{report_type}_report_{resource_id}.pdf"),
                    "Content-Length": str(len(pdf_bytes)),
                },
            )
        except Exception as e2:
            logger.error("导出PDF兜底也失败: %s", e2, exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="导出失败")

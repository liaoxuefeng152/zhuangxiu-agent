"""
装修决策Agent - 报告PDF导出API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import CompanyScan, Quote, Contract, AcceptanceAnalysis, User

router = APIRouter(prefix="/reports", tags=["报告导出"])
logger = logging.getLogger(__name__)

STAGE_NAMES = {"S00": "材料进场", "S01": "隐蔽工程", "S02": "泥瓦工", "S03": "木工", "S04": "油漆", "S05": "安装收尾"}

# 中文字体路径（Docker/本机无中文时用 ASCII 降级）
_CJK_FONT_REGISTERED = None
_CJK_FONT_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]


def _ensure_cjk_font():
    """注册一个支持中文的字体，用于 PDF 导出；失败则仅用内置字体（中文可能显示为方框）"""
    global _CJK_FONT_REGISTERED
    if _CJK_FONT_REGISTERED is not None:
        return _CJK_FONT_REGISTERED
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        for path in _CJK_FONT_PATHS:
            if os.path.isfile(path):
                pdfmetrics.registerFont(TTFont("CJK", path))
                _CJK_FONT_REGISTERED = "CJK"
                return "CJK"
    except Exception as e:
        logger.debug("ReportLab CJK font registration skipped: %s", e)
    _CJK_FONT_REGISTERED = "Helvetica"
    return "Helvetica"


def _safe_paragraph(text: str, styles, style_name: str = "Normal"):
    """若当前样式字体不支持中文，则用 ASCII 占位避免崩溃"""
    s = styles[style_name]
    font_name = getattr(s, "fontName", "Helvetica")
    try:
        return Paragraph(text, s)
    except Exception:
        # 降级：仅保留 ASCII
        safe = "".join(c if ord(c) < 128 else "?" for c in (text or ""))
        return Paragraph(safe or "-", s)


def _build_company_pdf(scan: CompanyScan) -> BytesIO:
    try:
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        font = _ensure_cjk_font()
        for name in ("Title", "Normal", "Heading2"):
            styles[name].fontName = font
        story = []
        story.append(_safe_paragraph("装修公司风险检测报告", styles, "Title"))
        story.append(Spacer(1, 0.5*cm))
        story.append(_safe_paragraph(f"公司名称：{scan.company_name or '未命名'}", styles))
        story.append(_safe_paragraph(f"生成时间：{scan.created_at.strftime('%Y-%m-%d %H:%M') if scan.created_at else '-'}", styles))
        story.append(_safe_paragraph(f"风险等级：{scan.risk_level or 'pending'}", styles))
        story.append(_safe_paragraph(f"风险评分：{scan.risk_score or 0}分", styles))
        story.append(Spacer(1, 0.5*cm))
        if scan.risk_reasons:
            story.append(_safe_paragraph("风险原因：", styles, "Heading2"))
            for r in (scan.risk_reasons if isinstance(scan.risk_reasons, list) else []):
                story.append(_safe_paragraph(f"• {r}", styles))
        if scan.legal_risks:
            story.append(Spacer(1, 0.3*cm))
            story.append(_safe_paragraph("法律风险：", styles, "Heading2"))
            for r in (scan.legal_risks if isinstance(scan.legal_risks, list) else []):
                if isinstance(r, dict):
                    story.append(_safe_paragraph(f"• {r.get('desc', r)}", styles))
                else:
                    story.append(_safe_paragraph(f"• {r}", styles))
        doc.build(story)
        buf.seek(0)
        return buf
    except Exception as e:
        logger.warning("Company PDF with CJK failed, falling back to ASCII: %s", e)
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("Company Risk Report", styles["Title"]),
            Spacer(1, 0.5*cm),
            Paragraph(f"Company: {scan.company_name or 'N/A'}", styles["Normal"]),
            Paragraph(f"Time: {scan.created_at.strftime('%Y-%m-%d %H:%M') if scan.created_at else '-'}", styles["Normal"]),
            Paragraph(f"Risk level: {scan.risk_level or 'pending'}", styles["Normal"]),
            Paragraph(f"Score: {scan.risk_score or 0}", styles["Normal"]),
        ]
        doc.build(story)
        buf.seek(0)
        return buf


def _build_quote_pdf(quote: Quote) -> BytesIO:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("报价单分析报告", styles["Title"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"文件名：{quote.file_name or '未命名'}", styles["Normal"]))
    story.append(Paragraph(f"生成时间：{quote.created_at.strftime('%Y-%m-%d %H:%M') if quote.created_at else '-'}", styles["Normal"]))
    story.append(Paragraph(f"风险评分：{quote.risk_score or 0}分", styles["Normal"]))
    if quote.total_price:
        story.append(Paragraph(f"总价：{quote.total_price}元", styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))
    for label, items, key in [
        ("高风险项", quote.high_risk_items, "description"),
        ("警告项", quote.warning_items, "description"),
        ("漏项", quote.missing_items, "item"),
        ("虚高项", quote.overpriced_items, "item")
    ]:
        if items and isinstance(items, list):
            story.append(Paragraph(label + "：", styles["Heading2"]))
            for it in items:
                txt = it.get(key, it.get("item", str(it))) if isinstance(it, dict) else str(it)
                story.append(Paragraph(f"• {txt}", styles["Normal"]))
            story.append(Spacer(1, 0.3*cm))
    doc.build(story)
    buf.seek(0)
    return buf


def _build_contract_pdf(contract: Contract) -> BytesIO:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("合同审核报告", styles["Title"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"文件名：{contract.file_name or '未命名'}", styles["Normal"]))
    story.append(Paragraph(f"生成时间：{contract.created_at.strftime('%Y-%m-%d %H:%M') if contract.created_at else '-'}", styles["Normal"]))
    story.append(Paragraph(f"风险等级：{contract.risk_level or 'pending'}", styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))
    for label, items, key in [
        ("风险条款", contract.risk_items, "term"),
        ("不公平条款", contract.unfair_terms, "term"),
        ("缺失条款", contract.missing_terms, "term")
    ]:
        if items and isinstance(items, list):
            story.append(Paragraph(label + "：", styles["Heading2"]))
            for it in items:
                txt = it.get(key, it.get("term", str(it))) if isinstance(it, dict) else str(it)
                story.append(Paragraph(f"• {txt}", styles["Normal"]))
            story.append(Spacer(1, 0.3*cm))
    if contract.suggested_modifications and isinstance(contract.suggested_modifications, list):
        story.append(Paragraph("修改建议：", styles["Heading2"]))
        for it in contract.suggested_modifications:
            txt = it.get("modified", it.get("original", str(it))) if isinstance(it, dict) else str(it)
            story.append(Paragraph(f"• {txt}", styles["Normal"]))
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
        story.append(_safe_paragraph(f"生成时间：{analysis.created_at.strftime('%Y-%m-%d %H:%M') if analysis.created_at else '-'}", styles))
        story.append(_safe_paragraph(f"验收结果：{getattr(analysis, 'result_status', 'completed') or 'completed'}", styles))
        story.append(_safe_paragraph(f"风险等级：{analysis.severity or '-'}", styles))
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
                txt = it.get("suggestion", it.get("content", str(it))) if isinstance(it, dict) else str(it)
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
            Paragraph(f"Time: {analysis.created_at.strftime('%Y-%m-%d %H:%M') if analysis.created_at else '-'}", styles["Normal"]),
            Paragraph(f"Result: {getattr(analysis, 'result_status', 'completed') or 'completed'}", styles["Normal"]),
        ]
        doc.build(story)
        buf.seek(0)
        return buf


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
            if not obj.is_unlocked:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="请先解锁报告")
            buf = _build_quote_pdf(obj)
            filename = f"报价单分析报告_{obj.file_name or resource_id}.pdf"
        elif report_type == "contract":
            r = await db.execute(select(Contract).where(
                Contract.id == resource_id,
                Contract.user_id == user_id
            ))
            obj = r.scalar_one_or_none()
            if not obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")
            if not obj.is_unlocked:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="请先解锁报告")
            buf = _build_contract_pdf(obj)
            filename = f"合同审核报告_{obj.file_name or resource_id}.pdf"
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
            nickname = user.nickname or "用户" if user else "用户"
            buf = _build_acceptance_pdf(obj, nickname)
            date_str = obj.created_at.strftime("%Y-%m-%d") if obj.created_at else ""
            stage_name = STAGE_NAMES.get(obj.stage or "", obj.stage or "验收")
            filename = f"{stage_name}验收报告-{nickname}-{date_str}.pdf"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的报告类型")

        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出PDF失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="导出失败")

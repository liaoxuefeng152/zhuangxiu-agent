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
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import CompanyScan, Quote, Contract, AcceptanceAnalysis, User
from app.schemas import ApiResponse

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
    try:
        return Paragraph(text, s)
    except Exception:
        # 降级：仅保留 ASCII
        safe = "".join(c if ord(c) < 128 else "?" for c in (str(text or "")[:2000]))
        return Paragraph(safe or "-", s)


def _safe_strftime(dt, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """安全格式化时间，避免 None 或非法类型抛错"""
    if dt is None:
        return "-"
    try:
        return dt.strftime(fmt)
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
    """报价单 PDF：与前端报告页一致，含建议/摘要 + 每条完整文案"""
    rj = getattr(quote, "result_json", None) or {}
    high_risk_items = rj.get("high_risk_items") or getattr(quote, "high_risk_items", None) or []
    warning_items = rj.get("warning_items") or getattr(quote, "warning_items", None) or []
    missing_items = rj.get("missing_items") or getattr(quote, "missing_items", None) or []
    overpriced_items = rj.get("overpriced_items") or getattr(quote, "overpriced_items", None) or []
    suggestions = rj.get("suggestions") or []

    def item_text(parts):
        txt = " ".join(str(p) for p in parts if p)
        return (txt[:500] if txt else "—").replace("\n", " ")

    try:
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        font = _ensure_cjk_font()
        for name in ("Title", "Normal", "Heading2"):
            styles[name].fontName = font
        story = []
        story.append(_safe_paragraph("报价单分析报告", styles, "Title"))
        story.append(Spacer(1, 0.5*cm))
        story.append(_safe_paragraph(f"文件名：{quote.file_name or '未命名'}", styles))
        story.append(_safe_paragraph(f"生成时间：{_safe_strftime(quote.created_at)}", styles))
        story.append(_safe_paragraph(f"风险评分：{quote.risk_score or 0}分", styles))
        if quote.total_price:
            story.append(_safe_paragraph(f"总价：{quote.total_price}元", styles))
        if suggestions and isinstance(suggestions, list):
            story.append(Spacer(1, 0.3*cm))
            story.append(_safe_paragraph("建议摘要：", styles, "Heading2"))
            for s in suggestions[:20]:
                story.append(_safe_paragraph(f"• {(str(s)[:400])}", styles))
            story.append(Spacer(1, 0.3*cm))
        story.append(Spacer(1, 0.5*cm))

        if high_risk_items and isinstance(high_risk_items, list):
            story.append(_safe_paragraph("高风险项：", styles, "Heading2"))
            for it in high_risk_items:
                i = it.get("item", it.get("description", "")) if isinstance(it, dict) else str(it)
                d = it.get("description", "") if isinstance(it, dict) else ""
                imp = it.get("impact", "") if isinstance(it, dict) else ""
                story.append(_safe_paragraph("• " + item_text([i, "：", d, f"（{imp}）" if imp else ""]), styles))
            story.append(Spacer(1, 0.3*cm))
        if warning_items and isinstance(warning_items, list):
            story.append(_safe_paragraph("警告项：", styles, "Heading2"))
            for it in warning_items:
                i = it.get("item", "") if isinstance(it, dict) else str(it)
                d = it.get("description", "") if isinstance(it, dict) else ""
                story.append(_safe_paragraph("• " + item_text([i, "：", d]), styles))
            story.append(Spacer(1, 0.3*cm))
        if missing_items and isinstance(missing_items, list):
            story.append(_safe_paragraph("漏项：", styles, "Heading2"))
            for it in missing_items:
                i = it.get("item", "") if isinstance(it, dict) else str(it)
                imp = it.get("importance", "中") if isinstance(it, dict) else "中"
                r = it.get("reason", "") if isinstance(it, dict) else ""
                story.append(_safe_paragraph("• " + item_text([i, "（", imp, "）：", r]), styles))
            story.append(Spacer(1, 0.3*cm))
        if overpriced_items and isinstance(overpriced_items, list):
            story.append(_safe_paragraph("虚高项：", styles, "Heading2"))
            for it in overpriced_items:
                i = it.get("item", "") if isinstance(it, dict) else str(it)
                qp = it.get("quoted_price", "")
                mr = it.get("market_ref_price", "")
                pd = it.get("price_diff", "")
                story.append(_safe_paragraph("• " + item_text([i, "：报价", qp, "元，", mr, pd]), styles))
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
            Paragraph(f"Time: {quote.created_at.strftime('%Y-%m-%d %H:%M') if quote.created_at else '-'}", styles["Normal"]),
            Paragraph(f"Risk score: {quote.risk_score or 0}", styles["Normal"]),
        ]
        doc.build(story)
        buf.seek(0)
        return buf


def _build_contract_pdf(contract: Contract) -> BytesIO:
    """合同 PDF：与前端报告页一致，含摘要 + 每条完整文案（term+description 等）"""
    def safe_append_para(story, text: str, style_name: str = "Normal"):
        try:
            story.append(_safe_paragraph(text, styles, style_name))
        except Exception:
            story.append(_safe_paragraph("—", styles))

    # 与前端一致：优先 result_json，否则用顶层字段
    rj = getattr(contract, "result_json", None) or {}
    risk_items = (rj.get("risk_items") or getattr(contract, "risk_items", None) or [])
    unfair_terms = (rj.get("unfair_terms") or getattr(contract, "unfair_terms", None) or [])
    missing_terms = (rj.get("missing_terms") or getattr(contract, "missing_terms", None) or [])
    suggested_modifications = (rj.get("suggested_modifications") or getattr(contract, "suggested_modifications", None) or [])
    summary = (rj.get("summary") or "").strip()

    try:
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        font = _ensure_cjk_font()
        for name in ("Title", "Normal", "Heading2"):
            styles[name].fontName = font
        story = []
        safe_append_para(story, "合同审核报告", "Title")
        story.append(Spacer(1, 0.5*cm))
        safe_append_para(story, f"文件名：{(contract.file_name or '未命名')}")
        safe_append_para(story, f"生成时间：{_safe_strftime(contract.created_at)}")
        safe_append_para(story, f"风险等级：{(contract.risk_level or 'pending')}")
        if summary:
            story.append(Spacer(1, 0.3*cm))
            safe_append_para(story, f"摘要：{summary[:800]}")
        story.append(Spacer(1, 0.5*cm))

        def item_text(parts):
            txt = " ".join(str(p) for p in parts if p)
            return (txt[:500] if txt else "—").replace("\n", " ")

        if risk_items and isinstance(risk_items, list):
            safe_append_para(story, "风险条款：", "Heading2")
            for it in risk_items:
                t = it.get("term", it.get("description", "")) if isinstance(it, dict) else str(it)
                d = it.get("description", "") if isinstance(it, dict) else ""
                safe_append_para(story, "• " + item_text([t, "：", d]))
            story.append(Spacer(1, 0.3*cm))
        if unfair_terms and isinstance(unfair_terms, list):
            safe_append_para(story, "不公平条款：", "Heading2")
            for it in unfair_terms:
                t = it.get("term", "") if isinstance(it, dict) else str(it)
                d = it.get("description", "") if isinstance(it, dict) else ""
                safe_append_para(story, "• " + item_text([t, "：", d]))
            story.append(Spacer(1, 0.3*cm))
        if missing_terms and isinstance(missing_terms, list):
            safe_append_para(story, "缺失条款：", "Heading2")
            for it in missing_terms:
                t = it.get("term", it.get("item", "")) if isinstance(it, dict) else str(it)
                imp = it.get("importance", "中") if isinstance(it, dict) else "中"
                r = it.get("reason", "") if isinstance(it, dict) else ""
                safe_append_para(story, "• " + item_text([t, "（", imp, "）：", r]))
            story.append(Spacer(1, 0.3*cm))
        if suggested_modifications and isinstance(suggested_modifications, list):
            safe_append_para(story, "修改建议：", "Heading2")
            for it in suggested_modifications:
                m = it.get("modified", it.get("original", "")) if isinstance(it, dict) else str(it)
                r = it.get("reason", "") if isinstance(it, dict) else ""
                safe_append_para(story, "• " + item_text([m, "：", r]))
        doc.build(story)
        buf.seek(0)
        return buf
    except Exception as e:
        logger.warning("Contract PDF build failed, fallback ASCII: %s", e)
    try:
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
    except Exception as e2:
        logger.warning("Contract PDF ASCII fallback failed: %s", e2)
    try:
        return _minimal_pdf("ContractReport", getattr(contract, "id", 0))
    except Exception:
        return BytesIO(_static_minimal_pdf_bytes())


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
            if not getattr(obj, "is_unlocked", True):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="请先解锁报告")
            u = await db.execute(select(User).where(User.id == user_id))
            user = u.scalar_one_or_none()
            nickname = user.nickname or "用户" if user else "用户"
            buf = _build_acceptance_pdf(obj, nickname)
            date_str = obj.created_at.strftime("%Y-%m-%d") if obj.created_at else ""
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

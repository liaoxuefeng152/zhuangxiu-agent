"""
开发环境 - 测试数据种子接口（仅 DEBUG 时可用）
用于 API 测试脚本造数
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_user_id
from app.core.config import settings
from app.models import Quote, Contract, CompanyScan

router = APIRouter(prefix="/dev", tags=["开发-测试数据"])


class AnalyzeQuoteTextRequest(BaseModel):
    """开发环境：用文本直接调报价分析（不经过上传/OCR）"""
    text: str
    total_price: Optional[float] = None


class AnalyzeContractTextRequest(BaseModel):
    """开发环境：用文本直接调合同分析（不经过上传/OCR）"""
    text: str


@router.post("/analyze-quote-text")
async def analyze_quote_text(
    body: AnalyzeQuoteTextRequest = Body(...),
    user_id: int = Depends(get_user_id),
):
    """开发环境专用：用报价单文本直接调用 AI 分析并返回结果（便于测试扣子/DeepSeek）"""
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not Found")
    from app.services.risk_analyzer import risk_analyzer_service
    result = await risk_analyzer_service.analyze_quote(body.text, body.total_price)
    return result


@router.post("/analyze-contract-text")
async def analyze_contract_text(
    body: AnalyzeContractTextRequest = Body(...),
    user_id: int = Depends(get_user_id),
):
    """开发环境专用：用合同文本直接调用 AI 分析并返回结果（便于测试扣子/DeepSeek）"""
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not Found")
    from app.services.risk_analyzer import risk_analyzer_service
    result = await risk_analyzer_service.analyze_contract(body.text)
    return result


@router.post("/seed")
async def seed_test_data(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建测试用报价单、合同、公司扫描记录（仅 DEBUG 时可用）"""
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not Found")

    from sqlalchemy import select

    # 检查是否已有数据
    rq = await db.execute(select(Quote).where(Quote.user_id == user_id).limit(1))
    q = rq.scalar_one_or_none()
    rc = await db.execute(select(Contract).where(Contract.user_id == user_id).limit(1))
    c = rc.scalar_one_or_none()
    rs = await db.execute(select(CompanyScan).where(CompanyScan.user_id == user_id).limit(1))
    s = rs.scalar_one_or_none()

    quote_id = q.id if q else None
    contract_id = c.id if c else None
    scan_id = s.id if s else None

    if not q:
        q = Quote(
            user_id=user_id,
            file_url="https://example.com/test_quote.pdf",
            file_name="测试报价单.pdf",
            file_size=1024,
            file_type="pdf",
            status="completed",
            risk_score=65,
            total_price=88000.0,
            is_unlocked=True,
        )
        db.add(q)
        await db.flush()
        quote_id = q.id

    if not c:
        c = Contract(
            user_id=user_id,
            file_url="https://example.com/test_contract.pdf",
            file_name="测试合同.pdf",
            file_size=2048,
            file_type="pdf",
            status="completed",
            risk_level="warning",
            is_unlocked=True,
        )
        db.add(c)
        await db.flush()
        contract_id = c.id

    if not s:
        s = CompanyScan(
            user_id=user_id,
            company_name="测试装修公司",
            status="completed",
            risk_level="compliant",
            risk_score=20,
        )
        db.add(s)
        await db.flush()
        scan_id = s.id

    await db.commit()

    return {
        "quote_id": quote_id,
        "contract_id": contract_id,
        "scan_id": scan_id,
    }

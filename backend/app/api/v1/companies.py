"""
装修决策Agent - 公司风险检测API
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import logging

from app.core.database import get_db, AsyncSessionLocal
from app.core.security import get_user_id
from app.models import CompanyScan, User, Quote, Contract
from app.services import tianyancha_service
from app.schemas import (
    CompanyScanRequest, CompanyScanResponse, ApiResponse, RiskLevel, ScanStatus
)

router = APIRouter(prefix="/companies", tags=["公司检测"])
logger = logging.getLogger(__name__)


async def analyze_company_background(company_scan_id: int, company_name: str, db: AsyncSession):
    """
    后台任务：分析公司风险

    Args:
        company_scan_id: 扫描记录ID
        company_name: 公司名称
        db: 数据库会话
    """
    try:
        logger.info(f"开始分析公司风险: {company_name}")

        # 调用天眼查API分析
        risk_analysis = await tianyancha_service.analyze_company_risk(company_name)

        # 更新数据库
        result = await db.execute(select(CompanyScan).where(CompanyScan.id == company_scan_id))
        company_scan = result.scalar_one_or_none()

        if company_scan:
            company_scan.risk_level = risk_analysis["risk_level"]
            company_scan.risk_score = risk_analysis["risk_score"]
            company_scan.risk_reasons = risk_analysis["risk_reasons"]
            company_scan.complaint_count = risk_analysis["complaint_count"]
            company_scan.legal_risks = risk_analysis["legal_risks"]
            company_scan.status = "completed"

            await db.commit()
            logger.info(f"公司风险分析完成: {company_name}, 风险等级: {risk_analysis['risk_level']}")

            # P1 首次免费：若用户无任何已解锁报告（报价/合同/公司），则本条公司检测自动免费解锁
            try:
                async with AsyncSessionLocal() as new_db:
                    r = await new_db.execute(select(CompanyScan).where(CompanyScan.id == company_scan_id))
                    cs = r.scalar_one_or_none()
                    if cs:
                        uid = cs.user_id
                        has_quote = await new_db.execute(
                            select(Quote.id).where(Quote.user_id == uid, Quote.is_unlocked == True).limit(1)
                        )
                        has_contract = await new_db.execute(
                            select(Contract.id).where(Contract.user_id == uid, Contract.is_unlocked == True).limit(1)
                        )
                        has_other_company = await new_db.execute(
                            select(CompanyScan.id).where(
                                CompanyScan.user_id == uid,
                                CompanyScan.is_unlocked == True,
                                CompanyScan.id != company_scan_id,
                            ).limit(1)
                        )
                        if (
                            not has_quote.scalar_one_or_none()
                            and not has_contract.scalar_one_or_none()
                            and not has_other_company.scalar_one_or_none()
                        ):
                            cs.is_unlocked = True
                            cs.unlock_type = "first_free"
                            await new_db.commit()
                            logger.info(f"首次报告免费解锁: 公司检测 {company_scan_id}, 用户 {uid}")
            except Exception as e:
                logger.warning(f"公司检测首次免费逻辑执行失败: {e}")
        else:
            logger.error(f"公司扫描记录不存在: {company_scan_id}")

    except Exception as e:
        logger.error(f"公司风险分析失败: {e}", exc_info=True)

        # 更新为失败状态
        try:
            result = await db.execute(select(CompanyScan).where(CompanyScan.id == company_scan_id))
            company_scan = result.scalar_one_or_none()
            if company_scan:
                company_scan.status = "failed"
                company_scan.error_message = str(e)
                await db.commit()
        except:
            pass


@router.get("/search")
async def search_companies(
    q: str = Query(..., min_length=3, max_length=100),
    limit: int = Query(5, ge=1, le=10),
    user_id: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    公司名称模糊搜索（PRD FR-012）
    输入≥3字符时返回匹配建议，优先天眼查，fallback 本地历史
    """
    keyword = q.strip()
    if len(keyword) < 3:
        return ApiResponse(code=0, msg="success", data={"list": []})

    results = []
    try:
        # 1. 尝试天眼查搜索
        tyc_result = await tianyancha_service.search_companies(keyword, limit)
        if tyc_result:
            results = [{"name": r["name"]} for r in tyc_result if r.get("name")]
    except Exception as e:
        logger.debug(f"天眼查搜索失败: {e}")

    # 2. 本地 company_scans 表模糊匹配补充
    if len(results) < limit and user_id:
        try:
            from sqlalchemy import or_
            stmt = (
                select(CompanyScan.company_name)
                .where(CompanyScan.company_name.ilike(f"%{keyword}%"))
                .distinct()
                .limit(limit - len(results))
            )
            if user_id:
                stmt = stmt.where(CompanyScan.user_id == user_id)
            r = await db.execute(stmt)
            local_names = [row[0] for row in r.all()]
            seen = {x["name"] for x in results}
            for n in local_names:
                if n not in seen and len(results) < limit:
                    results.append({"name": n})
                    seen.add(n)
        except Exception as e:
            logger.debug(f"本地搜索失败: {e}")

    return ApiResponse(code=0, msg="success", data={"list": results[:limit]})


@router.post("/scan", response_model=CompanyScanResponse)
async def scan_company(
    request: CompanyScanRequest,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    扫描装修公司风险

    Args:
        request: 扫描请求（公司名称）
        user_id: 用户ID
        background_tasks: 后台任务
        db: 数据库会话

    Returns:
        扫描结果
    """
    try:
        # 创建扫描记录
        company_scan = CompanyScan(
            user_id=user_id,
            company_name=request.company_name,
            status="pending"
        )

        db.add(company_scan)
        await db.commit()
        await db.refresh(company_scan)

        # 启动后台分析任务
        background_tasks.add_task(
            analyze_company_background,
            company_scan.id,
            request.company_name,
            db
        )

        logger.info(f"公司扫描任务已创建: {request.company_name}, ID: {company_scan.id}")

        return CompanyScanResponse(
            id=company_scan.id,
            company_name=company_scan.company_name,
            risk_level=RiskLevel.COMPLIANT,
            risk_score=0,
            risk_reasons=[],
            complaint_count=0,
            legal_risks=[],
            status=ScanStatus(company_scan.status) if company_scan.status else ScanStatus.PENDING,
            created_at=company_scan.created_at
        )

    except Exception as e:
        logger.error(f"创建公司扫描任务失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建扫描任务失败"
        )


@router.get("/scan/{scan_id}", response_model=CompanyScanResponse)
async def get_scan_result(
    scan_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取公司扫描结果

    Args:
        scan_id: 扫描记录ID
        user_id: 用户ID
        db: 数据库会话

    Returns:
        扫描结果
    """
    try:
        result = await db.execute(
            select(CompanyScan)
            .where(CompanyScan.id == scan_id, CompanyScan.user_id == user_id)
        )
        company_scan = result.scalar_one_or_none()

        if not company_scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="扫描记录不存在"
            )

        return CompanyScanResponse(
            id=company_scan.id,
            company_name=company_scan.company_name,
            risk_level=RiskLevel(company_scan.risk_level) if company_scan.risk_level else RiskLevel.COMPLIANT,
            risk_score=company_scan.risk_score if company_scan.risk_score is not None else 0,
            risk_reasons=company_scan.risk_reasons or [],
            complaint_count=company_scan.complaint_count or 0,
            legal_risks=company_scan.legal_risks or [],
            status=ScanStatus(company_scan.status) if company_scan.status else ScanStatus.PENDING,
            is_unlocked=getattr(company_scan, "is_unlocked", False),
            created_at=company_scan.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取扫描结果失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取扫描结果失败"
        )


@router.get("/scans")
async def list_scans(
    user_id: int = Depends(get_user_id),
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户的扫描记录列表

    Args:
        user_id: 用户ID
        page: 页码
        page_size: 每页数量
        db: 数据库会话

    Returns:
        扫描记录列表
    """
    try:
        # 计算偏移量
        offset = (page - 1) * page_size

        # 查询扫描记录
        result = await db.execute(
            select(CompanyScan)
            .where(CompanyScan.user_id == user_id)
            .order_by(CompanyScan.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        scans = result.scalars().all()

        # 查询总数
        count_result = await db.execute(
            select(CompanyScan.id)
            .where(CompanyScan.user_id == user_id)
        )
        total = len(count_result.all())

        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": [
                    {
                        "id": scan.id,
                        "company_name": scan.company_name,
                        "risk_level": scan.risk_level,
                        "risk_score": scan.risk_score,
                        "status": scan.status,
                        "created_at": scan.created_at.isoformat() if scan.created_at else None
                    }
                    for scan in scans
                ],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        )

    except Exception as e:
        logger.error(f"获取扫描列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取扫描列表失败"
        )

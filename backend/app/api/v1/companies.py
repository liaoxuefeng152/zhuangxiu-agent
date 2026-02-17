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
from app.services.juhecha_service import juhecha_service
from app.schemas import (
    CompanyScanRequest, CompanyScanResponse, ApiResponse, RiskLevel, ScanStatus
)

router = APIRouter(prefix="/companies", tags=["公司检测"])
logger = logging.getLogger(__name__)


async def analyze_company_background(company_scan_id: int, company_name: str, db: AsyncSession):
    """
    后台任务：分析公司信息（使用聚合数据API，支持缓存）
    只返回原始数据，不做风险评价

    Args:
        company_scan_id: 扫描记录ID
        company_name: 公司名称
        db: 数据库会话
    """
    try:
        logger.info(f"开始分析公司信息: {company_name}")

        # 1. 先检查是否已经有其他用户扫描过这个公司（缓存机制）
        # 查找最近30天内完成的相同公司扫描记录
        from datetime import datetime, timedelta
        from sqlalchemy import and_
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        cache_result = await db.execute(
            select(CompanyScan)
            .where(
                and_(
                    CompanyScan.company_name == company_name,
                    CompanyScan.status == "completed",
                    CompanyScan.created_at >= thirty_days_ago
                )
            )
            .order_by(CompanyScan.created_at.desc())
            .limit(1)
        )
        cached_scan = cache_result.scalar_one_or_none()
        
        comprehensive_result = None
        use_cache = False
        
        if cached_scan and cached_scan.company_info and cached_scan.legal_risks:
            # 使用缓存的数据
            logger.info(f"使用缓存的公司分析数据: {company_name}")
            use_cache = True
            
            # 从缓存记录构建分析结果
            comprehensive_result = {
                "enterprise_info": cached_scan.company_info or {},
                "legal_analysis": {
                    "legal_case_count": cached_scan.legal_risks.get("legal_case_count", 0),
                    "decoration_related_cases": cached_scan.legal_risks.get("decoration_related_cases", 0),
                    "recent_cases": cached_scan.legal_risks.get("legal_cases", []),
                    "case_types": cached_scan.legal_risks.get("case_types", [])
                }
            }
        else:
            # 没有缓存，调用聚合数据API
            logger.info(f"调用聚合数据API分析公司: {company_name}")
            comprehensive_result = await juhecha_service.analyze_company_comprehensive(company_name)
        
        if not comprehensive_result:
            raise Exception("公司分析失败，无法获取分析结果")
        
        # 获取企业信息
        enterprise_info = comprehensive_result.get("enterprise_info", {})
        
        # 获取法律分析结果
        legal_analysis = comprehensive_result.get("legal_analysis", {})
        
        # 更新数据库
        result = await db.execute(select(CompanyScan).where(CompanyScan.id == company_scan_id))
        company_scan = result.scalar_one_or_none()

        if company_scan:
            # 存储企业信息
            company_scan.company_info = enterprise_info
            
            # 不再存储风险等级和评分（只保留字段兼容性，设为默认值）
            company_scan.risk_level = "compliant"  # 默认值，用于兼容
            company_scan.risk_score = 0  # 默认值，用于兼容
            
            # 不再存储风险原因
            company_scan.risk_reasons = []
            
            # 存储法律案件信息
            legal_info = {
                "legal_case_count": legal_analysis.get("legal_case_count", 0),
                "legal_cases": legal_analysis.get("recent_cases", []),
                "decoration_related_cases": legal_analysis.get("decoration_related_cases", 0),
                "case_types": legal_analysis.get("case_types", []),
                "recent_case_date": legal_analysis.get("recent_case_date", "")
            }
            company_scan.legal_risks = legal_info
            
            company_scan.status = "completed"
            
            # 标记是否使用了缓存
            if use_cache:
                company_scan.unlock_type = "cached"  # 新增字段，标记使用了缓存

            await db.commit()
            logger.info(f"公司信息分析完成: {company_name}")
            logger.info(f"企业信息: {enterprise_info.get('name', '未知')}, 成立时间: {enterprise_info.get('start_date', '未知')}")
            logger.info(f"法律案件数量: {legal_info.get('legal_case_count', 0)}, 装修相关案件: {legal_info.get('decoration_related_cases', 0)}")
            if use_cache:
                logger.info(f"✓ 使用了缓存数据，节省了API调用")

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
        logger.error(f"公司信息分析失败: {e}", exc_info=True)

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
    输入≥3字符时返回匹配建议，使用聚合数据企业工商信息API
    """
    keyword = q.strip()
    if len(keyword) < 3:
        return ApiResponse(code=0, msg="success", data={"list": []})

    results = []
    try:
        # 1. 使用聚合数据企业工商信息API搜索
        logger.info(f"搜索公司: {keyword}, limit: {limit}")
        enterprise_result = await juhecha_service.search_enterprise_info(keyword, limit)
        logger.info(f"聚合数据API返回结果数量: {len(enterprise_result) if enterprise_result else 0}")
        if enterprise_result:
            results = [{"name": r["name"]} for r in enterprise_result if r.get("name")]
            logger.info(f"处理后结果数量: {len(results)}")
    except Exception as e:
        logger.error(f"聚合数据企业搜索失败: {e}", exc_info=True)

    # 2. 本地 company_scans 表模糊匹配补充（仅当有用户ID时）
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
            legal_risks=None,
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

        # 安全地转换risk_level，避免无效枚举值导致异常
        risk_level_value = RiskLevel.COMPLIANT
        if company_scan.risk_level:
            try:
                risk_level_value = RiskLevel(company_scan.risk_level)
            except ValueError:
                logger.warning(f"无效的risk_level值: {company_scan.risk_level}, 使用默认值COMPLIANT")
                risk_level_value = RiskLevel.COMPLIANT

        # 安全地转换status
        status_value = ScanStatus.PENDING
        if company_scan.status:
            try:
                status_value = ScanStatus(company_scan.status)
            except ValueError:
                logger.warning(f"无效的status值: {company_scan.status}, 使用默认值PENDING")
                status_value = ScanStatus.PENDING

        # 构建预览数据（用于解锁页面展示）
        preview_data = None
        if company_scan.company_info or company_scan.legal_risks:
            preview_data = {
                "enterprise_info_preview": {
                    "name": company_scan.company_name,
                    "enterprise_age": company_scan.company_info.get("enterprise_age") if company_scan.company_info else None,
                    "start_date": company_scan.company_info.get("start_date") if company_scan.company_info else None,
                } if company_scan.company_info else None,
                "legal_analysis_preview": {
                    "legal_case_count": company_scan.legal_risks.get("legal_case_count", 0) if company_scan.legal_risks else 0,
                    "decoration_related_cases": company_scan.legal_risks.get("decoration_related_cases", 0) if company_scan.legal_risks else 0,
                    "recent_case_date": company_scan.legal_risks.get("recent_case_date", "") if company_scan.legal_risks else "",
                    "case_types": company_scan.legal_risks.get("case_types", []) if company_scan.legal_risks else [],
                } if company_scan.legal_risks else None,
                "risk_summary_preview": {
                    "risk_level": company_scan.risk_level,
                    "risk_score": company_scan.risk_score if company_scan.risk_score is not None else 0,
                    "top_risk_reasons": company_scan.risk_reasons[:3] if company_scan.risk_reasons else [],
                }
            }
        
        return CompanyScanResponse(
            id=company_scan.id,
            company_name=company_scan.company_name,
            risk_level=risk_level_value,
            risk_score=company_scan.risk_score if company_scan.risk_score is not None else 0,
            risk_reasons=company_scan.risk_reasons or [],
            complaint_count=company_scan.complaint_count or 0,
            legal_risks=company_scan.legal_risks,
            status=status_value,
            is_unlocked=getattr(company_scan, "is_unlocked", False),
            created_at=company_scan.created_at,
            # 添加预览数据字段
            preview_data=preview_data
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


@router.delete("/scans/{scan_id}")
async def delete_scan(
    scan_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    删除公司扫描记录

    Args:
        scan_id: 扫描记录ID
        user_id: 用户ID
        db: 数据库会话

    Returns:
        删除结果
    """
    try:
        # 查询扫描记录
        result = await db.execute(
            select(CompanyScan)
            .where(CompanyScan.id == scan_id, CompanyScan.user_id == user_id)
        )
        scan = result.scalar_one_or_none()

        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="扫描记录不存在"
            )

        # 删除记录
        await db.delete(scan)
        await db.commit()

        return ApiResponse(
            code=0,
            msg="success",
            data={"deleted": True, "scan_id": scan_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除扫描记录失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除失败"
        )

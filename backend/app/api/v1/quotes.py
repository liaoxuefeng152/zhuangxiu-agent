"""
装修决策Agent - 报价单分析API
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging
import oss2

from app.core.database import get_db
from app.core.config import settings
from app.models import Quote, User
from app.services import ocr_service, risk_analyzer_service
from app.schemas import (
    QuoteUploadRequest, QuoteUploadResponse, QuoteAnalysisResponse, ApiResponse
)

router = APIRouter(prefix="/quotes", tags=["报价单分析"])
logger = logging.getLogger(__name__)


async def analyze_quote_background(quote_id: int, ocr_text: str, db: AsyncSession):
    """
    后台任务：分析报价单

    Args:
        quote_id: 报价单ID
        ocr_text: OCR识别的文本
        db: 数据库会话
    """
    try:
        logger.info(f"开始分析报价单: {quote_id}")

        # 提取总价
        import re
        total_price = None
        price_match = re.search(r'[总合]计[^\d]*(\d+(?:\.\d+)?)', ocr_text)
        if price_match:
            total_price = float(price_match.group(1))

        # 调用AI分析
        analysis_result = await risk_analyzer_service.analyze_quote(ocr_text, total_price)

        # 更新数据库
        result = await db.execute(select(Quote).where(Quote.id == quote_id))
        quote = result.scalar_one_or_none()

        if quote:
            quote.status = "completed"
            quote.ocr_result = {"text": ocr_text}
            quote.result_json = analysis_result
            quote.risk_score = analysis_result.get("risk_score", 0)
            quote.high_risk_items = analysis_result.get("high_risk_items", [])
            quote.warning_items = analysis_result.get("warning_items", [])
            quote.missing_items = analysis_result.get("missing_items", [])
            quote.overpriced_items = analysis_result.get("overpriced_items", [])
            quote.total_price = analysis_result.get("total_price") or total_price
            quote.market_ref_price = analysis_result.get("market_ref_price")

            await db.commit()
            logger.info(f"报价单分析完成: {quote_id}, 风险评分: {quote.risk_score}")
        else:
            logger.error(f"报价单不存在: {quote_id}")

    except Exception as e:
        logger.error(f"报价单分析失败: {e}", exc_info=True)

        try:
            result = await db.execute(select(Quote).where(Quote.id == quote_id))
            quote = result.scalar_one_or_none()
            if quote:
                quote.status = "failed"
                await db.commit()
        except:
            pass


def upload_file_to_oss(file: UploadFile, file_type: str = "quote") -> str:
    """
    上传文件到阿里云OSS

    Args:
        file: 上传的文件
        file_type: 文件类型

    Returns:
        文件URL
    """
    try:
        # 初始化OSS客户端
        auth = oss2.Auth(
            settings.ALIYUN_ACCESS_KEY_ID,
            settings.ALIYUN_ACCESS_KEY_SECRET
        )
        bucket = oss2.Bucket(
            auth,
            settings.ALIYUN_OSS_ENDPOINT,
            settings.ALIYUN_OSS_BUCKET
        )

        # 生成文件名
        import time
        import random
        filename = f"{file_type}/{int(time.time())}_{random.randint(1000, 9999)}_{file.filename}"

        # 上传文件
        bucket.put_object(filename, file.file)

        # 返回文件URL
        file_url = f"https://{settings.ALIYUN_OSS_BUCKET}.{settings.ALIYUN_OSS_ENDPOINT}/{filename}"
        logger.info(f"文件上传成功: {file_url}")
        return file_url

    except Exception as e:
        logger.error(f"OSS文件上传失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件上传失败"
        )


@router.post("/upload", response_model=QuoteUploadResponse)
async def upload_quote(
    user_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    上传报价单并开始分析

    Args:
        user_id: 用户ID
        background_tasks: 后台任务
        file: 上传的文件
        db: 数据库会话

    Returns:
        上传响应
    """
    try:
        # 验证文件类型
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小不能超过{settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB"
            )

        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"仅支持{', '.join(settings.ALLOWED_FILE_TYPES)}格式"
            )

        # 上传到OSS
        file_url = upload_file_to_oss(file, "quote")

        # 创建报价单记录
        quote = Quote(
            user_id=user_id,
            file_url=file_url,
            file_name=file.filename,
            file_size=file.size,
            file_type=file_ext,
            status="analyzing"
        )

        db.add(quote)
        await db.commit()
        await db.refresh(quote)

        # OCR识别
        ocr_result = await ocr_service.recognize_quote(file_url, file_ext)
        if not ocr_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OCR识别失败，请重新上传"
            )

        ocr_text = ocr_result.get("content", "")

        # 启动后台分析任务
        background_tasks.add_task(
            analyze_quote_background,
            quote.id,
            ocr_text,
            db
        )

        logger.info(f"报价单上传成功: {file.filename}, ID: {quote.id}")

        return QuoteUploadResponse(
            task_id=quote.id,
            file_name=quote.file_name,
            file_type=quote.file_type,
            status=quote.status
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"报价单上传失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="上传失败"
        )


@router.get("/quote/{quote_id}", response_model=QuoteAnalysisResponse)
async def get_quote_analysis(
    quote_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取报价单分析结果

    Args:
        quote_id: 报价单ID
        user_id: 用户ID
        db: 数据库会话

    Returns:
        分析结果
    """
    try:
        result = await db.execute(
            select(Quote)
            .where(Quote.id == quote_id, Quote.user_id == user_id)
        )
        quote = result.scalar_one_or_none()

        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报价单不存在"
            )

        return QuoteAnalysisResponse(
            id=quote.id,
            file_name=quote.file_name,
            status=quote.status,
            risk_score=quote.risk_score,
            high_risk_items=quote.high_risk_items or [],
            warning_items=quote.warning_items or [],
            missing_items=quote.missing_items or [],
            overpriced_items=quote.overpriced_items or [],
            total_price=quote.total_price,
            market_ref_price=quote.market_ref_price,
            is_unlocked=quote.is_unlocked,
            created_at=quote.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取报价单分析结果失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取分析结果失败"
        )


@router.get("/list")
async def list_quotes(
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户的报价单列表

    Args:
        user_id: 用户ID
        page: 页码
        page_size: 每页数量
        db: 数据库会话

    Returns:
        报价单列表
    """
    try:
        offset = (page - 1) * page_size

        result = await db.execute(
            select(Quote)
            .where(Quote.user_id == user_id)
            .order_by(Quote.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        quotes = result.scalars().all()

        count_result = await db.execute(
            select(Quote.id)
            .where(Quote.user_id == user_id)
        )
        total = len(count_result.all())

        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": [
                    {
                        "id": quote.id,
                        "file_name": quote.file_name,
                        "total_price": quote.total_price,
                        "risk_score": quote.risk_score,
                        "status": quote.status,
                        "is_unlocked": quote.is_unlocked,
                        "created_at": quote.created_at.isoformat() if quote.created_at else None
                    }
                    for quote in quotes
                ],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        )

    except Exception as e:
        logger.error(f"获取报价单列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取列表失败"
        )

"""
装修决策Agent - 报价单分析API
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging
import oss2
import base64
import io

from app.core.database import get_db
from app.core.security import get_user_id
from app.core.config import settings
from app.models import Quote, User
from app.services import coze_service, risk_analyzer_service, send_progress_reminder
from app.services.message_service import create_message
from app.schemas import (
    QuoteUploadRequest, QuoteUploadResponse, QuoteAnalysisResponse, ApiResponse
)

router = APIRouter(prefix="/quotes", tags=["报价单分析"])
logger = logging.getLogger(__name__)


async def analyze_quote_background(quote_id: int, image_url: str, db: AsyncSession):
    """
    后台任务：分析报价单（使用扣子智能体）

    Args:
        quote_id: 报价单ID
        image_url: 图片URL（OSS签名URL）
        db: 数据库会话
    """
    try:
        logger.info(f"开始分析报价单: {quote_id}, 图片URL: {image_url[:100]}...")

        # 查询报价单记录
        result = await db.execute(select(Quote).where(Quote.id == quote_id))
        quote = result.scalar_one_or_none()
        
        if not quote:
            logger.error(f"报价单不存在: {quote_id}")
            return

        # V2.6.2优化：更新分析进度
        quote.analysis_progress = {"step": "analyzing", "progress": 50, "message": "正在分析报价单..."}
        await db.commit()

        # 调用扣子智能体分析图片
        analysis_result = await coze_service.analyze_quote(image_url, quote.user_id)
        
        if not analysis_result:
            logger.error(f"扣子智能体分析失败: {quote_id}")
            quote.status = "failed"
            quote.analysis_progress = {"step": "failed", "progress": 0, "message": "AI分析失败"}
            await db.commit()
            return

        # 检查是否为原始文本格式
        if "raw_text" in analysis_result:
            logger.warning(f"扣子返回原始文本，尝试使用风险分析器: {quote_id}")
            # 如果扣子返回原始文本，尝试使用原有的风险分析器
            raw_text = analysis_result["raw_text"]
            try:
                # 提取总价
                import re
                total_price = None
                price_match = re.search(r'[总合]计[^\d]*(\d+(?:\.\d+)?)', raw_text)
                if price_match:
                    total_price = float(price_match.group(1))
                
                # 调用AI分析
                analysis_result = await risk_analyzer_service.analyze_quote(raw_text, total_price)
            except Exception as e:
                logger.error(f"风险分析器处理失败: {e}", exc_info=True)
                quote.status = "failed"
                quote.analysis_progress = {"step": "failed", "progress": 0, "message": "AI分析失败"}
                await db.commit()
                return

        # 若返回的是"服务不可用"兜底结果，视为分析失败
        suggestions = analysis_result.get("suggestions") or []
        if suggestions and suggestions[0] == "AI分析服务暂时不可用，请稍后重试":
            quote.status = "failed"
            quote.analysis_progress = {"step": "failed", "progress": 0, "message": "AI分析服务暂时不可用"}
            await db.commit()
            logger.warning(f"报价单 {quote_id} AI 返回兜底结果，标记为失败")
            return

        # V2.6.2优化：更新分析进度
        quote.analysis_progress = {"step": "generating", "progress": 90, "message": "生成报告中..."}
        await db.commit()

        # 更新报价单记录
        quote.status = "completed"
        quote.result_json = analysis_result
        quote.risk_score = analysis_result.get("risk_score", 0)
        quote.high_risk_items = analysis_result.get("high_risk_items", [])
        quote.warning_items = analysis_result.get("warning_items", [])
        quote.missing_items = analysis_result.get("missing_items", [])
        quote.overpriced_items = analysis_result.get("overpriced_items", [])
        quote.total_price = analysis_result.get("total_price")
        
        # 处理market_ref_price
        market_ref_price = analysis_result.get("market_ref_price")
        if isinstance(market_ref_price, str):
            # 尝试从字符串中提取数字范围（如"65000-75000元"）
            import re
            price_match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)', market_ref_price)
            if price_match:
                # 取平均值
                min_price = float(price_match.group(1))
                max_price = float(price_match.group(2))
                quote.market_ref_price = (min_price + max_price) / 2
            else:
                # 尝试提取单个数字
                single_match = re.search(r'(\d+(?:\.\d+)?)', market_ref_price)
                if single_match:
                    quote.market_ref_price = float(single_match.group(1))
                else:
                    quote.market_ref_price = None
        elif isinstance(market_ref_price, (int, float)):
            quote.market_ref_price = float(market_ref_price)
        else:
            quote.market_ref_price = None

        # V2.6.2优化：首次报告免费 - 检查用户是否首次使用
        user_result = await db.execute(select(User).where(User.id == quote.user_id))
        user = user_result.scalar_one_or_none()
        if user:
            # 检查用户是否有其他已解锁的报告（报价单、合同、公司检测）
            from app.models import Contract, CompanyScan
            has_unlocked_quote = await db.execute(
                select(Quote.id).where(
                    Quote.user_id == quote.user_id,
                    Quote.id != quote_id,
                    Quote.is_unlocked == True
                ).limit(1)
            )
            has_unlocked_contract = await db.execute(
                select(Contract.id).where(
                    Contract.user_id == quote.user_id,
                    Contract.is_unlocked == True
                ).limit(1)
            )
            has_unlocked_company = await db.execute(
                select(CompanyScan.id).where(
                    CompanyScan.user_id == quote.user_id
                ).limit(1)
            )
            
            # 如果用户是首次使用（没有任何已解锁的报告），自动免费解锁
            if not has_unlocked_quote.scalar_one_or_none() and \
               not has_unlocked_contract.scalar_one_or_none() and \
               not has_unlocked_company.scalar_one_or_none():
                quote.is_unlocked = True
                quote.unlock_type = "first_free"
                logger.info(f"首次报告免费解锁: 报价单 {quote_id}, 用户 {quote.user_id}")

        # V2.6.2优化：分析完成，更新进度
        quote.analysis_progress = {"step": "completed", "progress": 100, "message": "分析完成"}
        # 写入消息中心，与验收报告一致，用户可在小程序内看到通知
        from urllib.parse import quote as url_quote
        _name = (quote.file_name or "报价分析报告")
        await create_message(
            db, quote.user_id,
            category="report",
            title="报价分析报告已生成",
            content=f"风险评分：{quote.risk_score}，请查看详情",
            summary=f"报价单分析完成，风险评分 {quote.risk_score}",
            link_url=f"/pages/report-detail/index?type=quote&scanId={quote_id}&name={url_quote(_name)}",
        )
        await db.commit()
        logger.info(f"报价单分析完成: {quote_id}, 风险评分: {quote.risk_score}")
        # 发送微信模板消息「家装服务进度提醒」
        try:
            user_result = await db.execute(select(User).where(User.id == quote.user_id))
            user = user_result.scalar_one_or_none()
            if user and getattr(user, "wx_openid", None):
                send_progress_reminder(user.wx_openid, "报价单分析报告")
        except Exception as e:
            logger.debug("发送报价单模板消息跳过: %s", e)

    except Exception as e:
        logger.error(f"报价单分析失败: {e}", exc_info=True)

        try:
            result = await db.execute(select(Quote).where(Quote.id == quote_id))
            quote = result.scalar_one_or_none()
            if quote:
                quote.status = "failed"
                quote.analysis_progress = {"step": "failed", "progress": 0, "message": "分析过程异常"}
                await db.commit()
        except:
            pass


def upload_file_to_oss(file: UploadFile, file_type: str = "quote", user_id: Optional[int] = None, 
                       is_photo: bool = True) -> str:
    """
    上传文件到阿里云OSS（统一入口）
    
    使用统一的OSS服务，确保所有照片都上传到OSS
    - 照片上传到 zhuangxiu-images-dev-photo (生命周期1年)
    - 其他文件上传到 zhuangxiu-images-dev

    Args:
        file: 上传的文件
        file_type: 文件类型（quote/contract/acceptance/construction/material-check）
        user_id: 用户ID（可选，用于路径组织）
        is_photo: 是否为照片（True使用照片bucket，False使用默认bucket）

    Returns:
        对象键（object_key），用于存储及通过 GET /api/v1/oss/sign-url 获取临时 URL
    """
    from app.services.oss_service import oss_service
    
    try:
        return oss_service.upload_upload_file(file, file_type, user_id, is_photo=is_photo)
    except Exception as e:
        logger.error(f"OSS文件上传失败: {e}", exc_info=True)
        # 开发环境：如果OSS上传失败，返回模拟URL
        if hasattr(settings, 'DEBUG') and settings.DEBUG:
            import time
            import random
            fname = file.filename or "photo.jpg"
            filename = f"{file_type}/{int(time.time())}_{random.randint(1000, 9999)}_{fname}"
            logger.warning(f"OSS上传失败，使用模拟URL: {filename}")
            return f"https://mock-oss.example.com/{filename}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )


@router.post("/upload", response_model=QuoteUploadResponse)
async def upload_quote(
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_user_id),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    上传报价单并开始分析（使用扣子智能体）

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

        # 上传到OSS（统一使用OSS服务，报价单不是照片，使用默认bucket）
        object_key = upload_file_to_oss(file, "quote", user_id, is_photo=False)
        
        # 生成OSS签名URL（有效期1小时）
        from app.services.oss_service import oss_service
        try:
            image_url = oss_service.generate_signed_url(object_key, expires=3600)
            logger.info(f"生成OSS签名URL: {image_url[:100]}...")
        except Exception as e:
            logger.error(f"生成OSS签名URL失败: {e}", exc_info=True)
            # 如果生成签名URL失败，使用原始object_key
            image_url = f"https://{settings.ALIYUN_OSS_BUCKET}.{settings.ALIYUN_OSS_ENDPOINT}/{object_key}"

        # 创建报价单记录
        quote = Quote(
            user_id=user_id,
            file_url=object_key,
            file_name=file.filename,
            file_size=file.size,
            file_type=file_ext,
            status="analyzing",
            analysis_progress={"step": "uploading", "progress": 0, "message": "正在上传文件..."}
        )

        db.add(quote)
        await db.commit()
        await db.refresh(quote)

        # V2.6.2优化：更新分析进度
        quote.analysis_progress = {"step": "processing", "progress": 30, "message": "正在处理图片..."}
        await db.commit()

        # 启动后台分析任务（使用扣子智能体）
        background_tasks.add_task(
            analyze_quote_background,
            quote.id,
            image_url,
            db
        )

        logger.info(f"报价单上传成功: {file.filename}, ID: {quote.id}, 图片URL: {image_url[:100]}...")

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
    user_id: int = Depends(get_user_id),
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

        result_json = quote.result_json
        if quote.status == "failed":
            result_json = None
        elif isinstance(result_json, dict):
            suggestions = result_json.get("suggestions") or []
            if suggestions and suggestions[0] == "AI分析服务暂时不可用，请稍后重试":
                result_json = None

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
            created_at=quote.created_at,
            # V2.6.2优化：返回分析进度
            analysis_progress=quote.analysis_progress or {"step": "pending", "progress": 0, "message": "等待分析"},
            # 返回AI分析完整结果（失败或兜底时不返回假数据）
            result_json=result_json
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
    user_id: int = Depends(get_user_id),
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


@router.delete("/{quote_id}")
async def delete_quote(
    quote_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    删除报价单记录

    Args:
        quote_id: 报价单ID
        user_id: 用户ID
        db: 数据库会话

    Returns:
        删除结果
    """
    try:
        # 查询报价单记录
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

        # 删除记录
        await db.delete(quote)
        await db.commit()

        return ApiResponse(
            code=0,
            msg="success",
            data={"deleted": True, "quote_id": quote_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除报价单记录失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除失败"
        )

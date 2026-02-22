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
from app.services import ocr_service, risk_analyzer_service, send_progress_reminder
from app.services.message_service import create_message
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

        # 若返回的是“服务不可用”兜底结果，视为分析失败，不按成功落库
        suggestions = analysis_result.get("suggestions") or []
        if suggestions and suggestions[0] == "AI分析服务暂时不可用，请稍后重试":
            result = await db.execute(select(Quote).where(Quote.id == quote_id))
            quote = result.scalar_one_or_none()
            if quote:
                quote.status = "failed"
                await db.commit()
                logger.warning(f"报价单 {quote_id} AI 返回兜底结果，标记为失败")
            return

        # 更新数据库
        result = await db.execute(select(Quote).where(Quote.id == quote_id))
        quote = result.scalar_one_or_none()

        if quote:
            # V2.6.2优化：更新分析进度
            quote.analysis_progress = {"step": "generating", "progress": 90, "message": "生成报告中..."}
            await db.commit()

            quote.status = "completed"
            quote.ocr_result = {"text": ocr_text}
            quote.result_json = analysis_result
            quote.risk_score = analysis_result.get("risk_score", 0)
            quote.high_risk_items = analysis_result.get("high_risk_items", [])
            quote.warning_items = analysis_result.get("warning_items", [])
            quote.missing_items = analysis_result.get("missing_items", [])
            quote.overpriced_items = analysis_result.get("overpriced_items", [])
            quote.total_price = analysis_result.get("total_price") or total_price
            # 处理market_ref_price：如果是字符串，尝试提取数字；如果是数字，直接使用；否则为None
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

        # 上传到OSS（统一使用OSS服务，报价单不是照片，使用默认bucket）
        object_key = upload_file_to_oss(file, "quote", user_id, is_photo=False)
        
        # 如果OSS配置不存在，使用Base64编码的文件内容进行OCR识别
        ocr_input = object_key
        if object_key.startswith("https://mock-oss.example.com"):
            # 开发环境：将文件内容转换为Base64
            import base64
            file.file.seek(0)  # 重置文件指针
            file_content = await file.read()
            base64_str = base64.b64encode(file_content).decode("utf-8")
            # PDF文件使用data:application/pdf;base64,前缀
            if file_ext == "pdf":
                ocr_input = f"data:application/pdf;base64,{base64_str}"
            else:
                ocr_input = f"data:image/{file_ext};base64,{base64_str}"
            logger.info(f"使用Base64编码进行OCR识别，文件大小: {len(file_content)} bytes")
        else:
            from app.services.oss_service import oss_service

            # 尝试使用Base64编码而不是URL，避免阿里云OCR API的URL编码问题
            try:
                # 读取文件内容并转换为Base64
                file.file.seek(0)  # 重置文件指针
                file_content = await file.read()
                file.file.seek(0)  # 再次重置，以防后续使用
                
                base64_str = base64.b64encode(file_content).decode("utf-8")
                if file_ext == "pdf":
                    ocr_input = f"data:application/pdf;base64,{base64_str}"
                else:
                    ocr_input = f"data:image/{file_ext};base64,{base64_str}"
                logger.info(f"使用Base64编码进行OCR识别，避免URL编码问题，文件大小: {len(file_content)} bytes")
            except Exception as e:
                logger.warning(f"Base64编码失败，回退到URL方式: {e}")
                ocr_input = oss_service.sign_url_for_key(object_key, expires=3600)

        # 创建报价单记录
        quote = Quote(
            user_id=user_id,
            file_url=object_key,
            file_name=file.filename,
            file_size=file.size,
            file_type=file_ext,
            status="analyzing",
            analysis_progress={"step": "ocr", "progress": 0, "message": "正在识别文字..."}
        )

        db.add(quote)
        await db.commit()
        await db.refresh(quote)

        # V2.6.2优化：更新分析进度
        quote.analysis_progress = {"step": "ocr", "progress": 20, "message": "正在识别文字..."}
        await db.commit()

        # OCR识别
        logger.info(f"开始OCR识别，文件类型: {file_ext}, 输入类型: {'URL' if ocr_input.startswith('http') else 'Base64'}")
        
        try:
            ocr_result = await ocr_service.recognize_quote(ocr_input, file_ext)
        except Exception as ocr_error:
            logger.error(f"OCR识别异常: {ocr_error}", exc_info=True)
            ocr_result = None
        
        if not ocr_result:
            logger.error(f"OCR识别失败，文件: {file.filename}, 类型: {file_ext}, 输入类型: {'URL' if ocr_input.startswith('http') else 'Base64'}")
            
            # 尝试使用更小的图片重试（如果图片太大）
            try:
                logger.info("尝试使用图片压缩后重试OCR识别...")
                
                # 将Base64解码为图片
                import io
                from PIL import Image
                
                if ocr_input.startswith("data:image/"):
                    # 提取Base64部分
                    base64_data = ocr_input.split(",")[1]
                    image_data = base64.b64decode(base64_data)
                else:
                    # 已经是Base64
                    image_data = base64.b64decode(ocr_input)
                
                # 打开图片
                image = Image.open(io.BytesIO(image_data))
                
                # 检查图片尺寸
                width, height = image.size
                logger.info(f"图片原始尺寸: {width}x{height}")
                
                # 如果图片太高（长宽比超过10:1），进行裁剪
                if height > width * 10:
                    logger.info(f"图片长宽比过高 ({height/width:.1f}:1)，进行裁剪")
                    # 裁剪为多个部分
                    max_height = width * 10
                    parts = []
                    for i in range(0, height, max_height):
                        part_height = min(max_height, height - i)
                        box = (0, i, width, i + part_height)
                        part = image.crop(box)
                        parts.append(part)
                    
                    # 分别识别每个部分
                    all_text = ""
                    for j, part in enumerate(parts):
                        logger.info(f"识别图片第 {j+1}/{len(parts)} 部分")
                        # 将部分转换为Base64
                        buffered = io.BytesIO()
                        part.save(buffered, format="PNG")
                        part_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                        part_url = f"data:image/png;base64,{part_base64}"
                        
                        # 识别部分
                        part_result = await ocr_service.recognize_quote(part_url, "image")
                        if part_result:
                            all_text += part_result.get("content", "") + "\n"
                    
                    if all_text:
                        logger.info(f"分段OCR识别成功，总文本长度: {len(all_text)}")
                        ocr_text = all_text
                        
                        # 更新报价单状态
                        quote.analysis_progress = {"step": "analyzing", "progress": 50, "message": "正在分析风险..."}
                        await db.commit()
                    else:
                        raise Exception("分段OCR识别也失败")
                else:
                    # 图片尺寸正常，但OCR失败
                    raise Exception("OCR识别失败，图片尺寸正常")
                    
            except Exception as retry_error:
                logger.error(f"OCR重试也失败: {retry_error}")
                
                # 更新报价单状态为失败
                quote.status = "failed"
                quote.analysis_progress = {"step": "failed", "progress": 0, "message": "OCR识别失败"}
                await db.commit()
                
                # 生产环境：返回更友好的错误信息
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OCR识别失败，请检查：1. 图片是否清晰 2. 文件格式是否正确 3. 图片尺寸是否过大（建议宽度:高度不超过1:10）4. 或联系客服"
                )
        else:
            ocr_text = ocr_result.get("content", "")

        # V2.6.2优化：更新分析进度
        quote.analysis_progress = {"step": "analyzing", "progress": 50, "message": "正在分析风险..."}
        await db.commit()

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
            result_json=result_json,
            # 返回OCR识别结果
            ocr_result=quote.ocr_result
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

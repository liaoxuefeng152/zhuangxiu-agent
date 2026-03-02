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


def _parse_raw_text_to_structured(raw_text: str) -> dict:
    """
    将原始文本解析为结构化数据
    
    Args:
        raw_text: AI返回的原始文本
        
    Returns:
        结构化分析结果
    """
    import re
    import json
    
    result = {
        "raw_text": raw_text,
        "risk_score": 50,
        "high_risk_items": [],
        "warning_items": [],
        "missing_items": [],
        "overpriced_items": [],
        "total_price": None,
        "market_ref_price": None,
        "suggestions": [],
        "summary": "报价单分析完成"
    }
    
    try:
        # 1. 提取总价
        price_match = re.search(r'[总合]计[^\d]*(\d+(?:\.\d+)?)', raw_text)
        if price_match:
            result["total_price"] = float(price_match.group(1))
        
        # 2. 提取风险评分
        risk_match = re.search(r'风险[^\d]*(\d+(?:\.\d+)?)', raw_text)
        if risk_match:
            result["risk_score"] = int(float(risk_match.group(1)))
        
        # 3. 提取高风险项目
        high_risk_section = re.search(r'高风险[项项]?目[：:](.*?)(?=\n\n|\n[A-Za-z]|$)', raw_text, re.DOTALL)
        if high_risk_section:
            high_risk_text = high_risk_section.group(1)
            # 按行分割，每行作为一个高风险项目
            lines = [line.strip() for line in high_risk_text.split('\n') if line.strip()]
            for line in lines:
                if line and len(line) > 3:  # 过滤空行和过短的行
                    result["high_risk_items"].append({
                        "name": line[:50],
                        "reason": line
                    })
        
        # 4. 提取警告项目
        warning_section = re.search(r'警告[项项]?目[：:](.*?)(?=\n\n|\n[A-Za-z]|$)', raw_text, re.DOTALL)
        if warning_section:
            warning_text = warning_section.group(1)
            lines = [line.strip() for line in warning_text.split('\n') if line.strip()]
            for line in lines:
                if line and len(line) > 3:
                    result["warning_items"].append({
                        "name": line[:50],
                        "reason": line
                    })
        
        # 5. 提取缺失项目
        missing_section = re.search(r'缺失[项项]?目[：:](.*?)(?=\n\n|\n[A-Za-z]|$)', raw_text, re.DOTALL)
        if missing_section:
            missing_text = missing_section.group(1)
            lines = [line.strip() for line in missing_text.split('\n') if line.strip()]
            for line in lines:
                if line and len(line) > 3:
                    result["missing_items"].append({
                        "name": line[:50],
                        "suggestion": "建议补充此项"
                    })
        
        # 6. 提取价格过高项目
        overprice_section = re.search(r'价格过高[项项]?目[：:](.*?)(?=\n\n|\n[A-Za-z]|$)', raw_text, re.DOTALL)
        if overprice_section:
            overprice_text = overprice_section.group(1)
            lines = [line.strip() for line in overprice_text.split('\n') if line.strip()]
            for line in lines:
                if line and len(line) > 3:
                    # 尝试提取价格
                    price_matches = re.findall(r'(\d+(?:\.\d+)?)', line)
                    current_price = float(price_matches[0]) if price_matches else 0
                    market_price = float(price_matches[1]) if len(price_matches) > 1 else current_price * 0.8
                    
                    result["overpriced_items"].append({
                        "name": line[:50],
                        "current_price": current_price,
                        "market_price": market_price
                    })
        
        # 7. 提取建议
        suggestions_section = re.search(r'建议[：:](.*?)(?=\n\n|\n[A-Za-z]|$)', raw_text, re.DOTALL)
        if suggestions_section:
            suggestions_text = suggestions_section.group(1)
            lines = [line.strip() for line in suggestions_text.split('\n') if line.strip()]
            result["suggestions"] = lines
        
        # 8. 提取总结
        summary_match = re.search(r'总结[：:](.*?)(?=\n\n|\n[A-Za-z]|$)', raw_text, re.DOTALL)
        if summary_match:
            result["summary"] = summary_match.group(1).strip()[:200]
        
        logger.info(f"成功从原始文本中提取结构化数据")
        return result
        
    except Exception as e:
        logger.error(f"解析原始文本失败: {e}", exc_info=True)
        # 返回基本结果
        return result


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

        # 根据用户要求：前端必须原样展示AI智能体返回的数据
        # 不再进行二次分析，直接使用扣子智能体返回的结果
        logger.info(f"直接使用扣子智能体返回的报价单分析结果，不进行二次分析: {quote_id}")
        
        # 检查是否为原始文本格式
        if "raw_text" in analysis_result:
            logger.warning(f"扣子返回原始文本，尝试解析为结构化数据: {quote_id}")
            raw_text = analysis_result["raw_text"]
            
            # 尝试从原始文本中提取结构化数据
            try:
                # 首先尝试直接解析为JSON（可能AI返回了JSON但被包装在raw_text中）
                import json
                import re
                
                # 尝试查找JSON结构
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    try:
                        parsed_json = json.loads(json_str)
                        # 检查是否包含必要的字段
                        if "risk_score" in parsed_json or "total_price" in parsed_json:
                            logger.info(f"成功从原始文本中解析出JSON结构: {quote_id}")
                            analysis_result = parsed_json
                        else:
                            logger.warning(f"解析的JSON缺少必要字段，尝试智能解析: {quote_id}")
                            analysis_result = _parse_raw_text_to_structured(raw_text)
                    except json.JSONDecodeError:
                        logger.warning(f"原始文本中的JSON解析失败，尝试智能解析: {quote_id}")
                        analysis_result = _parse_raw_text_to_structured(raw_text)
                else:
                    # 没有找到JSON结构，尝试智能解析
                    logger.warning(f"原始文本中没有找到JSON结构，尝试智能解析: {quote_id}")
                    analysis_result = _parse_raw_text_to_structured(raw_text)
                    
            except Exception as parse_error:
                logger.error(f"解析原始文本失败: {parse_error}", exc_info=True)
                # 解析失败时，使用原始文本但提供更好的提示
                import re
                total_price = None
                price_match = re.search(r'[总合]计[^\d]*(\d+(?:\.\d+)?)', raw_text)
                if price_match:
                    total_price = float(price_match.group(1))
                
                analysis_result = {
                    "raw_text": raw_text,
                    "risk_score": 50,
                    "high_risk_items": [],
                    "warning_items": [],
                    "missing_items": [],
                    "overpriced_items": [],
                    "total_price": total_price,
                    "market_ref_price": None,
                    "suggestions": ["AI返回了文本分析结果，但格式需要优化"],
                    "summary": "报价单分析完成，已提取关键信息"
                }

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
        # 发送小程序订阅消息「报告生成通知」
        try:
            user_result = await db.execute(select(User).where(User.id == quote.user_id))
            user = user_result.scalar_one_or_none()
            if user and getattr(user, "wx_openid", None):
                # 导入小程序订阅消息服务
                from app.services.wechat_template_service import send_miniprogram_report_notification
                await send_miniprogram_report_notification(
                    user.wx_openid, 
                    "quote", 
                    quote.file_name or "报价分析报告",
                    quote_id
                )
        except Exception as e:
            logger.debug("发送小程序订阅消息跳过: %s", e)

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

        # 构建预览数据（用于解锁页面展示）
        preview_data = None
        if quote.status == "completed" and quote.result_json:
            # 从分析结果中提取预览数据
            result_json = quote.result_json
            preview_data = {
                "risk_summary_preview": {
                    "risk_score": quote.risk_score or 0,
                    "risk_level": "high" if (quote.risk_score or 0) >= 70 else "moderate" if (quote.risk_score or 0) >= 40 else "low",
                    "total_price": quote.total_price,
                    "market_ref_price": quote.market_ref_price,
                },
                "analysis_preview": {
                    "high_risk_items_count": len(quote.high_risk_items or []),
                    "warning_items_count": len(quote.warning_items or []),
                    "missing_items_count": len(quote.missing_items or []),
                    "overpriced_items_count": len(quote.overpriced_items or []),
                    "top_risks": [item.get("description", "风险项目")[:30] for item in (quote.high_risk_items or [])[:3]]
                }
            }
        elif quote.status == "analyzing":
            # 分析中的预览数据
            preview_data = {
                "analysis_status": "analyzing",
                "progress_message": quote.analysis_progress.get("message", "正在分析中...") if quote.analysis_progress else "正在分析中...",
                "progress_percentage": quote.analysis_progress.get("progress", 0) if quote.analysis_progress else 0
            }
        
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
            # 返回预览数据
            preview_data=preview_data
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

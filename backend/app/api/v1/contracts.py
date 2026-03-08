"""
装修决策Agent - 合同审核API
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.core.config import settings
from app.models import Contract, User
from app.services import send_progress_reminder
from app.services.message_service import create_message
from app.schemas import (
    ContractUploadRequest, ContractUploadResponse, ContractAnalysisResponse, ApiResponse
)
from app.api.v1.quotes import upload_file_to_oss

router = APIRouter(prefix="/contracts", tags=["合同审核"])
logger = logging.getLogger(__name__)


async def analyze_contract_background_with_coze_result(contract_id: int, coze_result: Dict[str, Any], ocr_text: str, db: AsyncSession):
    """
    后台任务：使用扣子智能体结果更新合同分析

    Args:
        contract_id: 合同ID
        coze_result: 扣子智能体返回的分析结果
        ocr_text: OCR识别的文本
        db: 数据库会话
    """
    try:
        logger.info(f"开始更新合同分析结果: {contract_id}")

        # 查询合同记录
        result = await db.execute(select(Contract).where(Contract.id == contract_id))
        contract = result.scalar_one_or_none()

        if not contract:
            logger.error(f"合同不存在: {contract_id}")
            return

        # V2.6.2优化：更新分析进度
        contract.analysis_progress = {"step": "generating", "progress": 90, "message": "生成报告中..."}
        await db.commit()

        # 根据用户要求：前端必须原样展示AI智能体返回的数据
        # 直接使用扣子智能体返回的结果，不进行格式转换
        contract.status = "completed"
        contract.ocr_result = {"text": ocr_text}
        contract.result_json = coze_result
        
        # 尝试从扣子结果中提取关键字段（兼容旧格式）
        # 注意：这些字段可能不存在，前端应该直接使用result_json
        
        # 处理risk_level字段：确保是字符串类型
        risk_level_value = coze_result.get("risk_level") or coze_result.get("risk_score")
        if isinstance(risk_level_value, (int, float)):
            # 将数字转换为字符串风险等级
            if risk_level_value >= 70:
                contract.risk_level = "high"
            elif risk_level_value >= 40:
                contract.risk_level = "medium"
            else:
                contract.risk_level = "low"
        elif isinstance(risk_level_value, str):
            contract.risk_level = risk_level_value
        else:
            contract.risk_level = "medium"  # 默认值
        
        contract.risk_items = coze_result.get("risk_items", []) or coze_result.get("high_risk_clauses", [])
        contract.unfair_terms = coze_result.get("unfair_terms", []) or coze_result.get("unfair_clauses", [])
        contract.missing_terms = coze_result.get("missing_terms", []) or coze_result.get("missing_clauses", [])
        
        # 处理suggested_modifications字段，确保是字典列表
        suggested_modifications = coze_result.get("suggested_modifications", [])
        if not suggested_modifications:
            suggestions = coze_result.get("suggestions", [])
            if suggestions:
                # 将字符串列表转换为字典列表
                suggested_modifications = []
                for suggestion in suggestions:
                    if isinstance(suggestion, dict):
                        # 如果已经是字典，直接使用
                        suggested_modifications.append(suggestion)
                    else:
                        # 如果是字符串，转换为字典格式
                        suggested_modifications.append({
                            "modification": str(suggestion),
                            "priority": "medium"
                        })
        contract.suggested_modifications = suggested_modifications

        # V2.6.2优化：首次报告免费 - 检查用户是否首次使用
        user_result = await db.execute(select(User).where(User.id == contract.user_id))
        user = user_result.scalar_one_or_none()
        if user:
            # 检查用户是否有其他已解锁的报告（报价单、合同、公司检测）
            from app.models import Quote, CompanyScan
            has_unlocked_quote = await db.execute(
                select(Quote.id).where(
                    Quote.user_id == contract.user_id,
                    Quote.is_unlocked == True
                ).limit(1)
            )
            has_unlocked_contract = await db.execute(
                select(Contract.id).where(
                    Contract.user_id == contract.user_id,
                    Contract.id != contract_id,
                    Contract.is_unlocked == True
                ).limit(1)
            )
            has_unlocked_company = await db.execute(
                select(CompanyScan.id).where(
                    CompanyScan.user_id == contract.user_id
                ).limit(1)
            )
            
            # 如果用户是首次使用（没有任何已解锁的报告），自动免费解锁
            if not has_unlocked_quote.scalar_one_or_none() and \
               not has_unlocked_contract.scalar_one_or_none() and \
               not has_unlocked_company.scalar_one_or_none():
                contract.is_unlocked = True
                contract.unlock_type = "first_free"
                logger.info(f"首次报告免费解锁: 合同 {contract_id}, 用户 {contract.user_id}")

        # V2.6.2优化：分析完成，更新进度
        contract.analysis_progress = {"step": "completed", "progress": 100, "message": "分析完成"}
        # 写入消息中心，与验收报告一致，用户可在小程序内看到通知
        from urllib.parse import quote as url_quote
        _name = (contract.file_name or "合同审核报告")
        await create_message(
            db, contract.user_id,
            category="report",
            title="合同审核报告已生成",
            content=f"风险等级：{contract.risk_level}，请查看详情",
            summary=f"合同审核完成，风险等级 {contract.risk_level}",
            link_url=f"/pages/report-detail/index?type=contract&scanId={contract_id}&name={url_quote(_name)}",
        )
        await db.commit()
        logger.info(f"合同分析完成: {contract_id}, 风险等级: {contract.risk_level}")
        # 发送小程序订阅消息「报告生成通知」
        try:
            user_result = await db.execute(select(User).where(User.id == contract.user_id))
            user = user_result.scalar_one_or_none()
            if user and getattr(user, "wx_openid", None):
                # 导入小程序订阅消息服务
                from app.services.wechat_template_service import send_miniprogram_report_notification
                await send_miniprogram_report_notification(
                    user.wx_openid, 
                    "contract", 
                    contract.file_name or "合同审核报告",
                    contract_id
                )
        except Exception as e:
            logger.debug("发送小程序订阅消息跳过: %s", e)

    except Exception as e:
        logger.error(f"合同分析结果更新失败: {e}", exc_info=True)

        try:
            result = await db.execute(select(Contract).where(Contract.id == contract_id))
            contract = result.scalar_one_or_none()
            if contract:
                contract.status = "failed"
                await db.commit()
        except:
            pass


@router.post("/upload", response_model=ContractUploadResponse)
async def upload_contract(
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_user_id),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    上传合同并开始分析

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

        # 上传到OSS（统一使用OSS服务，合同也使用照片bucket，确保扣子智能体能够访问）
        # 使用is_photo=True，确保使用照片bucket（zhuangxiu-images-photo），该bucket应该有正确的权限配置
        object_key = upload_file_to_oss(file, "contract", user_id, is_photo=True)
        
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
            ocr_input = oss_service.sign_url_for_key(object_key, expires=3600)

        # 创建合同记录
        contract = Contract(
            user_id=user_id,
            file_url=object_key,
            file_name=file.filename,
            file_size=file.size,
            file_type=file_ext,
            status="analyzing",
            analysis_progress={"step": "ocr", "progress": 0, "message": "正在识别文字..."}
        )

        db.add(contract)
        await db.commit()
        await db.refresh(contract)

        # V2.6.2优化：更新分析进度
        contract.analysis_progress = {"step": "ocr", "progress": 20, "message": "正在识别文字..."}
        await db.commit()

        # 合同审核重构：使用扣子智能体直接分析合同文件
        from app.services.coze_service import coze_service
        
        analysis_result = None
        try:
            # 直接使用OSS签名URL调用扣子智能体分析合同
            # 扣子智能体支持直接访问URL，无需Base64编码
            from app.services.oss_service import oss_service
            signed_url = oss_service.sign_url_for_key(object_key, expires=3600)
            
            logger.info(f"使用签名URL调用扣子智能体分析合同: {signed_url[:100]}...")
            
            # 使用签名URL调用扣子智能体
            analysis_result = await coze_service.analyze_contract(signed_url, user_id)
            
            if analysis_result:
                logger.info("✅ 合同分析成功")
            else:
                logger.error("❌ 合同分析返回空结果")
                    
        except Exception as error:
            logger.error(f"合同分析失败: {error}", exc_info=True)
            analysis_result = None
        
        if not analysis_result:
            # 扣子智能体分析失败，根据用户要求：不要返回假数据
            # 设置合同状态为失败，让前端显示错误信息
            logger.error("扣子智能体合同分析失败，返回空结果")
            contract.status = "failed"
            contract.analysis_progress = {"step": "failed", "progress": 0, "message": "AI分析服务暂时不可用，请稍后重试"}
            await db.commit()
            
            return ContractUploadResponse(
                task_id=contract.id,
                file_name=contract.file_name,
                file_type=contract.file_type,
                status=contract.status
            )
        
        # 根据用户要求：前端必须原样展示AI智能体返回的数据
        # 不再进行二次分析，直接使用扣子智能体返回的结果
        logger.info("直接使用扣子智能体返回的合同分析结果，不进行二次分析")
        
        # 提取OCR文本（如果存在）
        ocr_text = ""
        if "raw_text" in analysis_result:
            ocr_text = analysis_result["raw_text"]
        elif "ocr_text" in analysis_result:
            ocr_text = analysis_result["ocr_text"]
        elif "summary" in analysis_result:
            ocr_text = analysis_result["summary"]
        else:
            ocr_text = "合同文本内容"
        
        # V2.6.2优化：更新分析进度
        contract.analysis_progress = {"step": "analyzing", "progress": 50, "message": "正在分析风险..."}
        await db.commit()

        # 启动后台分析任务，直接使用扣子智能体的结果
        background_tasks.add_task(
            analyze_contract_background_with_coze_result,
            contract.id,
            analysis_result,
            ocr_text,
            db
        )

        logger.info(f"合同上传成功: {file.filename}, ID: {contract.id}")

        return ContractUploadResponse(
            task_id=contract.id,
            file_name=contract.file_name,
            file_type=contract.file_type,
            status=contract.status
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"合同上传失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="上传失败"
        )


def map_risk_level(risk_level: str) -> str:
    """
    将扣子智能体返回的风险等级映射到系统定义的RiskLevel枚举值
    
    Args:
        risk_level: 扣子智能体返回的风险等级
        
    Returns:
        映射后的风险等级
    """
    if not risk_level:
        return "compliant"
    
    risk_level = risk_level.lower().strip()
    
    # 映射规则
    mapping = {
        # 高风险相关
        "high": "needs_attention",
        "高风险": "needs_attention",
        "danger": "needs_attention",
        "critical": "needs_attention",
        "needs_attention": "needs_attention",
        
        # 中风险相关
        "medium": "moderate_concern",
        "中风险": "moderate_concern",
        "warning": "moderate_concern",
        "moderate": "moderate_concern",
        "moderate_concern": "moderate_concern",
        
        # 低风险/合规相关
        "low": "compliant",
        "低风险": "compliant",
        "safe": "compliant",
        "compliant": "compliant",
        "合规": "compliant",
        "normal": "compliant",
    }
    
    return mapping.get(risk_level, "compliant")


@router.get("/contract/{contract_id}", response_model=ContractAnalysisResponse)
async def get_contract_analysis(
    contract_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取合同分析结果

    Args:
        contract_id: 合同ID
        user_id: 用户ID
        db: 数据库会话

    Returns:
        分析结果
    """
    try:
        result = await db.execute(
            select(Contract)
            .where(Contract.id == contract_id, Contract.user_id == user_id)
        )
        contract = result.scalar_one_or_none()

        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="合同不存在"
            )

        summary = None
        result_json = contract.result_json
        # 分析失败时不清空数据，但前端通过 status 与 summary 判断是否展示失败态
        if contract.status == "failed":
            # 不返回可能导致前端误展示为「合规」的假数据
            result_json = None
        elif getattr(contract, "result_json", None) and isinstance(contract.result_json, dict):
            summary = contract.result_json.get("summary")
            if summary == "AI分析服务暂时不可用，请稍后重试":
                result_json = None
                summary = None
        
        # 构建预览数据（用于解锁页面展示）
        preview_data = None
        if contract.status == "completed" and contract.result_json:
            # 从分析结果中提取预览数据
            preview_data = {
                "risk_summary_preview": {
                    "risk_level": contract.risk_level,
                    "risk_level_text": "高风险" if contract.risk_level == "needs_attention" else "中风险" if contract.risk_level == "moderate_concern" else "低风险",
                    "risk_items_count": len(contract.risk_items or []),
                    "unfair_terms_count": len(contract.unfair_terms or []),
                    "missing_terms_count": len(contract.missing_terms or []),
                },
                "analysis_preview": {
                    "top_risks": [item.get("description", "风险条款")[:30] for item in (contract.risk_items or [])[:3]],
                    "key_unfair_terms": [term.get("clause", "霸王条款")[:30] for term in (contract.unfair_terms or [])[:2]],
                    "key_missing_terms": [term.get("clause", "缺失条款")[:30] for term in (contract.missing_terms or [])[:2]],
                }
            }
        elif contract.status == "analyzing":
            # 分析中的预览数据
            preview_data = {
                "analysis_status": "analyzing",
                "progress_message": contract.analysis_progress.get("message", "正在分析中...") if contract.analysis_progress else "正在分析中...",
                "progress_percentage": contract.analysis_progress.get("progress", 0) if contract.analysis_progress else 0
            }
        
        # 映射风险等级到正确的枚举值
        mapped_risk_level = None
        if contract.risk_level:
            mapped_risk_level = map_risk_level(contract.risk_level)
        
        return ContractAnalysisResponse(
            id=contract.id,
            file_name=contract.file_name,
            status=contract.status,
            risk_level=mapped_risk_level,
            risk_items=contract.risk_items or [],
            unfair_terms=contract.unfair_terms or [],
            missing_terms=contract.missing_terms or [],
            suggested_modifications=contract.suggested_modifications or [],
            summary=summary,
            is_unlocked=contract.is_unlocked,
            created_at=contract.created_at,
            # V2.6.2优化：返回分析进度
            analysis_progress=contract.analysis_progress or {"step": "pending", "progress": 0, "message": "等待分析"},
            # 返回AI分析完整结果（失败或兜底时不返回假数据）
            result_json=result_json,
            # 返回OCR识别结果
            ocr_result=contract.ocr_result,
            # 返回预览数据
            preview_data=preview_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取合同分析结果失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取分析结果失败"
        )


@router.get("/list")
async def list_contracts(
    user_id: int = Depends(get_user_id),
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户的合同列表

    Args:
        user_id: 用户ID
        page: 页码
        page_size: 每页数量
        db: 数据库会话

    Returns:
        合同列表
    """
    try:
        offset = (page - 1) * page_size

        result = await db.execute(
            select(Contract)
            .where(Contract.user_id == user_id)
            .order_by(Contract.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        contracts = result.scalars().all()

        count_result = await db.execute(
            select(Contract.id)
            .where(Contract.user_id == user_id)
        )
        total = len(count_result.all())

        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": [
                    {
                        "id": contract.id,
                        "file_name": contract.file_name,
                        "risk_level": contract.risk_level,
                        "status": contract.status,
                        "is_unlocked": contract.is_unlocked,
                        "created_at": contract.created_at.isoformat() if contract.created_at else None
                    }
                    for contract in contracts
                ],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        )

    except Exception as e:
        logger.error(f"获取合同列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取列表失败"
        )


@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    删除合同记录

    Args:
        contract_id: 合同ID
        user_id: 用户ID
        db: 数据库会话

    Returns:
        删除结果
    """
    try:
        # 查询合同记录
        result = await db.execute(
            select(Contract)
            .where(Contract.id == contract_id, Contract.user_id == user_id)
        )
        contract = result.scalar_one_or_none()

        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="合同不存在"
            )

        # 删除记录
        await db.delete(contract)
        await db.commit()

        return ApiResponse(
            code=0,
            msg="success",
            data={"deleted": True, "contract_id": contract_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除合同记录失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除失败"
        )

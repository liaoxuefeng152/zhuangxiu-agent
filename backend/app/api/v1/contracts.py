"""
装修决策Agent - 合同审核API
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.core.config import settings
from app.models import Contract, User
from app.services import ocr_service, risk_analyzer_service
from app.schemas import (
    ContractUploadRequest, ContractUploadResponse, ContractAnalysisResponse, ApiResponse
)
from app.api.v1.quotes import upload_file_to_oss

router = APIRouter(prefix="/contracts", tags=["合同审核"])
logger = logging.getLogger(__name__)


async def analyze_contract_background(contract_id: int, ocr_text: str, db: AsyncSession):
    """
    后台任务：分析合同

    Args:
        contract_id: 合同ID
        ocr_text: OCR识别的文本
        db: 数据库会话
    """
    try:
        logger.info(f"开始分析合同: {contract_id}")

        # 调用AI分析
        analysis_result = await risk_analyzer_service.analyze_contract(ocr_text)

        # 更新数据库
        result = await db.execute(select(Contract).where(Contract.id == contract_id))
        contract = result.scalar_one_or_none()

        if contract:
            contract.status = "completed"
            contract.ocr_result = {"text": ocr_text}
            contract.result_json = analysis_result
            contract.risk_level = analysis_result.get("risk_level")
            contract.risk_items = analysis_result.get("risk_items", [])
            contract.unfair_terms = analysis_result.get("unfair_terms", [])
            contract.missing_terms = analysis_result.get("missing_terms", [])
            contract.suggested_modifications = analysis_result.get("suggested_modifications", [])

            await db.commit()
            logger.info(f"合同分析完成: {contract_id}, 风险等级: {contract.risk_level}")
        else:
            logger.error(f"合同不存在: {contract_id}")

    except Exception as e:
        logger.error(f"合同分析失败: {e}", exc_info=True)

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

        # 上传到OSS
        file_url = upload_file_to_oss(file, "contract")
        
        # 如果OSS配置不存在，使用Base64编码的文件内容进行OCR识别
        ocr_input = file_url
        if file_url.startswith("https://mock-oss.example.com"):
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

        # 创建合同记录
        contract = Contract(
            user_id=user_id,
            file_url=file_url,
            file_name=file.filename,
            file_size=file.size,
            file_type=file_ext,
            status="analyzing"
        )

        db.add(contract)
        await db.commit()
        await db.refresh(contract)

        # OCR识别
        ocr_result = await ocr_service.recognize_contract(ocr_input)
        if not ocr_result:
            # 开发环境：如果OCR失败，使用模拟OCR文本继续测试
            if hasattr(settings, 'DEBUG') and settings.DEBUG:
                logger.warning("开发环境：OCR识别失败，使用模拟OCR文本继续测试")
                # 使用模拟的合同文本
                ocr_text = """
深圳市住宅装饰装修工程施工合同

甲方（委托方）：张三
乙方（承包方）：深圳XX装饰工程有限公司

第一条 工程概况
1.1 工程地点：深圳市南山区XX小区XX栋XX室
1.2 工程内容：住宅室内装修
1.3 工程承包方式：半包
1.4 工程期限：90天

第二条 工程价款
2.1 工程总价款：80000元（人民币捌万元整）
2.2 付款方式：
   - 合同签订时支付30%：24000元
   - 水电验收后支付30%：24000元
   - 泥木验收后支付30%：24000元
   - 竣工验收后支付10%：8000元

第三条 材料供应
3.1 主材由甲方采购
3.2 辅材由乙方提供

第四条 工程质量
4.1 工程质量标准：符合国家相关标准
4.2 保修期：2年

第五条 违约责任
5.1 如乙方延期完工，每延期一天支付违约金500元
5.2 如甲方延期付款，每延期一天支付违约金500元

第六条 其他条款
6.1 本合同一式两份，甲乙双方各执一份
6.2 本合同自双方签字之日起生效

甲方签字：张三
乙方签字：XX装饰公司
日期：2026年1月1日
"""
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="OCR识别失败，请重新上传"
                )
        else:
            ocr_text = ocr_result.get("content", "")

        # 启动后台分析任务
        background_tasks.add_task(
            analyze_contract_background,
            contract.id,
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
        if getattr(contract, "result_json", None) and isinstance(contract.result_json, dict):
            summary = contract.result_json.get("summary")
        return ContractAnalysisResponse(
            id=contract.id,
            file_name=contract.file_name,
            status=contract.status,
            risk_level=contract.risk_level,
            risk_items=contract.risk_items or [],
            unfair_terms=contract.unfair_terms or [],
            missing_terms=contract.missing_terms or [],
            suggested_modifications=contract.suggested_modifications or [],
            summary=summary,
            is_unlocked=contract.is_unlocked,
            created_at=contract.created_at
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

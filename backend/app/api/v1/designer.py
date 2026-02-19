"""
AI设计师智能体 API
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.database import get_db
from app.services.risk_analyzer import risk_analyzer_service
from app.core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


class DesignerConsultRequest(BaseModel):
    """AI设计师咨询请求"""
    question: str
    context: Optional[str] = None


class DesignerConsultResponse(BaseModel):
    """AI设计师咨询响应"""
    answer: str
    success: bool = True


@router.post("/consult", response_model=DesignerConsultResponse)
async def consult_designer(
    request: DesignerConsultRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    AI设计师咨询接口
    
    用户可以向AI设计师咨询装修设计相关问题，包括：
    - 装修风格选择
    - 空间布局规划
    - 材料选择建议
    - 色彩搭配
    - 预算控制
    - 装修流程等
    """
    try:
        logger.info(f"AI设计师咨询请求: user_id={current_user.get('id')}, question={request.question[:100]}...")
        
        # 调用AI设计师智能体
        answer = await risk_analyzer_service.consult_designer(
            user_question=request.question,
            context=request.context or ""
        )
        
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI设计师服务暂时不可用，请稍后重试"
            )
        
        return DesignerConsultResponse(answer=answer)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI设计师咨询失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI设计师咨询服务异常，请稍后重试"
        )


@router.get("/health")
async def health_check():
    """AI设计师服务健康检查"""
    try:
        # 测试一个简单的问题
        test_question = "现代简约风格的特点是什么？"
        answer = await risk_analyzer_service.consult_designer(test_question)
        
        if not answer:
            return {"status": "unhealthy", "message": "AI设计师返回空结果"}
        
        return {
            "status": "healthy",
            "service": "ai_designer",
            "message": "AI设计师服务正常运行"
        }
    except Exception as e:
        logger.error(f"AI设计师健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "service": "ai_designer",
            "message": f"AI设计师服务异常: {str(e)}"
        }

"""
AI设计师智能体 API - 支持多轮对话的聊天机器人
"""
import logging
import uuid
import time
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
import redis.asyncio as redis
import os
import uuid
from datetime import datetime

from app.core.database import get_db
from app.services.risk_analyzer import risk_analyzer_service
from app.services.oss_service import oss_service
from app.core.security import get_current_user
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Redis连接池（用于存储对话session）
_redis_pool = None

async def get_redis():
    """获取Redis连接"""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True
        )
    return _redis_pool


class Message(BaseModel):
    """对话消息"""
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: float


class ChatSessionCreateRequest(BaseModel):
    """创建聊天session请求"""
    initial_question: Optional[str] = None


class ChatSessionResponse(BaseModel):
    """聊天session响应"""
    session_id: str
    created_at: float
    messages: List[Message]
    user_id: int


class ChatMessageRequest(BaseModel):
    """发送聊天消息请求"""
    session_id: str
    message: str
    image_urls: Optional[List[str]] = None


class ImageUploadResponse(BaseModel):
    """图片上传响应"""
    success: bool
    image_url: Optional[str] = None
    error_message: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """聊天消息响应"""
    session_id: str
    message_id: str
    answer: str
    messages: List[Message]


class ClearChatRequest(BaseModel):
    """清空聊天记录请求"""
    session_id: str


class ClearChatResponse(BaseModel):
    """清空聊天记录响应"""
    session_id: str
    cleared: bool
    message_count: int


async def create_session_key(user_id: int, session_id: str) -> str:
    """创建session存储key"""
    return f"designer:session:{user_id}:{session_id}"


async def create_user_sessions_key(user_id: int) -> str:
    """创建用户sessions列表key"""
    return f"designer:user_sessions:{user_id}"


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    request: ChatSessionCreateRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    创建新的AI设计师聊天session
    
    支持多轮对话，每个session维护独立的对话历史
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 生成session ID
        session_id = str(uuid.uuid4())
        created_at = time.time()
        
        # 初始化消息列表
        messages = []
        
        # 如果有初始问题，添加到消息列表
        if request.initial_question:
            messages.append(Message(
                role="user",
                content=request.initial_question,
                timestamp=created_at
            ))
            
            # 获取AI回答
            answer = await risk_analyzer_service.consult_designer(
                user_question=request.initial_question,
                context=""
            )
            
            if answer:
                messages.append(Message(
                    role="assistant",
                    content=answer,
                    timestamp=time.time()
                ))
        
        # 存储session到Redis
        redis_client = await get_redis()
        session_key = await create_session_key(user_id, session_id)
        
        # 存储session数据
        import json
        session_data = {
            "session_id": session_id,
            "user_id": str(user_id),
            "created_at": str(created_at),
            "messages": json.dumps([msg.dict() for msg in messages])
        }
        
        # 使用Hash存储session数据
        await redis_client.hset(session_key, mapping=session_data)
        
        # 设置过期时间（7天）
        await redis_client.expire(session_key, 7 * 24 * 3600)
        
        # 将session ID添加到用户sessions列表
        user_sessions_key = await create_user_sessions_key(user_id)
        await redis_client.sadd(user_sessions_key, session_id)
        await redis_client.expire(user_sessions_key, 7 * 24 * 3600)
        
        logger.info(f"创建AI设计师聊天session: user_id={user_id}, session_id={session_id}")
        
        return ChatSessionResponse(
            session_id=session_id,
            created_at=created_at,
            messages=messages,
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建聊天session失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建聊天session失败"
        )


@router.post("/chat", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    发送消息到AI设计师聊天session
    
    支持多轮对话，AI会基于对话历史进行回答
    支持携带图片URL
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 验证session归属
        session_key = await create_session_key(user_id, request.session_id)
        redis_client = await get_redis()
        
        if not await redis_client.exists(session_key):
            raise HTTPException(status_code=404, detail="聊天session不存在或已过期")
        
        # 获取session数据
        session_data = await redis_client.hgetall(session_key)
        if not session_data:
            raise HTTPException(status_code=404, detail="聊天session数据丢失")
        
        # 解析消息历史
        messages = []
        if "messages" in session_data:
            import json
            try:
                messages_data = json.loads(session_data["messages"])
                messages = [Message(**msg) for msg in messages_data]
            except:
                messages = []
        
        # 构建消息内容（包含图片URL）
        message_content = request.message
        if request.image_urls and len(request.image_urls) > 0:
            image_info = f"\n\n📸 上传了{len(request.image_urls)}张图片："
            for i, url in enumerate(request.image_urls[:3]):  # 最多显示3张图片
                image_info += f"\n图片{i+1}: {url}"
            if len(request.image_urls) > 3:
                image_info += f"\n...等{len(request.image_urls)}张图片"
            message_content += image_info
        
        # 添加用户消息
        user_message = Message(
            role="user",
            content=message_content,
            timestamp=time.time()
        )
        messages.append(user_message)
        
        # 构建对话历史（用于AI理解上下文）
        conversation_history = ""
        for msg in messages[-10:]:  # 只保留最近10条消息作为上下文
            role = "用户" if msg.role == "user" else "AI设计师"
            conversation_history += f"{role}: {msg.content}\n"
        
        # 如果有图片URL，将其包含在用户问题中
        user_question = request.message
        if request.image_urls and len(request.image_urls) > 0:
            user_question += f"\n\n用户上传了{len(request.image_urls)}张图片，请基于图片内容进行分析。"
        
        # 调用AI设计师智能体（传入对话历史作为上下文）
        answer = await risk_analyzer_service.consult_designer(
            user_question=user_question,
            context=conversation_history,
            image_urls=request.image_urls
        )
        
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI设计师服务暂时不可用，请稍后重试"
            )
        
        # 添加AI回答
        ai_message = Message(
            role="assistant",
            content=answer,
            timestamp=time.time()
        )
        messages.append(ai_message)
        
        # 更新session数据
        session_data["messages"] = json.dumps([msg.dict() for msg in messages])
        await redis_client.hset(session_key, mapping=session_data)
        
        # 生成消息ID
        message_id = str(uuid.uuid4())
        
        logger.info(f"AI设计师聊天消息: user_id={user_id}, session_id={request.session_id}, message_len={len(request.message)}, image_count={len(request.image_urls) if request.image_urls else 0}")
        
        return ChatMessageResponse(
            session_id=request.session_id,
            message_id=message_id,
            answer=answer,
            messages=messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发送聊天消息失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送消息失败，请稍后重试"
        )


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    获取聊天session详情
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 验证session归属
        session_key = await create_session_key(user_id, session_id)
        redis_client = await get_redis()
        
        if not await redis_client.exists(session_key):
            raise HTTPException(status_code=404, detail="聊天session不存在或已过期")
        
        # 获取session数据
        session_data = await redis_client.hgetall(session_key)
        if not session_data:
            raise HTTPException(status_code=404, detail="聊天session数据丢失")
        
        # 解析消息历史
        messages = []
        if "messages" in session_data:
            import json
            try:
                messages_data = json.loads(session_data["messages"])
                messages = [Message(**msg) for msg in messages_data]
            except:
                messages = []
        
        return ChatSessionResponse(
            session_id=session_id,
            created_at=float(session_data.get("created_at", time.time())),
            messages=messages,
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取聊天session失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取聊天session失败"
        )


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    获取用户的所有聊天session
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        redis_client = await get_redis()
        user_sessions_key = await create_user_sessions_key(user_id)
        
        # 获取用户的所有session ID
        session_ids = await redis_client.smembers(user_sessions_key)
        
        sessions = []
        for session_id in session_ids:
            session_key = await create_session_key(user_id, session_id)
            if await redis_client.exists(session_key):
                session_data = await redis_client.hgetall(session_key)
                if session_data:
                    # 解析消息历史
                    messages = []
                    if "messages" in session_data:
                        import json
                        try:
                            messages_data = json.loads(session_data["messages"])
                            messages = [Message(**msg) for msg in messages_data]
                        except:
                            messages = []
                    
                    sessions.append(ChatSessionResponse(
                        session_id=session_id,
                        created_at=float(session_data.get("created_at", time.time())),
                        messages=messages,
                        user_id=user_id
                    ))
        
        # 按创建时间倒序排序
        sessions.sort(key=lambda x: x.created_at, reverse=True)
        
        return sessions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取聊天sessions列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取聊天sessions列表失败"
        )


@router.post("/clear", response_model=ClearChatResponse)
async def clear_chat_history(
    request: ClearChatRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    清空聊天session的历史记录
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 验证session归属
        session_key = await create_session_key(user_id, request.session_id)
        redis_client = await get_redis()
        
        if not await redis_client.exists(session_key):
            raise HTTPException(status_code=404, detail="聊天session不存在或已过期")
        
        # 获取当前消息数量
        session_data = await redis_client.hgetall(session_key)
        message_count = 0
        if "messages" in session_data:
            import json
            try:
                messages_data = json.loads(session_data["messages"])
                message_count = len(messages_data)
            except:
                message_count = 0
        
        # 清空消息历史
        session_data["messages"] = "[]"
        await redis_client.hset(session_key, mapping=session_data)
        
        logger.info(f"清空聊天历史: user_id={user_id}, session_id={request.session_id}, cleared_messages={message_count}")
        
        return ClearChatResponse(
            session_id=request.session_id,
            cleared=True,
            message_count=message_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清空聊天历史失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清空聊天历史失败"
        )


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    删除聊天session
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        redis_client = await get_redis()
        session_key = await create_session_key(user_id, session_id)
        
        # 删除session数据
        deleted = await redis_client.delete(session_key)
        
        # 从用户sessions列表中移除
        user_sessions_key = await create_user_sessions_key(user_id)
        await redis_client.srem(user_sessions_key, session_id)
        
        if deleted:
            logger.info(f"删除聊天session: user_id={user_id}, session_id={session_id}")
            return {"deleted": True, "session_id": session_id}
        else:
            raise HTTPException(status_code=404, detail="聊天session不存在")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除聊天session失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除聊天session失败"
        )


# 保留旧的单次咨询接口（向后兼容）
class DesignerConsultRequest(BaseModel):
    """AI设计师咨询请求（单次，向后兼容）"""
    question: str
    context: Optional[str] = None


class DesignerConsultResponse(BaseModel):
    """AI设计师咨询响应（单次，向后兼容）"""
    answer: str
    success: bool = True


@router.post("/consult", response_model=DesignerConsultResponse)
async def consult_designer_legacy(
    request: DesignerConsultRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    AI设计师咨询接口（单次，向后兼容）
    
    保持与旧版前端的兼容性
    """
    try:
        logger.info(f"AI设计师单次咨询请求: user_id={current_user.get('user_id')}, question={request.question[:100]}...")
        
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
        logger.error(f"AI设计师单次咨询失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI设计师咨询服务异常，请稍后重试"
        )


@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_designer_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    上传户型图到AI设计师
    
    支持JPG、PNG格式，最大10MB
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未认证")
        
        # 检查文件类型
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return ImageUploadResponse(
                success=False,
                error_message=f"不支持的文件格式。请上传以下格式的图片：{', '.join(allowed_extensions)}"
            )
        
        # 检查文件大小（最大10MB）
        max_size = 10 * 1024 * 1024  # 10MB
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置文件指针
        
        if file_size > max_size:
            return ImageUploadResponse(
                success=False,
                error_message=f"文件太大。最大支持{max_size // (1024*1024)}MB"
            )
        
        # 使用OSS服务的upload_upload_file方法上传文件
        object_key = oss_service.upload_upload_file(
            file=file,
            file_type="designer",
            user_id=user_id,
            is_photo=True  # 设计师图片属于照片类型
        )
        
        # 由于OSS bucket已经是公共读，直接生成公共URL而不是签名URL
        # 这样AI设计师智能体更容易访问
        from app.core.config import settings
        bucket_name = settings.ALIYUN_OSS_BUCKET1
        endpoint = settings.ALIYUN_OSS_ENDPOINT
        
        # 生成公共URL（不需要签名）
        public_url = f"https://{bucket_name}.{endpoint}/{object_key}"
        
        logger.info(f"AI设计师图片上传成功: user_id={user_id}, object_key={object_key}, size={file_size}, public_url={public_url}")
        
        return ImageUploadResponse(
            success=True,
            image_url=public_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI设计师图片上传失败: {e}", exc_info=True)
        return ImageUploadResponse(
            success=False,
            error_message="图片上传失败，请稍后重试"
        )


@router.get("/health")
async def health_check():
    """AI设计师服务健康检查"""
    try:
        # 创建一个新的RiskAnalyzerService实例，避免使用可能未正确初始化的全局实例
        from app.services.risk_analyzer import RiskAnalyzerService
        service = RiskAnalyzerService()
        
        # 测试一个简单的问题
        test_question = "现代简约风格的特点是什么？"
        answer = await service.consult_designer(test_question)

        if not answer:
            return {"status": "unhealthy", "service": "ai_designer", "message": "AI设计师返回空结果"}

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

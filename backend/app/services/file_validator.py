"""
文件上传安全验证服务
"""
import magic
import os
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# MIME类型与扩展名映射表
MIME_EXT_MAP = {
    'application/pdf': 'pdf',
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/jpg': 'jpg'
}


async def validate_upload_file(file: UploadFile) -> dict:
    """
    严格验证上传文件

    Args:
        file: FastAPI上传文件对象

    Returns:
        包含文件信息的字典

    Raises:
        HTTPException: 文件验证失败时抛出400异常
    """
    # 1. 验证文件名
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空"
        )

    # 清理文件名，移除路径遍历字符
    safe_filename = os.path.basename(file.filename)
    if safe_filename != file.filename:
        logger.warning(f"检测到路径遍历攻击尝试: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名包含非法字符"
        )

    # 2. 读取文件内容进行MIME类型验证
    file_content = await file.read()

    # 3. 验证文件大小
    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小不能超过{settings.MAX_UPLOAD_SIZE // (1024*1024)}MB"
        )

    # 4. 验证MIME类型
    try:
        file_mime = magic.from_buffer(file_content, mime=True)
    except Exception as e:
        logger.error(f"MIME类型检测失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件类型检测失败"
        )

    if file_mime not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file_mime}"
        )

    # 5. 验证扩展名与MIME类型是否匹配
    file_ext = safe_filename.split('.')[-1].lower()
    expected_ext = MIME_EXT_MAP.get(file_mime)

    if expected_ext and file_ext != expected_ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件扩展名与内容不匹配，应为.{expected_ext}"
        )

    # 6. 验证扩展名是否在允许列表中
    if file_ext not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件扩展名: .{file_ext}"
        )

    # 重置文件指针
    await file.seek(0)

    logger.info(f"文件验证通过: {safe_filename}, 类型: {file_mime}, 大小: {len(file_content)}")

    return {
        'filename': safe_filename,
        'size': len(file_content),
        'mime_type': file_mime,
        'extension': file_ext
    }

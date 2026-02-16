from .ocr_service import ocr_service
from .risk_analyzer import risk_analyzer_service
# 延迟导入message_service，避免循环导入（message_service内部导入models）
# from .message_service import create_message
from .wechat_template_service import send_progress_reminder

# 延迟导入函数
def get_create_message():
    """延迟导入create_message，避免循环导入"""
    from .message_service import create_message
    return create_message
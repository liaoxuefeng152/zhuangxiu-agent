from .risk_analyzer import risk_analyzer_service
from .tianyancha_service import tianyancha_service
from .juhecha_service import juhecha_service
from .oss_service import oss_service
from .coze_service import coze_service
# 延迟导入message_service，避免循环导入（message_service内部导入models）
# from .message_service import create_message
from .wechat_template_service import send_progress_reminder, send_miniprogram_report_notification
from .wechat_miniprogram_service import wechat_miniprogram_service

# 延迟导入函数
def get_create_message():
    """延迟导入create_message，避免循环导入"""
    from .message_service import create_message
    return create_message

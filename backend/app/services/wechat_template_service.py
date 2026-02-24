"""
微信模板消息服务 - 家装服务进度提醒（方案已生成）
模板内容：您的装修方案已生成:{{方案名称.DATA}},请点击查看
"""
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_progress_reminder(openid: str, plan_name: str, url: Optional[str] = None) -> bool:
    """
    发送「家装服务进度提醒」模板消息。

    :param openid: 用户微信 openid（公众号 openid）
    :param plan_name: 方案名称，展示在模板中 {{方案名称.DATA}}
    :param url: 可选，点击消息跳转链接
    :return: 是否发送成功
    """
    template_id = getattr(settings, "WECHAT_TEMPLATE_PROGRESS_REMINDER", None) or ""
    app_id = getattr(settings, "WECHAT_APP_ID", None) or ""
    app_secret = getattr(settings, "WECHAT_APP_SECRET", None) or ""
    if not template_id or not app_id or not app_secret:
        logger.debug("微信模板消息未配置 WECHAT_TEMPLATE_PROGRESS_REMINDER / WECHAT_APP_ID / WECHAT_APP_SECRET，跳过发送")
        return False
    if not openid or not openid.strip():
        logger.debug("openid 为空，跳过发送模板消息")
        return False
    plan_name = (plan_name or "方案").strip()[:20]  # 微信限制字段长度

    try:
        from wechatpy import WeChatClient
        from wechatpy.exceptions import WeChatClientException

        client = WeChatClient(app_id, app_secret)
        data = {
            "方案名称": {"value": plan_name, "color": "#173177"},
        }
        
        # 添加更详细的日志记录
        logger.info("尝试发送微信模板消息: openid=%s, plan_name=%s, template_id=%s", 
                   openid[:8] + "***", plan_name, template_id)
        
        client.message.send_template(openid, template_id, data, url=url)
        logger.info("微信模板消息发送成功: openid=%s, plan_name=%s", openid[:8] + "***", plan_name)
        return True
    except WeChatClientException as e:
        # 微信客户端异常，记录详细错误信息
        error_code = getattr(e, 'errcode', 'unknown')
        error_msg = getattr(e, 'errmsg', str(e))
        
        logger.error("微信模板消息发送失败 (WeChatClientException): code=%s, message=%s", error_code, error_msg)
        
        # 根据错误代码提供具体建议
        if error_code == 48001:
            logger.error("错误代码48001: API功能未授权。请检查：")
            logger.error("1. 公众号是否已开通模板消息功能")
            logger.error("2. 阿里云服务器IP (120.26.201.61) 是否已添加到公众号IP白名单")
            logger.error("3. 模板ID是否正确配置")
        elif error_code == 40037:
            logger.error("错误代码40037: 模板ID不正确")
        elif error_code == 40003:
            logger.error("错误代码40003: 无效的openid")
        elif error_code == 41028:
            logger.error("错误代码41028: 表单ID不正确或已过期")
        elif error_code == 45009:
            logger.error("错误代码45009: 接口调用超过限制")
        
        return False
    except Exception as e:
        logger.error("微信模板消息发送失败 (其他异常): %s", e, exc_info=True)
        return False

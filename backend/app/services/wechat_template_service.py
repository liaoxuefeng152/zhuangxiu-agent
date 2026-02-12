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

        client = WeChatClient(app_id, app_secret)
        data = {
            "方案名称": {"value": plan_name, "color": "#173177"},
        }
        client.message.send_template(openid, template_id, data, url=url)
        logger.info("微信模板消息发送成功: openid=%s, plan_name=%s", openid[:8] + "***", plan_name)
        return True
    except Exception as e:
        logger.warning("微信模板消息发送失败: %s", e, exc_info=True)
        return False

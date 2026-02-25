"""
微信消息服务 - 兼容层
注意：用户要求只用小程序消息推送，不需要公众号
此文件保持向后兼容，但实际使用小程序订阅消息
"""
import logging
from typing import Optional

from app.core.config import settings
from app.services.wechat_miniprogram_service import send_report_notification

logger = logging.getLogger(__name__)


def send_progress_reminder(openid: str, plan_name: str, url: Optional[str] = None) -> bool:
    """
    发送进度提醒消息（兼容函数）
    
    注意：用户要求只用小程序消息推送，不需要公众号
    此函数现在使用小程序订阅消息发送报告生成通知
    
    :param openid: 用户微信 openid（小程序 openid）
    :param plan_name: 方案/报告名称
    :param url: 可选，点击消息跳转链接（小程序订阅消息使用page参数）
    :return: 是否发送成功
    """
    if not openid or not openid.strip():
        logger.debug("openid 为空，跳过发送消息")
        return False
        
    plan_name = (plan_name or "方案").strip()[:20]  # 微信限制字段长度
    
    # 记录日志但不实际发送公众号模板消息
    logger.info("用户要求只用小程序消息推送，跳过公众号模板消息: openid=%s, plan_name=%s", 
               openid[:8] + "***", plan_name)
    
    # 返回False表示不发送公众号模板消息
    # 实际的小程序订阅消息在报价单、合同等API中单独调用
    return False


async def send_miniprogram_report_notification(
    openid: str, 
    report_type: str, 
    report_name: str,
    report_id: int
) -> bool:
    """
    发送小程序报告生成通知
    
    Args:
        openid: 用户openid
        report_type: 报告类型 (company/quote/contract)
        report_name: 报告名称
        report_id: 报告ID
    
    Returns:
        是否发送成功
    """
    return await send_report_notification(openid, report_type, report_name, report_id)

"""
微信小程序订阅消息服务
用于向小程序用户发送订阅消息（如报告生成通知）
"""
import logging
import httpx
from typing import Optional, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class WeChatMiniProgramService:
    """微信小程序服务"""
    
    def __init__(self):
        self.app_id = settings.WECHAT_APP_ID
        self.app_secret = settings.WECHAT_APP_SECRET
        self.access_token = None
        self.token_expire_time = 0
        
    async def get_access_token(self) -> Optional[str]:
        """
        获取小程序access_token
        
        Returns:
            access_token字符串，失败返回None
        """
        import time
        
        # 检查token是否有效
        if self.access_token and time.time() < self.token_expire_time:
            return self.access_token
            
        if not self.app_id or not self.app_secret:
            logger.error("微信小程序配置缺失: WECHAT_APP_ID=%s, WECHAT_APP_SECRET=%s", 
                        self.app_id[:8] + "***" if self.app_id else "None",
                        self.app_secret[:8] + "***" if self.app_secret else "None")
            return None
            
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                result = response.json()
                
            if "access_token" in result:
                self.access_token = result["access_token"]
                self.token_expire_time = time.time() + result.get("expires_in", 7200) - 300  # 提前5分钟过期
                logger.info("获取小程序access_token成功")
                return self.access_token
            else:
                logger.error("获取小程序access_token失败: %s", result)
                return None
                
        except Exception as e:
            logger.error("获取小程序access_token异常: %s", e, exc_info=True)
            return None
    
    async def send_subscribe_message(
        self, 
        openid: str, 
        template_id: str, 
        data: Dict[str, Dict[str, str]],
        page: Optional[str] = None,
        miniprogram_state: str = "formal"
    ) -> bool:
        """
        发送小程序订阅消息
        
        Args:
            openid: 用户openid
            template_id: 订阅消息模板ID
            data: 模板内容，格式如 {"thing1": {"value": "内容"}, "thing2": {"value": "内容"}}
            page: 点击消息跳转的小程序页面路径
            miniprogram_state: 跳转小程序类型 developer为开发版，trial为体验版，formal为正式版
        
        Returns:
            是否发送成功
        """
        if not openid or not openid.strip():
            logger.debug("openid为空，跳过发送订阅消息")
            return False
            
        access_token = await self.get_access_token()
        if not access_token:
            logger.error("无法获取access_token，跳过发送订阅消息")
            return False
            
        url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}"
        
        payload = {
            "touser": openid,
            "template_id": template_id,
            "data": data,
            "miniprogram_state": miniprogram_state
        }
        
        if page:
            payload["page"] = page
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                result = response.json()
                
            if result.get("errcode") == 0:
                logger.info("小程序订阅消息发送成功: openid=%s, template_id=%s", 
                           openid[:8] + "***", template_id)
                return True
            else:
                error_code = result.get("errcode", "unknown")
                error_msg = result.get("errmsg", str(result))
                logger.error("小程序订阅消息发送失败: code=%s, message=%s", error_code, error_msg)
                
                # 常见错误处理
                if error_code == 40037:
                    logger.error("错误代码40037: 模板ID不正确")
                elif error_code == 40003:
                    logger.error("错误代码40003: 无效的openid")
                elif error_code == 43101:
                    logger.error("错误代码43101: 用户拒绝接收消息")
                elif error_code == 47003:
                    logger.error("错误代码47003: 模板参数不准确")
                    
                return False
                
        except Exception as e:
            logger.error("小程序订阅消息发送异常: %s", e, exc_info=True)
            return False
    
    async def send_report_notification(
        self, 
        openid: str, 
        report_type: str, 
        report_name: str,
        report_id: int
    ) -> bool:
        """
        发送报告生成通知
        
        Args:
            openid: 用户openid
            report_type: 报告类型 (company/quote/contract)
            report_name: 报告名称
            report_id: 报告ID
        
        Returns:
            是否发送成功
        """
        # 这里需要配置小程序订阅消息模板ID
        # 模板示例：报告名称{{thing1.DATA}}已生成，请点击查看详情
        
        template_id = getattr(settings, "WECHAT_SUBSCRIBE_REPORT_NOTIFICATION", "")
        if not template_id:
            logger.debug("未配置小程序订阅消息模板ID，跳过发送")
            return False
            
        # 根据报告类型设置页面路径
        page_map = {
            "company": f"/pages/report-detail/index?type=company&scanId={report_id}",
            "quote": f"/pages/report-detail/index?type=quote&scanId={report_id}",
            "contract": f"/pages/report-detail/index?type=contract&scanId={report_id}"
        }
        
        page = page_map.get(report_type, "/pages/index/index")
        
        # 构建消息数据
        data = {
            "thing1": {"value": report_name[:20]},  # 报告名称，最多20个字符
            "thing2": {"value": "已生成"}  # 状态
        }
        
        return await self.send_subscribe_message(openid, template_id, data, page)


# 创建全局实例
wechat_miniprogram_service = WeChatMiniProgramService()


async def send_report_notification(
    openid: str, 
    report_type: str, 
    report_name: str,
    report_id: int
) -> bool:
    """
    发送报告生成通知（便捷函数）
    """
    return await wechat_miniprogram_service.send_report_notification(
        openid, report_type, report_name, report_id
    )

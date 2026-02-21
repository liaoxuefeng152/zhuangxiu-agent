"""
告警通知服务 - 支持邮件和钉钉告警
"""
import smtplib
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import httpx

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class AlertLevel:
    """告警级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertService:
    """告警服务"""
    
    def __init__(self):
        self.enabled = settings.ALERT_ENABLED
        self.min_level = settings.ALERT_LEVEL
        
        # 邮件配置
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.ALERT_EMAIL_FROM
        self.email_to = settings.ALERT_EMAIL_TO
        
        # 钉钉配置
        self.dingtalk_webhook = settings.DINGTALK_WEBHOOK_URL
        self.dingtalk_secret = settings.DINGTALK_SECRET
        self.dingtalk_at_mobiles = settings.DINGTALK_AT_MOBILES
        self.dingtalk_at_all = settings.DINGTALK_AT_ALL
        
        # 级别映射到数字用于比较
        self.level_priority = {
            AlertLevel.DEBUG: 0,
            AlertLevel.INFO: 1,
            AlertLevel.WARNING: 2,
            AlertLevel.ERROR: 3,
            AlertLevel.CRITICAL: 4
        }
    
    def should_send_alert(self, level: str) -> bool:
        """检查是否应该发送告警"""
        if not self.enabled:
            return False
        
        current_priority = self.level_priority.get(level, 0)
        min_priority = self.level_priority.get(self.min_level, 0)
        
        return current_priority >= min_priority
    
    def send_email_alert(self, subject: str, content: str, level: str = AlertLevel.ERROR) -> bool:
        """发送邮件告警"""
        if not self.should_send_alert(level):
            logger.debug(f"告警级别 {level} 低于配置的最小级别 {self.min_level}，跳过邮件发送")
            return False
        
        if not all([self.smtp_server, self.smtp_username, self.smtp_password, self.email_from, self.email_to]):
            logger.warning("邮件配置不完整，跳过邮件告警发送")
            return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)
            msg['Subject'] = f"[{level.upper()}] {subject}"
            
            # 添加内容
            body = f"""
            告警级别: {level.upper()}
            时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
            应用: {settings.APP_NAME}
            
            内容:
            {content}
            
            ---
            此邮件由装修决策Agent系统自动发送
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"邮件告警发送成功: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件告警失败: {e}")
            return False
    
    def _generate_dingtalk_signature(self, timestamp: int) -> str:
        """生成钉钉签名"""
        if not self.dingtalk_secret:
            return ""
        
        string_to_sign = f"{timestamp}\n{self.dingtalk_secret}"
        hmac_code = hmac.new(
            self.dingtalk_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return sign
    
    def send_dingtalk_alert(self, title: str, content: str, level: str = AlertLevel.ERROR) -> bool:
        """发送钉钉告警"""
        if not self.should_send_alert(level):
            logger.debug(f"告警级别 {level} 低于配置的最小级别 {self.min_level}，跳过钉钉发送")
            return False
        
        if not self.dingtalk_webhook:
            logger.warning("钉钉Webhook未配置，跳过钉钉告警发送")
            return False
        
        try:
            # 准备消息内容
            level_colors = {
                AlertLevel.DEBUG: "#CCCCCC",
                AlertLevel.INFO: "#1890FF",
                AlertLevel.WARNING: "#FAAD14",
                AlertLevel.ERROR: "#FF4D4F",
                AlertLevel.CRITICAL: "#722ED1"
            }
            
            color = level_colors.get(level, "#FF4D4F")
            
            # 构建消息
            text = f"### {title}\n\n"
            text += f"**告警级别**: {level.upper()}\n\n"
            text += f"**时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            text += f"**应用**: {settings.APP_NAME}\n\n"
            text += f"**内容**:\n{content}\n\n"
            text += "---\n此消息由装修决策Agent系统自动发送"
            
            # 构建请求数据
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": f"[{level.upper()}] {title}",
                    "text": text
                },
                "at": {
                    "atMobiles": self.dingtalk_at_mobiles,
                    "isAtAll": self.dingtalk_at_all
                }
            }
            
            # 如果有secret，生成签名
            url = self.dingtalk_webhook
            if self.dingtalk_secret:
                timestamp = int(time.time() * 1000)
                sign = self._generate_dingtalk_signature(timestamp)
                url = f"{self.dingtalk_webhook}&timestamp={timestamp}&sign={sign}"
            
            # 发送请求
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=data)
                response.raise_for_status()
                result = response.json()
                
                if result.get("errcode") == 0:
                    logger.info(f"钉钉告警发送成功: {title}")
                    return True
                else:
                    logger.error(f"钉钉告警发送失败: {result}")
                    return False
                    
        except Exception as e:
            logger.error(f"发送钉钉告警失败: {e}")
            return False
    
    def send_alert(self, title: str, content: str, level: str = AlertLevel.ERROR, 
                   channels: List[str] = None) -> Dict[str, bool]:
        """发送告警到指定通道"""
        if channels is None:
            channels = ["email", "dingtalk"]
        
        results = {}
        
        for channel in channels:
            if channel == "email":
                results["email"] = self.send_email_alert(title, content, level)
            elif channel == "dingtalk":
                results["dingtalk"] = self.send_dingtalk_alert(title, content, level)
            else:
                logger.warning(f"不支持的告警通道: {channel}")
                results[channel] = False
        
        return results
    
    def alert_system_error(self, error_type: str, error_message: str, 
                          traceback: str = None, context: Dict[str, Any] = None):
        """系统错误告警"""
        title = f"系统错误: {error_type}"
        content = f"错误信息: {error_message}\n"
        
        if traceback:
            content += f"堆栈跟踪:\n{traceback[:500]}...\n"
        
        if context:
            content += f"上下文:\n{json.dumps(context, ensure_ascii=False, indent=2)}\n"
        
        return self.send_alert(title, content, AlertLevel.ERROR)
    
    def alert_service_down(self, service_name: str, error_message: str):
        """服务宕机告警"""
        title = f"服务不可用: {service_name}"
        content = f"服务 {service_name} 不可用\n错误信息: {error_message}"
        
        return self.send_alert(title, content, AlertLevel.CRITICAL)
    
    def alert_high_resource_usage(self, resource_type: str, usage_percent: float, threshold: float):
        """高资源使用率告警"""
        title = f"高资源使用率: {resource_type}"
        content = f"{resource_type} 使用率: {usage_percent:.1f}%\n阈值: {threshold:.1f}%"
        
        level = AlertLevel.CRITICAL if usage_percent > 90 else AlertLevel.WARNING
        return self.send_alert(title, content, level)
    
    def alert_backup_failed(self, backup_type: str, error_message: str):
        """备份失败告警"""
        title = f"备份失败: {backup_type}"
        content = f"{backup_type} 备份失败\n错误信息: {error_message}"
        
        return self.send_alert(title, content, AlertLevel.ERROR)
    
    def alert_backup_verification_failed(self, backup_type: str, error_message: str):
        """备份验证失败告警"""
        title = f"备份验证失败: {backup_type}"
        content = f"{backup_type} 备份验证失败\n错误信息: {error_message}"
        
        return self.send_alert(title, content, AlertLevel.WARNING)


# 全局告警服务实例（懒加载）
_alert_service_instance = None


def _get_alert_service():
    """获取告警服务实例（懒加载）"""
    global _alert_service_instance
    if _alert_service_instance is None:
        _alert_service_instance = AlertService()
    return _alert_service_instance


def send_alert(title: str, content: str, level: str = AlertLevel.ERROR, 
               channels: List[str] = None) -> Dict[str, bool]:
    """发送告警的便捷函数"""
    return _get_alert_service().send_alert(title, content, level, channels)


def alert_system_error(error_type: str, error_message: str, 
                      traceback: str = None, context: Dict[str, Any] = None):
    """系统错误告警的便捷函数"""
    return _get_alert_service().alert_system_error(error_type, error_message, traceback, context)


def alert_service_down(service_name: str, error_message: str):
    """服务宕机告警的便捷函数"""
    return _get_alert_service().alert_service_down(service_name, error_message)


def alert_high_resource_usage(resource_type: str, usage_percent: float, threshold: float):
    """高资源使用率告警的便捷函数"""
    return _get_alert_service().alert_high_resource_usage(resource_type, usage_percent, threshold)


def alert_backup_failed(backup_type: str, error_message: str):
    """备份失败告警的便捷函数"""
    return _get_alert_service().alert_backup_failed(backup_type, error_message)


def alert_backup_verification_failed(backup_type: str, error_message: str):
    """备份验证失败告警的便捷函数"""
    return _get_alert_service().alert_backup_verification_failed(backup_type, error_message)

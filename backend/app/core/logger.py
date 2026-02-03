"""
结构化日志记录模块
实现统一的日志格式和审计日志功能
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
from loguru import logger as loguru_logger

# 请求上下文
request_context: ContextVar[Dict[str, Any]] = ContextVar('request_context', default={})


class StructuredLogger:
    """结构化日志记录器"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _get_context(self) -> Dict[str, Any]:
        """获取请求上下文"""
        return request_context.get()

    def _format_log(self, message: str, extra: Dict[str, Any] = None) -> str:
        """格式化日志"""
        context = self._get_context()

        log_data = {
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            **context,
            **(extra or {})
        }

        return json.dumps(log_data, ensure_ascii=False)

    def info(self, message: str, extra: Dict[str, Any] = None):
        """记录信息日志"""
        log_data = self._format_log(message, extra)
        self.logger.info(log_data)
        loguru_logger.info(log_data)

    def warning(self, message: str, extra: Dict[str, Any] = None):
        """记录警告日志"""
        log_data = self._format_log(message, extra)
        self.logger.warning(log_data)
        loguru_logger.warning(log_data)

    def error(self, message: str, extra: Dict[str, Any] = None, exc_info: bool = False):
        """记录错误日志"""
        log_data = self._format_log(message, extra)
        self.logger.error(log_data, exc_info=exc_info)
        loguru_logger.error(log_data)

    def audit(self, action: str, user_id: int, extra: Dict[str, Any] = None):
        """记录审计日志"""
        audit_data = {
            'type': 'audit',
            'action': action,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            **(extra or {})
        }

        context = self._get_context()
        audit_data.update(context)

        log_message = json.dumps(audit_data, ensure_ascii=False)
        self.logger.info(log_message)
        loguru_logger.info(f"[AUDIT] {log_message}")


# 创建全局日志记录器
def get_logger(name: str) -> StructuredLogger:
    """获取结构化日志记录器"""
    return StructuredLogger(name)

"""
监控API - 提供系统监控、告警和备份状态接口
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.services.monitor_service import (
    collect_metrics,
    get_service_status,
    get_system_overview
)
from app.services.backup_service import (
    perform_full_backup,
    upload_backups_to_oss,
    get_backup_status
)
from app.services.alert_service import send_alert, AlertLevel

router = APIRouter()


@router.get("/metrics", response_model=Dict[str, Any])
async def get_system_metrics():
    """
    获取系统监控指标
    
    返回系统CPU、内存、磁盘、网络等实时指标
    """
    try:
        metrics = await collect_metrics()
        return {
            "code": 0,
            "msg": "success",
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取监控指标失败: {str(e)}")


@router.get("/status", response_model=Dict[str, Any])
async def get_system_status():
    """
    获取系统服务状态
    
    返回数据库、Redis、OSS等服务连接状态
    """
    try:
        status = await get_service_status()
        return {
            "code": 0,
            "msg": "success",
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取服务状态失败: {str(e)}")


@router.get("/overview", response_model=Dict[str, Any])
async def get_system_overview_api():
    """
    获取系统概览
    
    返回系统指标和服务状态的综合信息
    """
    try:
        overview = await get_system_overview()
        return {
            "code": 0,
            "msg": "success",
            "data": overview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统概览失败: {str(e)}")


@router.get("/backup/status", response_model=Dict[str, Any])
async def get_backup_status_api():
    """
    获取备份状态
    
    返回备份文件列表、大小、保留策略等信息
    """
    try:
        status = await get_backup_status()
        return {
            "code": 0,
            "msg": "success",
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取备份状态失败: {str(e)}")


@router.post("/backup/run", response_model=Dict[str, Any])
async def run_backup():
    """
    手动执行完整备份
    
    触发数据库和文件备份，包含自动验证
    """
    try:
        result = await perform_full_backup()
        return {
            "code": 0,
            "msg": "备份执行完成",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行备份失败: {str(e)}")


@router.post("/backup/upload", response_model=Dict[str, Any])
async def upload_backup_to_oss():
    """
    上传备份到OSS
    
    将本地备份文件上传到阿里云OSS
    """
    try:
        result = await upload_backups_to_oss()
        return {
            "code": 0,
            "msg": "备份上传完成",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传备份失败: {str(e)}")


@router.post("/alert/test", response_model=Dict[str, Any])
async def test_alert(
    title: str = "测试告警",
    content: str = "这是一条测试告警消息",
    level: str = AlertLevel.INFO,
    channels: str = "email,dingtalk"
):
    """
    测试告警通知
    
    发送测试告警到指定通道，验证告警功能是否正常
    """
    try:
        channel_list = [c.strip() for c in channels.split(",")]
        results = send_alert(title, content, level, channel_list)
        
        return {
            "code": 0,
            "msg": "测试告警发送完成",
            "data": {
                "title": title,
                "content": content,
                "level": level,
                "channels": channel_list,
                "results": results
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送测试告警失败: {str(e)}")


@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check():
    """
    详细健康检查
    
    返回系统各项服务的详细健康状态
    """
    try:
        # 收集所有健康信息
        metrics = await collect_metrics()
        status = await get_service_status()
        backup_status = await get_backup_status()
        
        # 评估整体健康状态
        overall_health = "healthy"
        issues = []
        
        # 检查系统指标
        if "error" in metrics:
            overall_health = "degraded"
            issues.append(f"监控指标收集错误: {metrics.get('error')}")
        
        # 检查服务状态
        if status.get("overall") != "healthy":
            overall_health = "degraded"
            for service_name, service_info in status.get("services", {}).items():
                if service_info.get("status") != "healthy":
                    issues.append(f"服务 {service_name} 异常: {service_info.get('message')}")
        
        # 检查备份状态
        if "error" in backup_status:
            overall_health = "degraded"
            issues.append(f"备份状态检查错误: {backup_status.get('error')}")
        
        return {
            "code": 0,
            "msg": "success",
            "data": {
                "overall": overall_health,
                "timestamp": metrics.get("timestamp") if "timestamp" in metrics else status.get("timestamp"),
                "metrics": metrics,
                "services": status,
                "backup": backup_status,
                "issues": issues if issues else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"详细健康检查失败: {str(e)}")

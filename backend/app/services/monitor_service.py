"""
系统监控服务 - 收集系统指标和业务指标
"""
import psutil
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from app.core.config import settings
from app.core.logger import get_logger
from app.core.database import get_db
from app.services.alert_service import alert_high_resource_usage, AlertLevel
from app.services.redis_cache import cache

logger = get_logger(__name__)


class SystemMetrics:
    """系统指标收集"""
    
    @staticmethod
    def get_cpu_usage() -> float:
        """获取CPU使用率"""
        return psutil.cpu_percent(interval=1)
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """获取内存使用情况"""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
            "free": memory.free
        }
    
    @staticmethod
    def get_disk_usage() -> Dict[str, Any]:
        """获取磁盘使用情况"""
        try:
            disk = psutil.disk_usage('/')
            return {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            }
        except Exception as e:
            logger.error(f"获取磁盘使用情况失败: {e}")
            return {
                "total": 0,
                "used": 0,
                "free": 0,
                "percent": 0
            }
    
    @staticmethod
    def get_network_io() -> Dict[str, Any]:
        """获取网络IO"""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errin": net_io.errin,
            "errout": net_io.errout,
            "dropin": net_io.dropin,
            "dropout": net_io.dropout
        }
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "boot_time": psutil.boot_time(),
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        }


class DatabaseMetrics:
    """数据库指标收集"""
    
    @staticmethod
    async def get_connection_stats() -> Dict[str, Any]:
        """获取数据库连接统计"""
        try:
            async with get_db() as conn:
                # 获取连接数
                result = await conn.fetchrow("""
                    SELECT 
                        count(*) as total_connections,
                        count(*) filter (where state = 'active') as active_connections,
                        count(*) filter (where state = 'idle') as idle_connections,
                        count(*) filter (where state = 'idle in transaction') as idle_in_transaction
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """)
                
                # 获取数据库大小
                size_result = await conn.fetchrow("""
                    SELECT pg_database_size(current_database()) as db_size
                """)
                
                return {
                    "total_connections": result["total_connections"] if result else 0,
                    "active_connections": result["active_connections"] if result else 0,
                    "idle_connections": result["idle_connections"] if result else 0,
                    "idle_in_transaction": result["idle_in_transaction"] if result else 0,
                    "database_size": size_result["db_size"] if size_result else 0
                }
        except Exception as e:
            logger.error(f"获取数据库连接统计失败: {e}")
            return {
                "total_connections": 0,
                "active_connections": 0,
                "idle_connections": 0,
                "idle_in_transaction": 0,
                "database_size": 0
            }
    
    @staticmethod
    async def get_table_stats() -> Dict[str, Any]:
        """获取表统计信息"""
        try:
            async with get_db() as conn:
                result = await conn.fetch("""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) as total_size,
                        pg_total_relation_size(schemaname || '.' || tablename) as total_size_bytes,
                        n_live_tup as row_count
                    FROM pg_stat_user_tables
                    ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC
                    LIMIT 10
                """)
                
                tables = []
                for row in result:
                    tables.append({
                        "schema": row["schemaname"],
                        "table": row["tablename"],
                        "size": row["total_size"],
                        "size_bytes": row["total_size_bytes"],
                        "row_count": row["row_count"]
                    })
                
                return {"tables": tables}
        except Exception as e:
            logger.error(f"获取表统计信息失败: {e}")
            return {"tables": []}


class RedisMetrics:
    """Redis指标收集"""
    
    @staticmethod
    async def get_redis_stats() -> Dict[str, Any]:
        """获取Redis统计信息"""
        try:
            if not cache.client:
                return {"connected": False}
            
            # 获取Redis信息
            info = await cache.client.info()
            
            return {
                "connected": True,
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "used_memory_peak": info.get("used_memory_peak", 0),
                "used_memory_peak_human": info.get("used_memory_peak_human", "0B"),
                "used_memory_rss": info.get("used_memory_rss", 0),
                "used_memory_rss_human": info.get("used_memory_rss_human", "0B"),
                "connected_clients": info.get("connected_clients", 0),
                "total_connections_received": info.get("total_connections_received", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": info.get("keyspace_hits", 0) / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
            }
        except Exception as e:
            logger.error(f"获取Redis统计信息失败: {e}")
            return {"connected": False}


class BusinessMetrics:
    """业务指标收集"""
    
    @staticmethod
    async def get_user_stats() -> Dict[str, Any]:
        """获取用户统计"""
        try:
            async with get_db() as conn:
                # 总用户数
                total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
                
                # 今日新增用户
                today = datetime.now().date()
                today_users = await conn.fetchval("""
                    SELECT COUNT(*) FROM users 
                    WHERE DATE(created_at) = $1
                """, today)
                
                # 会员用户数
                member_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_member = true")
                
                return {
                    "total_users": total_users,
                    "today_new_users": today_users,
                    "member_users": member_users,
                    "regular_users": total_users - member_users
                }
        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            return {
                "total_users": 0,
                "today_new_users": 0,
                "member_users": 0,
                "regular_users": 0
            }
    
    @staticmethod
    async def get_order_stats() -> Dict[str, Any]:
        """获取订单统计"""
        try:
            async with get_db() as conn:
                # 总订单数
                total_orders = await conn.fetchval("SELECT COUNT(*) FROM orders")
                
                # 今日订单
                today = datetime.now().date()
                today_orders = await conn.fetchval("""
                    SELECT COUNT(*) FROM orders 
                    WHERE DATE(created_at) = $1
                """, today)
                
                # 成功订单
                success_orders = await conn.fetchval("""
                    SELECT COUNT(*) FROM orders 
                    WHERE status = 'paid'
                """)
                
                # 总金额
                total_amount = await conn.fetchval("""
                    SELECT COALESCE(SUM(amount), 0) FROM orders 
                    WHERE status = 'paid'
                """) or 0
                
                return {
                    "total_orders": total_orders,
                    "today_orders": today_orders,
                    "success_orders": success_orders,
                    "failed_orders": total_orders - success_orders,
                    "total_amount": float(total_amount)
                }
        except Exception as e:
            logger.error(f"获取订单统计失败: {e}")
            return {
                "total_orders": 0,
                "today_orders": 0,
                "success_orders": 0,
                "failed_orders": 0,
                "total_amount": 0.0
            }
    
    @staticmethod
    async def get_scan_stats() -> Dict[str, Any]:
        """获取扫描统计"""
        try:
            async with get_db() as conn:
                # 公司扫描统计
                company_scans = await conn.fetchval("SELECT COUNT(*) FROM company_scans")
                successful_scans = await conn.fetchval("""
                    SELECT COUNT(*) FROM company_scans 
                    WHERE status = 'completed'
                """)
                
                # 报价单扫描
                quote_scans = await conn.fetchval("SELECT COUNT(*) FROM quotes")
                successful_quotes = await conn.fetchval("""
                    SELECT COUNT(*) FROM quotes 
                    WHERE status = 'completed'
                """)
                
                # 合同扫描
                contract_scans = await conn.fetchval("SELECT COUNT(*) FROM contracts")
                successful_contracts = await conn.fetchval("""
                    SELECT COUNT(*) FROM contracts 
                    WHERE status = 'completed'
                """)
                
                return {
                    "company_scans": {
                        "total": company_scans,
                        "successful": successful_scans,
                        "failed": company_scans - successful_scans
                    },
                    "quote_scans": {
                        "total": quote_scans,
                        "successful": successful_quotes,
                        "failed": quote_scans - successful_quotes
                    },
                    "contract_scans": {
                        "total": contract_scans,
                        "successful": successful_contracts,
                        "failed": contract_scans - successful_contracts
                    }
                }
        except Exception as e:
            logger.error(f"获取扫描统计失败: {e}")
            return {
                "company_scans": {"total": 0, "successful": 0, "failed": 0},
                "quote_scans": {"total": 0, "successful": 0, "failed": 0},
                "contract_scans": {"total": 0, "successful": 0, "failed": 0}
            }


class MonitorService:
    """监控服务"""
    
    def __init__(self):
        self.enabled = settings.MONITOR_ENABLED
        self.interval = settings.MONITOR_INTERVAL_SECONDS
        self.system_metrics = SystemMetrics()
        self.db_metrics = DatabaseMetrics()
        self.redis_metrics = RedisMetrics()
        self.business_metrics = BusinessMetrics()
        
        # 告警阈值
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
    
    async def collect_all_metrics(self) -> Dict[str, Any]:
        """收集所有指标"""
        if not self.enabled:
            return {"monitoring_disabled": True}
        
        timestamp = datetime.now().isoformat()
        
        try:
            # 收集系统指标
            system_metrics = {
                "cpu_usage": self.system_metrics.get_cpu_usage(),
                "memory_usage": self.system_metrics.get_memory_usage(),
                "disk_usage": self.system_metrics.get_disk_usage(),
                "network_io": self.system_metrics.get_network_io(),
                "system_info": self.system_metrics.get_system_info()
            }
            
            # 收集数据库指标
            db_stats = await self.db_metrics.get_connection_stats()
            table_stats = await self.db_metrics.get_table_stats()
            
            # 收集Redis指标
            redis_stats = await self.redis_metrics.get_redis_stats()
            
            # 收集业务指标
            user_stats = await self.business_metrics.get_user_stats()
            order_stats = await self.business_metrics.get_order_stats()
            scan_stats = await self.business_metrics.get_scan_stats()
            
            # 检查告警
            await self.check_alerts(system_metrics)
            
            return {
                "timestamp": timestamp,
                "system": system_metrics,
                "database": {**db_stats, **table_stats},
                "redis": redis_stats,
                "business": {
                    "users": user_stats,
                    "orders": order_stats,
                    "scans": scan_stats
                }
            }
            
        except Exception as e:
            logger.error(f"收集监控指标失败: {e}")
            return {
                "timestamp": timestamp,
                "error": str(e)
            }
    
    async def check_alerts(self, system_metrics: Dict[str, Any]):
        """检查告警条件"""
        try:
            # CPU使用率告警
            cpu_usage = system_metrics["cpu_usage"]
            if cpu_usage > self.cpu_threshold:
                alert_high_resource_usage("CPU", cpu_usage, self.cpu_threshold)
            
            # 内存使用率告警
            memory_percent = system_metrics["memory_usage"]["percent"]
            if memory_percent > self.memory_threshold:
                alert_high_resource_usage("内存", memory_percent, self.memory_threshold)
            
            # 磁盘使用率告警
            disk_percent = system_metrics["disk_usage"]["percent"]
            if disk_percent > self.disk_threshold:
                alert_high_resource_usage("磁盘", disk_percent, self.disk_threshold)
                
        except Exception as e:
            logger.error(f"检查告警条件失败: {e}")
    
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        try:
            # 检查数据库连接
            try:
                async with get_db() as conn:
                    await conn.execute("SELECT 1")
                status["services"]["database"] = {
                    "status": "healthy",
                    "message": "数据库连接正常"
                }
            except Exception as e:
                status["services"]["database"] = {
                    "status": "unhealthy",
                    "message": f"数据库连接失败: {str(e)}"
                }
            
            # 检查Redis连接
            try:
                if cache.client:
                    await cache.client.ping()
                    status["services"]["redis"] = {
                        "status": "healthy",
                        "message": "Redis连接正常"
                    }
                else:
                    status["services"]["redis"] = {
                        "status": "disabled",
                        "message": "Redis未配置"
                    }
            except Exception as e:
                status["services"]["redis"] = {
                    "status": "unhealthy",
                    "message": f"Redis连接失败: {str(e)}"
                }
            
            # 检查OSS连接（简化检查）
            status["services"]["oss"] = {
                "status": "unknown",
                "message": "OSS连接状态需要实际文件操作测试"
            }
            
            # 总体状态
            unhealthy_count = sum(1 for s in status["services"].values() if s["status"] == "unhealthy")
            if unhealthy_count == 0:
                status["overall"] = "healthy"
            elif unhealthy_count == 1:
                status["overall"] = "degraded"
            else:
                status["overall"] = "unhealthy"
            
            return status
            
        except Exception as e:
            logger.error(f"获取服务状态失败: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "overall": "unknown"
            }


# 全局监控服务实例
monitor_service = MonitorService()


async def collect_metrics() -> Dict[str, Any]:
    """收集指标的便捷函数"""
    return await monitor_service.collect_all_metrics()


async def get_service_status() -> Dict[str, Any]:
    """获取服务状态的便捷函数"""
    return await monitor_service.get_service_status()


async def get_system_overview() -> Dict[str, Any]:
    """获取系统概览"""
    metrics = await collect_metrics()
    status = await get_service_status()
    
    return {
        "metrics": metrics,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }

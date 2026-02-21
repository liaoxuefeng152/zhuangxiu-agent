"""
备份服务 - 数据库和文件备份，支持自动验证
"""
import os
import subprocess
import shutil
import hashlib
import json
import tarfile
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import asyncio
from pathlib import Path

from app.core.config import settings
from app.core.logger import get_logger
from app.core.database import get_db
from app.services.alert_service import alert_backup_failed, alert_backup_verification_failed
from app.services.oss_service import oss_service

logger = get_logger(__name__)


class DatabaseBackup:
    """数据库备份"""
    
    def __init__(self):
        self.backup_path = settings.BACKUP_STORAGE_PATH
        self.retention_days = settings.BACKUP_RETENTION_DAYS
        
        # 确保备份目录存在
        os.makedirs(self.backup_path, exist_ok=True)
    
    def _get_database_info(self) -> Dict[str, Any]:
        """从DATABASE_URL解析数据库信息"""
        db_url = settings.DATABASE_URL
        if not db_url:
            raise ValueError("DATABASE_URL未配置")
        
        # 解析PostgreSQL连接字符串
        # postgresql://user:password@host:port/database
        import re
        pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
        match = re.match(pattern, db_url)
        
        if not match:
            raise ValueError(f"无法解析DATABASE_URL: {db_url}")
        
        return {
            "host": match.group(3),
            "port": match.group(4),
            "database": match.group(5),
            "username": match.group(1),
            "password": match.group(2)
        }
    
    def create_backup(self) -> Tuple[bool, str, Optional[str]]:
        """创建数据库备份"""
        try:
            db_info = self._get_database_info()
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"zhuangxiu_db_{timestamp}.sql"
            backup_filepath = os.path.join(self.backup_path, backup_filename)
            
            # 设置环境变量（避免密码出现在命令行）
            env = os.environ.copy()
            env['PGPASSWORD'] = db_info["password"]
            
            # 使用pg_dump备份
            cmd = [
                "pg_dump",
                "-h", db_info["host"],
                "-p", db_info["port"],
                "-U", db_info["username"],
                "-d", db_info["database"],
                "-F", "c",  # 自定义格式（压缩）
                "-f", backup_filepath
            ]
            
            logger.info(f"开始数据库备份: {backup_filename}")
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 计算文件哈希
            file_hash = self._calculate_file_hash(backup_filepath)
            file_size = os.path.getsize(backup_filepath)
            
            logger.info(f"数据库备份完成: {backup_filename}, 大小: {file_size/1024/1024:.2f}MB")
            
            return True, backup_filepath, file_hash
            
        except subprocess.CalledProcessError as e:
            error_msg = f"数据库备份失败: {e.stderr}"
            logger.error(error_msg)
            alert_backup_failed("database", error_msg)
            return False, "", None
            
        except Exception as e:
            error_msg = f"数据库备份异常: {str(e)}"
            logger.error(error_msg)
            alert_backup_failed("database", error_msg)
            return False, "", None
    
    def verify_backup(self, backup_filepath: str) -> Tuple[bool, str]:
        """验证数据库备份文件"""
        try:
            if not os.path.exists(backup_filepath):
                return False, "备份文件不存在"
            
            # 检查文件大小
            file_size = os.path.getsize(backup_filepath)
            if file_size < 1024:  # 小于1KB的备份文件可能有问题
                return False, f"备份文件过小: {file_size}字节"
            
            # 使用pg_restore测试备份文件
            db_info = self._get_database_info()
            
            # 设置环境变量
            env = os.environ.copy()
            env['PGPASSWORD'] = db_info["password"]
            
            # 创建临时数据库进行恢复测试
            temp_db_name = f"test_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 创建测试数据库
            create_cmd = [
                "createdb",
                "-h", db_info["host"],
                "-p", db_info["port"],
                "-U", db_info["username"],
                temp_db_name
            ]
            
            subprocess.run(
                create_cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            try:
                # 尝试恢复备份到测试数据库
                restore_cmd = [
                    "pg_restore",
                    "-h", db_info["host"],
                    "-p", db_info["port"],
                    "-U", db_info["username"],
                    "-d", temp_db_name,
                    "-v",  # 详细输出
                    backup_filepath
                ]
                
                result = subprocess.run(
                    restore_cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                logger.info(f"备份验证成功: {backup_filepath}")
                return True, "备份验证成功"
                
            finally:
                # 清理测试数据库
                drop_cmd = [
                    "dropdb",
                    "-h", db_info["host"],
                    "-p", db_info["port"],
                    "-U", db_info["username"],
                    temp_db_name
                ]
                
                subprocess.run(
                    drop_cmd,
                    env=env,
                    capture_output=True,
                    text=True
                )
                
        except subprocess.CalledProcessError as e:
            error_msg = f"备份验证失败: {e.stderr}"
            logger.error(error_msg)
            alert_backup_verification_failed("database", error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"备份验证异常: {str(e)}"
            logger.error(error_msg)
            alert_backup_verification_failed("database", error_msg)
            return False, error_msg
    
    def cleanup_old_backups(self):
        """清理旧的备份文件"""
        try:
            backup_files = []
            for filename in os.listdir(self.backup_path):
                if filename.startswith("zhuangxiu_db_") and filename.endswith(".sql"):
                    filepath = os.path.join(self.backup_path, filename)
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    backup_files.append((filepath, mtime))
            
            # 按修改时间排序
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # 保留最近N天的备份
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            deleted_count = 0
            
            for filepath, mtime in backup_files:
                if mtime < cutoff_date:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                        logger.info(f"删除旧备份: {os.path.basename(filepath)}")
                    except Exception as e:
                        logger.error(f"删除备份文件失败 {filepath}: {e}")
            
            logger.info(f"清理完成，删除了 {deleted_count} 个旧备份")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理旧备份失败: {e}")
            return 0
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """计算文件哈希值"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class FileBackup:
    """文件备份"""
    
    def __init__(self):
        self.backup_path = settings.BACKUP_STORAGE_PATH
        
        # 需要备份的重要目录
        self.important_dirs = [
            "backend/app/core",  # 配置文件
            "backend/app/services",  # 服务代码
            "backend/app/api",  # API代码
            "backend/app/models",  # 数据模型
            "config",  # 配置文件
            "scripts",  # 脚本文件
            "database",  # 数据库迁移脚本
        ]
        
        # 需要备份的重要文件
        self.important_files = [
            "backend/requirements.txt",
            "backend/Dockerfile",
            "docker-compose.dev.yml",
            "docker-compose.server-dev.yml",
            ".env.example",
        ]
        
        # 确保备份目录存在
        os.makedirs(self.backup_path, exist_ok=True)
    
    def create_backup(self) -> Tuple[bool, str, Optional[str]]:
        """创建文件备份"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"zhuangxiu_files_{timestamp}.tar.gz"
            backup_filepath = os.path.join(self.backup_path, backup_filename)
            
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                backup_dir = os.path.join(temp_dir, "backup")
                os.makedirs(backup_dir)
                
                # 备份重要目录
                for dir_path in self.important_dirs:
                    if os.path.exists(dir_path):
                        dest_dir = os.path.join(backup_dir, dir_path)
                        os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
                        shutil.copytree(dir_path, dest_dir, dirs_exist_ok=True)
                        logger.info(f"备份目录: {dir_path}")
                
                # 备份重要文件
                for file_path in self.important_files:
                    if os.path.exists(file_path):
                        dest_file = os.path.join(backup_dir, file_path)
                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                        shutil.copy2(file_path, dest_file)
                        logger.info(f"备份文件: {file_path}")
                
                # 创建备份清单
                backup_manifest = {
                    "timestamp": timestamp,
                    "backup_type": "files",
                    "directories": self.important_dirs,
                    "files": self.important_files,
                    "created_at": datetime.now().isoformat()
                }
                
                manifest_path = os.path.join(backup_dir, "backup_manifest.json")
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_manifest, f, ensure_ascii=False, indent=2)
                
                # 创建tar.gz压缩包
                with tarfile.open(backup_filepath, "w:gz") as tar:
                    tar.add(backup_dir, arcname="zhuangxiu_files")
                
                # 计算文件哈希
                file_hash = self._calculate_file_hash(backup_filepath)
                file_size = os.path.getsize(backup_filepath)
                
                logger.info(f"文件备份完成: {backup_filename}, 大小: {file_size/1024/1024:.2f}MB")
                
                return True, backup_filepath, file_hash
                
        except Exception as e:
            error_msg = f"文件备份失败: {str(e)}"
            logger.error(error_msg)
            alert_backup_failed("files", error_msg)
            return False, "", None
    
    def verify_backup(self, backup_filepath: str) -> Tuple[bool, str]:
        """验证文件备份"""
        try:
            if not os.path.exists(backup_filepath):
                return False, "备份文件不存在"
            
            # 检查文件大小
            file_size = os.path.getsize(backup_filepath)
            if file_size < 1024:  # 小于1KB的备份文件可能有问题
                return False, f"备份文件过小: {file_size}字节"
            
            # 尝试解压并检查清单文件
            with tempfile.TemporaryDirectory() as temp_dir:
                with tarfile.open(backup_filepath, "r:gz") as tar:
                    tar.extractall(temp_dir)
                
                # 检查清单文件
                manifest_path = os.path.join(temp_dir, "zhuangxiu_files", "backup_manifest.json")
                if not os.path.exists(manifest_path):
                    return False, "备份清单文件缺失"
                
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                if manifest.get("backup_type") != "files":
                    return False, "备份类型不匹配"
                
                logger.info(f"文件备份验证成功: {backup_filepath}")
                return True, "备份验证成功"
                
        except tarfile.TarError as e:
            error_msg = f"备份文件损坏: {str(e)}"
            logger.error(error_msg)
            alert_backup_verification_failed("files", error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"备份验证异常: {str(e)}"
            logger.error(error_msg)
            alert_backup_verification_failed("files", error_msg)
            return False, error_msg
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """计算文件哈希值"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class BackupService:
    """备份服务"""
    
    def __init__(self):
        self.enabled = settings.BACKUP_ENABLED
        self.verification_enabled = settings.BACKUP_VERIFICATION_ENABLED
        self.db_backup = DatabaseBackup()
        self.file_backup = FileBackup()
    
    async def perform_full_backup(self) -> Dict[str, Any]:
        """执行完整备份"""
        if not self.enabled:
            return {"status": "disabled", "message": "备份功能已禁用"}
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "database": {"success": False},
            "files": {"success": False},
            "overall": "failed"
        }
        
        try:
            # 数据库备份
            db_success, db_path, db_hash = self.db_backup.create_backup()
            results["database"]["success"] = db_success
            results["database"]["path"] = db_path
            results["database"]["hash"] = db_hash
            
            if db_success and self.verification_enabled:
                verify_success, verify_msg = self.db_backup.verify_backup(db_path)
                results["database"]["verification"] = {
                    "success": verify_success,
                    "message": verify_msg
                }
            
            # 文件备份
            file_success, file_path, file_hash = self.file_backup.create_backup()
            results["files"]["success"] = file_success
            results["files"]["path"] = file_path
            results["files"]["hash"] = file_hash
            
            if file_success and self.verification_enabled:
                verify_success, verify_msg = self.file_backup.verify_backup(file_path)
                results["files"]["verification"] = {
                    "success": verify_success,
                    "message": verify_msg
                }
            
            # 清理旧备份
            deleted_count = self.db_backup.cleanup_old_backups()
            results["cleanup"] = {"deleted_count": deleted_count}
            
            # 确定总体状态
            if db_success and file_success:
                results["overall"] = "success"
                logger.info("完整备份执行成功")
            elif db_success or file_success:
                results["overall"] = "partial"
                logger.warning("备份部分成功")
            else:
                results["overall"] = "failed"
                logger.error("备份完全失败")
            
            return results
            
        except Exception as e:
            error_msg = f"备份执行异常: {str(e)}"
            logger.error(error_msg)
            results["error"] = error_msg
            return results
    
    async def upload_backups_to_oss(self) -> Dict[str, Any]:
        """上传备份到OSS"""
        try:
            results = {
                "timestamp": datetime.now().isoformat(),
                "uploads": []
            }
            
            # 查找最新的备份文件
            backup_files = []
            for filename in os.listdir(self.db_backup.backup_path):
                if filename.startswith("zhuangxiu_") and (filename.endswith(".sql") or filename.endswith(".tar.gz")):
                    filepath = os.path.join(self.db_backup.backup_path, filename)
                    mtime = os.path.getmtime(filepath)
                    backup_files.append((filepath, filename, mtime))
            
            # 只上传今天创建的备份
            today = datetime.now().date()
            uploaded_count = 0
            
            for filepath, filename, mtime in backup_files:
                file_date = datetime.fromtimestamp(mtime).date()
                if file_date == today:
                    try:
                        # 上传到OSS
                        oss_path = f"backups/{filename}"
                        try:
                            # 读取文件内容
                            with open(filepath, 'rb') as f:
                                file_data = f.read()
                            
                            # 使用oss_service上传
                            object_key = oss_service.upload_file(file_data, oss_path, bucket_name='photo')
                            success = True
                            message = f"上传成功: {object_key}"
                        except Exception as upload_error:
                            success = False
                            message = str(upload_error)
                        
                        results["uploads"].append({
                            "file": filename,
                            "success": success,
                            "message": message,
                            "oss_path": oss_path
                        })
                        
                        if success:
                            uploaded_count += 1
                            logger.info(f"备份上传成功: {filename} -> {oss_path}")
                        else:
                            logger.error(f"备份上传失败: {filename} - {message}")
                            
                    except Exception as e:
                        logger.error(f"上传备份文件失败 {filename}: {e}")
                        results["uploads"].append({
                            "file": filename,
                            "success": False,
                            "message": str(e)
                        })
            
            results["uploaded_count"] = uploaded_count
            results["total_files"] = len(backup_files)
            
            logger.info(f"备份上传完成，成功上传 {uploaded_count}/{len(backup_files)} 个文件")
            return results
            
        except Exception as e:
            error_msg = f"上传备份到OSS失败: {str(e)}"
            logger.error(error_msg)
            return {
                "timestamp": datetime.now().isoformat(),
                "error": error_msg,
                "uploads": []
            }
    
    async def get_backup_status(self) -> Dict[str, Any]:
        """获取备份状态"""
        try:
            # 统计备份文件
            backup_files = []
            total_size = 0
            
            for filename in os.listdir(self.db_backup.backup_path):
                if filename.startswith("zhuangxiu_") and (filename.endswith(".sql") or filename.endswith(".tar.gz")):
                    filepath = os.path.join(self.db_backup.backup_path, filename)
                    if os.path.exists(filepath):
                        mtime = os.path.getmtime(filepath)
                        size = os.path.getsize(filepath)
                        total_size += size
                        
                        backup_files.append({
                            "name": filename,
                            "size": size,
                            "size_human": self._format_size(size),
                            "modified": datetime.fromtimestamp(mtime).isoformat(),
                            "age_days": (datetime.now() - datetime.fromtimestamp(mtime)).days
                        })
            
            # 按修改时间排序
            backup_files.sort(key=lambda x: x["modified"], reverse=True)
            
            # 计算磁盘使用情况
            disk_usage = shutil.disk_usage(self.db_backup.backup_path)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "backup_enabled": self.enabled,
                "verification_enabled": self.verification_enabled,
                "backup_path": self.db_backup.backup_path,
                "retention_days": self.db_backup.retention_days,
                "total_backups": len(backup_files),
                "total_size": total_size,
                "total_size_human": self._format_size(total_size),
                "disk_free": disk_usage.free,
                "disk_free_human": self._format_size(disk_usage.free),
                "disk_total": disk_usage.total,
                "disk_total_human": self._format_size(disk_usage.total),
                "disk_usage_percent": (disk_usage.used / disk_usage.total) * 100,
                "recent_backups": backup_files[:10]  # 最近10个备份
            }
            
        except Exception as e:
            error_msg = f"获取备份状态失败: {str(e)}"
            logger.error(error_msg)
            return {
                "timestamp": datetime.now().isoformat(),
                "error": error_msg
            }
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"


# 全局备份服务实例
backup_service = BackupService()


async def perform_full_backup() -> Dict[str, Any]:
    """执行完整备份的便捷函数"""
    return await backup_service.perform_full_backup()


async def upload_backups_to_oss() -> Dict[str, Any]:
    """上传备份到OSS的便捷函数"""
    return await backup_service.upload_backups_to_oss()


async def get_backup_status() -> Dict[str, Any]:
    """获取备份状态的便捷函数"""
    return await backup_service.get_backup_status()

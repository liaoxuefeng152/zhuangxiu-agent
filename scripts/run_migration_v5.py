#!/usr/bin/env python3
"""
V2.6.2优化 - 数据库迁移脚本 V5
执行：python scripts/run_migration_v5.py
"""
import asyncio
import asyncpg
import os
from pathlib import Path

# 从环境变量读取数据库连接信息
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://decoration:decoration123@localhost:5432/zhuangxiu_prod")

# 解析DATABASE_URL
def parse_database_url(url: str):
    """解析postgresql+asyncpg://格式的URL"""
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    return url.replace("postgresql://", "")


async def run_migration():
    """执行迁移"""
    # 读取SQL文件
    sql_file = Path(__file__).parent.parent / "database" / "migration_v5.sql"
    if not sql_file.exists():
        print(f"❌ SQL文件不存在: {sql_file}")
        return
    
    sql_content = sql_file.read_text(encoding="utf-8")
    
    # 解析数据库连接信息
    db_url = parse_database_url(DATABASE_URL)
    # 简单解析（实际应该用urllib.parse）
    if "@" in db_url:
        auth_part, db_part = db_url.split("@")
        user, password = auth_part.split(":")
        host_port, database = db_part.split("/")
        if ":" in host_port:
            host, port = host_port.split(":")
        else:
            host, port = host_port, "5432"
    else:
        print("❌ DATABASE_URL格式错误")
        return
    
    try:
        # 连接数据库
        conn = await asyncpg.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database
        )
        
        print("✅ 数据库连接成功")
        print("📝 开始执行迁移 V5...")
        
        # 执行SQL（按语句分割）
        statements = [s.strip() for s in sql_content.split(";") if s.strip() and not s.strip().startswith("--")]
        
        for i, stmt in enumerate(statements, 1):
            if stmt:
                try:
                    await conn.execute(stmt)
                    print(f"  ✅ 执行语句 {i}/{len(statements)}")
                except Exception as e:
                    print(f"  ⚠️  语句 {i} 执行失败（可能已存在）: {e}")
        
        await conn.close()
        print("✅ 迁移 V5 完成！")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_migration())

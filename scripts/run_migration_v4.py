#!/usr/bin/env python3
"""
执行 database/migration_v4.sql（PRD V2.6.1）
用法：在项目根目录执行
  python scripts/run_migration_v4.py
或（若在 backend 目录且已配置 .env）
  cd backend && python -c "
import asyncio, os, sys
sys.path.insert(0, '.')
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
import asyncpg
async def run():
    url = os.getenv('DATABASE_URL', '').replace('postgresql+asyncpg://', 'postgresql://')
    if not url:
        print('DATABASE_URL 未设置'); return
    conn = await asyncpg.connect(url)
    sql_path = Path(__file__).parent.parent / 'database' / 'migration_v4.sql'
    sql = sql_path.read_text(encoding='utf-8')
    for stmt in sql.split(';'):
        stmt = stmt.strip()
        if not stmt or stmt.startswith('--') or stmt.startswith('\\'):
            continue
        try:
            await conn.execute(stmt)
            print('OK:', stmt[:60].replace(chr(10), ' '))
        except Exception as e:
            print('SKIP/ERR:', e, '|', stmt[:80])
    await conn.close()
    print('Migration V4 done.')
asyncio.run(run())
"
"""
import asyncio
import os
import sys
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def main():
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass

    url = os.getenv("DATABASE_URL", "")
    if not url:
        print("未设置 DATABASE_URL，请配置 .env 或环境变量")
        sys.exit(1)
    url = url.replace("postgresql+asyncpg://", "postgresql://")

    sql_path = ROOT / "database" / "migration_v4.sql"
    if not sql_path.exists():
        print(f"未找到 {sql_path}")
        sys.exit(1)
    sql = sql_path.read_text(encoding="utf-8")

    async def run():
        import asyncpg
        conn = await asyncpg.connect(url)
        for raw in sql.split(";"):
            stmt = raw.strip()
            if not stmt or stmt.startswith("--") or stmt.startswith("\\"):
                continue
            try:
                await conn.execute(stmt)
                print("OK:", stmt[:70].replace("\n", " "))
            except Exception as e:
                print("ERR:", e, "|", stmt[:80])
        await conn.close()
        print("Migration V4 (PRD V2.6.1) 执行完成。")

    asyncio.run(run())


if __name__ == "__main__":
    main()

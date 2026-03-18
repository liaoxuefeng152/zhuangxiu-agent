#!/usr/bin/env python3
"""
测试脚本：查看合同分析结果的实际数据结构
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import select
from app.core.database import async_session_maker
from app.models import Contract
import json

async def check_contract_data():
    """检查最近的合同数据结构"""
    async with async_session_maker() as db:
        # 查询最近的一条合同记录
        result = await db.execute(
            select(Contract)
            .where(Contract.status == 'completed')
            .order_by(Contract.created_at.desc())
            .limit(1)
        )
        contract = result.scalar_one_or_none()
        
        if not contract:
            print("❌ 没有找到已完成的合同记录")
            return
        
        print(f"✅ 找到合同记录 ID: {contract.id}")
        print(f"文件名: {contract.file_name}")
        print(f"状态: {contract.status}")
        print(f"风险等级: {contract.risk_level}")
        print(f"是否解锁: {contract.is_unlocked}")
        print("\n" + "="*80)
        
        # 打印result_json的结构
        if contract.result_json:
            print("\n📋 result_json 数据结构:")
            print(json.dumps(contract.result_json, ensure_ascii=False, indent=2))
        else:
            print("\n❌ result_json 为空")
        
        print("\n" + "="*80)
        
        # 打印各个字段
        print("\n📋 风险条款 (risk_items):")
        if contract.risk_items:
            print(json.dumps(contract.risk_items, ensure_ascii=False, indent=2))
        else:
            print("  (空)")
        
        print("\n📋 不公平条款 (unfair_terms):")
        if contract.unfair_terms:
            print(json.dumps(contract.unfair_terms, ensure_ascii=False, indent=2))
        else:
            print("  (空)")
        
        print("\n📋 缺失条款 (missing_terms):")
        if contract.missing_terms:
            print(json.dumps(contract.missing_terms, ensure_ascii=False, indent=2))
        else:
            print("  (空)")
        
        print("\n📋 修改建议 (suggested_modifications):")
        if contract.suggested_modifications:
            print(json.dumps(contract.suggested_modifications, ensure_ascii=False, indent=2))
        else:
            print("  (空)")

if __name__ == "__main__":
    asyncio.run(check_contract_data())

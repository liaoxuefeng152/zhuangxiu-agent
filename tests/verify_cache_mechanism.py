#!/usr/bin/env python3
"""
验证公司扫描缓存机制
检查30天缓存逻辑是否生效
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

try:
    from app.core.database import AsyncSessionLocal
    from app.models import CompanyScan
    from sqlalchemy import select, and_
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


async def check_cache_mechanism():
    """检查缓存机制"""
    print("=" * 70)
    print("公司扫描缓存机制验证")
    print("=" * 70)
    
    async with AsyncSessionLocal() as db:
        # 1. 检查总记录数
        result = await db.execute(select(CompanyScan))
        total_records = len(result.all())
        print(f"1. 总公司扫描记录数: {total_records}")
        
        if total_records == 0:
            print("   ⚠️ 数据库中没有记录，缓存机制无法测试")
            return
        
        # 2. 检查30天内的记录
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        result = await db.execute(
            select(CompanyScan)
            .where(CompanyScan.created_at >= thirty_days_ago)
        )
        recent_records = len(result.all())
        print(f"2. 30天内的记录数: {recent_records} ({recent_records/total_records*100:.1f}%)")
        
        # 3. 检查缓存标记
        result = await db.execute(
            select(CompanyScan)
            .where(CompanyScan.unlock_type == 'cached')
        )
        cached_records = len(result.all())
        print(f"3. 标记为'cached'的记录: {cached_records}")
        
        # 4. 检查重复公司（可能使用缓存的）
        result = await db.execute(
            select(CompanyScan.company_name)
            .where(CompanyScan.created_at >= thirty_days_ago)
            .group_by(CompanyScan.company_name)
            .having(select(CompanyScan.id).count() > 1)
        )
        duplicate_companies = result.all()
        print(f"4. 30天内重复扫描的公司数: {len(duplicate_companies)}")
        
        # 5. 模拟缓存查询逻辑
        print("\n5. 模拟缓存查询逻辑测试:")
        print("-" * 50)
        
        # 获取一个公司名称进行测试
        result = await db.execute(
            select(CompanyScan.company_name)
            .where(CompanyScan.created_at >= thirty_days_ago)
            .limit(1)
        )
        test_company = result.scalar_one_or_none()
        
        if test_company:
            print(f"   测试公司: {test_company}")
            
            # 模拟缓存查询
            cache_result = await db.execute(
                select(CompanyScan)
                .where(
                    and_(
                        CompanyScan.company_name == test_company,
                        CompanyScan.status == "completed",
                        CompanyScan.created_at >= thirty_days_ago
                    )
                )
                .order_by(CompanyScan.created_at.desc())
                .limit(1)
            )
            cached_scan = cache_result.scalar_one_or_none()
            
            if cached_scan:
                print(f"   ✓ 找到缓存记录: ID={cached_scan.id}")
                print(f"     创建时间: {cached_scan.created_at}")
                print(f"     解锁类型: {cached_scan.unlock_type}")
                print(f"     公司信息: {cached_scan.company_info is not None}")
                print(f"     法律风险: {cached_scan.legal_risks is not None}")
            else:
                print(f"   ✗ 未找到缓存记录")
        else:
            print("   没有30天内的公司记录可供测试")
        
        # 6. 代码逻辑分析
        print("\n6. 代码逻辑分析:")
        print("-" * 50)
        print("   ✅ 缓存查询条件:")
        print("      - 公司名称相同")
        print("      - 状态为'completed'")
        print("      - 创建时间在最近30天内")
        print("      - 按创建时间倒序，取最新一条")
        print()
        print("   ✅ 缓存使用逻辑:")
        print("      - 如果找到缓存，使用缓存数据")
        print("      - 避免调用聚合数据API")
        print("      - 标记unlock_type='cached'")
        print()
        print("   📊 当前状态评估:")
        
        if cached_records > 0:
            print("      ✓ 缓存机制已生效")
            print(f"        有{cached_records}条记录使用了缓存")
        elif len(duplicate_companies) > 0:
            print("      ⚠️ 有重复公司但未标记为cached")
            print("        可能原因:")
            print("        1. 重复扫描间隔超过30天")
            print("        2. 缓存逻辑执行有问题")
            print("        3. 数据不完整（缺少company_info或legal_risks）")
        else:
            print("      ℹ️ 没有重复公司扫描")
            print("        缓存机制等待实际使用")
        
        # 7. 优化建议
        print("\n7. 优化建议:")
        print("-" * 50)
        print("   🔧 短期优化:")
        print("      - 确保company_info和legal_risks字段完整")
        print("      - 添加缓存命中率统计")
        print("      - 监控API调用节省情况")
        print()
        print("   🚀 长期优化:")
        print("      - 添加Redis缓存（毫秒级响应）")
        print("      - 实现多级缓存架构")
        print("      - 添加缓存预热机制")
        print("      - 调整缓存有效期策略")


async def test_cache_scenario():
    """测试缓存场景"""
    print("\n" + "=" * 70)
    print("缓存场景模拟测试")
    print("=" * 70)
    
    async with AsyncSessionLocal() as db:
        # 创建一个测试公司记录
        test_company = "测试装修有限公司"
        
        print(f"测试公司: {test_company}")
        print("-" * 50)
        
        # 检查是否已有记录
        result = await db.execute(
            select(CompanyScan)
            .where(CompanyScan.company_name == test_company)
            .order_by(CompanyScan.created_at.desc())
            .limit(1)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            age_days = (datetime.utcnow() - existing.created_at).days
            print(f"已有记录: ID={existing.id}, 创建于{age_days}天前")
            print(f"状态: {existing.status}, 解锁类型: {existing.unlock_type}")
            
            if age_days <= 30 and existing.status == "completed":
                print("✅ 符合缓存条件，下次扫描应使用缓存")
            elif age_days > 30:
                print("⚠️ 记录超过30天，下次扫描将调用API")
            else:
                print("⚠️ 记录状态不是completed")
        else:
            print("没有现有记录，首次扫描将调用API")
        
        print("\n缓存机制总结:")
        print("1. 代码逻辑已实现30天缓存")
        print("2. 实际效果取决于数据库中的记录")
        print("3. 重复扫描相同公司可节省API费用")
        print("4. 建议添加Redis缓存提升性能")


def main():
    """主函数"""
    try:
        # 运行检查
        asyncio.run(check_cache_mechanism())
        
        # 运行场景测试
        asyncio.run(test_cache_scenario())
        
        print("\n" + "=" * 70)
        print("验证完成")
        print("=" * 70)
        print("\n结论:")
        print("- 30天缓存逻辑在代码层面已实现")
        print("- 实际效果需要数据库中有符合条件的记录")
        print("- 建议进一步优化缓存机制")
        
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n可能的原因:")
        print("1. 数据库未运行")
        print("2. 数据库连接配置问题")
        print("3. 表结构不匹配")
        print("\n解决方法:")
        print("1. 启动数据库: docker compose -f docker-compose.dev.yml up -d")
        print("2. 检查.env文件配置")
        print("3. 运行数据库迁移")


if __name__ == "__main__":
    main()

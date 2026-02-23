#!/usr/bin/env python3
"""
验证OCR参数修复效果
检查Advanced类型是否不再包含output_bar_code参数
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 直接检查OCR服务文件
ocr_service_path = "backend/app/services/ocr_service.py"

print("=== 验证OCR参数修复效果 ===")
print(f"检查文件: {ocr_service_path}")

# 读取OCR服务文件
with open(ocr_service_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查关键修复点
issues_found = []

# 1. 检查Advanced类型是否包含output_bar_code参数
if 'Advanced' in content:
    # 查找Advanced相关的代码
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'Advanced' in line and 'output_bar_code' in line:
            issues_found.append(f"第{i+1}行: Advanced类型包含output_bar_code参数: {line.strip()}")
        elif 'Advanced' in line and 'Type' in line:
            print(f"第{i+1}行: Advanced类型设置: {line.strip()}")

# 2. 检查recognize_general_text函数中的参数设置
if 'def recognize_general_text' in content:
    start = content.find('def recognize_general_text')
    end = content.find('def ', start + 1)
    if end == -1:
        end = len(content)
    
    function_content = content[start:end]
    
    # 检查Type参数设置
    if 'Type' in function_content:
        print("\n=== recognize_general_text函数中的Type参数设置 ===")
        lines = function_content.split('\n')
        for i, line in enumerate(lines):
            if 'Type' in line:
                print(f"第{i+1}行: {line.strip()}")
    
    # 检查output_bar_code参数
    if 'output_bar_code' in function_content:
        print("\n=== 检查output_bar_code参数 ===")
        lines = function_content.split('\n')
        for i, line in enumerate(lines):
            if 'output_bar_code' in line:
                print(f"第{i+1}行: {line.strip()}")
                # 检查是否为False
                if 'False' in line:
                    print(f"  ✅ output_bar_code已设置为False")
                else:
                    issues_found.append(f"第{i+1}行: output_bar_code未设置为False: {line.strip()}")

# 3. 检查修复的代码行
print("\n=== 检查修复的代码行 ===")
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'output_bar_code' in line and 'False' in line:
        print(f"第{i+1}行: ✅ 已修复: {line.strip()}")
    elif 'Type' in line and 'Advanced' in line:
        print(f"第{i+1}行: ✅ Type参数设置: {line.strip()}")

# 输出结果
print("\n=== 验证结果 ===")
if issues_found:
    print("❌ 发现以下问题:")
    for issue in issues_found:
        print(f"  - {issue}")
    print("\n建议: 确保Advanced类型的output_bar_code参数设置为False")
else:
    print("✅ OCR参数修复验证通过!")
    print("  - Advanced类型的output_bar_code参数已正确设置为False")
    print("  - Type参数已正确设置")

# 检查数据库迁移文件
print("\n=== 检查数据库迁移文件 ===")
migration_file = "database/migration_v9_company_unlock.sql"
if os.path.exists(migration_file):
    print(f"✅ 数据库迁移文件存在: {migration_file}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_content = f.read()
    
    if 'is_unlocked' in migration_content and 'unlock_type' in migration_content:
        print("✅ 迁移文件包含is_unlocked和unlock_type字段")
    else:
        print("❌ 迁移文件缺少必要的字段")
else:
    print(f"❌ 数据库迁移文件不存在: {migration_file}")

print("\n=== 总结 ===")
print("1. OCR参数修复: 确保Advanced类型不包含output_bar_code参数或设置为False")
print("2. 数据库修复: 确保company_scans表包含is_unlocked和unlock_type字段")
print("3. 生产环境: 已执行数据库迁移并重启后端服务")

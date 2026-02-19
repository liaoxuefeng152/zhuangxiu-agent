import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

print("=== 检查验收报告数据库数据 ===")

# 首先检查Docker容器是否在运行
print("\n1. 检查PostgreSQL容器状态:")
cmd = ['docker', 'ps', '-f', 'name=decoration-postgres-dev', '--format', 'table {{.Names}}\t{{.Status}}']
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0 or 'decoration-postgres-dev' not in result.stdout:
    print("⚠️ PostgreSQL容器可能未运行，尝试启动...")
    cmd = ['docker', 'compose', '-f', 'docker-compose.dev.yml', 'ps', 'postgres']
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

# 查询验收报告表结构
print("\n2. 查询验收报告表结构:")
cmd = [
    'docker', 'exec', 'decoration-postgres-dev',
    'psql', '-U', 'postgres', '-d', 'zhuangxiu_dev',
    '-c', "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'acceptance_analysis' ORDER BY ordinal_position LIMIT 15;"
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print(result.stdout)
else:
    print(f"查询失败: {result.stderr}")
    # 尝试使用docker-compose exec
    cmd = [
        'docker-compose', '-f', 'docker-compose.dev.yml', 'exec', '-T', 'postgres',
        'psql', '-U', 'postgres', '-d', 'zhuangxiu_dev',
        '-c', "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'acceptance_analysis' ORDER BY ordinal_position LIMIT 15;"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

# 查询所有验收报告数据
print("\n3. 查询所有验收报告数据:")
cmd = [
    'docker', 'exec', 'decoration-postgres-dev',
    'psql', '-U', 'postgres', '-d', 'zhuangxiu_dev',
    '-c', "SELECT id, stage, severity, result_status, created_at FROM acceptance_analysis WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT 20;"
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print(result.stdout)
else:
    cmd = [
        'docker-compose', '-f', 'docker-compose.dev.yml', 'exec', '-T', 'postgres',
        'psql', '-U', 'postgres', '-d', 'zhuangxiu_dev',
        '-c', "SELECT id, stage, severity, result_status, created_at FROM acceptance_analysis WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT 20;"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

# 按阶段统计
print("\n4. 按阶段统计验收报告数量:")
cmd = [
    'docker', 'exec', 'decoration-postgres-dev',
    'psql', '-U', 'postgres', '-d', 'zhuangxiu_dev',
    '-c', "SELECT stage, COUNT(*) as count FROM acceptance_analysis WHERE deleted_at IS NULL GROUP BY stage ORDER BY stage;"
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print(result.stdout)
else:
    cmd = [
        'docker-compose', '-f', 'docker-compose.dev.yml', 'exec', '-T', 'postgres',
        'psql', '-U', 'postgres', '-d', 'zhuangxiu_dev',
        '-c', "SELECT stage, COUNT(*) as count FROM acceptance_analysis WHERE deleted_at IS NULL GROUP BY stage ORDER BY stage;"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

# 特别检查S03相关记录
print("\n5. 检查S03或woodwork阶段的记录:")
cmd = [
    'docker', 'exec', 'decoration-postgres-dev',
    'psql', '-U', 'postgres', '-d', 'zhuangxiu_dev',
    '-c', "SELECT id, stage, severity, result_status, created_at FROM acceptance_analysis WHERE deleted_at IS NULL AND (stage = 'S03' OR stage = 'woodwork' OR stage LIKE '%S03%' OR stage LIKE '%woodwork%') ORDER BY created_at DESC;"
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print(result.stdout)
else:
    cmd = [
        'docker-compose', '-f', 'docker-compose.dev.yml', 'exec', '-T', 'postgres',
        'psql', '-U', 'postgres', '-d', 'zhuangxiu_dev',
        '-c', "SELECT id, stage, severity, result_status, created_at FROM acceptance_analysis WHERE deleted_at IS NULL AND (stage = 'S03' OR stage = 'woodwork' OR stage LIKE '%S03%' OR stage LIKE '%woodwork%') ORDER BY created_at DESC;"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

# 检查验收报告创建时的阶段映射
print("\n6. 检查验收报告创建逻辑（查看后端代码）:")
print("从backend/app/api/v1/acceptance.py查看analyze函数中的阶段处理...")
try:
    with open('backend/app/api/v1/acceptance.py', 'r') as f:
        content = f.read()
        # 查找analyze函数
        import re
        analyze_match = re.search(r'async def analyze_acceptance.*?def', content, re.DOTALL)
        if analyze_match:
            analyze_func = analyze_match.group(0)
            print("找到analyze_acceptance函数，检查阶段处理逻辑...")
            # 查找stage参数的使用
            if 'request.stage' in analyze_func:
                print("  - 使用request.stage参数")
            # 查找阶段验证逻辑
            if 'STAGES' in analyze_func or 'STAGES_LEGACY' in analyze_func:
                print("  - 引用了STAGES或STAGES_LEGACY常量")
        else:
            print("未找到analyze_acceptance函数")
except Exception as e:
    print(f"读取文件失败: {e}")

print("\n✅ 数据库检查完成")

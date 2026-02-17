import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

print("=== 检查验收报告数据库数据（使用正确用户） ===")

# 获取数据库配置
db_user = os.getenv('DB_USER', 'decoration_dev')
db_password = os.getenv('DB_PASSWORD', '')
db_name = os.getenv('DB_NAME', 'zhuangxiu_dev')

print(f"数据库用户: {db_user}")
print(f"数据库名称: {db_name}")

# 首先检查Docker容器是否在运行
print("\n1. 检查PostgreSQL容器状态:")
cmd = ['docker', 'ps', '-f', 'name=decoration-postgres-dev', '--format', 'table {{.Names}}\t{{.Status}}']
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)

# 查询验收报告表结构 - 使用正确的用户
print("\n2. 查询验收报告表结构:")
cmd = [
    'docker', 'exec', 'decoration-postgres-dev',
    'psql', '-U', db_user, '-d', db_name,
    '-c', "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'acceptance_analysis' ORDER BY ordinal_position LIMIT 15;"
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print(result.stdout)
else:
    print(f"查询失败: {result.stderr}")
    # 尝试使用环境变量传递密码
    cmd = [
        'docker', 'exec', '-e', f'PGPASSWORD={db_password}', 'decoration-postgres-dev',
        'psql', '-U', db_user, '-d', db_name,
        '-c', "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'acceptance_analysis' ORDER BY ordinal_position LIMIT 15;"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

# 查询所有验收报告数据
print("\n3. 查询所有验收报告数据:")
cmd = [
    'docker', 'exec', '-e', f'PGPASSWORD={db_password}', 'decoration-postgres-dev',
    'psql', '-U', db_user, '-d', db_name,
    '-c', "SELECT id, stage, severity, result_status, created_at FROM acceptance_analysis WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT 20;"
]
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)

# 按阶段统计
print("\n4. 按阶段统计验收报告数量:")
cmd = [
    'docker', 'exec', '-e', f'PGPASSWORD={db_password}', 'decoration-postgres-dev',
    'psql', '-U', db_user, '-d', db_name,
    '-c', "SELECT stage, COUNT(*) as count FROM acceptance_analysis WHERE deleted_at IS NULL GROUP BY stage ORDER BY stage;"
]
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)

# 特别检查S03相关记录
print("\n5. 检查S03或woodwork阶段的记录:")
cmd = [
    'docker', 'exec', '-e', f'PGPASSWORD={db_password}', 'decoration-postgres-dev',
    'psql', '-U', db_user, '-d', db_name,
    '-c', "SELECT id, stage, severity, result_status, created_at FROM acceptance_analysis WHERE deleted_at IS NULL AND (stage = 'S03' OR stage = 'woodwork' OR stage LIKE '%S03%' OR stage LIKE '%woodwork%') ORDER BY created_at DESC;"
]
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)

# 检查验收报告创建时的阶段映射 - 直接读取后端代码
print("\n6. 检查验收报告创建逻辑:")
try:
    with open('backend/app/api/v1/acceptance.py', 'r') as f:
        content = f.read()
        
    # 查找STAGES定义
    import re
    stages_match = re.search(r'STAGES\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if stages_match:
        print(f"STAGES定义: {stages_match.group(0)[:100]}...")
    
    # 查找STAGES_LEGACY定义
    legacy_match = re.search(r'STAGES_LEGACY\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if legacy_match:
        print(f"STAGES_LEGACY定义: {legacy_match.group(0)[:100]}...")
    
    # 查找阶段映射
    mapping_match = re.search(r'_ACCEPTANCE_STAGE_TO_S\s*=\s*\{(.*?)\}', content, re.DOTALL)
    if mapping_match:
        print(f"阶段映射: {mapping_match.group(0)[:150]}...")
    
    # 查找analyze_acceptance函数中的阶段处理
    analyze_match = re.search(r'async def analyze_acceptance\(.*?\):(.*?)(?=\n\n|\ndef|\nclass)', content, re.DOTALL)
    if analyze_match:
        analyze_func = analyze_match.group(1)
        # 检查阶段参数使用
        if 'request.stage' in analyze_func:
            print("  - analyze_acceptance函数使用request.stage参数")
        # 检查阶段验证
        if 'stage not in STAGES' in analyze_func or 'stage not in STAGES_LEGACY' in analyze_func:
            print("  - 有阶段验证逻辑")
        # 检查阶段存储
        if 'stage=' in analyze_func:
            print("  - 有阶段存储逻辑")
            
except Exception as e:
    print(f"读取文件失败: {e}")

print("\n✅ 数据库检查完成")

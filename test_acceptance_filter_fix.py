import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

print("=== 测试验收报告阶段筛选功能修复 ===")

# 获取API基础URL
base_url = os.getenv('TARO_APP_API_BASE_URL', 'http://localhost:8000/api/v1')
print(f"API Base URL: {base_url}")

# 尝试从.env文件读取测试token
token = os.getenv('TEST_ACCESS_TOKEN')
if not token:
    print("未找到测试token，尝试从本地存储读取...")
    import subprocess
    try:
        result = subprocess.run(['cat', '/tmp/test_token.txt'], capture_output=True, text=True)
        if result.returncode == 0:
            token = result.stdout.strip()
    except:
        pass

if not token:
    print("❌ 未找到有效的测试token，无法测试API")
    exit(1)

print(f"使用测试token: {token[:20]}...")
headers = {'Authorization': f'Bearer {token}'}

# 测试函数
def test_stage_filter(stage_param, expected_stage_codes):
    """测试阶段筛选功能"""
    print(f"\n测试阶段筛选: {stage_param}")
    
    url = f"{base_url}/acceptance"
    params = {'page': 1, 'page_size': 10}
    if stage_param:
        params['stage'] = stage_param
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"  请求URL: {response.url}")
        print(f"  响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                items = data.get('data', {}).get('list', [])
                print(f"  返回记录数: {len(items)}")
                
                if items:
                    print(f"  返回的阶段代码:")
                    for item in items:
                        stage = item.get('stage', '未知')
                        print(f"    - ID: {item.get('id')}, 阶段: {stage}, 状态: {item.get('result_status')}")
                        
                    # 验证阶段代码
                    all_stages = [item.get('stage') for item in items]
                    valid = any(stage in expected_stage_codes for stage in all_stages)
                    if valid:
                        print(f"  ✅ 筛选成功: 找到了{stage_param}阶段的验收报告")
                    else:
                        print(f"  ⚠️  警告: 返回的阶段代码{all_stages}不包含预期的{expected_stage_codes}")
                else:
                    print(f"  ℹ️  信息: 没有找到{stage_param}阶段的验收报告")
            else:
                print(f"  ❌ API返回错误: {data.get('msg')}")
        else:
            print(f"  ❌ API请求失败: {response.text}")
            
    except Exception as e:
        print(f"  ❌ 请求异常: {e}")

# 执行测试
print("\n1. 测试全部验收报告:")
test_stage_filter(None, [])

print("\n2. 测试S03木工阶段筛选:")
# S03应该匹配数据库中存储的"woodwork"或"S03"
test_stage_filter("S03", ["S03", "woodwork"])

print("\n3. 测试woodwork阶段筛选:")
test_stage_filter("woodwork", ["woodwork", "S03"])

print("\n4. 测试S01隐蔽工程阶段筛选:")
# S01应该匹配数据库中存储的"plumbing"或"S01"
test_stage_filter("S01", ["S01", "plumbing"])

print("\n5. 测试S02泥瓦工阶段筛选:")
# S02应该匹配数据库中存储的"carpentry"或"S02"
test_stage_filter("S02", ["S02", "carpentry"])

print("\n6. 测试S04油漆阶段筛选:")
# S04应该匹配数据库中存储的"painting"或"S04"
test_stage_filter("S04", ["S04", "painting"])

print("\n7. 测试S05安装收尾阶段筛选:")
# S05应该匹配数据库中存储的"installation"或"S05"
test_stage_filter("S05", ["S05", "installation"])

print("\n✅ 测试完成")
print("\n修复说明:")
print("1. 前端数据管理页面发送 stage='S03' 进行筛选")
print("2. 后端API现在支持阶段代码映射:")
print("   - S03 -> woodwork (数据库中可能存储的是woodwork)")
print("   - S01 -> plumbing")
print("   - S02 -> carpentry")
print("   - S04 -> painting")
print("   - S05 -> installation")
print("3. 修复后，无论数据库中存储的是'S03'还是'woodwork'，都能正确筛选出来")

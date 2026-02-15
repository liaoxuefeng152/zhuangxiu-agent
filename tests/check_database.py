#!/usr/bin/env python3
"""
查询数据库中的施工陪伴相关数据
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://120.26.201.61:8001/api/v1"

def login():
    """登录获取token"""
    resp = requests.post(
        f"{BASE_URL}/users/login",
        json={"code": "dev_weapp_mock"},
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        data = result.get("data", {})
    else:
        data = result
    
    token = data.get("access_token")
    user_id = data.get("user_id")
    
    return token, user_id

def check_construction_data(token, user_id):
    """检查施工进度数据"""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    print("\n" + "="*80)
    print("1. 施工进度数据 (constructions)")
    print("="*80)
    
    resp = requests.get(
        f"{BASE_URL}/constructions/schedule",
        headers=headers,
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        data = result.get("data", {})
    else:
        data = result
    
    print(f"开工日期: {data.get('start_date', '未设置')}")
    print(f"预计完工日期: {data.get('estimated_end_date', '未设置')}")
    print(f"进度百分比: {data.get('progress_percentage', 0)}%")
    print(f"是否延期: {data.get('is_delayed', False)}")
    print(f"延期天数: {data.get('delay_days', 0)}")
    
    stages = data.get("stages", {})
    print(f"\n阶段状态:")
    for stage_key, stage_info in stages.items():
        print(f"  {stage_key}: {stage_info.get('status', 'pending')} "
              f"(开始: {stage_info.get('start_date', '')[:10]}, "
              f"结束: {stage_info.get('end_date', '')[:10]})")
    
    return data

def check_material_checks(token, user_id):
    """检查材料核对数据"""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    print("\n" + "="*80)
    print("2. 材料核对数据 (material_checks)")
    print("="*80)
    
    resp = requests.get(
        f"{BASE_URL}/material-checks/latest",
        headers=headers,
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        data = result.get("data", {})
    else:
        data = result
    
    if data:
        print(f"最新材料核对ID: {data.get('id')}")
        print(f"核对结果: {data.get('result')}")
        print(f"问题备注: {data.get('problem_note', '无')}")
        print(f"提交时间: {data.get('submitted_at', '')[:19]}")
        items = data.get("items", [])
        print(f"材料项数: {len(items)}")
        for i, item in enumerate(items[:5], 1):
            print(f"  {i}. {item.get('material_name')} "
                  f"({item.get('spec_brand', '无规格')}) "
                  f"数量: {item.get('quantity', '无')} "
                  f"照片数: {len(item.get('photo_urls', []))}")
    else:
        print("无材料核对记录")
    
    return data

def check_acceptance_analyses(token, user_id):
    """检查验收分析数据"""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    print("\n" + "="*80)
    print("3. 验收分析数据 (acceptance_analyses)")
    print("="*80)
    
    resp = requests.get(
        f"{BASE_URL}/acceptance",
        headers=headers,
        params={"page": 1, "page_size": 20},
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        data = result.get("data", {})
        analyses = data.get("list", [])
        total = data.get("total", len(analyses))
    else:
        analyses = result.get("list", [])
        total = len(analyses)
    
    print(f"总记录数: {total}")
    print(f"\n最近10条验收记录:")
    print(f"{'ID':<8} {'阶段':<15} {'状态':<15} {'严重程度':<12} {'创建时间':<20}")
    print("-" * 80)
    
    for analysis in analyses[:10]:
        print(f"{analysis.get('id', ''):<8} "
              f"{analysis.get('stage', ''):<15} "
              f"{analysis.get('status', ''):<15} "
              f"{analysis.get('severity', ''):<12} "
              f"{analysis.get('created_at', '')[:19]:<20}")
    
    # 按阶段统计
    stage_counts = {}
    for analysis in analyses:
        stage = analysis.get('stage', 'unknown')
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    
    print(f"\n按阶段统计:")
    for stage, count in sorted(stage_counts.items()):
        print(f"  {stage}: {count}条")
    
    return analyses

def check_construction_photos(token, user_id):
    """检查施工照片数据"""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    print("\n" + "="*80)
    print("4. 施工照片数据 (construction_photos)")
    print("="*80)
    
    resp = requests.get(
        f"{BASE_URL}/construction-photos",
        headers=headers,
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        data = result.get("data", {})
        photos_by_stage = data.get("photos", {})
        photos_list = data.get("list", [])
    else:
        photos_by_stage = result.get("photos", {})
        photos_list = result.get("list", [])
    
    total_photos = len(photos_list)
    print(f"总照片数: {total_photos}")
    
    if photos_by_stage:
        print(f"\n按阶段分组:")
        for stage, photos in photos_by_stage.items():
            print(f"  {stage}: {len(photos)}张")
            for photo in photos[:3]:
                print(f"    - {photo.get('file_name', '未命名')} "
                      f"(ID: {photo.get('id')}, "
                      f"创建时间: {photo.get('created_at', '')[:19]})")
    else:
        print("无施工照片记录")
    
    return photos_list

def main():
    print("\n" + "="*80)
    print("数据库数据检查")
    print("="*80)
    
    try:
        token, user_id = login()
        print(f"\n登录成功 (User ID: {user_id})")
        
        # 检查各项数据
        construction_data = check_construction_data(token, user_id)
        material_check_data = check_material_checks(token, user_id)
        acceptance_analyses = check_acceptance_analyses(token, user_id)
        construction_photos = check_construction_photos(token, user_id)
        
        # 总结
        print("\n" + "="*80)
        print("数据总结")
        print("="*80)
        print(f"✅ 施工进度: {'已设置' if construction_data.get('start_date') else '未设置'}")
        print(f"✅ 材料核对: {'有记录' if material_check_data else '无记录'}")
        print(f"✅ 验收分析: {len(acceptance_analyses)}条记录")
        print(f"✅ 施工照片: {len(construction_photos)}张")
        
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

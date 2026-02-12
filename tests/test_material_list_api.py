#!/usr/bin/env python3
"""
测试P37材料核对页材料清单接口
测试接口：GET /api/v1/material-checks/material-list
"""
import requests
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://120.26.201.61:8001/api/v1"

def test_material_list_api():
    """测试材料清单接口"""
    print("=" * 60)
    print("测试P37材料核对页材料清单接口")
    print("=" * 60)
    
    # 1. 先登录获取token
    print("\n1. 登录获取token...")
    login_url = f"{BASE_URL}/users/login"
    login_data = {"code": "dev_weapp_mock"}
    
    try:
        login_resp = requests.post(login_url, json=login_data, timeout=10)
        login_resp.raise_for_status()
        login_result = login_resp.json()
        
        # 兼容两种响应格式
        if login_result.get("code") == 0:
            data = login_result.get("data", {})
        else:
            data = login_result
        
        token = data.get("access_token")
        user_id = data.get("user_id")
        
        if not token:
            print("❌ 登录失败：未获取到token")
            print(f"响应: {json.dumps(login_result, indent=2, ensure_ascii=False)}")
            return False
        
        print(f"✅ 登录成功")
        print(f"   Token: {token[:20]}...")
        print(f"   User ID: {user_id}")
        
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return False
    
    # 2. 测试材料清单接口
    print("\n2. 测试材料清单接口...")
    material_list_url = f"{BASE_URL}/material-checks/material-list"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.get(material_list_url, headers=headers, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        
        print(f"✅ 请求成功 (状态码: {resp.status_code})")
        print(f"\n响应数据:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 验证响应格式
        if result.get("code") == 0:
            data = result.get("data", {})
            material_list = data.get("list", [])
            source = data.get("source", "unknown")
            source_id = data.get("source_id")
            total_count = data.get("total_count", 0)
            
            print(f"\n✅ 响应格式正确")
            print(f"   数据来源: {source}")
            print(f"   来源ID: {source_id}")
            print(f"   材料总数: {total_count}")
            print(f"   返回材料数: {len(material_list)}")
            
            if material_list:
                print(f"\n📋 材料清单预览（前5项）:")
                for i, mat in enumerate(material_list[:5], 1):
                    print(f"   {i}. {mat.get('material_name', 'N/A')}")
                    print(f"      规格/品牌: {mat.get('spec_brand', 'N/A')}")
                    print(f"      数量: {mat.get('quantity', 'N/A')}")
                    print(f"      类别: {mat.get('category', 'N/A')}")
                    print()
                
                # 验证排序：关键材料应该在前面
                key_materials = [m for m in material_list if "关键" in m.get("category", "")]
                auxiliary_materials = [m for m in material_list if "辅助" in m.get("category", "")]
                
                if key_materials and auxiliary_materials:
                    key_indices = [i for i, m in enumerate(material_list) if "关键" in m.get("category", "")]
                    aux_indices = [i for i, m in enumerate(material_list) if "辅助" in m.get("category", "")]
                    
                    if max(key_indices) < min(aux_indices):
                        print("✅ 排序正确：关键材料在辅助材料之前")
                    else:
                        print("⚠️  排序可能有问题：关键材料应该在辅助材料之前")
                
            else:
                print("⚠️  材料清单为空")
                hint = data.get("hint", "")
                if hint:
                    print(f"   提示: {hint}")
            
            return True
        else:
            print(f"❌ 响应格式错误: code={result.get('code')}, msg={result.get('msg')}")
            return False
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP错误: {e}")
        if e.response is not None:
            print(f"   状态码: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"   错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   响应内容: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_material_list_without_token():
    """测试未登录时的401错误"""
    print("\n" + "=" * 60)
    print("测试未登录时的401错误")
    print("=" * 60)
    
    material_list_url = f"{BASE_URL}/material-checks/material-list"
    
    try:
        resp = requests.get(material_list_url, timeout=10)
        if resp.status_code == 401:
            print("✅ 正确返回401未授权错误")
            return True
        else:
            print(f"❌ 期望401，实际返回: {resp.status_code}")
            print(f"   响应: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


if __name__ == "__main__":
    print("开始测试材料清单接口...\n")
    
    # 测试1: 正常流程
    success1 = test_material_list_api()
    
    # 测试2: 未登录401
    success2 = test_material_list_without_token()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"材料清单接口测试: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"401错误测试: {'✅ 通过' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查")
        sys.exit(1)

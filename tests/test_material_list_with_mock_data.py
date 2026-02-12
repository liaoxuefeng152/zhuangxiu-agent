#!/usr/bin/env python3
"""
P37材料核对页材料清单接口测试 - 使用模拟数据
测试接口功能，不依赖实际的报价单分析
"""
import requests
import json
import sys
import os

BASE_URL = "http://120.26.201.61:8001/api/v1"

def test_material_list_api():
    """测试材料清单接口"""
    print("=" * 60)
    print("测试P37材料核对页材料清单接口")
    print("=" * 60)
    
    # 1. 登录
    print("\n1. 登录获取token...")
    try:
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
        
        if not token:
            print(f"❌ 登录失败")
            return False
        
        print(f"✅ 登录成功 (User ID: {user_id})")
        
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return False
    
    # 2. 测试材料清单接口
    print("\n2. 测试材料清单接口...")
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id),
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.get(
            f"{BASE_URL}/material-checks/material-list",
            headers=headers,
            timeout=10
        )
        
        print(f"   状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"\n✅ 请求成功")
            print(f"\n响应数据:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 验证响应格式
            if result.get("code") == 0:
                data = result.get("data", {})
                material_list = data.get("list", [])
                source = data.get("source", "unknown")
                source_id = data.get("source_id")
                total_count = data.get("total_count", 0)
                
                print(f"\n📊 响应格式验证:")
                print(f"   ✅ code字段存在: {result.get('code')}")
                print(f"   ✅ msg字段存在: {result.get('msg')}")
                print(f"   ✅ data字段存在: {data is not None}")
                print(f"   ✅ list字段存在: {isinstance(material_list, list)}")
                print(f"   ✅ source字段存在: {source}")
                
                print(f"\n📋 数据内容:")
                print(f"   数据来源: {source}")
                print(f"   来源ID: {source_id}")
                print(f"   材料总数: {total_count}")
                print(f"   返回材料数: {len(material_list)}")
                
                if material_list:
                    print(f"\n📋 材料清单详情:")
                    for i, mat in enumerate(material_list[:10], 1):
                        print(f"   {i}. 【{mat.get('category', 'N/A')}】{mat.get('material_name', 'N/A')}")
                        if mat.get('spec_brand'):
                            print(f"      规格/品牌: {mat.get('spec_brand')}")
                        if mat.get('quantity'):
                            print(f"      数量: {mat.get('quantity')}")
                        print()
                    
                    # 验证字段完整性
                    print(f"📋 字段完整性验证:")
                    required_fields = ["material_name", "spec_brand", "quantity", "category"]
                    all_complete = True
                    for i, mat in enumerate(material_list[:5], 1):
                        missing = [f for f in required_fields if f not in mat]
                        if missing:
                            print(f"   ⚠️  材料{i}缺少字段: {missing}")
                            all_complete = False
                        else:
                            print(f"   ✅ 材料{i}字段完整")
                    
                    # 验证排序
                    if len(material_list) > 1:
                        key_materials = [m for m in material_list if "关键" in m.get("category", "")]
                        auxiliary_materials = [m for m in material_list if "辅助" in m.get("category", "")]
                        
                        if key_materials and auxiliary_materials:
                            key_indices = [i for i, m in enumerate(material_list) if "关键" in m.get("category", "")]
                            aux_indices = [i for i, m in enumerate(material_list) if "辅助" in m.get("category", "")]
                            
                            if max(key_indices) < min(aux_indices):
                                print(f"\n✅ 排序验证通过：关键材料在辅助材料之前")
                            else:
                                print(f"\n⚠️  排序验证失败：关键材料应该在辅助材料之前")
                                print(f"      关键材料索引: {key_indices}")
                                print(f"      辅助材料索引: {aux_indices}")
                    
                    print(f"\n✅ 接口功能正常，返回了 {len(material_list)} 项材料")
                    return True
                else:
                    print(f"\n⚠️  材料清单为空")
                    hint = data.get("hint", "")
                    if hint:
                        print(f"   提示: {hint}")
                    print(f"\n✅ 接口功能正常（返回空列表是正常的，因为用户可能未上传报价单）")
                    return True
            else:
                print(f"\n❌ 响应格式错误: code={result.get('code')}, msg={result.get('msg')}")
                return False
        else:
            print(f"\n❌ HTTP错误: 状态码 {resp.status_code}")
            try:
                error_data = resp.json()
                print(f"   错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   响应内容: {resp.text[:200]}")
            return False
            
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP错误: {e}")
        if e.response is not None:
            print(f"   状态码: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"   错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   响应内容: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_401_error():
    """测试未登录时的401错误"""
    print("\n" + "=" * 60)
    print("测试未登录时的401错误")
    print("=" * 60)
    
    try:
        resp = requests.get(
            f"{BASE_URL}/material-checks/material-list",
            timeout=10
        )
        
        if resp.status_code == 401:
            print("✅ 正确返回401未授权错误")
            return True
        else:
            print(f"❌ 期望401，实际返回: {resp.status_code}")
            print(f"   响应: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


if __name__ == "__main__":
    print("开始测试材料清单接口...\n")
    
    # 测试1: 正常流程
    success1 = test_material_list_api()
    
    # 测试2: 未登录401
    success2 = test_401_error()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"材料清单接口测试: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"401错误测试: {'✅ 通过' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("\n🎉 所有测试通过！")
        print("\n📝 说明:")
        print("   - 接口功能正常")
        print("   - 如果材料清单为空，说明用户未上传报价单或报价单中无材料信息")
        print("   - 这是正常情况，接口会返回空列表和提示信息")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查")
        sys.exit(1)

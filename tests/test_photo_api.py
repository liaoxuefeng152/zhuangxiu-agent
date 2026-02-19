#!/usr/bin/env python3
"""
测试施工照片API是否返回签名URL
"""
import requests
import json
import sys

# 阿里云服务器地址
BASE_URL = "http://120.26.201.61:8001/api/v1"

def test_construction_photos_api():
    """测试施工照片API"""
    print("测试施工照片API是否返回签名URL...")
    
    # 注意：实际测试需要有效的token和user_id
    # 这里只是展示测试方法
    headers = {
        "Authorization": "Bearer <需要有效的token>",
        "X-User-Id": "<需要有效的user_id>"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/construction-photos",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"API响应状态: {response.status_code}")
            print(f"API响应消息: {data.get('msg')}")
            
            # 检查返回的数据结构
            if data.get('code') == 0:
                photos_data = data.get('data', {})
                photos_by_stage = photos_data.get('photos', {})
                photo_list = photos_data.get('list', [])
                
                print(f"找到 {len(photo_list)} 张照片")
                
                # 检查是否有照片
                if photo_list:
                    first_photo = photo_list[0]
                    file_url = first_photo.get('file_url', '')
                    object_key = first_photo.get('object_key', '')
                    
                    print(f"\n第一张照片信息:")
                    print(f"  ID: {first_photo.get('id')}")
                    print(f"  阶段: {first_photo.get('stage')}")
                    print(f"  文件名: {first_photo.get('file_name')}")
                    print(f"  object_key: {object_key}")
                    print(f"  file_url: {file_url}")
                    
                    # 检查file_url是否是签名URL
                    if file_url and file_url.startswith('http'):
                        if 'Signature=' in file_url or 'Expires=' in file_url or 'OSSAccessKeyId=' in file_url:
                            print("✅ file_url 是签名URL（包含签名参数）")
                        elif 'aliyuncs.com' in file_url:
                            print("✅ file_url 是OSS URL（可能是签名URL）")
                        else:
                            print("⚠️  file_url 是HTTP URL，但不是明显的签名URL")
                    elif file_url and not file_url.startswith('http'):
                        print("❌ file_url 不是HTTP URL，可能是object_key")
                    else:
                        print("❌ file_url 为空")
                        
                    # 检查是否有object_key字段
                    if object_key:
                        print(f"✅ 保留了object_key字段: {object_key[:50]}...")
                    else:
                        print("⚠️  缺少object_key字段")
                else:
                    print("没有找到照片数据")
            else:
                print(f"API返回错误: {data}")
                
        elif response.status_code == 401:
            print("❌ 认证失败：需要有效的token")
        elif response.status_code == 403:
            print("❌ 权限不足")
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        print(f"响应内容: {response.text}")

def check_api_documentation():
    """检查API文档"""
    print("\nAPI文档检查:")
    print(f"施工照片API端点: {BASE_URL}/construction-photos")
    print("修改内容: 返回签名URL而不是object_key")
    print("修改文件: backend/app/api/v1/construction_photos.py")
    print("修改方法: list_photos() 函数")

if __name__ == "__main__":
    print("=" * 60)
    print("施工照片API测试脚本")
    print("=" * 60)
    
    check_api_documentation()
    print("\n" + "-" * 60)
    
    # 由于需要认证，这里只展示测试方法
    # 实际测试需要有效的token
    test_construction_photos_api()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n说明:")
    print("1. 这是一个测试脚本，实际测试需要有效的认证token")
    print("2. 修改后的API应该返回签名URL（以http/https开头）")
    print("3. 签名URL应该包含OSS签名参数或指向aliyuncs.com域名")
    print("4. 同时保留了object_key字段供其他用途")

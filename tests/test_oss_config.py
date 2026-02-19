#!/usr/bin/env python3
"""
测试OSS配置和签名URL生成
"""
import os
import sys
import dotenv

# 加载环境变量
dotenv.load_dotenv('/Users/mac/zhuangxiu-agent-backup-dev/.env')

# 直接读取环境变量
ALIYUN_ACCESS_KEY_ID = os.getenv('ALIYUN_ACCESS_KEY_ID')
ALIYUN_ACCESS_KEY_SECRET = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
ALIYUN_OSS_BUCKET1 = os.getenv('ALIYUN_OSS_BUCKET1')
ALIYUN_OSS_ENDPOINT = os.getenv('ALIYUN_OSS_ENDPOINT')

import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_oss_config():
    """测试OSS配置"""
    print("=" * 60)
    print("测试OSS配置和签名URL生成")
    print("=" * 60)
    
    print("\n1. 检查环境变量配置:")
    print(f"   ALIYUN_ACCESS_KEY_ID: {'已设置' if ALIYUN_ACCESS_KEY_ID else '未设置'}")
    print(f"   ALIYUN_ACCESS_KEY_SECRET: {'已设置' if ALIYUN_ACCESS_KEY_SECRET else '未设置'}")
    print(f"   ALIYUN_OSS_BUCKET1 (照片bucket): {ALIYUN_OSS_BUCKET1}")
    print(f"   ALIYUN_OSS_ENDPOINT: {ALIYUN_OSS_ENDPOINT}")
    
    print("\n2. 初始化OSS服务:")
    try:
        oss_service = OSSService()
        
        if oss_service.auth is None:
            print("   ❌ OSS认证未初始化（可能配置缺失）")
            print("   可能的原因:")
            print("   - ALIYUN_ACCESS_KEY_ID 或 ALIYUN_ACCESS_KEY_SECRET 未设置")
            print("   - 环境变量配置错误")
            return False
        else:
            print("   ✅ OSS认证初始化成功")
            
        if oss_service.photo_bucket is None:
            print("   ❌ 照片bucket未初始化")
            print(f"   检查 ALIYUN_OSS_BUCKET1: {settings.ALIYUN_OSS_BUCKET1}")
            return False
        else:
            print(f"   ✅ 照片bucket初始化成功: {oss_service.photo_bucket.bucket_name}")
            
    except Exception as e:
        print(f"   ❌ OSS服务初始化失败: {e}")
        return False
    
    print("\n3. 测试签名URL生成:")
    try:
        # 测试一个示例object_key
        test_object_key = "construction/1/test_photo.jpg"
        signed_url = oss_service.sign_url_for_key(test_object_key, expires=60)
        
        print(f"   测试object_key: {test_object_key}")
        print(f"   生成的签名URL: {signed_url[:100]}...")
        
        if signed_url.startswith("https://"):
            print("   ✅ 签名URL生成成功（HTTPS格式）")
            
            # 检查是否包含签名参数
            if 'Signature=' in signed_url or 'OSSAccessKeyId=' in signed_url:
                print("   ✅ 签名URL包含签名参数")
            else:
                print("   ⚠️  签名URL可能不包含签名参数（可能是公共读URL）")
                
        elif signed_url.startswith("http://"):
            print("   ⚠️  签名URL是HTTP格式（可能被强制转换为HTTPS）")
        else:
            print(f"   ❌ 签名URL格式异常: {signed_url}")
            return False
            
    except Exception as e:
        print(f"   ❌ 签名URL生成失败: {e}")
        return False
    
    print("\n4. 检查数据库中的施工照片:")
    try:
        import asyncpg
        import asyncio
        
        async def check_photos():
            conn = await asyncpg.connect(
                host='localhost',
                port=5432,
                user='decoration',
                password='decoration123',
                database='zhuangxiu_dev'
            )
            
            count = await conn.fetchval('SELECT COUNT(*) FROM construction_photos')
            print(f"   数据库中的施工照片数量: {count}")
            
            if count > 0:
                photos = await conn.fetch('SELECT id, file_url FROM construction_photos LIMIT 3')
                print(f"   前{len(photos)}张照片:")
                for photo in photos:
                    print(f"     ID: {photo['id']}, file_url: {photo['file_url'][:50]}...")
                    
                    # 测试为实际照片生成签名URL
                    if photo['file_url'] and not photo['file_url'].startswith('http'):
                        try:
                            signed = oss_service.sign_url_for_key(photo['file_url'], expires=60)
                            print(f"       签名URL: {signed[:80]}...")
                        except Exception as e:
                            print(f"       生成签名URL失败: {e}")
            else:
                print("   ⚠️  数据库中没有施工照片记录")
                print("   可能的原因:")
                print("   - 用户还没有上传施工照片")
                print("   - 照片上传功能有问题")
                
            await conn.close()
            
        asyncio.run(check_photos())
        
    except Exception as e:
        print(f"   ❌ 检查数据库失败: {e}")
        print("   可能的原因:")
        print("   - 数据库未运行")
        print("   - 数据库连接配置错误")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    print("\n建议:")
    print("1. 如果OSS配置有问题，请检查.env文件中的阿里云配置")
    print("2. 如果数据库中没有照片，请先上传一张施工照片测试")
    print("3. 如果签名URL生成失败，考虑将OSS bucket设置为公共读")
    print("4. 公共读设置方法: 阿里云OSS控制台 → 选择bucket → 权限管理 → 公共读")
    
    return True

if __name__ == "__main__":
    test_oss_config()

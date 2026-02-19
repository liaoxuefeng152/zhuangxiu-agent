#!/usr/bin/env python3
"""
简单检查OSS配置
"""
import os
import sys
import dotenv

# 加载环境变量
env_path = '/Users/mac/zhuangxiu-agent-backup-dev/.env'
if os.path.exists(env_path):
    dotenv.load_dotenv(env_path)
    print(f"✅ 已加载环境变量文件: {env_path}")
else:
    print(f"❌ 环境变量文件不存在: {env_path}")
    sys.exit(1)

# 直接读取环境变量
ALIYUN_ACCESS_KEY_ID = os.getenv('ALIYUN_ACCESS_KEY_ID')
ALIYUN_ACCESS_KEY_SECRET = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
ALIYUN_OSS_BUCKET1 = os.getenv('ALIYUN_OSS_BUCKET1')
ALIYUN_OSS_ENDPOINT = os.getenv('ALIYUN_OSS_ENDPOINT')

print("=" * 60)
print("OSS配置检查")
print("=" * 60)

print("\n1. 环境变量配置:")
print(f"   ALIYUN_ACCESS_KEY_ID: {'已设置' if ALIYUN_ACCESS_KEY_ID else '❌ 未设置'}")
if ALIYUN_ACCESS_KEY_ID:
    print(f"     值: {ALIYUN_ACCESS_KEY_ID[:10]}...{ALIYUN_ACCESS_KEY_ID[-4:] if len(ALIYUN_ACCESS_KEY_ID) > 14 else ''}")

print(f"   ALIYUN_ACCESS_KEY_SECRET: {'已设置' if ALIYUN_ACCESS_KEY_SECRET else '❌ 未设置'}")
if ALIYUN_ACCESS_KEY_SECRET:
    print(f"     值: {ALIYUN_ACCESS_KEY_SECRET[:10]}...{ALIYUN_ACCESS_KEY_SECRET[-4:] if len(ALIYUN_ACCESS_KEY_SECRET) > 14 else ''}")

print(f"   ALIYUN_OSS_BUCKET1: {ALIYUN_OSS_BUCKET1 or '❌ 未设置'}")
print(f"   ALIYUN_OSS_ENDPOINT: {ALIYUN_OSS_ENDPOINT or '❌ 未设置'}")

# 检查配置是否完整
config_ok = all([ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET, ALIYUN_OSS_BUCKET1, ALIYUN_OSS_ENDPOINT])

if not config_ok:
    print("\n❌ OSS配置不完整，无法初始化OSS服务")
    print("\n建议:")
    print("1. 检查.env文件中的阿里云配置")
    print("2. 确保以下变量已设置:")
    print("   - ALIYUN_ACCESS_KEY_ID")
    print("   - ALIYUN_ACCESS_KEY_SECRET")
    print("   - ALIYUN_OSS_BUCKET1")
    print("   - ALIYUN_OSS_ENDPOINT")
    sys.exit(1)

print("\n✅ OSS配置完整")

# 尝试导入OSS服务
print("\n2. 尝试导入OSS服务...")
try:
    sys.path.append('/Users/mac/zhuangxiu-agent-backup-dev/backend')
    from app.services.oss_service import OSSService
    
    print("✅ 成功导入OSSService")
    
    # 初始化OSS服务
    print("\n3. 初始化OSS服务...")
    oss_service = OSSService()
    
    if oss_service.auth is None:
        print("❌ OSS认证未初始化")
        print("可能的原因:")
        print("- AccessKey无效或过期")
        print("- 网络问题")
    else:
        print("✅ OSS认证初始化成功")
        
    if oss_service.photo_bucket is None:
        print("❌ 照片bucket未初始化")
        print(f"检查 bucket 名称: {ALIYUN_OSS_BUCKET1}")
    else:
        print(f"✅ 照片bucket初始化成功: {oss_service.photo_bucket.bucket_name}")
        
        # 测试签名URL生成
        print("\n4. 测试签名URL生成...")
        try:
            test_object_key = "construction/1/test_photo.jpg"
            signed_url = oss_service.sign_url_for_key(test_object_key, expires=60)
            
            print(f"   测试 object_key: {test_object_key}")
            print(f"   生成的签名URL: {signed_url[:100]}...")
            
            if signed_url.startswith("https://"):
                print("   ✅ 签名URL生成成功（HTTPS格式）")
                
                # 检查是否包含签名参数
                if 'Signature=' in signed_url or 'OSSAccessKeyId=' in signed_url:
                    print("   ✅ 签名URL包含签名参数（私有bucket）")
                else:
                    print("   ⚠️  签名URL不包含签名参数（可能是公共读bucket）")
                    
            elif signed_url.startswith("http://"):
                print("   ⚠️  签名URL是HTTP格式")
            else:
                print(f"   ❌ 签名URL格式异常: {signed_url}")
                
        except Exception as e:
            print(f"   ❌ 签名URL生成失败: {e}")
            print("   可能的原因:")
            print("   - AccessKey权限不足")
            print("   - bucket不存在")
            print("   - 网络问题")
            
except ImportError as e:
    print(f"❌ 导入OSS服务失败: {e}")
    print("可能的原因:")
    print("- 后端代码路径不正确")
    print("- 缺少依赖包")
except Exception as e:
    print(f"❌ OSS服务初始化失败: {e}")

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)

print("\n下一步建议:")
print("1. 如果OSS配置正确但签名URL生成失败，考虑将bucket设置为公共读")
print("2. 公共读设置方法:")
print("   阿里云OSS控制台 → 选择bucket → 权限管理 → 公共读")
print("3. 设置公共读后，照片URL可以直接访问，无需签名")

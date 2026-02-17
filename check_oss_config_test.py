#!/usr/bin/env python3
"""
测试OSS配置是否正确
"""
import oss2
from app.core.config import settings

def test_oss_config():
    print("=== 测试OSS配置 ===")
    
    # 检查配置是否存在
    print("1. 检查OSS配置...")
    print(f"ALIYUN_ACCESS_KEY_ID: {'已设置' if settings.ALIYUN_ACCESS_KEY_ID else '未设置'}")
    print(f"ALIYUN_ACCESS_KEY_SECRET: {'已设置' if settings.ALIYUN_ACCESS_KEY_SECRET else '未设置'}")
    print(f"ALIYUN_OSS_BUCKET: {settings.ALIYUN_OSS_BUCKET}")
    print(f"ALIYUN_OSS_BUCKET1: {settings.ALIYUN_OSS_BUCKET1}")
    print(f"ALIYUN_OSS_ENDPOINT: {settings.ALIYUN_OSS_ENDPOINT}")
    
    # 尝试初始化OSS客户端
    print("\n2. 尝试初始化OSS客户端...")
    try:
        auth = oss2.Auth(
            settings.ALIYUN_ACCESS_KEY_ID,
            settings.ALIYUN_ACCESS_KEY_SECRET
        )
        print("✅ OSS认证初始化成功")
        
        # 尝试连接bucket1（照片bucket）
        if settings.ALIYUN_OSS_BUCKET1:
            bucket1 = oss2.Bucket(
                auth,
                settings.ALIYUN_OSS_ENDPOINT,
                settings.ALIYUN_OSS_BUCKET1
            )
            print(f"✅ 照片Bucket连接成功: {settings.ALIYUN_OSS_BUCKET1}")
            
            # 尝试列出一些文件（限制为5个）
            try:
                print("\n3. 尝试列出Bucket中的文件（前5个）...")
                result = bucket1.list_objects(max_keys=5)
                file_count = 0
                for obj in result.object_list:
                    print(f"   - {obj.key} ({obj.size} bytes)")
                    file_count += 1
                print(f"✅ 成功列出 {file_count} 个文件")
            except Exception as e:
                print(f"⚠️  列出文件失败: {e}")
                print("   可能原因：权限不足或Bucket为空")
        
        # 尝试连接默认bucket
        if settings.ALIYUN_OSS_BUCKET:
            bucket = oss2.Bucket(
                auth,
                settings.ALIYUN_OSS_ENDPOINT,
                settings.ALIYUN_OSS_BUCKET
            )
            print(f"✅ 默认Bucket连接成功: {settings.ALIYUN_OSS_BUCKET}")
            
    except Exception as e:
        print(f"❌ OSS初始化失败: {e}")
        return False
    
    return True

if __name__ == '__main__':
    # 需要设置环境变量
    import os
    import sys
    
    # 添加backend目录到Python路径
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    sys.path.insert(0, backend_dir)
    
    # 设置环境变量
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"已加载环境变量文件: {env_path}")
    else:
        print(f"⚠️  环境变量文件不存在: {env_path}")
    
    try:
        success = test_oss_config()
        if success:
            print("\n✅ OSS配置测试通过")
            sys.exit(0)
        else:
            print("\n❌ OSS配置测试失败")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

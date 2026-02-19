#!/usr/bin/env python3
"""
检查OSS bucket是否为公共读
"""
import oss2
import os
from dotenv import load_dotenv

load_dotenv()

def check_bucket_permission():
    """检查bucket权限"""
    print("检查OSS bucket权限状态...")
    
    # 获取配置
    access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
    access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
    endpoint = os.getenv('ALIYUN_OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com')
    bucket_name = os.getenv('ALIYUN_OSS_BUCKET1', 'zhuangxiu-images-dev-photo')
    
    if not access_key_id or not access_key_secret:
        print("✗ OSS配置不完整，无法检查")
        return
    
    print(f"Bucket: {bucket_name}")
    print(f"Endpoint: {endpoint}")
    
    try:
        # 创建认证对象
        auth = oss2.Auth(access_key_id, access_key_secret)
        
        # 创建bucket对象
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        
        # 获取bucket ACL（访问控制列表）
        acl = bucket.get_bucket_acl()
        print(f"Bucket ACL: {acl.acl}")
        
        if acl.acl == oss2.BUCKET_ACL_PUBLIC_READ:
            print("✓ Bucket已经是公共读权限")
            return True
        elif acl.acl == oss2.BUCKET_ACL_PRIVATE:
            print("✗ Bucket是私有权限（需要签名URL）")
            print("  这是导致AI设计师无法访问图片的原因")
            return False
        elif acl.acl == oss2.BUCKET_ACL_PUBLIC_READ_WRITE:
            print("⚠ Bucket是公共读写权限（不安全）")
            return True
        else:
            print(f"⚠ 未知权限: {acl.acl}")
            return False
            
    except Exception as e:
        print(f"✗ 检查bucket权限失败: {e}")
        return False

def test_public_url():
    """测试公共URL访问"""
    print("\n测试公共URL访问...")
    
    # 从日志中获取一个实际的图片路径
    test_object_key = "designer/1/1771495823_1545.png"
    bucket_name = os.getenv('ALIYUN_OSS_BUCKET1', 'zhuangxiu-images-dev-photo')
    endpoint = os.getenv('ALIYUN_OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com')
    
    # 构造公共URL
    public_url = f"https://{bucket_name}.{endpoint}/{test_object_key}"
    print(f"测试URL: {public_url}")
    
    import requests
    try:
        response = requests.get(public_url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ 公共URL可访问")
            return True
        elif response.status_code == 403:
            print("✗ 公共URL返回403 Forbidden")
            print("  说明bucket不是公共读，或者文件是私有的")
            return False
        elif response.status_code == 404:
            print("✗ 公共URL返回404 Not Found")
            print("  文件不存在或路径错误")
            return False
        else:
            print(f"⚠ 返回异常状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 访问URL失败: {e}")
        return False

def main():
    print("=" * 70)
    print("OSS Bucket权限检查")
    print("=" * 70)
    
    # 检查bucket权限
    is_public = check_bucket_permission()
    
    # 测试公共URL访问
    if is_public:
        test_public_url()
    else:
        print("\n由于bucket是私有权限，无法测试公共URL访问")
    
    print("\n" + "=" * 70)
    print("问题分析:")
    print("=" * 70)
    
    if not is_public:
        print("1. 当前OSS bucket是私有权限")
        print("2. AI设计师智能体（扣子站点）无法访问私有URL")
        print("3. 即使生成了签名URL，外部服务也可能无法访问")
        print("\n解决方案:")
        print("1. 将OSS bucket设置为公共读（推荐）")
        print("2. 或者修改AI设计师智能体配置，使其能处理签名URL")
        print("\n操作步骤:")
        print("1. 登录阿里云OSS控制台")
        print("2. 找到bucket: zhuangxiu-images-dev-photo")
        print("3. 设置权限为'公共读'")
        print("4. 重启后端服务")
        
        print("\n这是一个**后台问题**，需要修改OSS配置。")
    else:
        print("✓ OSS bucket已经是公共读权限")
        print("✓ AI设计师应该能访问图片URL")
        print("\n如果仍有问题，可能是:")
        print("1. AI设计师智能体配置问题")
        print("2. 图片URL格式问题")
        print("3. 网络访问限制")
    
    print("\n" + "=" * 70)
    print("检查完成")
    print("=" * 70)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
测试AI设计师接收到的URL格式
"""
import os
import sys
sys.path.append('backend')

from dotenv import load_dotenv
load_dotenv()

def test_oss_url_generation():
    """测试OSS URL生成格式"""
    print("测试OSS URL生成格式...")
    
    try:
        from app.services.oss_service import oss_service
        
        # 测试一个object_key
        test_object_key = "designer/1/1771495823_1545.png"
        
        print(f"测试object_key: {test_object_key}")
        print(f"OSS Service配置: auth={oss_service.auth is not None}")
        print(f"Photo bucket: {oss_service.photo_bucket.bucket_name if oss_service.photo_bucket else 'None'}")
        
        # 生成签名URL（24小时）
        signed_url = oss_service.sign_url_for_key(test_object_key, expires=24*3600)
        print(f"\n生成的签名URL: {signed_url}")
        
        # 分析URL格式
        if signed_url.startswith("https://"):
            print("✓ URL以https://开头")
            
            # 检查是否是签名URL（包含?Expires=等参数）
            if "?" in signed_url:
                print("⚠ 这是签名URL（包含查询参数）")
                print("  签名URL格式: 包含Expires、OSSAccessKeyId、Signature等参数")
                
                # 提取基础URL（去掉签名参数）
                base_url = signed_url.split("?")[0]
                print(f"  基础URL: {base_url}")
                
                # 检查是否是公共URL格式
                bucket_name = os.getenv('ALIYUN_OSS_BUCKET1', 'zhuangxiu-images-dev-photo')
                endpoint = os.getenv('ALIYUN_OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com')
                expected_public_url = f"https://{bucket_name}.{endpoint}/{test_object_key}"
                
                if base_url == expected_public_url:
                    print(f"  ✓ 基础URL匹配公共URL格式")
                else:
                    print(f"  ✗ 基础URL不匹配公共URL格式")
                    print(f"     期望: {expected_public_url}")
                    print(f"     实际: {base_url}")
            else:
                print("✓ 这是公共URL（无查询参数）")
                
        else:
            print("✗ URL不以https://开头")
            
        # 测试公共URL访问
        print("\n测试公共URL访问...")
        bucket_name = os.getenv('ALIYUN_OSS_BUCKET1', 'zhuangxiu-images-dev-photo')
        endpoint = os.getenv('ALIYUN_OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com')
        public_url = f"https://{bucket_name}.{endpoint}/{test_object_key}"
        
        import requests
        try:
            response = requests.get(public_url, timeout=10)
            print(f"公共URL状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ 公共URL可访问")
                
                # 测试签名URL访问
                print("\n测试签名URL访问...")
                try:
                    response2 = requests.get(signed_url, timeout=10)
                    print(f"签名URL状态码: {response2.status_code}")
                    
                    if response2.status_code == 200:
                        print("✓ 签名URL也可访问")
                    else:
                        print(f"✗ 签名URL返回 {response2.status_code}")
                        
                except Exception as e:
                    print(f"✗ 签名URL访问失败: {e}")
                    
            else:
                print(f"✗ 公共URL返回 {response.status_code}")
                
        except Exception as e:
            print(f"✗ 公共URL访问失败: {e}")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def check_designer_api_response():
    """检查designer API返回的URL格式"""
    print("\n" + "="*70)
    print("分析问题:")
    print("="*70)
    
    print("1. 从日志看，图片上传成功:")
    print("   'AI设计师图片上传成功: user_id=1, object_key=designer/1/1771495823_1545.png'")
    print("   '生成签名 URL 成功: designer/1/1771495823_1545.png, 过期: 86400秒'")
    
    print("\n2. 问题分析:")
    print("   - OSS bucket是公共读，图片可以直接访问")
    print("   - 但AI设计师智能体可能接收的是签名URL")
    print("   - 签名URL可能包含特殊字符或格式，导致AI无法访问")
    
    print("\n3. 可能的解决方案:")
    print("   a) 修改designer.py，返回公共URL而不是签名URL")
    print("   b) 修改AI设计师智能体配置，使其能处理签名URL")
    print("   c) 检查签名URL格式，确保AI能正确解析")
    
    print("\n4. 建议修复:")
    print("   在backend/app/api/v1/designer.py的upload_designer_image函数中:")
    print("   - 生成公共URL而不是签名URL")
    print("   - 或者同时返回两种URL格式")
    
    print("\n这是一个**后台问题**，需要修改designer.py中的URL生成逻辑。")

def main():
    print("=" * 70)
    print("AI设计师URL格式分析")
    print("=" * 70)
    
    test_oss_url_generation()
    check_designer_api_response()
    
    print("\n" + "=" * 70)
    print("修复建议:")
    print("=" * 70)
    print("修改backend/app/api/v1/designer.py中的upload_designer_image函数:")
    print("将签名URL改为公共URL，因为OSS bucket已经是公共读。")
    
    print("\n具体修改:")
    print("1. 在upload_designer_image函数中，生成公共URL:")
    print("   bucket_name = settings.ALIYUN_OSS_BUCKET1")
    print("   endpoint = settings.ALIYUN_OSS_ENDPOINT")
    print("   public_url = f'https://{bucket_name}.{endpoint}/{object_key}'")
    print("2. 返回public_url而不是签名URL")
    
    print("\n" + "=" * 70)
    print("分析完成")
    print("=" * 70)

if __name__ == "__main__":
    main()

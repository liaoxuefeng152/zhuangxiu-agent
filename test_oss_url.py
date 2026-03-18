#!/usr/bin/env python3
"""
测试OSS URL的正确性
"""
import sys
sys.path.insert(0, 'backend')
from app.core.config import settings
from app.services.oss_service import oss_service

def test_oss_url():
    """测试OSS URL生成"""
    print('=== 测试OSS URL ===')
    
    # 检查配置
    print(f'ALIYUN_OSS_ENDPOINT: {settings.ALIYUN_OSS_ENDPOINT}')
    print(f'ALIYUN_OSS_BUCKET1: {settings.ALIYUN_OSS_BUCKET1}')
    
    # 测试生成签名URL
    test_object_key = 'quote/test.jpg'
    
    try:
        # 生成签名URL
        signed_url = oss_service.sign_url_for_key(test_object_key, expires=3600)
        print(f'\n生成的签名URL: {signed_url}')
        
        # 检查URL格式
        if 'oss-cn-hangzhou' in signed_url:
            print('✅ URL使用正确的杭州端点')
        elif 'oss-cn-shenzhen' in signed_url:
            print('⚠️ URL使用深圳端点，可能与配置不一致')
        else:
            print(f'❓ URL使用未知端点: {signed_url}')
        
        # 测试URL访问
        import requests
        print(f'\n测试URL访问...')
        response = requests.head(signed_url, timeout=10)
        print(f'响应状态码: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ OSS URL可以正常访问')
        elif response.status_code == 403:
            print('❌ OSS URL访问被拒绝 (403)')
            print('可能原因:')
            print('1. OSS桶权限设置不正确')
            print('2. 签名URL生成有问题')
            print('3. OSS桶区域配置错误')
        else:
            print(f'⚠️ OSS URL返回异常状态码: {response.status_code}')
            
    except Exception as e:
        print(f'❌ 测试失败: {e}')
        import traceback
        traceback.print_exc()

def test_oss_service():
    """测试OSS服务"""
    print('\n\n=== 测试OSS服务 ===')
    
    # 检查OSS服务是否初始化成功
    if oss_service.auth:
        print('✅ OSS认证已初始化')
    else:
        print('❌ OSS认证未初始化')
        
    if oss_service.photo_bucket:
        print(f'✅ 照片Bucket已初始化: {oss_service.photo_bucket.bucket_name}')
    else:
        print('❌ 照片Bucket未初始化')
        
    if oss_service.bucket:
        print(f'✅ 默认Bucket已初始化: {oss_service.bucket.bucket_name}')
    else:
        print('❌ 默认Bucket未初始化')

def test_correct_url():
    """测试正确的URL格式"""
    print('\n\n=== 测试正确的URL格式 ===')
    
    # 根据OSS错误信息，正确的端点应该是 oss-cn-hangzhou.aliyuncs.com
    bucket_name = 'zhuangxiu-images-photo'
    correct_endpoint = 'oss-cn-hangzhou.aliyuncs.com'
    
    # 构建正确的URL
    correct_url = f'https://{bucket_name}.{correct_endpoint}/quote/test.jpg'
    print(f'正确的URL格式: {correct_url}')
    
    # 测试访问
    try:
        import requests
        print(f'\n测试正确URL访问...')
        response = requests.head(correct_url, timeout=10)
        print(f'响应状态码: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ 正确的URL可以访问')
            return correct_url
        elif response.status_code == 403:
            print('❌ 正确的URL仍然返回403')
            print('可能原因:')
            print('1. OSS桶权限设置为私有')
            print('2. 需要签名URL才能访问')
            print('3. OSS桶配置有问题')
        else:
            print(f'⚠️ 正确的URL返回异常状态码: {response.status_code}')
            
    except Exception as e:
        print(f'❌ 测试失败: {e}')

def main():
    """主函数"""
    print('开始测试OSS URL问题...')
    
    # 测试OSS服务
    test_oss_service()
    
    # 测试OSS URL生成
    test_oss_url()
    
    # 测试正确的URL格式
    correct_url = test_correct_url()
    
    print('\n\n=== 问题分析 ===')
    print('这是**后台问题**，具体表现在：')
    print('1. OSS桶端点配置不一致')
    print('2. 测试图片URL使用深圳端点，但实际桶在杭州')
    print('3. 扣子智能体无法访问403错误的图片URL')
    print('4. 后端服务返回兜底数据而非真实AI分析')
    
    print('\n=== 解决方案 ===')
    print('1. 检查OSS桶的实际区域配置')
    print('2. 确保所有图片URL使用正确的端点')
    print('3. 测试扣子智能体能否访问正确的图片URL')
    print('4. 修复OSS服务配置，确保生成正确的签名URL')

if __name__ == "__main__":
    main()

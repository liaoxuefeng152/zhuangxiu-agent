#!/usr/bin/env python3
"""
测试OCR服务使用AccessKey认证
"""
import sys
import os
from dotenv import load_dotenv

# 加载.env.dev文件
env_file = os.path.join(os.path.dirname(__file__), '.env.dev')
if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"已加载环境变量文件: {env_file}")
else:
    print(f"警告: 环境变量文件不存在: {env_file}")

# 设置环境变量
os.environ['DEBUG'] = 'true'  # 设置为开发模式，避免生产环境验证
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://test:test@localhost:5432/test'  # 虚拟数据库URL

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ocr_service import OcrService

def test_ocr_initialization():
    """测试OCR服务初始化"""
    print("测试OCR服务使用AccessKey认证...")
    
    try:
        # 创建OCR服务实例
        ocr_service = OcrService()
        
        if ocr_service.client is None:
            print("❌ OCR客户端初始化失败")
            print("请检查以下配置：")
            print("1. ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET 是否已配置")
            print("2. 阿里云OCR服务是否已开通")
            return False
        
        print("✅ OCR客户端初始化成功")
        print(f"配置信息：")
        print(f"  - AccessKey ID: {ocr_service.config.access_key_id[:10]}...")
        print(f"  - 区域: {ocr_service.config.region_id}")
        print(f"  - 端点: {ocr_service.config.endpoint}")
        
        # 测试连接
        print("\n测试OCR连接...")
        try:
            ocr_service._test_connection()
            print("✅ OCR连接测试通过")
        except Exception as e:
            print(f"⚠️  OCR连接测试异常（可能权限或网络问题）: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR服务初始化异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ocr_initialization()
    sys.exit(0 if success else 1)

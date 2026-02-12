#!/usr/bin/env python3
"""
验证OCR配置是否正确
"""
import os
from dotenv import load_dotenv

load_dotenv()

access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID", "")
access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET", "")
endpoint = os.getenv("ALIYUN_OCR_ENDPOINT", "ocr-api.cn-hangzhou.aliyuncs.com")

print("=" * 60)
print("OCR配置验证")
print("=" * 60)
print(f"Access Key ID: {access_key_id[:10]}..." if access_key_id else "❌ 未配置")
print(f"Access Key Secret: {'已配置' if access_key_secret else '❌ 未配置'}")
print(f"Endpoint: {endpoint}")

if not access_key_id or not access_key_secret:
    print("\n⚠️  警告: OCR配置不完整，请检查.env文件")
else:
    print("\n✅ OCR配置已加载")
    
    # 尝试初始化OCR客户端
    try:
        from alibabacloud_ocr_api20210707.client import Client as OcrClient
        from alibabacloud_tea_openapi import models as open_api_models
        
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )
        config.endpoint = endpoint
        client = OcrClient(config)
        print("✅ OCR客户端初始化成功")
    except Exception as e:
        print(f"❌ OCR客户端初始化失败: {e}")

print("=" * 60)

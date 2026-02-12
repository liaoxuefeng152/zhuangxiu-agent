#!/usr/bin/env python3
"""
验证OCR配置和测试真实OCR识别
"""
import os
import sys
_d = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(_d) not in sys.path:
    sys.path.insert(0, os.path.dirname(_d))
import base64
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_ocr_config():
    """测试OCR配置"""
    print("=" * 70)
    print("OCR配置验证")
    print("=" * 70)
    
    access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID", "")
    access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET", "")
    endpoint = os.getenv("ALIYUN_OCR_ENDPOINT", "ocr-api.cn-hangzhou.aliyuncs.com")
    
    print(f"\n📋 配置信息:")
    print(f"   Access Key ID: {access_key_id[:10]}..." if access_key_id else "   ❌ 未配置")
    print(f"   Access Key Secret: {'已配置' if access_key_secret else '❌ 未配置'}")
    print(f"   Endpoint: {endpoint}")
    
    if not access_key_id or not access_key_secret:
        print("\n❌ OCR配置不完整")
        return False
    
    # 测试OCR API调用
    print(f"\n🔍 测试OCR API调用...")
    try:
        from alibabacloud_ocr_api20210707.client import Client as OcrClient
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_ocr_api20210707 import models as ocr_models
        
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )
        config.endpoint = endpoint
        client = OcrClient(config)
        
        # 读取测试图片
        from tests import fixture_path, QUOTE_PNG
        test_file = fixture_path(QUOTE_PNG)
        if not os.path.exists(test_file):
            print(f"   ⚠️  测试文件不存在: {test_file}")
            return False
        
        with open(test_file, "rb") as f:
            file_content = f.read()
        
        # 转换为Base64
        base64_str = base64.b64encode(file_content).decode("utf-8")
        print(f"   📄 测试文件大小: {len(file_content)} bytes")
        print(f"   📊 Base64长度: {len(base64_str)} 字符")
        
        # 调用OCR API
        request = ocr_models.RecognizeGeneralRequest()
        request.body = base64_str
        
        print(f"   📤 发送OCR请求...")
        response = client.recognize_general(request)
        
        if response and response.body and response.body.data:
            text = response.body.data.content
            print(f"\n   ✅ OCR识别成功！")
            print(f"   📝 识别文本长度: {len(text)} 字符")
            print(f"   📝 文本预览（前200字符）:")
            print(f"   {text[:200]}...")
            
            # 检查是否识别到了"总计"或"合计"等关键词
            if "总计" in text or "合计" in text or "80000" in text:
                print(f"\n   ✅ 识别到了价格信息，OCR工作正常！")
            else:
                print(f"\n   ⚠️  未识别到明显的价格信息")
            
            return True
        else:
            print(f"\n   ❌ OCR识别失败，响应为空")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"\n   ❌ OCR API调用失败")
        print(f"   错误: {error_msg}")
        
        if "InvalidAccessKeyId" in error_msg:
            print(f"\n   💡 问题诊断:")
            print(f"      AccessKey无效或不存在")
            print(f"      请检查:")
            print(f"      1. AccessKey ID是否正确")
            print(f"      2. AccessKey是否已启用")
            print(f"      3. AccessKey是否有OCR服务权限")
            print(f"      4. 后端服务是否已重启以加载新配置")
        elif "Forbidden" in error_msg or "403" in error_msg:
            print(f"\n   💡 问题诊断:")
            print(f"      AccessKey没有OCR服务权限")
            print(f"      请检查AccessKey的权限配置")
        
        return False


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("OCR配置和功能验证")
    print("=" * 70)
    
    result = test_ocr_config()
    
    print("\n" + "=" * 70)
    if result:
        print("✅ OCR配置有效，功能正常！")
        print("\n💡 提示:")
        print("   如果后端服务仍在使用模拟文本，请重启后端服务")
        print("   重启后，新的OCR配置将生效")
    else:
        print("❌ OCR配置无效或功能异常")
        print("\n💡 修复建议:")
        print("   1. 检查.env文件中的AccessKey配置")
        print("   2. 确认AccessKey有效且有OCR服务权限")
        print("   3. 重启后端服务以加载新配置")
    print("=" * 70)


if __name__ == "__main__":
    main()

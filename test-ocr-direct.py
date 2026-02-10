#!/usr/bin/env python3
"""
直接调用阿里云OCR API测试PNG图片识别
"""
import base64
import os
from alibabacloud_ocr_api20210707.client import Client as OcrClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_models
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_ocr():
    """测试OCR API"""
    access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
    access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
    endpoint = os.getenv("ALIYUN_OCR_ENDPOINT", "ocr-api.cn-hangzhou.aliyuncs.com")
    
    if not access_key_id or not access_key_secret:
        print("❌ OCR配置不存在")
        return
    
    print(f"✅ OCR配置已加载")
    print(f"   Access Key ID: {access_key_id[:10]}...")
    print(f"   Endpoint: {endpoint}")
    
    # 初始化OCR客户端
    try:
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )
        config.endpoint = endpoint
        client = OcrClient(config)
        print("✅ OCR客户端初始化成功")
    except Exception as e:
        print(f"❌ OCR客户端初始化失败: {e}")
        return
    
    # 测试报价单PNG
    quote_png_path = "2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png"
    if os.path.exists(quote_png_path):
        print(f"\n📄 测试文件: {quote_png_path}")
        with open(quote_png_path, "rb") as f:
            file_content = f.read()
        
        print(f"📊 文件大小: {len(file_content)} bytes ({len(file_content)/1024:.2f} KB)")
        
        # 转换为Base64
        base64_str = base64.b64encode(file_content).decode("utf-8")
        print(f"📊 Base64长度: {len(base64_str)} 字符")
        
        # 测试通用文本识别
        print("\n🔍 测试通用文本识别...")
        try:
            request = ocr_models.RecognizeGeneralRequest()
            request.body = base64_str
            
            print(f"📤 发送OCR请求...")
            response = client.recognize_general(request)
            
            if response and response.body and response.body.data:
                text = response.body.data.content
                print(f"✅ 识别成功！")
                print(f"📝 文本长度: {len(text)} 字符")
                print(f"📝 前200字符: {text[:200]}...")
            else:
                print("❌ 识别失败，响应为空")
        except Exception as e:
            print(f"❌ 识别异常: {e}")
            # 尝试获取详细错误信息
            if hasattr(e, 'response'):
                try:
                    if hasattr(e.response, 'body'):
                        print(f"   错误响应体: {e.response.body}")
                    else:
                        print(f"   错误响应: {e.response}")
                except:
                    pass
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_ocr()

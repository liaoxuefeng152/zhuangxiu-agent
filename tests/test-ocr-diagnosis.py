#!/usr/bin/env python3
"""
OCR诊断脚本
检查OCR配置、API调用和错误信息
"""
import os
import sys
import base64
from pathlib import Path

# 添加backend目录到路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def check_env_config():
    """检查环境变量配置"""
    print("=" * 60)
    print("1. 检查环境变量配置")
    print("=" * 60)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID", "")
    access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET", "")
    ocr_endpoint = os.getenv("ALIYUN_OCR_ENDPOINT", "")
    oss_bucket = os.getenv("ALIYUN_OSS_BUCKET", "")
    oss_endpoint = os.getenv("ALIYUN_OSS_ENDPOINT", "")
    
    print(f"ALIYUN_ACCESS_KEY_ID: {'已配置' if access_key_id else '未配置'} ({access_key_id[:10] if access_key_id else 'None'}...)")
    print(f"ALIYUN_ACCESS_KEY_SECRET: {'已配置' if access_key_secret else '未配置'} ({access_key_secret[:10] if access_key_secret else 'None'}...)")
    print(f"ALIYUN_OCR_ENDPOINT: {ocr_endpoint}")
    print(f"ALIYUN_OSS_BUCKET: {oss_bucket}")
    print(f"ALIYUN_OSS_ENDPOINT: {oss_endpoint}")
    
    return access_key_id and access_key_secret

def check_ocr_service_init():
    """检查OCR服务初始化"""
    print("\n" + "=" * 60)
    print("2. 检查OCR服务初始化")
    print("=" * 60)
    
    try:
        from app.services.ocr_service import ocr_service
        
        if ocr_service.client is None:
            print("❌ OCR客户端未初始化")
            print("   可能原因：")
            print("   1. ALIYUN_ACCESS_KEY_ID 或 ALIYUN_ACCESS_KEY_SECRET 未配置")
            print("   2. OCR客户端初始化失败")
            return False
        else:
            print("✅ OCR客户端已初始化")
            print(f"   Endpoint: {ocr_service.config.endpoint}")
            return True
    except Exception as e:
        print(f"❌ OCR服务初始化检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_pdf_file():
    """检查PDF文件"""
    print("\n" + "=" * 60)
    print("3. 检查PDF文件")
    print("=" * 60)
    
    pdf_files = [
        "2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.pdf",
        "深圳市住宅装饰装修工程施工合同（半包装修版）.pdf"
    ]
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            size = os.path.getsize(pdf_file)
            print(f"✅ {pdf_file}")
            print(f"   大小: {size} bytes ({size/1024:.2f} KB)")
            
            # 检查文件是否为有效的PDF
            with open(pdf_file, "rb") as f:
                header = f.read(4)
                if header == b"%PDF":
                    print(f"   ✅ 有效的PDF文件")
                else:
                    print(f"   ❌ 不是有效的PDF文件，文件头: {header}")
        else:
            print(f"❌ 文件不存在: {pdf_file}")

def test_base64_encoding():
    """测试Base64编码"""
    print("\n" + "=" * 60)
    print("4. 测试Base64编码")
    print("=" * 60)
    
    pdf_file = "2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.pdf"
    if not os.path.exists(pdf_file):
        print(f"❌ 文件不存在: {pdf_file}")
        return
    
    with open(pdf_file, "rb") as f:
        file_content = f.read()
    
    base64_str = base64.b64encode(file_content).decode("utf-8")
    base64_with_prefix = f"data:application/pdf;base64,{base64_str}"
    
    print(f"原始文件大小: {len(file_content)} bytes")
    print(f"Base64编码长度: {len(base64_str)} 字符")
    print(f"带前缀长度: {len(base64_with_prefix)} 字符")
    print(f"Base64编码是否为4的倍数: {len(base64_str) % 4 == 0}")
    print(f"Base64前缀: data:application/pdf;base64,")

def check_ocr_api_support():
    """检查OCR API支持情况"""
    print("\n" + "=" * 60)
    print("5. OCR API支持情况（根据文档）")
    print("=" * 60)
    
    print("根据阿里云OCR API文档：")
    print("❌ RecognizeGeneral API不支持PDF格式")
    print("   - 支持的格式：PNG、JPG、JPEG、BMP、GIF、TIFF、WebP")
    print("   - 不支持：PDF")
    print()
    print("❌ RecognizeGeneral API不支持Base64编码")
    print("   - 推荐使用：URL链接或二进制文件")
    print("   - Base64编码可能导致错误")
    print()
    print("✅ 解决方案：")
    print("   1. 将PDF文件上传到OSS")
    print("   2. 使用OSS URL调用OCR API")
    print("   3. 或者使用支持PDF的其他OCR接口")

def main():
    print("\n" + "=" * 60)
    print("OCR诊断报告")
    print("=" * 60)
    
    # 1. 检查环境变量
    env_ok = check_env_config()
    
    # 2. 检查OCR服务初始化
    if env_ok:
        ocr_init_ok = check_ocr_service_init()
    else:
        ocr_init_ok = False
    
    # 3. 检查PDF文件
    check_pdf_file()
    
    # 4. 测试Base64编码
    test_base64_encoding()
    
    # 5. OCR API支持情况
    check_ocr_api_support()
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)
    
    print("\n📋 总结：")
    if not env_ok:
        print("❌ 环境变量配置不完整")
    elif not ocr_init_ok:
        print("❌ OCR服务初始化失败")
    else:
        print("✅ OCR配置正常")
        print("⚠️  但RecognizeGeneral API不支持PDF格式和Base64编码")
        print("💡 建议：使用OSS URL方式调用OCR API")

if __name__ == "__main__":
    main()

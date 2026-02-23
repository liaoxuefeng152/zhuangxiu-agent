#!/usr/bin/env python3
"""
测试OCR优化功能
"""
import os
import sys
import base64
import asyncio
from pathlib import Path

# 设置环境变量
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/zhuangxiu_dev"
os.environ["ENVIRONMENT"] = "development"
os.environ["WECHAT_APP_ID"] = "test_app_id"
os.environ["WECHAT_APP_SECRET"] = "test_app_secret"
os.environ["ALIYUN_OCR_ENDPOINT"] = "ocr-api.cn-hangzhou.aliyuncs.com"

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ocr_service import OcrService

async def test_ocr_optimization():
    """测试OCR优化功能"""
    print("=" * 60)
    print("测试OCR优化功能")
    print("=" * 60)
    
    # 创建OCR服务实例
    ocr_service = OcrService()
    
    if ocr_service.client is None:
        print("❌ OCR客户端未初始化")
        return False
    
    print("✅ OCR客户端已初始化")
    
    # 读取测试文件
    fixture_path = Path("tests/fixtures/深圳市住宅装饰装修工程施工合同（半包装修版）.png")
    if not fixture_path.exists():
        print(f"❌ 测试文件不存在: {fixture_path}")
        # 尝试其他文件
        fixture_path = Path("tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png")
        if not fixture_path.exists():
            print(f"❌ 备用测试文件也不存在: {fixture_path}")
            return False
    
    print(f"📄 使用测试文件: {fixture_path}")
    file_size = os.path.getsize(fixture_path)
    print(f"📊 文件大小: {file_size} bytes")
    
    # 将文件转换为Base64
    with open(fixture_path, "rb") as f:
        file_data = f.read()
        base64_str = base64.b64encode(file_data).decode("utf-8")
    
    print(f"🔢 Base64长度: {len(base64_str)}")
    
    # 创建data URL
    file_url = f"data:image/png;base64,{base64_str}"
    
    # 测试OCR识别
    print("\n🔍 测试OCR识别...")
    try:
        result = await ocr_service.recognize_general_text(file_url, ocr_type="General")
        if result:
            print(f"✅ OCR识别成功!")
            print(f"  文本长度: {len(result.get('text', ''))} 字符")
            print(f"  OCR类型: {result.get('ocr_type', 'N/A')}")
            print(f"  处理段数: {result.get('segments_processed', 1)}")
            print(f"  错误数: {result.get('errors_encountered', 0)}")
            
            # 显示部分文本
            text = result.get('text', '')
            if text:
                print(f"  前200字符: {text[:200]}...")
            
            return True
        else:
            print("❌ OCR识别失败")
            return False
    except Exception as e:
        print(f"❌ OCR识别异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_image_optimization():
    """测试图片优化功能"""
    print("\n" + "=" * 60)
    print("测试图片优化功能")
    print("=" * 60)
    
    # 创建OCR服务实例
    ocr_service = OcrService()
    
    # 读取测试文件
    fixture_path = Path("tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png")
    if not fixture_path.exists():
        print(f"❌ 测试文件不存在: {fixture_path}")
        return False
    
    with open(fixture_path, "rb") as f:
        image_data = f.read()
    
    print(f"📄 测试图片大小: {len(image_data)} bytes")
    
    # 测试图片优化
    try:
        optimized_data, image_format, segments = ocr_service._optimize_image_for_ocr(image_data)
        
        print(f"✅ 图片优化成功!")
        print(f"  原始大小: {len(image_data)} bytes")
        print(f"  优化后大小: {len(optimized_data)} bytes")
        print(f"  图片格式: {image_format}")
        print(f"  分割段数: {len(segments)}")
        
        # 检查每段大小
        for i, segment in enumerate(segments):
            print(f"  段 {i+1}: {len(segment)} bytes")
        
        return True
    except Exception as e:
        print(f"❌ 图片优化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_quote_recognition():
    """测试报价单识别"""
    print("\n" + "=" * 60)
    print("测试报价单识别")
    print("=" * 60)
    
    # 创建OCR服务实例
    ocr_service = OcrService()
    
    if ocr_service.client is None:
        print("❌ OCR客户端未初始化")
        return False
    
    # 读取测试文件
    fixture_path = Path("tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png")
    if not fixture_path.exists():
        print(f"❌ 测试文件不存在: {fixture_path}")
        return False
    
    with open(fixture_path, "rb") as f:
        file_data = f.read()
        base64_str = base64.b64encode(file_data).decode("utf-8")
    
    # 创建data URL
    file_url = f"data:image/png;base64,{base64_str}"
    
    # 测试报价单识别
    try:
        result = await ocr_service.recognize_quote(file_url, "image")
        if result:
            print(f"✅ 报价单识别成功!")
            print(f"  类型: {result.get('type')}")
            print(f"  OCR类型: {result.get('ocr_type')}")
            print(f"  文本长度: {len(result.get('content', ''))} 字符")
            
            # 检查是否包含关键词
            content = result.get('content', '').lower()
            keywords = ['报价', '装修', '工程', '项目', '金额', '合计', '总计']
            found_keywords = [kw for kw in keywords if kw in content]
            print(f"  找到的关键词: {found_keywords}")
            
            return True
        else:
            print("❌ 报价单识别失败")
            return False
    except Exception as e:
        print(f"❌ 报价单识别异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("开始测试OCR优化功能...")
    
    # 测试图片优化
    optimization_ok = await test_image_optimization()
    
    # 测试OCR识别
    ocr_ok = await test_ocr_optimization()
    
    # 测试报价单识别
    quote_ok = await test_quote_recognition()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if optimization_ok and ocr_ok and quote_ok:
        print("✅ 所有测试通过!")
        print("OCR优化功能正常工作")
    else:
        print("❌ 部分测试失败")
        
        if not optimization_ok:
            print("问题: 图片优化功能失败")
        if not ocr_ok:
            print("问题: OCR识别功能失败")
        if not quote_ok:
            print("问题: 报价单识别功能失败")
    
    print("\n建议:")
    print("1. 检查Pillow库是否正确安装")
    print("2. 检查图片文件是否可读")
    print("3. 检查阿里云OCR服务配置")

if __name__ == "__main__":
    asyncio.run(main())

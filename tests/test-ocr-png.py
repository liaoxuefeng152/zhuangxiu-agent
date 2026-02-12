#!/usr/bin/env python3
"""
直接测试OCR服务对PNG图片的识别
"""
import asyncio
import base64
import os
import sys

# 添加项目根目录到路径（tests 包与 backend）
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'backend'))

from app.services.ocr_service import ocr_service


async def test_png_ocr():
    """测试PNG图片的OCR识别"""
    print("=" * 60)
    print("PNG图片OCR识别测试")
    print("=" * 60)
    
    # 检查OCR服务是否初始化
    if ocr_service.client is None:
        print("❌ OCR服务未初始化，请检查配置")
        return
    
    print("✅ OCR服务已初始化")
    
    from tests import fixture_path, QUOTE_PNG, CONTRACT_PNG
    # 测试报价单PNG
    quote_png_path = fixture_path(QUOTE_PNG)
    if os.path.exists(quote_png_path):
        print(f"\n📄 测试文件1: {quote_png_path}")
        with open(quote_png_path, "rb") as f:
            file_content = f.read()
        
        print(f"📊 文件大小: {len(file_content)} bytes ({len(file_content)/1024:.2f} KB)")
        
        # 转换为Base64
        base64_str = base64.b64encode(file_content).decode("utf-8")
        ocr_input = f"data:image/png;base64,{base64_str}"
        print(f"📊 Base64长度: {len(base64_str)} 字符")
        
        # 测试通用文本识别
        print("\n🔍 测试通用文本识别...")
        try:
            result = await ocr_service.recognize_general_text(ocr_input)
            if result:
                print(f"✅ 识别成功！文本长度: {len(result.get('text', ''))}")
                print(f"📝 前200字符: {result.get('text', '')[:200]}...")
            else:
                print("❌ 识别失败，返回None")
        except Exception as e:
            print(f"❌ 识别异常: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试表格识别
        print("\n🔍 测试表格识别...")
        try:
            result = await ocr_service.recognize_table(ocr_input)
            if result:
                print(f"✅ 识别成功！文本长度: {len(result.get('text', ''))}")
                print(f"📊 表格数量: {len(result.get('tables', []))}")
            else:
                print("❌ 识别失败，返回None")
        except Exception as e:
            print(f"❌ 识别异常: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试报价单识别（会先尝试表格，再降级到通用）
        print("\n🔍 测试报价单识别（完整流程）...")
        try:
            result = await ocr_service.recognize_quote(ocr_input, "image")
            if result:
                print(f"✅ 识别成功！类型: {result.get('type')}")
                print(f"📝 内容长度: {len(result.get('content', ''))}")
                print(f"📝 前200字符: {result.get('content', '')[:200]}...")
            else:
                print("❌ 识别失败，返回None")
        except Exception as e:
            print(f"❌ 识别异常: {e}")
            import traceback
            traceback.print_exc()
    
    # 测试合同PNG
    contract_png_path = fixture_path(CONTRACT_PNG)
    if os.path.exists(contract_png_path):
        print(f"\n\n📄 测试文件2: {contract_png_path}")
        with open(contract_png_path, "rb") as f:
            file_content = f.read()
        
        print(f"📊 文件大小: {len(file_content)} bytes ({len(file_content)/1024:.2f} KB)")
        
        # 转换为Base64
        base64_str = base64.b64encode(file_content).decode("utf-8")
        ocr_input = f"data:image/png;base64,{base64_str}"
        print(f"📊 Base64长度: {len(base64_str)} 字符")
        
        # 测试合同识别
        print("\n🔍 测试合同识别...")
        try:
            result = await ocr_service.recognize_contract(ocr_input)
            if result:
                print(f"✅ 识别成功！类型: {result.get('type')}")
                print(f"📝 内容长度: {len(result.get('content', ''))}")
                print(f"📝 前200字符: {result.get('content', '')[:200]}...")
            else:
                print("❌ 识别失败，返回None")
        except Exception as e:
            print(f"❌ 识别异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_png_ocr())

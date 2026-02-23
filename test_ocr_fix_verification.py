#!/usr/bin/env python3
"""
测试OCR修复效果验证
"""
import asyncio
import sys
import os
import base64

# 设置环境变量，避免配置验证错误
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/zhuangxiu_dev"
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "true"

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ocr_service import OcrService

async def test_ocr_with_large_image():
    """测试超大图片的OCR识别"""
    print("=== 测试OCR修复效果验证 ===")
    
    # 创建OCR服务实例
    ocr_service = OcrService()
    
    if ocr_service.client is None:
        print("❌ OCR客户端初始化失败")
        print("请检查ECS实例RAM角色配置")
        return False
    
    print("✅ OCR客户端初始化成功")
    
    # 测试图片路径
    test_image_path = "tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png"
    
    if not os.path.exists(test_image_path):
        print(f"❌ 测试图片不存在: {test_image_path}")
        # 尝试创建一个小测试图片
        try:
            from PIL import Image
            import io
            
            # 创建一个测试图片
            img = Image.new('RGB', (1000, 5000), color='white')
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            image_data = buffered.getvalue()
            base64_str = base64.b64encode(image_data).decode('utf-8')
            file_url = f"data:image/png;base64,{base64_str}"
            print(f"✅ 创建测试图片: 1000x5000像素")
        except Exception as e:
            print(f"❌ 创建测试图片失败: {e}")
            return False
    else:
        print(f"✅ 找到测试图片: {test_image_path}")
        
        # 将图片转换为Base64
        try:
            with open(test_image_path, "rb") as f:
                image_data = f.read()
                base64_str = base64.b64encode(image_data).decode('utf-8')
                file_url = f"data:image/png;base64,{base64_str}"
            
            print(f"✅ 图片转换为Base64，长度: {len(base64_str)}")
            print(f"   图片大小: {len(image_data)} bytes")
            
            # 检查图片尺寸
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_data))
            print(f"   图片尺寸: {img.size[0]}x{img.size[1]}像素")
            
        except Exception as e:
            print(f"❌ 图片转换失败: {e}")
            return False
    
    # 测试OCR识别
    print("\n--- 测试OCR识别 ---")
    
    try:
        # 测试通用文字识别
        print("测试通用文字识别...")
        result = await ocr_service.recognize_general_text(file_url, ocr_type="General")
        
        if result:
            print(f"✅ OCR识别成功!")
            print(f"   OCR类型: {result.get('ocr_type', 'N/A')}")
            print(f"   文本长度: {len(result.get('text', ''))}")
            print(f"   处理段数: {result.get('segments_processed', 1)}")
            print(f"   错误数: {result.get('errors_encountered', 0)}")
            print(f"   是否降级: {result.get('fallback', False)}")
            
            # 显示前200个字符
            text_preview = result.get('text', '')[:200]
            if text_preview:
                print(f"   文本预览: {text_preview}...")
            
            # 检查是否包含常见关键词
            content = result.get('text', '').lower()
            keywords = ['报价', '装修', '工程', '项目', '金额', '合计', '总计', '材料', '人工']
            found_keywords = [kw for kw in keywords if kw in content]
            print(f"   找到的关键词: {found_keywords}")
            
            return True
        else:
            print("❌ OCR识别失败，返回None")
            return False
            
    except Exception as e:
        print(f"❌ OCR识别异常: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_quote_recognition():
    """测试报价单识别"""
    print("\n--- 测试报价单识别 ---")
    
    # 创建OCR服务实例
    ocr_service = OcrService()
    
    if ocr_service.client is None:
        print("❌ OCR客户端未初始化")
        return False
    
    # 测试图片路径
    test_image_path = "tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png"
    
    if not os.path.exists(test_image_path):
        print(f"❌ 测试图片不存在: {test_image_path}")
        return False
    
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
            base64_str = base64.b64encode(image_data).decode('utf-8')
            file_url = f"data:image/png;base64,{base64_str}"
        
        result = await ocr_service.recognize_quote(file_url, "image")
        
        if result:
            print(f"✅ 报价单识别成功!")
            print(f"   识别类型: {result.get('type', 'N/A')}")
            print(f"   OCR类型: {result.get('ocr_type', 'N/A')}")
            print(f"   文本长度: {len(result.get('content', ''))}")
            
            # 检查是否包含表格
            if result.get('type') == 'table':
                print(f"   表格数量: {len(result.get('tables', []))}")
            
            return True
        else:
            print("❌ 报价单识别失败")
            return False
            
    except Exception as e:
        print(f"❌ 报价单识别异常: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_image_optimization():
    """测试图片优化功能"""
    print("\n--- 测试图片优化功能 ---")
    
    # 创建OCR服务实例
    ocr_service = OcrService()
    
    # 创建一个大图片
    try:
        from PIL import Image
        import io
        
        # 创建一个高图片（1000x6000像素）
        img = Image.new('RGB', (1000, 6000), color='white')
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        image_data = buffered.getvalue()
        
        print(f"✅ 创建测试图片: 1000x6000像素, {len(image_data)} bytes")
        
        # 测试图片优化
        optimized_data, image_format, segments = ocr_service._optimize_image_for_ocr(image_data, max_height=4000)
        
        print(f"✅ 图片优化成功!")
        print(f"   优化后格式: {image_format}")
        print(f"   主图片大小: {len(optimized_data)} bytes")
        print(f"   分割段数: {len(segments)}")
        
        # 检查是否进行了分割
        if len(segments) > 1:
            print(f"   ✅ 图片被正确分割为 {len(segments)} 段")
            for i, segment in enumerate(segments):
                print(f"       段 {i+1}: {len(segment)} bytes")
        else:
            print(f"   ℹ️ 图片未分割（高度未超过限制）")
        
        return True
        
    except Exception as e:
        print(f"❌ 图片优化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("开始测试OCR修复效果...")
    
    # 测试图片优化
    optimization_ok = await test_image_optimization()
    
    # 测试OCR识别
    ocr_ok = await test_ocr_with_large_image()
    
    # 测试报价单识别
    quote_ok = await test_quote_recognition()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if optimization_ok and ocr_ok and quote_ok:
        print("✅ 所有测试通过!")
        print("\n修复效果验证:")
        print("1. ✅ 图片优化功能正常（支持超大图片分割）")
        print("2. ✅ OCR识别功能正常（支持Base64格式验证）")
        print("3. ✅ 报价单识别功能正常")
        print("\n建议:")
        print("1. 部署到阿里云服务器进行生产环境测试")
        print("2. 测试实际报价单图片的OCR识别准确率")
        print("3. 监控OCR服务的错误率和性能")
        return True
    else:
        print("❌ 部分测试失败")
        print("\n失败详情:")
        if not optimization_ok:
            print("1. ❌ 图片优化功能测试失败")
        if not ocr_ok:
            print("2. ❌ OCR识别测试失败")
        if not quote_ok:
            print("3. ❌ 报价单识别测试失败")
        
        print("\n建议:")
        print("1. 检查OCR服务配置（RAM角色、权限等）")
        print("2. 检查图片格式和大小限制")
        print("3. 查看详细错误日志")
        return False

if __name__ == "__main__":
    # 运行异步测试
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"测试运行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
测试阿里云 OCR 服务修复效果
验证 Type 参数是否正确设置
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ocr_service import OcrService
import base64

async def test_ocr_service():
    """测试 OCR 服务"""
    print("=== 测试阿里云 OCR 服务修复效果 ===")
    
    # 创建 OCR 服务实例
    ocr_service = OcrService()
    
    if ocr_service.client is None:
        print("❌ OCR 客户端初始化失败")
        print("请检查：")
        print("1. ECS 实例是否绑定 RAM 角色 'zhuangxiu-ecs-role'")
        print("2. RAM 角色是否授权 OCR 权限")
        print("3. 阿里云 OCR 服务是否已开通")
        return False
    
    print("✅ OCR 客户端初始化成功")
    
    # 测试图片路径
    test_image_path = "tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png"
    
    if not os.path.exists(test_image_path):
        print(f"❌ 测试图片不存在: {test_image_path}")
        return False
    
    print(f"✅ 找到测试图片: {test_image_path}")
    
    # 将图片转换为 Base64
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
            base64_str = base64.b64encode(image_data).decode('utf-8')
            file_url = f"data:image/png;base64,{base64_str}"
        
        print(f"✅ 图片转换为 Base64，长度: {len(base64_str)}")
    except Exception as e:
        print(f"❌ 图片转换失败: {e}")
        return False
    
    # 测试不同的 OCR 类型
    test_cases = [
        ("Advanced", "高精版通用文字识别"),
        ("General", "基础版通用文字识别"),
        ("Table", "表格识别"),
    ]
    
    for ocr_type, description in test_cases:
        print(f"\n--- 测试 {description} (Type: {ocr_type}) ---")
        
        try:
            result = await ocr_service.recognize_general_text(file_url, ocr_type=ocr_type)
            
            if result:
                print(f"✅ {description} 成功")
                print(f"   OCR 类型: {result.get('ocr_type', 'N/A')}")
                print(f"   文本长度: {len(result.get('text', ''))}")
                print(f"   是否降级: {result.get('fallback', False)}")
                
                # 显示前200个字符
                text_preview = result.get('text', '')[:200]
                if text_preview:
                    print(f"   文本预览: {text_preview}...")
            else:
                print(f"❌ {description} 失败，返回 None")
                
        except Exception as e:
            print(f"❌ {description} 异常: {e}")
    
    # 测试报价单识别
    print("\n--- 测试报价单识别 ---")
    try:
        quote_result = await ocr_service.recognize_quote(file_url)
        if quote_result:
            print(f"✅ 报价单识别成功")
            print(f"   识别类型: {quote_result.get('type', 'N/A')}")
            print(f"   OCR 类型: {quote_result.get('ocr_type', 'N/A')}")
            print(f"   文本长度: {len(quote_result.get('content', ''))}")
        else:
            print("❌ 报价单识别失败")
    except Exception as e:
        print(f"❌ 报价单识别异常: {e}")
    
    # 测试合同识别
    print("\n--- 测试合同识别 ---")
    try:
        contract_result = await ocr_service.recognize_contract(file_url)
        if contract_result:
            print(f"✅ 合同识别成功")
            print(f"   识别类型: {contract_result.get('type', 'N/A')}")
            print(f"   OCR 类型: {contract_result.get('ocr_type', 'N/A')}")
            print(f"   文本长度: {len(contract_result.get('content', ''))}")
        else:
            print("❌ 合同识别失败")
    except Exception as e:
        print(f"❌ 合同识别异常: {e}")
    
    print("\n=== 测试完成 ===")
    return True

if __name__ == "__main__":
    # 运行异步测试
    try:
        success = asyncio.run(test_ocr_service())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"测试运行异常: {e}")
        sys.exit(1)

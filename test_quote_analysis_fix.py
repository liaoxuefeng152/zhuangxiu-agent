#!/usr/bin/env python3
"""
测试报价单分析功能修复
使用tests/fixtures中的真实报价单图片进行测试
"""
import sys
import os
import asyncio
import base64
from pathlib import Path

# 添加backend到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ocr_service import ocr_service

async def test_quote_analysis():
    """测试报价单分析功能"""
    print("=== 测试报价单分析功能修复 ===")
    
    # 测试图片路径
    test_image_path = "tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png"
    
    if not os.path.exists(test_image_path):
        print(f"❌ 测试图片不存在: {test_image_path}")
        return
    
    print(f"📷 使用测试图片: {test_image_path}")
    print(f"📏 文件大小: {os.path.getsize(test_image_path)} bytes")
    
    # 将图片转换为Base64
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
            base64_str = base64.b64encode(image_data).decode("utf-8")
            file_url = f"data:image/png;base64,{base64_str}"
        
        print("✅ 图片已转换为Base64格式")
        print(f"📊 Base64长度: {len(base64_str)}")
    except Exception as e:
        print(f"❌ 图片转换失败: {e}")
        return
    
    # 测试OCR服务初始化
    print("\n1. 测试OCR服务初始化...")
    if ocr_service.client is not None:
        print("✅ OCR客户端初始化成功")
    else:
        print("❌ OCR客户端初始化失败")
        print("提示: 检查ECS实例是否绑定RAM角色 'zhuangxiu-ecs-role'")
        return
    
    # 测试报价单识别
    print("\n2. 测试报价单识别...")
    try:
        print("开始OCR识别...")
        result = await ocr_service.recognize_quote(file_url, file_type="image")
        
        if result:
            print("✅ 报价单识别成功!")
            print(f"📄 识别类型: {result.get('type', 'N/A')}")
            print(f"🔤 OCR类型: {result.get('ocr_type', 'N/A')}")
            print(f"🔄 是否降级: {result.get('fallback', False)}")
            
            content = result.get('content', '')
            if content:
                print(f"📝 识别内容长度: {len(content)} 字符")
                print(f"📝 内容预览 (前500字符):")
                print("-" * 50)
                print(content[:500])
                print("-" * 50)
                
                # 检查是否包含关键信息
                keywords = ["报价", "项目", "金额", "合计", "装修", "平米", "㎡"]
                found_keywords = [kw for kw in keywords if kw in content]
                if found_keywords:
                    print(f"✅ 包含关键信息: {', '.join(found_keywords)}")
                else:
                    print("⚠️  未检测到常见报价单关键词")
            else:
                print("❌ 识别内容为空")
                
            # 检查是否有表格数据
            tables = result.get('tables', [])
            if tables:
                print(f"📊 识别到表格: {len(tables)} 个")
            else:
                print("📊 未识别到表格数据")
        else:
            print("❌ 报价单识别失败，返回None")
            
    except Exception as e:
        print(f"❌ 报价单识别异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试通用文字识别
    print("\n3. 测试通用文字识别...")
    try:
        print("开始通用文字识别...")
        general_result = await ocr_service.recognize_general_text(file_url, ocr_type="General")
        
        if general_result:
            print("✅ 通用文字识别成功!")
            print(f"🔤 OCR类型: {general_result.get('ocr_type', 'N/A')}")
            print(f"🔄 是否降级: {general_result.get('fallback', False)}")
            
            text = general_result.get('text', '')
            if text:
                print(f"📝 识别内容长度: {len(text)} 字符")
                print(f"📝 内容预览 (前300字符):")
                print("-" * 50)
                print(text[:300])
                print("-" * 50)
            else:
                print("❌ 识别文本为空")
        else:
            print("❌ 通用文字识别失败，返回None")
            
    except Exception as e:
        print(f"❌ 通用文字识别异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试完成 ===")
    print("\n修复验证总结:")
    print("1. ✅ OCR服务初始化检查")
    print("2. ✅ 报价单识别功能测试")
    print("3. ✅ 通用文字识别功能测试")
    print("\n如果测试成功，说明修复已生效，OCR功能正常工作。")
    print("如果仍有问题，请检查阿里云OCR服务是否已开通通用文字识别。")

if __name__ == "__main__":
    # 设置环境变量避免配置验证错误
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DATABASE_URL"] = "postgresql://zhuangxiu_user:zhuangxiu_password@localhost:5432/zhuangxiu_dev"
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["ALIYUN_OCR_ENDPOINT"] = "ocr-api.cn-hangzhou.aliyuncs.com"
    os.environ["ALIYUN_OCR_REGION"] = "cn-hangzhou"
    
    asyncio.run(test_quote_analysis())

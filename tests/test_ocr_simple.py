#!/usr/bin/env python3
"""
简单测试OCR服务 - 不依赖完整配置
"""
import os
import sys
import base64
import json
from pathlib import Path

# 设置所有必需的环境变量
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/zhuangxiu_dev"
os.environ["ENVIRONMENT"] = "development"
os.environ["WECHAT_APP_ID"] = "test_app_id"
os.environ["WECHAT_APP_SECRET"] = "test_app_secret"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_for_development_only"
os.environ["ALIYUN_OCR_ENDPOINT"] = "ocr-api.cn-hangzhou.aliyuncs.com"

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# 直接导入OCR服务，跳过配置验证
import importlib.util
import sys

# 动态导入OCR服务模块
ocr_service_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app', 'services', 'ocr_service.py')
spec = importlib.util.spec_from_file_location("ocr_service", ocr_service_path)
ocr_module = importlib.util.module_from_spec(spec)

# 设置模块的__name__以避免配置验证
ocr_module.__name__ = "app.services.ocr_service"

# 执行模块
sys.modules["app.services.ocr_service"] = ocr_module
spec.loader.exec_module(ocr_module)

# 获取OCR服务实例
ocr_service = ocr_module.ocr_service

async def test_ocr_service():
    """测试OCR服务"""
    print("=" * 60)
    print("测试OCR服务")
    print("=" * 60)
    
    # 检查OCR服务是否初始化成功
    if ocr_service.client is None:
        print("❌ OCR客户端未初始化")
        print("可能原因:")
        print("1. ECS实例未绑定RAM角色 'zhuangxiu-ecs-role'")
        print("2. RAM角色未授权OCR权限")
        print("3. 网络连接问题")
        print("4. 本地环境无法获取ECS元数据")
        return False
    
    print("✅ OCR客户端已初始化")
    
    # 读取测试文件
    fixture_path = Path("tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png")
    if not fixture_path.exists():
        print(f"❌ 测试文件不存在: {fixture_path}")
        return False
    
    print(f"📄 使用测试文件: {fixture_path}")
    file_size = os.path.getsize(fixture_path)
    print(f"📊 文件大小: {file_size} bytes")
    
    # 将文件转换为Base64
    with open(fixture_path, "rb") as f:
        file_data = f.read()
        base64_str = base64.b64encode(file_data).decode("utf-8")
    
    print(f"🔢 Base64长度: {len(base64_str)}")
    
    # 使用完整的data URL格式
    file_url = f"data:image/png;base64,{base64_str}"
    
    try:
        print(f"\n🔍 测试OCR识别...")
        print(f"  输入类型: data URL with Base64")
        print(f"  输入长度: {len(file_url)}")
        
        result = await ocr_service.recognize_general_text(file_url, ocr_type="General")
        if result:
            print(f"  ✅ OCR识别成功!")
            print(f"  文本长度: {len(result.get('text', ''))} 字符")
            print(f"  OCR类型: {result.get('ocr_type', 'N/A')}")
            print(f"  前100字符: {result.get('text', '')[:100]}...")
            
            # 检查是否包含关键词
            content = result.get('text', '').lower()
            keywords = ['报价', '装修', '工程', '项目', '金额', '合计', '总计']
            found_keywords = [kw for kw in keywords if kw in content]
            print(f"  找到的关键词: {found_keywords}")
            
            return True
        else:
            print(f"  ❌ OCR识别失败")
            return False
    except Exception as e:
        print(f"  ❌ OCR识别异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_quote_recognition():
    """测试报价单识别"""
    print("\n" + "=" * 60)
    print("测试报价单识别")
    print("=" * 60)
    
    fixture_path = Path("tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png")
    if not fixture_path.exists():
        print(f"❌ 测试文件不存在: {fixture_path}")
        return False
    
    with open(fixture_path, "rb") as f:
        file_data = f.read()
        base64_str = base64.b64encode(file_data).decode("utf-8")
    
    # 使用完整的data URL格式
    file_url = f"data:image/png;base64,{base64_str}"
    
    try:
        result = await ocr_service.recognize_quote(file_url, "image")
        if result:
            print(f"✅ 报价单识别成功!")
            print(f"  类型: {result.get('type')}")
            print(f"  OCR类型: {result.get('ocr_type')}")
            print(f"  文本长度: {len(result.get('content', ''))} 字符")
            print(f"  前200字符: {result.get('content', '')[:200]}...")
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
    print("开始测试OCR服务...")
    
    # 测试OCR服务
    ocr_ok = await test_ocr_service()
    
    # 测试报价单识别
    quote_ok = await test_quote_recognition()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if quote_ok:
        print("✅ 报价单OCR识别功能正常")
        print("问题可能出现在:")
        print("1. 报价单上传接口的文件处理逻辑")
        print("2. Base64编码格式问题")
        print("3. 文件大小限制")
        print("4. 阿里云生产环境配置问题")
    else:
        print("❌ 报价单OCR识别失败")
        
        if not ocr_ok:
            print("根本原因: OCR服务初始化或调用失败")
            print("可能原因:")
            print("1. 本地环境无法获取ECS RAM角色凭证")
            print("2. 阿里云OCR服务未开通")
            print("3. OCR API调用参数错误")
            print("4. 网络连接问题")
        else:
            print("根本原因: 报价单识别逻辑问题")
            print("可能原因:")
            print("1. recognize_quote函数逻辑错误")
            print("2. 文件类型判断错误")
    
    print("\n建议:")
    print("1. 检查阿里云生产环境OCR服务配置")
    print("2. 检查ECS实例RAM角色配置")
    print("3. 检查报价单上传接口的Base64编码逻辑")
    print("4. 尝试使用更小的测试图片")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

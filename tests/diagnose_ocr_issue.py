#!/usr/bin/env python3
"""
诊断报价单OCR识别问题
"""
import os
import sys
import base64
import json
from pathlib import Path

# 设置环境变量，避免配置验证错误
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/zhuangxiu_dev"
os.environ["ENVIRONMENT"] = "development"

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.ocr_service import ocr_service

async def test_ocr_directly():
    """直接测试OCR服务"""
    print("=" * 60)
    print("直接测试OCR服务")
    print("=" * 60)
    
    # 检查OCR服务是否初始化成功
    if ocr_service.client is None:
        print("❌ OCR客户端未初始化")
        print("可能原因:")
        print("1. ECS实例未绑定RAM角色 'zhuangxiu-ecs-role'")
        print("2. RAM角色未授权OCR权限")
        print("3. 网络连接问题")
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
    
    # 测试不同的输入格式
    test_cases = [
        {
            "name": "Base64 with data URL prefix",
            "input": f"data:image/png;base64,{base64_str}",
            "description": "完整的data URL格式"
        },
        {
            "name": "Raw Base64",
            "input": base64_str,
            "description": "纯Base64数据"
        },
        {
            "name": "Small Base64 (first 100KB)",
            "input": base64_str[:100000],
            "description": "截断的Base64数据"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🔍 测试用例 {i+1}: {test_case['name']}")
        print(f"  描述: {test_case['description']}")
        print(f"  输入长度: {len(test_case['input'])}")
        
        try:
            result = await ocr_service.recognize_general_text(test_case['input'], ocr_type="General")
            if result:
                print(f"  ✅ OCR识别成功!")
                print(f"  文本长度: {len(result.get('text', ''))} 字符")
                print(f"  OCR类型: {result.get('ocr_type', 'N/A')}")
                print(f"  前100字符: {result.get('text', '')[:100]}...")
                return True
            else:
                print(f"  ❌ OCR识别失败")
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

async def test_ocr_connection():
    """测试OCR连接"""
    print("\n" + "=" * 60)
    print("测试OCR连接")
    print("=" * 60)
    
    try:
        # 尝试获取ECS元数据
        import requests
        print("尝试获取ECS实例元数据...")
        
        # 获取RAM角色名称
        try:
            resp = requests.get('http://100.100.100.200/latest/meta-data/ram/security-credentials/', timeout=2)
            if resp.status_code == 200:
                role_name = resp.text.strip()
                print(f"✅ 获取到RAM角色名称: {role_name}")
                
                # 获取RAM角色凭证
                resp2 = requests.get(f'http://100.100.100.200/latest/meta-data/ram/security-credentials/{role_name}', timeout=2)
                if resp2.status_code == 200:
                    credentials = resp2.json()
                    print(f"✅ 获取到RAM角色凭证")
                    print(f"   AccessKeyId: {credentials.get('AccessKeyId', 'N/A')[:10]}...")
                    print(f"   Expiration: {credentials.get('Expiration', 'N/A')}")
                    return True
                else:
                    print(f"❌ 获取RAM角色凭证失败: HTTP {resp2.status_code}")
            else:
                print(f"❌ 获取RAM角色名称失败: HTTP {resp.status_code}")
        except Exception as e:
            print(f"❌ 获取ECS元数据失败: {str(e)}")
            print("可能原因:")
            print("1. 不在ECS实例环境中运行")
            print("2. 网络配置问题")
            print("3. 安全组规则限制")
        
        return False
    except Exception as e:
        print(f"❌ 测试OCR连接异常: {str(e)}")
        return False

async def main():
    print("开始诊断报价单OCR识别问题...")
    
    # 测试OCR连接
    connection_ok = await test_ocr_connection()
    
    # 直接测试OCR服务
    ocr_ok = await test_ocr_directly()
    
    # 测试报价单识别
    quote_ok = await test_quote_recognition()
    
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)
    
    if quote_ok:
        print("✅ 报价单OCR识别功能正常")
        print("问题可能出现在:")
        print("1. 报价单上传接口的文件处理逻辑")
        print("2. Base64编码格式问题")
        print("3. 文件大小限制")
    else:
        print("❌ 报价单OCR识别失败")
        
        if not connection_ok:
            print("根本原因: OCR连接问题")
            print("解决方案:")
            print("1. 检查ECS实例是否绑定RAM角色 'zhuangxiu-ecs-role'")
            print("2. 检查RAM角色是否授权OCR权限")
            print("3. 检查网络连接和安全组规则")
        elif not ocr_ok:
            print("根本原因: OCR服务调用失败")
            print("可能原因:")
            print("1. 阿里云OCR服务未开通")
            print("2. OCR API调用参数错误")
            print("3. 图片格式不支持")
            print("4. 图片质量太差")
        else:
            print("根本原因: 报价单识别逻辑问题")
            print("可能原因:")
            print("1. recognize_quote函数逻辑错误")
            print("2. 文件类型判断错误")
            print("3. 异常处理不当")
    
    print("\n建议:")
    print("1. 检查阿里云控制台OCR服务是否已开通")
    print("2. 检查ECS实例RAM角色配置")
    print("3. 尝试使用更小的测试图片")
    print("4. 检查图片格式和质量")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

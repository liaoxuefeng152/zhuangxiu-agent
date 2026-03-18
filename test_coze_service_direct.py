#!/usr/bin/env python3
"""
直接测试coze_service修复
"""

import sys
import os
import asyncio

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_coze_service_init():
    """测试coze_service初始化"""
    print("=== 测试coze_service初始化 ===")
    
    try:
        # 导入coze_service
        from backend.app.services.coze_service import CozeService
        
        # 创建实例
        service = CozeService()
        
        print(f"服务配置:")
        print(f"  - use_site_api: {service.use_site_api}")
        print(f"  - use_open_api: {service.use_open_api}")
        print(f"  - use_deepseek: {service.use_deepseek}")
        print(f"  - site_api_url: {service.site_api_url}")
        print(f"  - open_api_key: {'已设置' if service.open_api_key else '未设置'}")
        print(f"  - deepseek_api_key: {'已设置' if service.deepseek_api_key else '未设置'}")
        
        # 检查是否有可用的API
        if service.use_site_api or service.use_open_api or service.use_deepseek:
            print("✓ 至少有一个AI分析渠道可用")
            return True
        else:
            print("✗ 没有可用的AI分析渠道")
            return False
            
    except Exception as e:
        print(f"初始化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_quote_analysis():
    """测试报价单分析"""
    print("\n=== 测试报价单分析 ===")
    
    try:
        from backend.app.services.coze_service import CozeService
        
        service = CozeService()
        
        # 创建一个测试图片URL（模拟）
        test_image_url = "https://example.com/test.jpg"
        
        print(f"调用analyze_quote方法...")
        print(f"图片URL: {test_image_url}")
        
        # 调用分析方法
        result = await service.analyze_quote(test_image_url, user_id=1)
        
        if result:
            print(f"✓ 分析成功，返回结果类型: {type(result)}")
            print(f"结果结构:")
            for key in result.keys():
                print(f"  - {key}")
            
            # 检查关键字段
            required_fields = ["risk_score", "suggestions", "high_risk_items"]
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"⚠ 缺少字段: {missing_fields}")
            else:
                print(f"✓ 包含所有关键字段")
            
            # 检查是否是兜底结果
            is_fallback = result.get("is_fallback", False)
            if is_fallback:
                print(f"⚠ 返回的是兜底结果（服务可能不可用）")
            else:
                print(f"✓ 返回的是正常分析结果")
            
            return True
        else:
            print(f"✗ 分析返回None或空结果")
            return False
            
    except Exception as e:
        print(f"报价单分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_contract_analysis():
    """测试合同分析"""
    print("\n=== 测试合同分析 ===")
    
    try:
        from backend.app.services.coze_service import CozeService
        
        service = CozeService()
        
        # 创建一个测试图片URL（模拟）
        test_image_url = "https://example.com/contract.pdf"
        
        print(f"调用analyze_contract方法...")
        print(f"图片URL: {test_image_url}")
        
        # 调用分析方法
        result = await service.analyze_contract(test_image_url, user_id=1)
        
        if result:
            print(f"✓ 分析成功，返回结果类型: {type(result)}")
            print(f"结果结构:")
            for key in result.keys():
                print(f"  - {key}")
            
            # 检查关键字段
            required_fields = ["risk_level", "suggestions", "risk_items"]
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"⚠ 缺少字段: {missing_fields}")
            else:
                print(f"✓ 包含所有关键字段")
            
            # 检查是否是兜底结果
            is_fallback = result.get("is_fallback", False)
            if is_fallback:
                print(f"⚠ 返回的是兜底结果（服务可能不可用）")
            else:
                print(f"✓ 返回的是正常分析结果")
            
            return True
        else:
            print(f"✗ 分析返回None或空结果")
            return False
            
    except Exception as e:
        print(f"合同分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("开始直接测试coze_service修复...")
    
    # 测试初始化
    init_success = await test_coze_service_init()
    
    # 测试报价单分析
    quote_success = await test_quote_analysis()
    
    # 测试合同分析
    contract_success = await test_contract_analysis()
    
    # 总结
    print("\n=== 测试总结 ===")
    print(f"初始化测试: {'通过' if init_success else '失败'}")
    print(f"报价单分析测试: {'通过' if quote_success else '失败'}")
    print(f"合同分析测试: {'通过' if contract_success else '失败'}")
    
    overall_success = init_success and quote_success and contract_success
    print(f"\n总体测试结果: {'通过' if overall_success else '失败'}")
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

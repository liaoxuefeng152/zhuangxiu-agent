#!/usr/bin/env python3
"""
详细测试报价单分析流程
模拟完整的OCR识别和AI分析过程
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

# 导入服务
try:
    from app.services.ocr_service import ocr_service
    from app.services.risk_analyzer import risk_analyzer_service
    print("成功导入OCR服务和风险分析服务")
except ImportError as e:
    print(f"导入服务失败: {e}")
    sys.exit(1)

async def test_ocr_recognition():
    """测试OCR识别"""
    print("\n1. 测试OCR识别")
    
    # 使用测试数据中的报价单图片
    fixture_path = Path("tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png")
    if not fixture_path.exists():
        print(f"错误: 测试文件不存在: {fixture_path}")
        return None
    
    print(f"使用测试文件: {fixture_path}")
    
    try:
        # 将文件转换为Base64
        with open(fixture_path, "rb") as f:
            import base64
            file_data = f.read()
            base64_str = base64.b64encode(file_data).decode("utf-8")
            file_url = f"data:image/png;base64,{base64_str}"
        
        print(f"文件大小: {len(file_data)} bytes")
        print(f"Base64长度: {len(base64_str)}")
        
        # 测试OCR识别
        print("调用OCR识别...")
        result = await ocr_service.recognize_quote(file_url, "image")
        
        if result:
            print(f"OCR识别成功!")
            print(f"识别类型: {result.get('type')}")
            print(f"OCR类型: {result.get('ocr_type')}")
            content = result.get("content", "")
            print(f"文本长度: {len(content)} 字符")
            print(f"前200字符: {content[:200]}...")
            return content
        else:
            print("OCR识别失败")
            return None
            
    except Exception as e:
        print(f"OCR识别异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_ai_analysis(ocr_text):
    """测试AI分析"""
    print("\n2. 测试AI分析")
    
    if not ocr_text:
        print("错误: OCR文本为空")
        return None
    
    print(f"OCR文本长度: {len(ocr_text)} 字符")
    print(f"OCR文本预览: {ocr_text[:200]}...")
    
    try:
        # 提取总价（模拟报价单分析API中的逻辑）
        import re
        total_price = None
        price_match = re.search(r'[总合]计[^\d]*(\d+(?:\.\d+)?)', ocr_text)
        if price_match:
            total_price = float(price_match.group(1))
            print(f"提取到总价: {total_price}元")
        else:
            print("未提取到总价")
        
        # 测试AI分析
        print("调用AI分析...")
        analysis_result = await risk_analyzer_service.analyze_quote(ocr_text, total_price)
        
        if analysis_result:
            print(f"AI分析成功!")
            print(f"风险评分: {analysis_result.get('risk_score', 'N/A')}")
            print(f"高风险项数量: {len(analysis_result.get('high_risk_items', []))}")
            print(f"警告项数量: {len(analysis_result.get('warning_items', []))}")
            print(f"缺失项数量: {len(analysis_result.get('missing_items', []))}")
            print(f"虚高价项数量: {len(analysis_result.get('overpriced_items', []))}")
            
            # 检查是否是兜底数据
            suggestions = analysis_result.get("suggestions", [])
            if suggestions:
                print(f"建议: {suggestions[0][:100]}...")
                if suggestions[0] == "AI分析服务暂时不可用，请稍后重试":
                    print("警告: 返回的是兜底数据!")
                else:
                    print("返回的是模拟的真实数据")
            
            return analysis_result
        else:
            print("AI分析失败")
            return None
            
    except Exception as e:
        print(f"AI分析异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_default_analysis():
    """测试默认分析函数"""
    print("\n3. 测试默认分析函数")
    
    try:
        # 测试_get_default_quote_analysis函数
        default_result = risk_analyzer_service._get_default_quote_analysis()
        
        print(f"默认分析结果:")
        print(f"风险评分: {default_result.get('risk_score')}")
        print(f"高风险项数量: {len(default_result.get('high_risk_items', []))}")
        print(f"警告项数量: {len(default_result.get('warning_items', []))}")
        
        suggestions = default_result.get("suggestions", [])
        if suggestions:
            print(f"建议: {suggestions[0]}")
            if suggestions[0] == "AI分析服务暂时不可用，请稍后重试":
                print("这是旧的兜底提示")
            else:
                print("这是新的模拟真实数据")
        
        return default_result
        
    except Exception as e:
        print(f"测试默认分析函数异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_quote_api_logic():
    """测试报价单API逻辑"""
    print("\n4. 测试报价单API逻辑")
    
    # 模拟报价单分析API中的检查逻辑
    mock_analysis_result = {
        "risk_score": 45,
        "high_risk_items": [],
        "warning_items": [{
            "category": "漏项风险",
            "item": "防水工程",
            "description": "报价单中未明确防水工程",
            "suggestion": "要求补充防水工程明细"
        }],
        "missing_items": [],
        "overpriced_items": [],
        "total_price": None,
        "market_ref_price": "根据市场行情，类似装修项目参考价在30000-40000元之间",
        "suggestions": [
            "建议与装修公司明确所有施工细节",
            "要求提供材料品牌和型号",
            "分期付款，按进度支付"
        ]
    }
    
    print("模拟分析结果检查:")
    suggestions = mock_analysis_result.get("suggestions") or []
    print(f"建议列表: {suggestions}")
    
    if suggestions and suggestions[0] == "AI分析服务暂时不可用，请稍后重试":
        print("API会将此标记为失败 (status = 'failed')")
    else:
        print("API会将此标记为成功 (status = 'completed')")
    
    # 测试旧的兜底数据
    old_fallback_result = {
        "risk_score": 0,
        "high_risk_items": [],
        "warning_items": [],
        "missing_items": [],
        "overpriced_items": [],
        "total_price": None,
        "market_ref_price": None,
        "suggestions": ["AI分析服务暂时不可用，请稍后重试"]
    }
    
    print("\n旧的兜底数据检查:")
    old_suggestions = old_fallback_result.get("suggestions") or []
    print(f"建议列表: {old_suggestions}")
    
    if old_suggestions and old_suggestions[0] == "AI分析服务暂时不可用，请稍后重试":
        print("API会将此标记为失败 (status = 'failed')")
    else:
        print("API会将此标记为成功 (status = 'completed')")

async def main():
    print("=" * 60)
    print("报价单分析详细测试")
    print("=" * 60)
    
    # 测试OCR识别
    ocr_text = await test_ocr_recognition()
    
    # 测试AI分析
    if ocr_text:
        analysis_result = await test_ai_analysis(ocr_text)
    
    # 测试默认分析函数
    default_result = await test_default_analysis()
    
    # 测试API逻辑
    await test_quote_api_logic()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    print("根据测试结果，分析可能的问题:")
    print("1. 如果OCR识别失败，可能是阿里云OCR服务配置问题")
    print("2. 如果AI分析返回兜底数据，可能是扣子/DeepSeek服务配置问题")
    print("3. 最近的修改将兜底数据从'AI分析服务暂时不可用'改为模拟的真实数据")
    print("4. 用户可能希望恢复原来的兜底提示，或者有其他问题")
    
    print("\n建议:")
    print("1. 检查生产环境OCR服务配置（ECS RAM角色、阿里云OCR服务开通）")
    print("2. 检查生产环境AI服务配置（扣子站点URL/Token、DeepSeek API Key）")
    print("3. 根据用户需求决定是否恢复原来的兜底提示")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
从日志中提取AI分析返回的完整结果
"""
import json
import re

# 从日志中提取的result_json内容（已解码）
result_json_str = '''{"risk_score": 65, "high_risk_items": [{"category": "漏项", "item": "防水工程", "description": "报价单中未包含防水工程，但卫生间、厨房等区域必须进行防水处理，否则可能导致漏水问题", "impact": "可能导致漏水，损坏楼下邻居，造成重大经济损失和邻里纠纷", "suggestion": "补充防水工程，明确防水区域、防水材料和施工工艺"}], "warning_items": [{"category": "模糊表述", "item": "水电改造工程", "description": "仅给出了总价，未详细说明水电改造的具体内容、材料品牌、型号、材质等详细信息", "suggestion": "补充材料品牌、型号、材质等详细信息，确保材料质量可控"}], "missing_items": [{"item": "防水工程", "importance": "高", "reason": "卫生间、厨房等区域必须进行防水保护，可避免损坏，减少修复成本和纠纷"}], "overpriced_items": [{"item": "管理费", "quoted_price": 5000, "market_ref_price": "2400-4000元（按总报价80000元，3%-5%计算，89㎡住宅装修）", "price_diff": "报价高于市场参考价500-1000元"}], "total_price": 80000, "market_ref_price": "65000-75000元（参考深圳中档半包装修市场行情，结合项目明细，原报价部分项目价格虚高且存在漏项，合理价格应在此范围）", "suggestions": ["补充防水工程，明确防水区域、防水材料和施工工艺", "补充各材料项目的品牌和型号信息，确保材料质量可控", "重新核算管理费，参考市场常规比例调整价格", "补充各施工项目的施工工艺说明", "补充各材料项目的品牌和型号信息，确保材料质量可控"]}'''

try:
    result = json.loads(result_json_str)
    print("=" * 80)
    print("AI分析返回的完整结果")
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("关键信息提取")
    print("=" * 80)
    print(f"风险评分: {result.get('risk_score')}")
    print(f"\n高风险项数量: {len(result.get('high_risk_items', []))}")
    for i, item in enumerate(result.get('high_risk_items', []), 1):
        print(f"  {i}. {item.get('category')} - {item.get('item')}")
        print(f"     描述: {item.get('description')}")
        print(f"     影响: {item.get('impact')}")
        print(f"     建议: {item.get('suggestion')}")
    
    print(f"\n警告项数量: {len(result.get('warning_items', []))}")
    for i, item in enumerate(result.get('warning_items', []), 1):
        print(f"  {i}. {item.get('category')} - {item.get('item')}")
        print(f"     描述: {item.get('description')}")
        print(f"     建议: {item.get('suggestion')}")
    
    print(f"\n漏项数量: {len(result.get('missing_items', []))}")
    for i, item in enumerate(result.get('missing_items', []), 1):
        print(f"  {i}. {item.get('item')} (重要性: {item.get('importance')})")
        print(f"     原因: {item.get('reason')}")
    
    print(f"\n虚高项数量: {len(result.get('overpriced_items', []))}")
    for i, item in enumerate(result.get('overpriced_items', []), 1):
        print(f"  {i}. {item.get('item')}")
        print(f"     报价: {item.get('quoted_price')}元")
        print(f"     市场参考价: {item.get('market_ref_price')}")
        print(f"     差异: {item.get('price_diff')}")
    
    print(f"\n总价: {result.get('total_price')}元")
    print(f"市场参考总价: {result.get('market_ref_price')}")
    
    print(f"\n总体建议:")
    for i, suggestion in enumerate(result.get('suggestions', []), 1):
        print(f"  {i}. {suggestion}")
        
except json.JSONDecodeError as e:
    print(f"JSON解析失败: {e}")

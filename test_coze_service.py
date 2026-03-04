#!/usr/bin/env python3
"""
测试扣子智能体服务
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.coze_service import CozeService

async def test_coze_service():
    """测试扣子智能体服务"""
    print("测试扣子智能体服务...")
    
    try:
        # 创建服务实例
        coze_service = CozeService()
        
        # 测试报价单分析
        print("1. 测试报价单分析...")
        test_image_url = "https://zhuangxiu-agent-dev.oss-cn-hangzhou.aliyuncs.com/test_quote_pdf.pdf"
        
        # 模拟分析
        result = await coze_service.analyze_quote(test_image_url, user_id=1)
        
        if result:
            print(f"✅ 扣子智能体分析成功！")
            print(f"分析结果类型: {type(result)}")
            print(f"分析结果键: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
            
            # 检查关键字段
            if isinstance(result, dict):
                print(f"风险评分: {result.get('risk_score', 'N/A')}")
                print(f"总价: {result.get('total_price', 'N/A')}")
                print(f"市场参考价: {result.get('market_ref_price', 'N/A')}")
                print(f"高风险项目数量: {len(result.get('high_risk_items', []))}")
                print(f"警告项目数量: {len(result.get('warning_items', []))}")
                print(f"缺失项目数量: {len(result.get('missing_items', []))}")
                print(f"价格过高项目数量: {len(result.get('overpriced_items', []))}")
                
                # 检查是否有建议
                suggestions = result.get('suggestions', [])
                if suggestions:
                    print(f"建议数量: {len(suggestions)}")
                    print(f"第一条建议: {suggestions[0][:100]}...")
                
                # 检查是否有原始文本
                if 'raw_text' in result:
                    print(f"原始文本长度: {len(result['raw_text'])} 字符")
                    print(f"原始文本预览: {result['raw_text'][:200]}...")
            
            return True
        else:
            print("❌ 扣子智能体分析返回空结果")
            return False
            
    except Exception as e:
        print(f"❌ 测试扣子智能体服务失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    
    print("=" * 60)
    print("开始测试扣子智能体服务")
    print("=" * 60)
    
    success = asyncio.run(test_coze_service())
    
    print("\n" + "=" * 60)
    print(f"测试结果: {'✅ 成功' if success else '❌ 失败'}")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

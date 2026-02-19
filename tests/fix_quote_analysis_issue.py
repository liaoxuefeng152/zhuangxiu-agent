#!/usr/bin/env python3
"""
修复报价单分析问题 - 提供解决方案
"""
import os
import sys
import json

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))

def analyze_problem():
    """分析问题原因"""
    print("=== 报价单AI分析失败问题分析 ===")
    print("\n1. 问题现象:")
    print("   - 用户报告：报价单上传，AI分析失败")
    print("   - 测试结果：AI分析返回兜底结果 'AI分析服务暂时不可用，请稍后重试'")
    
    print("\n2. 根本原因:")
    print("   - 扣子API返回错误代码 4200: Bot ID不存在")
    print("   - 扣子API返回错误代码 4015: Bot未发布到Agent As API频道")
    print("   - Bot ID: 7603691852046368804 (COZE_SUPERVISOR_BOT_ID)")
    print("   - 问题：AI监理智能体未正确配置或未发布")
    
    print("\n3. 当前配置状态:")
    print("   - COZE_API_TOKEN: 已配置")
    print("   - COZE_SUPERVISOR_BOT_ID: 已配置 (7603691852046368804)")
    print("   - DEEPSEEK_API_KEY: 未配置 (无备用方案)")
    
    print("\n4. 问题归属:")
    print("   ✅ 这是**后台问题**")
    print("   - 原因：AI分析服务（扣子API）配置问题")
    print("   - 影响：报价单、合同、验收等所有AI分析功能")
    print("   - 需要：修复扣子智能体配置或配置备用AI服务")

def provide_solutions():
    """提供解决方案"""
    print("\n=== 解决方案 ===")
    
    print("\n方案一：修复扣子智能体配置（推荐）")
    print("1. 登录扣子平台 (https://www.coze.cn)")
    print("2. 找到智能体 ID: 7603691852046368804")
    print("3. 检查智能体是否已发布到 'Agent As API' 频道")
    print("4. 如果未发布，按照文档发布：https://www.coze.cn/docs/guides")
    print("5. 更新后的步骤：")
    print("   - 发布智能体到API频道")
    print("   - 获取正确的Bot ID（如果需要）")
    print("   - 更新.env文件中的COZE_SUPERVISOR_BOT_ID")
    print("   - 重启后端服务")
    
    print("\n方案二：配置DeepSeek作为备用方案")
    print("1. 获取DeepSeek API Key (https://platform.deepseek.com/api_keys)")
    print("2. 在.env文件中添加配置:")
    print("   DEEPSEEK_API_KEY=your_deepseek_api_key_here")
    print("3. 风险分析服务会自动降级使用DeepSeek")
    print("4. 重启后端服务")
    
    print("\n方案三：临时修复 - 使用模拟AI分析")
    print("1. 修改风险分析服务，在开发环境返回模拟数据")
    print("2. 确保前端能显示分析结果（即使是模拟数据）")
    print("3. 不影响用户体验，同时修复扣子配置")

def create_temp_fix():
    """创建临时修复方案"""
    print("\n=== 临时修复方案 ===")
    
    # 检查风险分析服务文件
    risk_analyzer_path = os.path.join(ROOT, "backend/app/services/risk_analyzer.py")
    
    if not os.path.exists(risk_analyzer_path):
        print(f"❌ 找不到风险分析服务文件: {risk_analyzer_path}")
        return False
    
    print(f"✅ 找到风险分析服务文件: {risk_analyzer_path}")
    
    # 读取文件内容
    with open(risk_analyzer_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经有模拟数据逻辑
    if "开发环境模拟数据" in content or "DEBUG_MOCK_AI" in content:
        print("✅ 文件中已包含模拟数据逻辑")
        return True
    
    print("⚠️  文件中未包含模拟数据逻辑，建议添加以下代码:")
    
    mock_code = '''
    # 开发环境模拟数据 - 临时修复扣子API问题
    def _get_mock_quote_analysis(self, ocr_text: str, total_price: float = None) -> Dict[str, Any]:
        """开发环境：返回模拟的报价单分析结果"""
        import random
        import re
        
        # 从OCR文本中提取一些信息
        materials = []
        if "水电" in ocr_text:
            materials.append("水电改造材料")
        if "瓷砖" in ocr_text or "地砖" in ocr_text:
            materials.append("瓷砖材料")
        if "油漆" in ocr_text or "乳胶漆" in ocr_text:
            materials.append("油漆材料")
        if "吊顶" in ocr_text:
            materials.append("吊顶材料")
        
        # 模拟风险分析
        risk_score = random.randint(30, 70)  # 30-70分风险
        
        high_risk_items = []
        warning_items = []
        missing_items = []
        overpriced_items = []
        
        if risk_score > 60:
            high_risk_items = [{
                "category": "价格虚高",
                "item": "水电改造",
                "description": "120元/米高于市场价100元/米",
                "impact": "可能多支付1600元",
                "suggestion": "协商降价至100元/米"
            }]
        
        if risk_score > 40:
            warning_items = [{
                "category": "漏项风险",
                "item": "防水工程",
                "description": "报价单中未明确防水工程",
                "suggestion": "要求补充防水工程明细"
            }]
        
        # 模拟市场参考价（总价的±20%）
        if total_price:
            market_min = total_price * 0.8
            market_max = total_price * 1.2
            market_ref_price = f"{market_min:.0f}-{market_max:.0f}元"
        else:
            market_ref_price = None
        
        return {
            "risk_score": risk_score,
            "high_risk_items": high_risk_items,
            "warning_items": warning_items,
            "missing_items": missing_items,
            "overpriced_items": overpriced_items,
            "total_price": total_price,
            "market_ref_price": market_ref_price,
            "suggestions": [
                "建议与装修公司明确所有施工细节",
                "要求提供材料品牌和型号",
                "分期付款，按进度支付"
            ]
        }
    
    # 然后在 analyze_quote 方法中添加
    # 在 try 块开始处添加：
    # if hasattr(settings, 'DEBUG') and settings.DEBUG:
    #     return self._get_mock_quote_analysis(ocr_text, total_price)
    '''
    
    print(mock_code)
    print("\n⚠️  注意：这只是临时解决方案，最终需要修复扣子API配置")
    
    return True

def check_backend_logs():
    """检查后端日志"""
    print("\n=== 检查后端日志 ===")
    
    log_path = os.path.join(ROOT, "logs/app-dev.log")
    
    if os.path.exists(log_path):
        print(f"✅ 找到日志文件: {log_path}")
        
        # 读取最后几行日志
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_lines = lines[-20:] if len(lines) > 20 else lines
            
            print("\n最近日志（最后20行）:")
            for line in last_lines:
                if "coze" in line.lower() or "扣子" in line.lower() or "ai" in line.lower():
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"❌ 读取日志失败: {e}")
    else:
        print(f"❌ 日志文件不存在: {log_path}")

def main():
    """主函数"""
    print("报价单AI分析问题诊断与修复方案")
    print("=" * 60)
    
    # 分析问题
    analyze_problem()
    
    # 检查日志
    check_backend_logs()
    
    # 提供解决方案
    provide_solutions()
    
    # 创建临时修复
    create_temp_fix()
    
    print("\n" + "=" * 60)
    print("执行步骤总结:")
    print("\n1. 立即措施:")
    print("   - 确认这是**后台问题**")
    print("   - 通知开发团队修复扣子智能体配置")
    
    print("\n2. 短期修复（1-2天）:")
    print("   - 方案一：修复扣子智能体发布配置")
    print("   - 方案二：配置DeepSeek作为备用")
    
    print("\n3. 长期建议:")
    print("   - 配置多个AI服务提供商（扣子、DeepSeek、OpenAI等）")
    print("   - 实现AI服务健康检查和自动切换")
    print("   - 添加更完善的错误监控和告警")
    
    print("\n4. 部署要求:")
    print("   - 修改后台代码后需要更新到阿里云")
    print("   - 执行: git push → SSH到服务器 → git pull → 重启后端")
    print("   - SSH命令: ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
简单测试报价单分析功能
直接调用后端API测试报价单上传和分析
"""
import os
import sys
import json
import httpx
import time

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "http://127.0.0.1:8001/api/v1"  # 本地开发环境

def test_quote_analysis():
    """测试报价单分析功能"""
    print("=== 开始测试报价单分析功能 ===")
    
    # 1. 用户登录
    print("\n1. 用户登录...")
    try:
        response = httpx.post(
            f"{BASE_URL}/users/login",
            json={"code": "dev_h5_mock"},
            timeout=15.0
        )
        if response.status_code != 200:
            print(f"登录失败: {response.status_code}")
            print(response.text[:300])
            return False
            
        data = response.json()
        token = data.get("access_token") or (data.get("data") or {}).get("access_token")
        if not token:
            print("登录响应中无 access_token:", data)
            return False
            
        print(f"登录成功，token: {token[:20]}...")
        
    except Exception as e:
        print(f"登录请求异常: {e}")
        return False
    
    # 2. 创建模拟的报价单文本
    print("\n2. 准备模拟报价单文本...")
    quote_text = """
装修报价单

项目名称：深圳住宅装修测试（89㎡三室一厅）
装修类型：半包装修
品质等级：中档品质

项目明细：
1. 水电改造工程
   - 强电改造：120元/米，共80米，合计：9600元
   - 弱电改造：80元/米，共50米，合计：4000元
   - 水路改造：150元/米，共60米，合计：9000元
   小计：22600元

2. 泥工工程
   - 地面找平：45元/㎡，共89㎡，合计：4005元
   - 墙砖铺贴：65元/㎡，共120㎡，合计：7800元
   - 地砖铺贴：55元/㎡，共89㎡，合计：4895元
   小计：16700元

3. 木工工程
   - 吊顶：120元/㎡，共60㎡，合计：7200元
   - 定制柜体：800元/延米，共15延米，合计：12000元
   小计：19200元

4. 油漆工程
   - 墙面乳胶漆：35元/㎡，共280㎡，合计：9800元
   - 木器漆：80元/㎡，共40㎡，合计：3200元
   小计：13000元

5. 其他费用
   - 垃圾清运费：2000元
   - 材料运输费：1500元
   - 管理费：5000元
   小计：8500元

总计：80000元

备注：以上价格不含主材，主材由业主自行采购。
"""
    
    # 3. 直接测试AI分析（绕过OCR）
    print("\n3. 直接测试AI分析服务...")
    try:
        # 首先检查是否有/dev/analyze-quote-text接口
        response = httpx.post(
            f"{BASE_URL}/dev/analyze-quote-text",
            json={"text": quote_text, "total_price": 80000.0},
            headers={"Authorization": f"Bearer {token}"},
            timeout=120.0
        )
        
        if response.status_code == 404:
            print("开发接口不存在，尝试直接调用风险分析服务...")
            # 直接导入并测试风险分析服务
            return test_risk_analyzer_directly(quote_text, 80000.0)
        elif response.status_code != 200:
            print(f"AI分析请求失败: {response.status_code}")
            print(response.text[:500])
            return False
            
        result = response.json()
        print("\nAI分析结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 检查是否返回了兜底结果
        suggestions = result.get("suggestions", [])
        if suggestions and "AI分析服务暂时不可用" in suggestions[0]:
            print("\n⚠️  AI分析返回了兜底结果，服务可能不可用")
            return False
            
        print(f"\n✅ AI分析成功，风险评分: {result.get('risk_score', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"AI分析测试异常: {e}")
        return False

def test_risk_analyzer_directly(quote_text, total_price):
    """直接测试风险分析服务"""
    print("\n直接测试风险分析服务...")
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    
    try:
        from app.services.risk_analyzer import risk_analyzer_service
        import asyncio
        
        # 创建异步任务
        async def analyze():
            return await risk_analyzer_service.analyze_quote(quote_text, total_price)
        
        result = asyncio.run(analyze())
        
        print("\n直接调用风险分析结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 检查是否返回了兜底结果
        suggestions = result.get("suggestions", [])
        if suggestions and "AI分析服务暂时不可用" in suggestions[0]:
            print("\n⚠️  风险分析服务返回了兜底结果")
            return False
            
        print(f"\n✅ 直接调用成功，风险评分: {result.get('risk_score', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"直接调用风险分析服务异常: {e}")
        return False

def test_coze_api_connection():
    """测试扣子API连接"""
    print("\n=== 测试扣子API连接 ===")
    
    # 读取.env文件获取配置
    env_path = os.path.join(ROOT, ".env")
    if not os.path.exists(env_path):
        print(f"找不到.env文件: {env_path}")
        return False
    
    config = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    coze_token = config.get("COZE_API_TOKEN")
    coze_bot_id = config.get("COZE_SUPERVISOR_BOT_ID") or config.get("COZE_BOT_ID")
    
    if not coze_token:
        print("❌ 未配置COZE_API_TOKEN")
        return False
    
    if not coze_bot_id:
        print("❌ 未配置COZE_SUPERVISOR_BOT_ID或COZE_BOT_ID")
        return False
    
    print(f"✅ 找到扣子配置:")
    print(f"   Token: {coze_token[:20]}...")
    print(f"   Bot ID: {coze_bot_id}")
    
    # 测试网络连接
    print("\n测试扣子API网络连接...")
    try:
        response = httpx.get("https://api.coze.cn", timeout=10.0)
        print(f"✅ 扣子API域名可访问，状态码: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 扣子API网络连接失败: {e}")
        return False

def main():
    """主函数"""
    print("装修报价单AI分析功能测试")
    print("=" * 50)
    
    # 测试扣子API连接
    if not test_coze_api_connection():
        print("\n⚠️  扣子API连接测试失败，可能影响AI分析功能")
    
    # 测试报价单分析
    print("\n" + "=" * 50)
    success = test_quote_analysis()
    
    if success:
        print("\n✅ 报价单分析功能测试通过")
    else:
        print("\n❌ 报价单分析功能测试失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

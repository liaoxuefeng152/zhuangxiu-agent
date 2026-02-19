#!/usr/bin/env python3
"""
检查配置读取
"""
import os
import sys

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))

def check_config():
    """检查配置读取"""
    print("=== 检查配置读取 ===")
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.join(ROOT, "backend"))
    
    try:
        from app.core.config import settings
        
        print("\n1. 扣子配置:")
        print(f"   COZE_API_TOKEN: '{getattr(settings, 'COZE_API_TOKEN', '')}'")
        print(f"   COZE_BOT_ID: '{getattr(settings, 'COZE_BOT_ID', '')}'")
        print(f"   COZE_SUPERVISOR_BOT_ID: '{getattr(settings, 'COZE_SUPERVISOR_BOT_ID', '')}'")
        print(f"   COZE_SITE_URL: '{getattr(settings, 'COZE_SITE_URL', '')}'")
        print(f"   COZE_SITE_TOKEN: '{getattr(settings, 'COZE_SITE_TOKEN', '')}'")
        print(f"   COZE_PROJECT_ID: '{getattr(settings, 'COZE_PROJECT_ID', '')}'")
        print(f"   DEEPSEEK_API_KEY: '{getattr(settings, 'DEEPSEEK_API_KEY', '')}'")
        
        print("\n2. 检查是否为空:")
        print(f"   COZE_SITE_URL为空: {not bool(getattr(settings, 'COZE_SITE_URL', '').strip())}")
        print(f"   COZE_SITE_TOKEN为空: {not bool(getattr(settings, 'COZE_SITE_TOKEN', '').strip())}")
        
        print("\n3. 检查_use_coze_site()逻辑:")
        url = getattr(settings, "COZE_SITE_URL", None) or ""
        token = getattr(settings, "COZE_SITE_TOKEN", None) or ""
        print(f"   url.strip(): '{url.strip()}'")
        print(f"   token.strip(): '{token.strip()}'")
        print(f"   bool(url.strip() and token.strip()): {bool(url.strip() and token.strip())}")
        
        # 检查risk_analyzer中的函数
        from app.services.risk_analyzer import _use_coze_site
        print(f"\n4. _use_coze_site()结果: {_use_coze_site()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("配置检查")
    print("=" * 50)
    
    success = check_config()
    
    if success:
        print("\n✅ 配置检查完成")
    else:
        print("\n❌ 配置检查失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

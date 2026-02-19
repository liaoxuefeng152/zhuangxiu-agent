#!/usr/bin/env python3
"""
直接测试扣子站点API
"""
import os
import sys
import json
import asyncio
import httpx

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))

async def test_coze_site_directly():
    """直接测试扣子站点API"""
    print("=== 直接测试扣子站点API ===")
    
    # 读取.env文件获取配置
    env_path = os.path.join(ROOT, ".env")
    if not os.path.exists(env_path):
        print(f"❌ 找不到.env文件: {env_path}")
        return False
    
    config = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    coze_site_url = config.get("COZE_SITE_URL", "").rstrip("/")
    coze_site_token = config.get("COZE_SITE_TOKEN", "")
    coze_project_id = config.get("COZE_PROJECT_ID", "")
    
    if not coze_site_url:
        print("❌ 未配置COZE_SITE_URL")
        return False
    
    if not coze_site_token:
        print("❌ 未配置COZE_SITE_TOKEN")
        return False
    
    print(f"✅ 找到扣子站点配置:")
    print(f"   URL: {coze_site_url}")
    print(f"   Token: {coze_site_token[:50]}...")
    print(f"   Project ID: {coze_project_id}")
    
    # 测试扣子站点API
    print("\n测试扣子站点API...")
    
    headers = {
        "Authorization": f"Bearer {coze_site_token}",
        "Content-Type": "application/json",
    }
    
    # 准备测试数据
    system_prompt = "你是一位专业的装修报价审核专家，拥有10年以上的装修行业经验。请对用户提供的装修报价单进行分析，识别其中的风险项。"
    user_content = "请分析以下装修报价单，总价：80000元\n\n报价单内容：\n测试报价单"
    combined = f"【系统要求】\n{system_prompt}\n\n【用户输入】\n{user_content}"
    
    session_id = f"decoration-test-{int(asyncio.get_event_loop().time() * 1000)}"
    payload = {
        "content": {
            "query": {
                "prompt": [
                    {"type": "text", "content": {"text": combined}}
                ]
            }
        },
        "type": "query",
        "session_id": session_id,
    }
    
    if coze_project_id:
        try:
            payload["project_id"] = int(coze_project_id) if coze_project_id.isdigit() else coze_project_id
        except:
            payload["project_id"] = coze_project_id
    
    url = f"{coze_site_url}"
    print(f"请求URL: {url}")
    print(f"请求头Authorization: Bearer {coze_site_token[:20]}...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("发送请求...")
            response = await client.post(
                url,
                headers=headers,
                json=payload
            )
        
        print(f"扣子站点API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 尝试解析响应
            try:
                # 扣子站点返回的是流式响应，每行以"data: "开头
                lines = response.text.strip().split('\n')
                print(f"收到 {len(lines)} 行响应")
                
                # 提取有效数据
                data_lines = []
                for line in lines:
                    line = line.strip()
                    if line.startswith("data: "):
                        data = line[6:]  # 去掉"data: "前缀
                        if data and data != "[DONE]":
                            data_lines.append(data)
                
                print(f"提取到 {len(data_lines)} 条数据消息")
                
                if data_lines:
                    # 解析第一条数据
                    try:
                        first_data = json.loads(data_lines[0])
                        print(f"第一条数据: {json.dumps(first_data, ensure_ascii=False, indent=2)[:500]}...")
                        
                        # 检查是否有错误
                        if "error" in first_data:
                            print(f"❌ 扣子站点API返回错误: {first_data['error']}")
                            return False
                        
                        print("✅ 扣子站点API连接成功！")
                        return True
                    except json.JSONDecodeError as e:
                        print(f"❌ 解析JSON失败: {e}")
                        print(f"原始数据: {data_lines[0][:200]}")
                else:
                    print("❌ 未收到有效数据消息")
                    print(f"原始响应前500字符: {response.text[:500]}")
                    
            except Exception as e:
                print(f"❌ 解析响应失败: {e}")
                print(f"响应内容前500字符: {response.text[:500]}")
        else:
            print(f"❌ 扣子站点API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
            # 检查常见错误
            if response.status_code == 401:
                print("⚠️  错误401: Token无效或过期")
            elif response.status_code == 404:
                print("⚠️  错误404: 端点不存在，请检查URL是否正确")
            elif response.status_code == 400:
                print("⚠️  错误400: 请求参数错误")
                
        return False
            
    except httpx.ConnectError as e:
        print(f"❌ 连接错误: {e}")
        print("⚠️  可能原因: 网络问题、URL错误、服务器不可达")
        return False
    except httpx.TimeoutException as e:
        print(f"❌ 请求超时: {e}")
        print("⚠️  可能原因: 网络慢、服务器响应慢、超时时间太短")
        return False
    except Exception as e:
        print(f"❌ 扣子站点API测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("扣子站点API直接测试")
    print("=" * 50)
    
    success = asyncio.run(test_coze_site_directly())
    
    if success:
        print("\n✅ 扣子站点API连接正常")
    else:
        print("\n❌ 扣子站点API连接失败")
        print("\n建议解决方案:")
        print("1. 检查扣子智能体是否已正确发布到站点")
        print("2. 验证站点URL是否正确")
        print("3. 检查Token是否有效（可能已过期）")
        print("4. 尝试使用扣子开放平台API方式")
        print("5. 配置DeepSeek作为备用方案")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

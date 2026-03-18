#!/usr/bin/env python3
"""
测试报价单分析功能完整流程
"""
import asyncio
import httpx
import json
import sys
import os

# 测试配置
BASE_URL = "http://120.26.201.61:8000"
USER_ID = 1  # 使用测试用户ID
TEST_IMAGE_PATH = "test_quote.jpg"

async def test_quote_analysis():
    """测试报价单分析完整流程"""
    print("=== 开始测试报价单分析功能 ===")
    
    # 1. 首先测试API是否可访问
    print("\n1. 测试API健康检查...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            print(f"  健康检查状态: {response.status_code}")
            if response.status_code == 200:
                print("  ✅ API服务正常")
            else:
                print(f"  ❌ API服务异常: {response.text}")
                return False
    except Exception as e:
        print(f"  ❌ API连接失败: {e}")
        return False
    
    # 2. 测试报价单上传
    print("\n2. 测试报价单上传...")
    try:
        # 创建测试图片文件
        if not os.path.exists(TEST_IMAGE_PATH):
            print(f"  创建测试图片文件: {TEST_IMAGE_PATH}")
            with open(TEST_IMAGE_PATH, "wb") as f:
                f.write(b"Fake image data for testing")
        
        # 上传文件
        files = {"file": ("test_quote.jpg", open(TEST_IMAGE_PATH, "rb"), "image/jpeg")}
        headers = {"X-User-ID": str(USER_ID)}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/quotes/upload",
                files=files,
                headers=headers
            )
            
            print(f"  上传响应状态: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ 上传成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
                quote_id = result.get("task_id")
                if quote_id:
                    print(f"  报价单ID: {quote_id}")
                    return quote_id
                else:
                    print("  ❌ 未获取到报价单ID")
                    return False
            else:
                print(f"  ❌ 上传失败: {response.text}")
                return False
                
    except Exception as e:
        print(f"  ❌ 上传异常: {e}")
        return False
    
async def check_analysis_result(quote_id):
    """检查分析结果"""
    print(f"\n3. 检查报价单分析结果 (ID: {quote_id})...")
    
    try:
        headers = {"X-User-ID": str(USER_ID)}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 等待分析完成，最多等待120秒
            max_wait = 120
            wait_interval = 5
            
            for attempt in range(max_wait // wait_interval):
                print(f"  第{attempt + 1}次检查...")
                
                response = await client.get(
                    f"{BASE_URL}/api/v1/quotes/quote/{quote_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status")
                    progress = result.get("analysis_progress", {})
                    
                    print(f"    状态: {status}")
                    if progress:
                        print(f"    进度: {progress.get('step')} - {progress.get('progress')}% - {progress.get('message')}")
                    
                    if status == "completed":
                        print(f"  ✅ 分析完成!")
                        print(f"    风险评分: {result.get('risk_score')}")
                        print(f"    总价: {result.get('total_price')}")
                        print(f"    是否解锁: {result.get('is_unlocked')}")
                        
                        # 打印详细结果
                        result_json = result.get("result_json")
                        if result_json:
                            print(f"    AI分析结果类型: {type(result_json)}")
                            if isinstance(result_json, dict):
                                print(f"    AI分析结果字段: {list(result_json.keys())}")
                                # 检查是否是兜底数据
                                if result_json.get("is_fallback"):
                                    print("    ⚠️ 注意: 返回的是兜底数据，AI分析可能失败")
                                if result_json.get("error_code"):
                                    print(f"    ⚠️ 错误代码: {result_json.get('error_code')}")
                        
                        return True
                    elif status == "failed":
                        print(f"  ❌ 分析失败")
                        print(f"    失败原因: {progress.get('message') if progress else '未知'}")
                        return False
                    elif status == "analyzing":
                        # 继续等待
                        await asyncio.sleep(wait_interval)
                    else:
                        print(f"  ⚠️ 未知状态: {status}")
                        await asyncio.sleep(wait_interval)
                else:
                    print(f"  ❌ 获取结果失败: {response.status_code} - {response.text}")
                    return False
            
            print(f"  ⚠️ 分析超时 (等待{max_wait}秒)")
            return False
            
    except Exception as e:
        print(f"  ❌ 检查结果异常: {e}")
        return False

async def test_direct_coze_api():
    """直接测试扣子API"""
    print("\n=== 直接测试扣子API ===")
    
    # 使用生产环境配置中的扣子站点配置
    site_url = "https://9n37hmztzw.coze.site"
    site_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImIxYmFkYTkxLTYyMjctNDAyYi1iZTMwLTU4ZTMxODQzYjJjYiJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbImhEbENJemNqZk83V1ZyTG5IblJlNjRQR05NOGJjbnUxIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzcyNjc1MzM2LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjAzNzA5MTg3MjY5NjA3NDYwIiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjEzNTgyNTk0OTEwNzE1OTEzIn0.HfN-fqpyZiVyDS_8RndLNgcmmcwhY6kGbHAeuidFOTDGhLXFVdPuf1WrEhd_zYzbjL2SXbx8Gg6acaUu8FQCJDQQQd46NeY_NoIQQti1Gh5ZXVry7K6qtxCLxkX46MzTZ_sP1PkqzgCRMFJMjLKZ3wAEBkALLxkR82uzdjYUoiRz6pFhm6Rhvwtk-3cxLFmwr5w6vfeRFCBQyBcti_Uks8JaKjp6nvqg_cseYmVrtym2Sp0bcDFUQx5F2ft6qm-4g0cT-n2DCFSyWaEVl_lvf09NQU43gU6ucDOpwDU4gduDss1en-OMfWIEfa7-u9_gXTn2AcQvwpNb7U4ZzCH7zg"
    project_id = "7603691852046368804"
    
    # 构建测试图片URL（使用一个公开的测试图片）
    test_image_url = "https://img.alicdn.com/imgextra/i4/O1CN01Z5p5LZ1M1J5Q6X8q5_!!6000000001378-2-tps-800-600.png"
    
    # 构建提示词
    prompt = """【重要指令】请分析这份装修报价单图片，返回JSON格式的结构化数据。

【明确要求】
1. 这是装修报价单图片，不是合同图片
2. 请分析报价单中的价格、项目、材料等信息
3. 返回纯JSON格式，不要包含其他任何文本

【必需字段】
{
  "total_price": 85000.00,
  "risk_score": 65,
  "high_risk_items": [
    {"name": "水电改造", "reason": "单价过高，超出市场价30%"}
  ],
  "warning_items": [
    {"name": "墙面处理", "reason": "材料规格不明确"}
  ],
  "missing_items": [
    {"name": "垃圾清运费", "suggestion": "建议明确包含在总价中"}
  ],
  "overpriced_items": [
    {"name": "水电改造", "current_price": "15000", "market_price": "10000", "reason": "单价过高"}
  ],
  "market_ref_price": "80000-90000",
  "suggestions": ["建议明确材料品牌和规格", "建议增加质保条款", "建议明确付款方式"],
  "summary": "报价单存在中等风险，主要问题是水电改造单价过高和材料规格不明确。"
}

【特别注意】
- 不要返回工具调用说明或函数调用格式
- 不要返回合同分析格式
- 直接返回JSON对象，不要用```json```包裹"""

    try:
        print("  调用扣子站点API...")
        
        # 构建请求数据
        api_url = f"{site_url.rstrip('/')}/stream_run"
        combined_prompt = f"{prompt}\n\n图片URL: {test_image_url}"
        
        data = {
            "content": {
                "query": {
                    "prompt": [
                        {
                            "type": "text",
                            "content": {
                                "text": combined_prompt
                            }
                        }
                    ]
                }
            },
            "type": "query",
            "session_id": f"session_test_{USER_ID}",
            "project_id": project_id,
            "config": {"recursion_limit": 25},
        }

        headers = {
            "Authorization": f"Bearer {site_token}",
            "Content-Type": "application/json"
        }

        # 处理流式响应
        async def _do_stream():
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", api_url, json=data, headers=headers) as response:
                    response.raise_for_status()
                    
                    chunks = []
                    async for line in response.aiter_lines():
                        line = (line or "").strip()
                        if not line or line == "data: [DONE]":
                            continue
                        if not line.startswith("data:"):
                            continue
                        json_str = line[5:].strip()
                        try:
                            data_chunk = json.loads(json_str)
                            # 提取内容
                            content = extract_content_from_stream(data_chunk)
                            if content:
                                chunks.append(content)
                        except json.JSONDecodeError:
                            continue
                    
                    full_content = "".join(chunks).strip()
                    return full_content if full_content else None

        def extract_content_from_stream(data_chunk):
            """从流式响应数据块中提取内容"""
            try:
                # 检查是否是事件类型消息
                event_type = data_chunk.get("type") or data_chunk.get("event") or ""
                if isinstance(event_type, str) and event_type.lower() in (
                    "message_start", "message_end", "ping", "session", "session.created", 
                    "conversation.message.created", "ping", "heartbeat", "done"
                ):
                    return None
                
                # 检查各个可能的字段
                for field in ["answer", "text", "output", "content", "delta"]:
                    value = data_chunk.get(field)
                    if isinstance(value, str) and value.strip():
                        return value.strip()
                    elif isinstance(value, dict):
                        # 如果是字典，递归检查
                        for sub_field in ["answer", "text", "content"]:
                            sub_value = value.get(sub_field)
                            if isinstance(sub_value, str) and sub_value.strip():
                                return sub_value.strip()
                
                return None
            except Exception:
                return None

        # 调用流式处理函数
        result_text = await _do_stream()
        
        if result_text:
            print(f"  ✅ 扣子API调用成功")
            print(f"  响应长度: {len(result_text)} 字符")
            print(f"  响应前200字符: {result_text[:200]}...")
            
            # 尝试解析JSON
            try:
                result_data = json.loads(result_text)
                print(f"  ✅ 成功解析为JSON")
                print(f"  JSON字段: {list(result_data.keys())}")
                
                # 检查是否是工具调用说明
                if "name" in result_data or "function_name" in result_data:
                    print("  ⚠️ 注意: 返回的是工具调用说明，不是分析结果")
                    return False
                
                # 检查是否是报价单分析结果
                if "total_price" in result_data or "risk_score" in result_data:
                    print("  ✅ 返回的是报价单分析结果")
                    return True
                else:
                    print(f"  ⚠️ 返回的不是标准报价单格式")
                    return False
                    
            except json.JSONDecodeError:
                print(f"  ❌ 响应不是有效的JSON格式")
                # 检查是否包含工具调用关键词
                if "analyze_contract_quote" in result_text or "tool_call" in result_text:
                    print("  ⚠️ 响应包含工具调用关键词")
                return False
        else:
            print("  ❌ 扣子API返回空响应")
            return False
            
    except httpx.TimeoutException:
        print("  ❌ 扣子API调用超时")
        return False
    except httpx.HTTPStatusError as e:
        print(f"  ❌ 扣子API HTTP错误: {e.response.status_code}")
        if e.response.status_code >= 500:
            print(f"    响应内容: {e.response.text[:200]}...")
        return False
    except Exception as e:
        print(f"  ❌ 扣子API调用异常: {e}")
        return False

async def main():
    """主函数"""
    print("=" * 60)
    print("装修决策Agent - 报价单分析功能测试")
    print("=" * 60)
    
    # 测试1: 直接测试扣子API
    coze_ok = await test_direct_coze_api()
    
    if not coze_ok:
        print("\n⚠️ 扣子API测试失败，可能的问题:")
        print("  1. 扣子站点配置错误")
        print("  2. 扣子站点令牌过期")
        print("  3. 扣子智能体工作流异常")
        print("  4. 网络连接问题")
    
    # 测试2: 完整流程测试
    print("\n" + "=" * 60)
    print("开始完整流程测试...")
    
    quote_id = await test_quote_analysis()
    if quote_id:
        result = await check_analysis_result(quote_id)
        if result:
            print("\n✅ 报价单分析功能测试通过!")
        else:
            print("\n❌ 报价单分析功能测试失败!")
    else:
        print("\n❌ 报价单上传测试失败!")
    
    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    asyncio.run(main())

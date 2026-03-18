#!/usr/bin/env python3
"""
测试生产环境的报价单分析功能
"""
import httpx
import json
import time

def test_production_quote_analysis():
    """测试生产环境的报价单分析功能"""
    print("=== 测试生产环境报价单分析功能 ===")
    
    # 生产环境API地址 - 后端服务运行在8000端口
    upload_url = "http://120.26.201.61:8000/api/v1/quotes/upload"
    
    # 使用本地测试图片文件
    test_image_path = "test_quote.jpg"
    
    # 检查测试图片是否存在
    import os
    if not os.path.exists(test_image_path):
        print(f"❌ 测试图片不存在: {test_image_path}")
        print("请确保test_quote.jpg文件存在")
        return
    
    print(f"发送请求到生产环境API: {upload_url}")
    print(f"使用测试图片: {test_image_path}")
    
    try:
        # 读取图片文件
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        
        # 准备文件上传
        files = {
            "file": ("test_quote.jpg", image_data, "image/jpeg")
        }
        
        # 添加用户ID参数
        params = {
            "user_id": 2  # 测试用户ID
        }
        
        # 发送请求
        start_time = time.time()
        response = httpx.post(
            upload_url,
            files=files,
            params=params,
            timeout=120.0  # 120秒超时，因为图片分析需要时间
        )
        end_time = time.time()
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            print("✅ 报价单上传成功!")
            
            # 解析响应
            try:
                result = response.json()
                print(f"上传响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                # 检查关键字段
                if isinstance(result, dict):
                    if "task_id" in result:
                        task_id = result["task_id"]
                        print(f"✅ 任务ID: {task_id}")
                        print(f"✅ 文件名称: {result.get('file_name')}")
                        print(f"✅ 状态: {result.get('status')}")
                        
                        # 等待几秒后查询分析结果
                        print("\n等待5秒后查询分析结果...")
                        time.sleep(5)
                        
                        # 查询分析结果
                        query_url = f"http://120.26.201.61:8000/api/v1/quotes/quote/{task_id}"
                        query_response = httpx.get(
                            query_url,
                            params={"user_id": 2},
                            timeout=30.0
                        )
                        
                        if query_response.status_code == 200:
                            query_result = query_response.json()
                            print(f"✅ 查询分析结果成功!")
                            print(f"分析状态: {query_result.get('status')}")
                            print(f"风险评分: {query_result.get('risk_score')}")
                            print(f"分析进度: {query_result.get('analysis_progress')}")
                            
                            # 检查是否有分析结果
                            if query_result.get("status") == "completed":
                                print("✅ 报价单分析完成!")
                                if "total_price" in query_result:
                                    print(f"总价: {query_result.get('total_price')}")
                                if "high_risk_items" in query_result:
                                    items = query_result.get("high_risk_items", [])
                                    print(f"高风险项目数量: {len(items)}")
                                if "suggestions" in query_result:
                                    suggestions = query_result.get("suggestions", [])
                                    print(f"建议数量: {len(suggestions)}")
                            elif query_result.get("status") == "analyzing":
                                print("⏳ 报价单正在分析中...")
                                progress = query_result.get("analysis_progress", {})
                                print(f"分析进度: {progress.get('progress', 0)}% - {progress.get('message', '')}")
                            elif query_result.get("status") == "failed":
                                print("❌ 报价单分析失败")
                        else:
                            print(f"❌ 查询分析结果失败: {query_response.status_code}")
                            print(f"错误信息: {query_response.text[:500]}")
                    else:
                        print("⚠️ 返回的结果缺少task_id字段")
                        print(f"完整响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
                else:
                    print(f"⚠️ 返回的结果不是字典类型: {type(result)}")
                    print(f"响应内容: {response.text[:500]}...")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text[:500]}...")
        else:
            print(f"❌ 报价单上传失败!")
            print(f"错误信息: {response.text[:500]}")
            
    except httpx.TimeoutException:
        print("❌ 请求超时（120秒）")
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP错误: {e.response.status_code}")
        print(f"错误信息: {e.response.text[:500]}")
    except Exception as e:
        print(f"❌ 异常: {e}")

if __name__ == "__main__":
    test_production_quote_analysis()

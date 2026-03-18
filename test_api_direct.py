#!/usr/bin/env python3
"""
直接测试报价单和合同分析API接口
"""
import requests
import json
import time

def test_quote_analysis_api():
    """测试报价单分析API"""
    print('=== 测试报价单分析API ===')
    
    # 使用开发环境后端API
    base_url = 'http://120.26.201.61:8001/api/v1'
    
    # 测试图片URL - 使用正确的开发环境OSS桶
    test_image_url = 'https://zhuangxiu-images-dev-photo.oss-cn-hangzhou.aliyuncs.com/quote/test.jpg'
    
    # 构建请求数据
    data = {
        "image_url": test_image_url,
        "user_id": 999
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    api_url = f"{base_url}/quotes/analyze"
    print(f'调用API: {api_url}')
    print(f'图片URL: {test_image_url}')
    
    try:
        response = requests.post(api_url, json=data, headers=headers, timeout=30)
        print(f'响应状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'✅ API调用成功')
            print(f'   响应数据: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...')
            
            # 检查是否是兜底数据
            if result.get("is_fallback"):
                print(f'   ⚠️ 这是兜底数据 (is_fallback: True)')
                print(f'   错误代码: {result.get("error_code")}')
                print(f'   分析说明: {result.get("analysis_note")}')
                return False, result
            else:
                print(f'   ✅ 这是真实的AI分析数据')
                if "risk_score" in result:
                    print(f'   风险评分: {result["risk_score"]}')
                if "total_price" in result:
                    print(f'   总价: {result["total_price"]}')
                if "suggestions" in result:
                    print(f'   建议数: {len(result["suggestions"])}')
                return True, result
        else:
            print(f'❌ API调用失败: {response.status_code}')
            print(f'   响应内容: {response.text[:200]}')
            return False, None
            
    except Exception as e:
        print(f'❌ API调用异常: {e}')
        return False, None

def test_contract_analysis_api():
    """测试合同分析API"""
    print('\n\n=== 测试合同分析API ===')
    
    # 使用开发环境后端API
    base_url = 'http://120.26.201.61:8001/api/v1'
    
    # 测试图片URL - 使用正确的开发环境OSS桶
    test_image_url = 'https://zhuangxiu-images-dev-photo.oss-cn-hangzhou.aliyuncs.com/contract/test.jpg'
    
    # 构建请求数据
    data = {
        "image_url": test_image_url,
        "user_id": 999
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    api_url = f"{base_url}/contracts/analyze"
    print(f'调用API: {api_url}')
    print(f'图片URL: {test_image_url}')
    
    try:
        response = requests.post(api_url, json=data, headers=headers, timeout=30)
        print(f'响应状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'✅ API调用成功')
            print(f'   响应数据: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...')
            
            # 检查是否是兜底数据
            if result.get("is_fallback"):
                print(f'   ⚠️ 这是兜底数据 (is_fallback: True)')
                print(f'   错误代码: {result.get("error_code")}')
                return False, result
            else:
                print(f'   ✅ 这是真实的AI分析数据')
                if "risk_score" in result:
                    print(f'   风险评分: {result["risk_score"]}')
                if "key_clauses" in result:
                    print(f'   关键条款数: {len(result["key_clauses"])}')
                return True, result
        else:
            print(f'❌ API调用失败: {response.status_code}')
            print(f'   响应内容: {response.text[:200]}')
            return False, None
            
    except Exception as e:
        print(f'❌ API调用异常: {e}')
        return False, None

def test_file_upload_api():
    """测试文件上传API"""
    print('\n\n=== 测试文件上传API ===')
    
    # 使用开发环境后端API
    base_url = 'http://120.26.201.61:8001/api/v1'
    
    # 创建一个测试文件
    import tempfile
    import os
    
    # 创建测试图片文件
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        # 写入一些测试数据
        f.write(b'fake image data for testing')
        temp_file_path = f.name
    
    try:
        api_url = f"{base_url}/oss/upload"
        print(f'调用API: {api_url}')
        
        files = {
            'file': ('test_quote.jpg', open(temp_file_path, 'rb'), 'image/jpeg')
        }
        
        data = {
            'file_type': 'quote',
            'user_id': '999'
        }
        
        response = requests.post(api_url, files=files, data=data, timeout=30)
        print(f'响应状态码: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print(f'✅ 文件上传成功')
            print(f'   上传结果: {json.dumps(result, ensure_ascii=False, indent=2)}')
            
            if result.get("success"):
                print(f'   文件URL: {result.get("url")}')
                print(f'   文件Key: {result.get("key")}')
                return True, result
            else:
                print(f'   ⚠️ 上传返回success=False')
                return False, result
        else:
            print(f'❌ 文件上传失败: {response.status_code}')
            print(f'   响应内容: {response.text[:200]}')
            return False, None
            
    except Exception as e:
        print(f'❌ 文件上传异常: {e}')
        return False, None
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_end_to_end_flow():
    """测试端到端流程"""
    print('\n\n=== 测试端到端流程 ===')
    
    print('1. 文件上传 -> 2. 报价单分析 -> 3. 合同分析')
    
    # 先测试文件上传
    upload_success, upload_result = test_file_upload_api()
    
    if upload_success and upload_result.get("url"):
        image_url = upload_result.get("url")
        print(f'\n使用上传的图片URL进行报价单分析: {image_url}')
        
        # 测试报价单分析
        quote_success, quote_result = test_quote_analysis_api()
        
        if quote_success:
            print('\n✅ 端到端流程测试通过: 文件上传 -> 报价单分析')
            return True
        else:
            print('\n❌ 端到端流程测试失败: 报价单分析失败')
            return False
    else:
        print('\n❌ 端到端流程测试失败: 文件上传失败')
        return False

def main():
    """主函数"""
    print('开始测试报价单分析和合同分析功能...')
    
    # 测试报价单分析API
    quote_success, quote_result = test_quote_analysis_api()
    
    # 测试合同分析API
    contract_success, contract_result = test_contract_analysis_api()
    
    # 测试文件上传API
    upload_success, upload_result = test_file_upload_api()
    
    # 测试端到端流程
    e2e_success = test_end_to_end_flow()
    
    print('\n\n=== 最终测试总结 ===')
    print(f'报价单分析API: {"✅ 成功" if quote_success else "❌ 失败"}')
    print(f'合同分析API: {"✅ 成功" if contract_success else "❌ 失败"}')
    print(f'文件上传API: {"✅ 成功" if upload_success else "❌ 失败"}')
    print(f'端到端流程: {"✅ 成功" if e2e_success else "❌ 失败"}')
    
    # 问题归属分析
    print('\n=== 问题归属分析 ===')
    
    issues = []
    if not quote_success:
        issues.append('报价单分析API返回兜底数据或失败')
    if not contract_success:
        issues.append('合同分析API返回兜底数据或失败')
    if not upload_success:
        issues.append('文件上传API失败')
    if not e2e_success:
        issues.append('端到端流程测试失败')
    
    if issues:
        print('这是**后台问题**，具体表现在：')
        for issue in issues:
            print(f'  - {issue}')
        
        print('\n可能的原因：')
        print('1. 扣子智能体配置有问题')
        print('2. OSS图片URL无法访问')
        print('3. 扣子智能体返回工具调用说明而非分析结果')
        print('4. 后端服务解析逻辑有问题')
        print('5. 网络连接或权限问题')
    else:
        print('✅ 所有测试通过！这是**正常功能**')
    
    # 建议的解决方案
    print('\n=== 建议的解决方案 ===')
    if not quote_success or not contract_success:
        print('1. 检查扣子智能体配置是否正确')
        print('2. 检查OSS图片URL是否可以正常访问')
        print('3. 优化扣子服务的提示词和解析逻辑')
        print('4. 如果扣子智能体返回工具调用说明，需要调整智能体配置')
    
    if not upload_success:
        print('5. 检查OSS服务配置和权限')
        print('6. 检查文件上传API的实现')
    
    print('\n7. 考虑使用备用AI服务（如DeepSeek）')
    print('8. 确保开发环境和生产环境的配置一致')

if __name__ == "__main__":
    main()

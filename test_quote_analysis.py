import requests
import json
import base64

# 生产环境后端地址
BASE_URL = "http://120.26.201.61:8001/api/v1"

# 测试报价单分析
def test_quote_analysis():
    print("测试报价单分析功能...")
    
    # 使用一个测试图片（这里用base64编码的简单图片）
    # 或者使用一个已有的测试图片URL
    test_image_url = "https://example.com/test.jpg"  # 这里需要替换为实际的测试图片URL
    
    # 或者使用base64编码的简单图片
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # 构建请求数据
    data = {
        "image_url": test_image_url,
        "prompt": "请分析这份装修报价单，提取关键信息如总价、项目明细、材料品牌等。",
        "user_id": 1
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/quotes/analyze",
            json=data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"分析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"请求异常: {e}")
        return False

if __name__ == "__main__":
    test_quote_analysis()

import requests
import json
import base64

# 生产环境后端地址 - 使用8000端口
BASE_URL = "http://120.26.201.61:8000/api/v1"

# 测试报价单分析
def test_quote_analysis():
    print("测试报价单分析功能...")
    
    # 使用一个测试图片URL（这里用base64编码的简单图片）
    # 注意：实际使用时需要替换为有效的图片URL
    test_image_url = "https://via.placeholder.com/300x400.png?text=报价单测试"
    
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

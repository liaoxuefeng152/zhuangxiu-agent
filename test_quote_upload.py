import requests
import json
import os

# 生产环境后端地址 - 使用8000端口
BASE_URL = "http://120.26.201.61:8000/api/v1"

# 测试报价单上传
def test_quote_upload():
    print("测试报价单上传功能...")
    
    # 创建一个测试图片文件
    test_image_path = "test_quote_image.jpg"
    
    # 如果没有测试图片，创建一个简单的图片
    if not os.path.exists(test_image_path):
        print(f"创建测试图片: {test_image_path}")
        # 创建一个简单的JPEG图片
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (300, 400), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((50, 180), "测试报价单", fill='black')
        draw.text((50, 200), "总价: 100,000元", fill='black')
        img.save(test_image_path, 'JPEG')
    
    try:
        # 上传文件
        with open(test_image_path, 'rb') as f:
            files = {'file': (test_image_path, f, 'image/jpeg')}
            response = requests.post(
                f"{BASE_URL}/quotes/upload",
                files=files,
                timeout=60
            )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"上传成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 获取任务ID
            task_id = result.get('task_id')
            if task_id:
                print(f"任务ID: {task_id}")
                print("等待5秒后查询分析结果...")
                import time
                time.sleep(5)
                
                # 查询分析结果
                response2 = requests.get(
                    f"{BASE_URL}/quotes/quote/{task_id}",
                    timeout=30
                )
                print(f"查询结果状态码: {response2.status_code}")
                print(f"查询结果: {response2.text}")
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    print(f"分析结果: {json.dumps(result2, ensure_ascii=False, indent=2)}")
                    return True
            return True
        else:
            print(f"上传失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"请求异常: {e}")
        return False

if __name__ == "__main__":
    test_quote_upload()

import requests
import json
import os

# 生产环境后端地址 - 使用8000端口
BASE_URL = "http://120.26.201.61:8000/api/v1"

# 测试报价单上传
def test_quote_upload():
    print("测试报价单上传功能...")
    
    # 创建一个简单的文本文件作为测试
    test_file_path = "test_quote.txt"
    
    # 创建测试文件
    with open(test_file_path, 'w') as f:
        f.write("测试报价单\n")
        f.write("总价: 100,000元\n")
        f.write("项目明细:\n")
        f.write("1. 水电改造: 20,000元\n")
        f.write("2. 墙面处理: 15,000元\n")
        f.write("3. 地面铺贴: 25,000元\n")
        f.write("4. 木工制作: 30,000元\n")
        f.write("5. 油漆工程: 10,000元\n")
    
    try:
        # 上传文件
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path, f, 'text/plain')}
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
                print("等待10秒后查询分析结果...")
                import time
                time.sleep(10)
                
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

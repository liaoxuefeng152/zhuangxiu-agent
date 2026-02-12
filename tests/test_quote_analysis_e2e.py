#!/usr/bin/env python3
"""
装修报价单分析功能 - 前后端联调测试
使用阿里云开发环境后端，测试真实报价单分析流程
"""
import requests
import json
import sys
import os
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://120.26.201.61:8001/api/v1"
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

# 测试报告
test_report = {
    "test_name": "装修报价单分析功能 - 前后端联调测试",
    "test_time": datetime.now().isoformat(),
    "backend_url": BASE_URL,
    "test_cases": [],
    "summary": {}
}

def log_test_case(name, status, details=None):
    """记录测试用例"""
    test_report["test_cases"].append({
        "name": name,
        "status": status,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    })
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{status_icon} {name}")

def login():
    """登录获取token"""
    print("\n" + "=" * 60)
    print("步骤1: 用户登录")
    print("=" * 60)
    
    try:
        resp = requests.post(
            f"{BASE_URL}/users/login",
            json={"code": "dev_weapp_mock"},
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") == 0:
            data = result.get("data", {})
        else:
            data = result
        
        token = data.get("access_token")
        user_id = data.get("user_id")
        
        if token and user_id:
            print(f"✅ 登录成功")
            print(f"   User ID: {user_id}")
            print(f"   Token: {token[:30]}...")
            log_test_case("用户登录", "PASS", {"user_id": user_id})
            return token, user_id
        else:
            print(f"❌ 登录失败：未获取到token")
            log_test_case("用户登录", "FAIL", {"error": "未获取到token", "response": result})
            return None, None
            
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        log_test_case("用户登录", "FAIL", {"error": str(e)})
        return None, None


def upload_quote(token, user_id, quote_file_path):
    """上传报价单"""
    print("\n" + "=" * 60)
    print(f"步骤2: 上传报价单")
    print("=" * 60)
    print(f"文件: {os.path.basename(quote_file_path)}")
    
    if not os.path.exists(quote_file_path):
        print(f"❌ 文件不存在: {quote_file_path}")
        log_test_case("报价单上传", "FAIL", {"error": "文件不存在"})
        return None
    
    file_size = os.path.getsize(quote_file_path)
    print(f"文件大小: {file_size / 1024:.2f} KB")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    try:
        # 根据文件扩展名确定Content-Type
        file_ext = os.path.splitext(quote_file_path)[1].lower()
        content_type_map = {
            ".pdf": "application/pdf",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg"
        }
        content_type = content_type_map.get(file_ext, "application/octet-stream")
        
        with open(quote_file_path, "rb") as f:
            files = {"file": (os.path.basename(quote_file_path), f, content_type)}
            resp = requests.post(
                f"{BASE_URL}/quotes/upload",
                headers=headers,
                files=files,
                timeout=60
            )
            resp.raise_for_status()
            result = resp.json()
            
            print(f"✅ 上传成功")
            print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            task_id = result.get("task_id")
            file_name = result.get("file_name")
            status = result.get("status")
            
            log_test_case("报价单上传", "PASS", {
                "task_id": task_id,
                "file_name": file_name,
                "status": status,
                "file_size": file_size
            })
            
            return task_id
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP错误: {e}")
        if e.response is not None:
            print(f"   状态码: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"   错误: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   响应: {e.response.text[:200]}")
        log_test_case("报价单上传", "FAIL", {"error": str(e), "status_code": e.response.status_code if e.response else None})
        return None
    except Exception as e:
        print(f"❌ 上传失败: {e}")
        import traceback
        traceback.print_exc()
        log_test_case("报价单上传", "FAIL", {"error": str(e)})
        return None


def wait_for_analysis(token, user_id, max_wait=180):
    """等待报价单分析完成"""
    print("\n" + "=" * 60)
    print("步骤3: 等待报价单分析完成")
    print("=" * 60)
    print(f"最多等待: {max_wait}秒")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    start_time = time.time()
    last_status = None
    check_count = 0
    
    while time.time() - start_time < max_wait:
        try:
            # 查询报价单列表，获取最新的报价单
            resp = requests.get(
                f"{BASE_URL}/quotes/list",
                headers=headers,
                params={"page": 1, "page_size": 1},
                timeout=10
            )
            resp.raise_for_status()
            result = resp.json()
            
            if result.get("code") == 0:
                quotes_data = result.get("data", {})
                quotes = quotes_data.get("quotes", []) or quotes_data.get("list", [])
            else:
                quotes = result.get("quotes", []) or result.get("list", [])
            
            if quotes:
                quote = quotes[0]
                quote_id = quote.get("id")
                status = quote.get("status")
                progress = quote.get("analysis_progress", {})
                
                check_count += 1
                
                # 状态变化时输出
                if status != last_status:
                    print(f"\n   状态变化: {last_status} → {status}")
                    last_status = status
                
                if status == "completed":
                    print(f"\n✅ 分析完成！")
                    print(f"   Quote ID: {quote_id}")
                    print(f"   检查次数: {check_count}")
                    print(f"   耗时: {int(time.time() - start_time)}秒")
                    log_test_case("报价单分析", "PASS", {
                        "quote_id": quote_id,
                        "status": status,
                        "check_count": check_count,
                        "duration_seconds": int(time.time() - start_time)
                    })
                    return quote_id
                elif status == "failed":
                    print(f"\n❌ 分析失败")
                    log_test_case("报价单分析", "FAIL", {
                        "quote_id": quote_id,
                        "status": status
                    })
                    return None
                else:
                    progress_msg = progress.get("message", "")
                    progress_pct = progress.get("progress", 0)
                    elapsed = int(time.time() - start_time)
                    print(f"   [{elapsed}s] 分析中... ({progress_pct}%) {progress_msg}", end="\r")
                    time.sleep(5)
            else:
                print(f"   等待报价单创建...", end="\r")
                time.sleep(3)
                
        except Exception as e:
            print(f"\n   查询状态失败: {e}")
            time.sleep(3)
    
    print(f"\n⚠️  等待超时（{max_wait}秒）")
    log_test_case("报价单分析", "TIMEOUT", {
        "max_wait": max_wait,
        "check_count": check_count
    })
    return None


def get_quote_analysis(token, user_id, quote_id):
    """获取报价单分析结果"""
    print("\n" + "=" * 60)
    print("步骤4: 获取报价单分析结果")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    try:
        resp = requests.get(
            f"{BASE_URL}/quotes/quote/{quote_id}",
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") == 0:
            quote = result.get("data", {})
        else:
            quote = result
        
        print(f"✅ 获取成功")
        
        # 提取关键信息
        status = quote.get("status")
        risk_score = quote.get("risk_score")
        total_price = quote.get("total_price")
        market_ref_price = quote.get("market_ref_price")
        high_risk_items = quote.get("high_risk_items", [])
        warning_items = quote.get("warning_items", [])
        missing_items = quote.get("missing_items", [])
        overpriced_items = quote.get("overpriced_items", [])
        result_json = quote.get("result_json", {})
        
        print(f"\n📊 分析结果概览:")
        print(f"   状态: {status}")
        print(f"   风险评分: {risk_score}")
        print(f"   总价: {total_price}")
        print(f"   市场参考价: {market_ref_price}")
        print(f"   高风险项: {len(high_risk_items)}项")
        print(f"   警告项: {len(warning_items)}项")
        print(f"   漏项: {len(missing_items)}项")
        print(f"   虚高项: {len(overpriced_items)}项")
        
        # 检查是否有材料信息
        materials = result_json.get("materials") or result_json.get("material_list") or []
        if materials:
            print(f"   材料清单: {len(materials)}项")
        
        # 显示高风险项（前3项）
        if high_risk_items:
            print(f"\n⚠️  高风险项（前3项）:")
            for i, item in enumerate(high_risk_items[:3], 1):
                item_name = item.get("item") or item.get("name") or item.get("description") or str(item)
                category = item.get("category", "")
                print(f"   {i}. [{category}] {item_name}")
        
        # 显示警告项（前3项）
        if warning_items:
            print(f"\n⚠️  警告项（前3项）:")
            for i, item in enumerate(warning_items[:3], 1):
                item_name = item.get("item") or item.get("name") or item.get("description") or str(item)
                category = item.get("category", "")
                print(f"   {i}. [{category}] {item_name}")
        
        log_test_case("获取分析结果", "PASS", {
            "quote_id": quote_id,
            "risk_score": risk_score,
            "total_price": total_price,
            "high_risk_count": len(high_risk_items),
            "warning_count": len(warning_items),
            "missing_count": len(missing_items),
            "overpriced_count": len(overpriced_items),
            "has_materials": len(materials) > 0,
            "material_count": len(materials)
        })
        
        return quote
        
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        import traceback
        traceback.print_exc()
        log_test_case("获取分析结果", "FAIL", {"error": str(e)})
        return None


def test_material_list(token, user_id):
    """测试材料清单接口"""
    print("\n" + "=" * 60)
    print("步骤5: 测试材料清单接口")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    try:
        resp = requests.get(
            f"{BASE_URL}/material-checks/material-list",
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") == 0:
            data = result.get("data", {})
            material_list = data.get("list", [])
            source = data.get("source")
            
            print(f"✅ 获取成功")
            print(f"   数据来源: {source}")
            print(f"   材料数量: {len(material_list)}")
            
            if material_list:
                print(f"\n📋 材料清单（前5项）:")
                for i, mat in enumerate(material_list[:5], 1):
                    print(f"   {i}. 【{mat.get('category', 'N/A')}】{mat.get('material_name', 'N/A')}")
                    if mat.get('spec_brand'):
                        print(f"      规格/品牌: {mat.get('spec_brand')}")
                    if mat.get('quantity'):
                        print(f"      数量: {mat.get('quantity')}")
                    print()
            
            log_test_case("材料清单接口", "PASS", {
                "source": source,
                "material_count": len(material_list)
            })
            return True
        else:
            print(f"❌ 响应错误: {result.get('msg')}")
            log_test_case("材料清单接口", "FAIL", {"error": result.get('msg')})
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        log_test_case("材料清单接口", "FAIL", {"error": str(e)})
        return False


def generate_report():
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("生成测试报告")
    print("=" * 60)
    
    # 统计测试结果
    total = len(test_report["test_cases"])
    passed = len([tc for tc in test_report["test_cases"] if tc["status"] == "PASS"])
    failed = len([tc for tc in test_report["test_cases"] if tc["status"] == "FAIL"])
    timeout = len([tc for tc in test_report["test_cases"] if tc["status"] == "TIMEOUT"])
    
    test_report["summary"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "timeout": timeout,
        "success_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "0%"
    }
    
    # 保存报告
    report_file = os.path.join(
        os.path.dirname(__file__),
        f"quote_analysis_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(test_report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 测试报告已保存: {report_file}")
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试用例: {total}")
    print(f"通过: {passed} ✅")
    print(f"失败: {failed} ❌")
    print(f"超时: {timeout} ⚠️")
    print(f"成功率: {test_report['summary']['success_rate']}")
    
    return report_file


def main():
    """主测试流程"""
    print("=" * 60)
    print("装修报价单分析功能 - 前后端联调测试")
    print("=" * 60)
    print(f"后端地址: {BASE_URL}")
    print(f"测试时间: {test_report['test_time']}")
    
    # 1. 登录
    token, user_id = login()
    if not token:
        print("\n❌ 测试终止：无法登录")
        generate_report()
        sys.exit(1)
    
    # 2. 查找测试文件
    quote_files = [
        "2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png",
        "quote-sample.pdf",
        "quote-sample.png"
    ]
    
    quote_file = None
    for filename in quote_files:
        file_path = os.path.join(FIXTURES_DIR, filename)
        if os.path.exists(file_path):
            quote_file = file_path
            break
    
    if not quote_file:
        print(f"\n❌ 未找到测试报价单文件")
        print(f"   查找目录: {FIXTURES_DIR}")
        print(f"   查找文件: {quote_files}")
        generate_report()
        sys.exit(1)
    
    # 3. 上传报价单
    task_id = upload_quote(token, user_id, quote_file)
    if not task_id:
        print("\n❌ 测试终止：报价单上传失败")
        generate_report()
        sys.exit(1)
    
    # 4. 等待分析完成
    quote_id = wait_for_analysis(token, user_id, max_wait=180)
    if not quote_id:
        print("\n⚠️  报价单分析未完成，但继续测试其他功能...")
    
    # 5. 获取分析结果
    if quote_id:
        quote_data = get_quote_analysis(token, user_id, quote_id)
        
        # 6. 测试材料清单接口
        test_material_list(token, user_id)
    
    # 7. 生成报告
    report_file = generate_report()
    
    print(f"\n📄 详细测试报告: {report_file}")
    print("\n测试完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        generate_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        generate_report()
        sys.exit(1)

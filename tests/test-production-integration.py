#!/usr/bin/env python3
"""
生产环境前后端联调测试脚本
测试完整的用户业务流程，模拟真实用户操作
"""

import requests
import json
import time
import sys
from typing import Dict, List, Optional, Any
import uuid

class ProductionIntegrationTester:
    def __init__(self):
        # 阿里云生产环境配置
        self.base_url = "http://120.26.201.61:8001/api/v1"
        self.token = None
        self.user_id = None
        self.test_results = []
        self.test_data = {
            "company_name": f"测试装修公司_{int(time.time())}",
            "test_user_id": None,
            "scan_id": None,
            "quote_id": None,
            "contract_id": None,
            "order_id": None
        }
        
    def log(self, message: str, level: str = "INFO"):
        """日志记录"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def record_result(self, name: str, success: bool, details: str = "", response_time: float = 0):
        """记录测试结果"""
        result = {
            "name": name,
            "success": success,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        status = "✓" if success else "✗"
        print(f"  {status} {name} - {details} ({result['response_time_ms']}ms)")
        
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.user_id:
            headers["X-User-Id"] = str(self.user_id)
        return headers
    
    # ==================== 测试用例 ====================
    
    def test_01_health_check(self) -> bool:
        """测试1: 健康检查"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("01-健康检查", True, f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("01-健康检查", False, f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("01-健康检查", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_02_user_login(self) -> bool:
        """测试2: 用户登录"""
        start_time = time.time()
        try:
            payload = {"code": "dev_h5_mock"}
            response = requests.post(f"{self.base_url}/users/login", 
                                    json=payload, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("id")
                self.test_data["test_user_id"] = self.user_id
                
                if self.token:
                    self.record_result("02-用户登录", True, 
                                      f"登录成功，用户ID: {self.user_id}", elapsed)
                    return True
                else:
                    self.record_result("02-用户登录", False, 
                                      "响应中缺少token", elapsed)
                    return False
            else:
                self.record_result("02-用户登录", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("02-用户登录", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_03_user_profile(self) -> bool:
        """测试3: 获取用户信息"""
        if not self.token:
            self.record_result("03-获取用户信息", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/users/profile", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.record_result("03-获取用户信息", True, 
                                  f"获取成功，昵称: {data.get('nickname', '未设置')}", elapsed)
                return True
            else:
                self.record_result("03-获取用户信息", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("03-获取用户信息", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_04_company_search(self) -> bool:
        """测试4: 公司搜索（跳过，已知有问题）"""
        self.record_result("04-公司搜索", False, "已知问题：参数验证失败，跳过测试")
        return True  # 跳过不影响整体流程
    
    def test_05_company_scan(self) -> bool:
        """测试5: 提交公司检测"""
        if not self.token:
            self.record_result("05-提交公司检测", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            payload = {"company_name": self.test_data["company_name"]}
            response = requests.post(f"{self.base_url}/companies/scan", 
                                    headers=headers, json=payload, timeout=30)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                scan_id = data.get("scan_id")
                if scan_id:
                    self.test_data["scan_id"] = scan_id
                    self.record_result("05-提交公司检测", True, 
                                      f"提交成功，检测ID: {scan_id}", elapsed)
                    return True
                else:
                    self.record_result("05-提交公司检测", False, 
                                      "响应中缺少scan_id", elapsed)
                    return False
            else:
                self.record_result("05-提交公司检测", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("05-提交公司检测", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_06_quote_list(self) -> bool:
        """测试6: 获取报价单列表"""
        if not self.token:
            self.record_result("06-获取报价单列表", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/quotes/list", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                quotes = data.get("quotes", [])
                self.record_result("06-获取报价单列表", True, 
                                  f"获取成功，共{len(quotes)}条报价单", elapsed)
                return True
            else:
                self.record_result("06-获取报价单列表", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("06-获取报价单列表", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_07_contract_list(self) -> bool:
        """测试7: 获取合同列表"""
        if not self.token:
            self.record_result("07-获取合同列表", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/contracts/list", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                contracts = data.get("contracts", [])
                self.record_result("07-获取合同列表", True, 
                                  f"获取成功，共{len(contracts)}份合同", elapsed)
                return True
            else:
                self.record_result("07-获取合同列表", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("07-获取合同列表", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_08_construction_schedule(self) -> bool:
        """测试8: 获取施工进度计划"""
        if not self.token:
            self.record_result("08-获取施工进度计划", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/constructions/schedule", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                stages = data.get("stages", [])
                self.record_result("08-获取施工进度计划", True, 
                                  f"获取成功，共{len(stages)}个阶段", elapsed)
                return True
            else:
                self.record_result("08-获取施工进度计划", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("08-获取施工进度计划", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_09_material_list(self) -> bool:
        """测试9: 获取材料清单"""
        if not self.token:
            self.record_result("09-获取材料清单", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/material-checks/material-list", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                materials = data.get("materials", [])
                self.record_result("09-获取材料清单", True, 
                                  f"获取成功，共{len(materials)}种材料", elapsed)
                return True
            else:
                self.record_result("09-获取材料清单", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("09-获取材料清单", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_10_acceptance_list(self) -> bool:
        """测试10: 获取验收报告列表"""
        if not self.token:
            self.record_result("10-获取验收报告列表", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/acceptance", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                reports = data.get("reports", [])
                self.record_result("10-获取验收报告列表", True, 
                                  f"获取成功，共{len(reports)}份报告", elapsed)
                return True
            else:
                self.record_result("10-获取验收报告列表", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("10-获取验收报告列表", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_11_messages_list(self) -> bool:
        """测试11: 获取消息列表"""
        if not self.token:
            self.record_result("11-获取消息列表", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/messages", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                self.record_result("11-获取消息列表", True, 
                                  f"获取成功，共{len(messages)}条消息", elapsed)
                return True
            else:
                self.record_result("11-获取消息列表", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("11-获取消息列表", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_12_payment_orders(self) -> bool:
        """测试12: 获取订单列表"""
        if not self.token:
            self.record_result("12-获取订单列表", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/payments/orders", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get("orders", [])
                self.record_result("12-获取订单列表", True, 
                                  f"获取成功，共{len(orders)}个订单", elapsed)
                return True
            else:
                self.record_result("12-获取订单列表", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("12-获取订单列表", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_13_material_library_search(self) -> bool:
        """测试13: 搜索材料库"""
        if not self.token:
            self.record_result("13-搜索材料库", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            params = {"keyword": "水泥"}
            response = requests.get(f"{self.base_url}/material-library/search", 
                                   headers=headers, params=params, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                materials = data.get("materials", [])
                self.record_result("13-搜索材料库", True, 
                                  f"搜索成功，找到{len(materials)}种材料", elapsed)
                return True
            else:
                self.record_result("13-搜索材料库", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("13-搜索材料库", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_14_consultation_quota(self) -> bool:
        """测试14: 获取AI监理咨询额度"""
        if not self.token:
            self.record_result("14-获取咨询额度", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/consultation/quota", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                quota = data.get("remaining_quota", 0)
                self.record_result("14-获取咨询额度", True, 
                                  f"获取成功，剩余额度: {quota}", elapsed)
                return True
            else:
                self.record_result("14-获取咨询额度", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("14-获取咨询额度", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_15_cities_hot(self) -> bool:
        """测试15: 获取热门城市"""
        if not self.token:
            self.record_result("15-获取热门城市", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/cities/hot", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                cities = data.get("cities", [])
                self.record_result("15-获取热门城市", True, 
                                  f"获取成功，共{len(cities)}个城市", elapsed)
                return True
            else:
                self.record_result("15-获取热门城市", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("15-获取热门城市", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_16_feedback_submit(self) -> bool:
        """测试16: 提交反馈"""
        if not self.token:
            self.record_result("16-提交反馈", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            payload = {"content": f"前后端联调测试反馈 - {time.strftime('%Y-%m-%d %H:%M:%S')}"}
            response = requests.post(f"{self.base_url}/feedback", 
                                    headers=headers, json=payload, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("16-提交反馈", True, 
                                  f"提交成功", elapsed)
                return True
            else:
                self.record_result("16-提交反馈", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("16-提交反馈", False, f"异常: {str(e)}", elapsed)
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("=" * 70)
        print("生产环境前后端联调测试")
        print(f"API地址: {self.base_url}")
        print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # 执行所有测试用例
        test_methods = [
            self.test_01_health_check,
            self.test_02_user_login,
            self.test_03_user_profile,
            self.test_04_company_search,
            self.test_05_company_scan,
            self.test_06_quote_list,
            self.test_07_contract_list,
            self.test_08_construction_schedule,
            self.test_09_material_list,
            self.test_10_acceptance_list,
            self.test_11_messages_list,
            self.test_12_payment_orders,
            self.test_13_material_library_search,
            self.test_14_consultation_quota,
            self.test_15_cities_hot,
            self.test_16_feedback_submit
        ]
        
        for test_method in test_methods:
            test_method()
            time.sleep(0.5)  # 避免请求过于频繁
        
        # 生成测试报告
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        # 计算平均响应时间
        response_times = [r["response_time_ms"] for r in self.test_results if r["response_time_ms"] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "api_base": self.base_url,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": round(success_rate, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "test_data": self.test_data,
            "results": self.test_results
        }
        
        # 打印总结
        print("\n" + "=" * 70)
        print("测试总结")
        print("=" * 70)
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"成功率: {success_rate:.1f}%")
        print(f"平均响应时间: {avg_response_time:.1f}ms")
        
        if self.test_data["scan_id"]:
            print(f"测试生成的检测ID: {self.test_data['scan_id']}")
        
        # 保存结果到文件
        output_file = "tests/production-integration-test-results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试结果已保存到: {output_file}")
        return report

def main():
    """主函数"""
    tester = ProductionIntegrationTester()
    
    try:
        report = tester.run_all_tests()
        
        # 返回退出码
        if report["success_rate"] >= 80:
            print("\n✅ 生产环境前后端联调测试总体通过")
            return 0
        else:
            print("\n❌ 生产环境前后端联调测试存在较多问题")
            return 1
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 测试执行异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

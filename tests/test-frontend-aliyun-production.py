#!/usr/bin/env python3
"""
前端阿里云生产环境API测试脚本
测试阿里云生产环境（IP直连）前端调用的所有API接口
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
import sys

class FrontendAliyunAPITester:
    def __init__(self):
        # 阿里云生产环境配置（IP直连）
        self.base_url = "http://120.26.201.61:8001/api/v1"
        self.token = None
        self.user_id = None
        self.test_results = []
        
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
        
    def test_health_check(self) -> bool:
        """测试健康检查接口"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("健康检查", True, f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("健康检查", False, f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("健康检查", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_user_login(self) -> bool:
        """测试用户登录（使用开发环境mock code，生产环境可能相同）"""
        start_time = time.time()
        try:
            # 尝试开发环境mock code
            payload = {"code": "dev_h5_mock"}
            response = requests.post(f"{self.base_url}/users/login", 
                                    json=payload, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("id")
                
                if self.token:
                    self.record_result("用户登录", True, 
                                      f"登录成功，用户ID: {self.user_id}", elapsed)
                    return True
                else:
                    self.record_result("用户登录", False, 
                                      "响应中缺少token", elapsed)
                    return False
            else:
                self.record_result("用户登录", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("用户登录", False, f"异常: {str(e)}", elapsed)
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.user_id:
            headers["X-User-Id"] = str(self.user_id)
        return headers
    
    def test_user_profile(self) -> bool:
        """测试获取用户信息"""
        if not self.token:
            self.record_result("获取用户信息", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/users/profile", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("获取用户信息", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("获取用户信息", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("获取用户信息", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_company_search(self) -> bool:
        """测试公司搜索"""
        if not self.token:
            self.record_result("搜索装修公司", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            params = {"q": "装修"}
            response = requests.get(f"{self.base_url}/companies/search", 
                                   headers=headers, params=params, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("搜索装修公司", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            elif response.status_code == 422:
                # 参数验证失败，尝试使用keyword参数
                params = {"keyword": "装修"}
                response = requests.get(f"{self.base_url}/companies/search", 
                                       headers=headers, params=params, timeout=10)
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    self.record_result("搜索装修公司", True, 
                                      f"HTTP {response.status_code} (使用keyword参数)", elapsed)
                    return True
                else:
                    self.record_result("搜索装修公司", False, 
                                      f"参数验证失败 HTTP {response.status_code}", elapsed)
                    return False
            else:
                self.record_result("搜索装修公司", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("搜索装修公司", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_quote_list(self) -> bool:
        """测试获取报价单列表"""
        if not self.token:
            self.record_result("获取报价单列表", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/quotes/list", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("获取报价单列表", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("获取报价单列表", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("获取报价单列表", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_contract_list(self) -> bool:
        """测试获取合同列表"""
        if not self.token:
            self.record_result("获取合同列表", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/contracts/list", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("获取合同列表", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("获取合同列表", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("获取合同列表", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_construction_schedule(self) -> bool:
        """测试获取施工进度计划"""
        if not self.token:
            self.record_result("获取施工进度计划", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/constructions/schedule", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("获取施工进度计划", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("获取施工进度计划", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("获取施工进度计划", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_material_list(self) -> bool:
        """测试获取材料清单"""
        if not self.token:
            self.record_result("获取材料清单", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/material-checks/material-list", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("获取材料清单", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("获取材料清单", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("获取材料清单", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_acceptance_list(self) -> bool:
        """测试获取验收报告列表"""
        if not self.token:
            self.record_result("获取验收报告列表", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/acceptance", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("获取验收报告列表", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("获取验收报告列表", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("获取验收报告列表", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_messages_list(self) -> bool:
        """测试获取消息列表"""
        if not self.token:
            self.record_result("获取消息列表", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/messages", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("获取消息列表", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("获取消息列表", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("获取消息列表", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_payment_orders(self) -> bool:
        """测试获取订单列表"""
        if not self.token:
            self.record_result("获取订单列表", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/payments/orders", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("获取订单列表", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("获取订单列表", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("获取订单列表", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_material_library_search(self) -> bool:
        """测试材料库搜索"""
        if not self.token:
            self.record_result("搜索材料库", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            params = {"keyword": "水泥"}
            response = requests.get(f"{self.base_url}/material-library/search", 
                                   headers=headers, params=params, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("搜索材料库", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("搜索材料库", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("搜索材料库", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_consultation_quota(self) -> bool:
        """测试获取AI监理咨询额度"""
        if not self.token:
            self.record_result("获取咨询额度", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/consultation/quota", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("获取咨询额度", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("获取咨询额度", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("获取咨询额度", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_cities_hot(self) -> bool:
        """测试获取热门城市"""
        if not self.token:
            self.record_result("获取热门城市", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/cities/hot", 
                                   headers=headers, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("获取热门城市", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("获取热门城市", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("获取热门城市", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_monitor_status(self) -> bool:
        """测试获取系统状态"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/monitor/status", timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("获取系统状态", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("获取系统状态", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("获取系统状态", False, f"异常: {str(e)}", elapsed)
            return False
    
    def test_feedback_submit(self) -> bool:
        """测试提交反馈"""
        if not self.token:
            self.record_result("提交反馈", False, "未登录")
            return False
            
        start_time = time.time()
        try:
            headers = self.get_auth_headers()
            payload = {"content": "前端API测试反馈"}
            response = requests.post(f"{self.base_url}/feedback", 
                                    headers=headers, json=payload, timeout=10)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                self.record_result("提交反馈", True, 
                                  f"HTTP {response.status_code}", elapsed)
                return True
            else:
                self.record_result("提交反馈", False, 
                                  f"HTTP {response.status_code}", elapsed)
                return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.record_result("提交反馈", False, f"异常: {str(e)}", elapsed)
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("=" * 60)
        print("前端阿里云生产环境API测试")
        print(f"API地址: {self.base_url}")
        print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 测试阶段1: 基础健康检查
        print("\n🔍 阶段1: 基础健康检查")
        self.test_health_check()
        self.test_monitor_status()
        
        # 测试阶段2: 用户认证
        print("\n🔍 阶段2: 用户认证")
        if self.test_user_login():
            # 测试阶段3: 需要认证的接口
            print("\n🔍 阶段3: 需要认证的接口")
            self.test_user_profile()
            self.test_company_search()
            self.test_quote_list()
            self.test_contract_list()
            self.test_construction_schedule()
            self.test_material_list()
            self.test_acceptance_list()
            self.test_messages_list()
            self.test_payment_orders()
            self.test_material_library_search()
            self.test_consultation_quota()
            self.test_cities_hot()
            self.test_feedback_submit()
        
        # 生成测试报告
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        # 计算平均响应时间
        response_times = [r["response_time_ms"] for r in self.test_results]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "api_base": self.base_url,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": round(success_rate, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "results": self.test_results
        }
        
        # 打印总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"成功率: {success_rate:.1f}%")
        print(f"平均响应时间: {avg_response_time:.1f}ms")
        
        # 保存结果到文件
        output_file = "tests/frontend-aliyun-production-test-results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试结果已保存到: {output_file}")
        return report

def main():
    """主函数"""
    tester = FrontendAliyunAPITester()
    
    try:
        report = tester.run_all_tests()
        
        # 返回退出码
        if report["success_rate"] >= 80:
            print("\n✅ 前端阿里云生产环境API测试总体通过")
            return 0
        else:
            print("\n❌ 前端阿里云生产环境API测试存在较多问题")
            return 1
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 测试执行异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

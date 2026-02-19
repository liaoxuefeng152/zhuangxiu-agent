#!/usr/bin/env python3
"""
装修避坑管家 - 全面性能测试脚本
测试类型：API性能基准测试、并发性能测试、负载测试
"""
import requests
import time
import json
import threading
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://120.26.201.61:8001/api/v1"

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

class PerformanceTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.results = {}
        
    def login(self):
        """获取测试token"""
        print_info("获取测试token...")
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
            
            self.token = data.get("access_token")
            self.user_id = data.get("user_id")
            
            if not self.token:
                print_error("登录失败：未获取到token")
                return False
            
            print_success(f"登录成功 (User ID: {self.user_id})")
            return True
        except Exception as e:
            print_error(f"登录失败: {e}")
            return False
    
    def get_headers(self):
        """获取请求头"""
        if not self.token:
            return {}
        return {
            "Authorization": f"Bearer {self.token}",
            "X-User-Id": str(self.user_id)
        }
    
    def test_single_api(self, name, method, endpoint, data=None, params=None):
        """测试单个API的性能"""
        print_info(f"测试 {name}...")
        
        url = f"{BASE_URL}/{endpoint}"
        headers = self.get_headers()
        
        times = []
        errors = 0
        
        # 测试5次取平均值
        for i in range(5):
            try:
                start_time = time.time()
                
                if method == "GET":
                    resp = requests.get(url, headers=headers, params=params, timeout=10)
                elif method == "POST":
                    resp = requests.post(url, headers=headers, json=data, timeout=10)
                elif method == "PUT":
                    resp = requests.put(url, headers=headers, json=data, timeout=10)
                elif method == "DELETE":
                    resp = requests.delete(url, headers=headers, timeout=10)
                else:
                    print_error(f"不支持的HTTP方法: {method}")
                    return None
                
                elapsed = (time.time() - start_time) * 1000  # 转换为毫秒
                times.append(elapsed)
                
                if resp.status_code >= 400:
                    print_warning(f"  {name} 第{i+1}次请求返回 {resp.status_code}")
                    errors += 1
                
            except Exception as e:
                print_warning(f"  {name} 第{i+1}次请求失败: {e}")
                errors += 1
        
        if not times:
            print_error(f"{name} 所有请求都失败")
            return None
        
        result = {
            "name": name,
            "method": method,
            "endpoint": endpoint,
            "avg_time_ms": statistics.mean(times),
            "min_time_ms": min(times),
            "max_time_ms": max(times),
            "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "errors": errors,
            "success_rate": ((5 - errors) / 5) * 100
        }
        
        status = "✅" if result["success_rate"] >= 80 and result["avg_time_ms"] < 1000 else "⚠️" if result["success_rate"] >= 50 else "❌"
        print(f"  {status} {name}: 平均 {result['avg_time_ms']:.2f}ms, 成功率 {result['success_rate']:.1f}%")
        
        return result
    
    def test_concurrent_requests(self, endpoint, num_requests=10, num_threads=5):
        """测试并发请求性能"""
        print_info(f"测试并发请求: {endpoint} (请求数: {num_requests}, 线程数: {num_threads})")
        
        url = f"{BASE_URL}/{endpoint}"
        headers = self.get_headers()
        
        times = []
        errors = 0
        lock = threading.Lock()
        
        def make_request(i):
            try:
                start_time = time.time()
                resp = requests.get(url, headers=headers, timeout=10)
                elapsed = (time.time() - start_time) * 1000
                
                with lock:
                    times.append(elapsed)
                    if resp.status_code >= 400:
                        return False
                return True
            except Exception as e:
                with lock:
                    errors += 1
                return False
        
        start_total = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            results = [f.result() for f in as_completed(futures)]
        
        total_time = (time.time() - start_total) * 1000
        
        if not times:
            print_error("所有并发请求都失败")
            return None
        
        result = {
            "endpoint": endpoint,
            "num_requests": num_requests,
            "num_threads": num_threads,
            "total_time_ms": total_time,
            "avg_time_ms": statistics.mean(times),
            "min_time_ms": min(times),
            "max_time_ms": max(times),
            "requests_per_second": num_requests / (total_time / 1000),
            "errors": errors,
            "success_rate": ((num_requests - errors) / num_requests) * 100
        }
        
        print(f"  📊 并发测试结果: {result['requests_per_second']:.2f} 请求/秒, 成功率 {result['success_rate']:.1f}%")
        
        return result
    
    def test_load_scenario(self, scenario_name, duration_seconds=30, requests_per_second=5):
        """测试负载场景"""
        print_info(f"测试负载场景: {scenario_name} (持续时间: {duration_seconds}秒, 请求频率: {requests_per_second}/秒)")
        
        # 测试多个API的混合负载
        endpoints = [
            ("users/profile", "GET"),
            ("constructions/schedule", "GET"),
            ("companies/scans", "GET"),
            ("quotes/list", "GET"),
        ]
        
        headers = self.get_headers()
        
        total_requests = 0
        successful_requests = 0
        response_times = []
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        print_info("开始负载测试...")
        
        while time.time() < end_time:
            batch_start = time.time()
            
            for endpoint, method in endpoints:
                if time.time() >= end_time:
                    break
                    
                try:
                    url = f"{BASE_URL}/{endpoint}"
                    request_start = time.time()
                    
                    if method == "GET":
                        resp = requests.get(url, headers=headers, timeout=5)
                    else:
                        continue
                    
                    elapsed = (time.time() - request_start) * 1000
                    response_times.append(elapsed)
                    total_requests += 1
                    
                    if resp.status_code < 400:
                        successful_requests += 1
                    
                except Exception:
                    total_requests += 1
                    # 继续测试，不中断
            
            # 控制请求频率
            batch_elapsed = time.time() - batch_start
            if batch_elapsed < 1.0 / requests_per_second:
                time.sleep(1.0 / requests_per_second - batch_elapsed)
        
        total_elapsed = time.time() - start_time
        
        if not response_times:
            print_error("负载测试没有成功请求")
            return None
        
        result = {
            "scenario_name": scenario_name,
            "duration_seconds": duration_seconds,
            "target_rps": requests_per_second,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "actual_rps": total_requests / total_elapsed,
            "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
            "p95_response_time_ms": sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0,
            "p99_response_time_ms": sorted(response_times)[int(len(response_times) * 0.99)] if response_times else 0,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0
        }
        
        print(f"  📈 负载测试结果: {result['actual_rps']:.2f} 实际请求/秒, 平均响应 {result['avg_response_time_ms']:.2f}ms, 成功率 {result['success_rate']:.1f}%")
        
        return result
    
    def run_api_benchmarks(self):
        """运行API基准测试"""
        print_header("API性能基准测试")
        
        benchmarks = [
            ("健康检查", "GET", "health", None, None),
            ("用户信息", "GET", "users/profile", None, None),
            ("城市列表", "GET", "cities/list", None, None),
            ("热门城市", "GET", "cities/hot", None, None),
            ("公司检测记录", "GET", "companies/scans", None, None),
            ("报价单列表", "GET", "quotes/list", None, None),
            ("合同列表", "GET", "contracts/list", None, None),
            ("施工进度", "GET", "constructions/schedule", None, None),
            ("消息列表", "GET", "messages", None, None),
            ("施工照片列表", "GET", "construction-photos", None, None),
        ]
        
        results = []
        for benchmark in benchmarks:
            result = self.test_single_api(*benchmark)
            if result:
                results.append(result)
        
        self.results["api_benchmarks"] = results
        return results
    
    def run_concurrency_tests(self):
        """运行并发测试"""
        print_header("并发性能测试")
        
        concurrency_tests = [
            ("users/profile", 20, 5),
            ("constructions/schedule", 20, 5),
            ("companies/scans", 20, 5),
        ]
        
        results = []
        for endpoint, num_requests, num_threads in concurrency_tests:
            result = self.test_concurrent_requests(endpoint, num_requests, num_threads)
            if result:
                results.append(result)
        
        self.results["concurrency_tests"] = results
        return results
    
    def run_load_tests(self):
        """运行负载测试"""
        print_header("负载测试")
        
        load_scenarios = [
            ("正常负载", 30, 5),
            ("中等负载", 30, 10),
            ("高负载", 30, 20),
        ]
        
        results = []
        for scenario_name, duration, rps in load_scenarios:
            result = self.test_load_scenario(scenario_name, duration, rps)
            if result:
                results.append(result)
        
        self.results["load_tests"] = results
        return results
    
    def generate_report(self):
        """生成性能测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"tests/performance_test_report_{timestamp}.md"
        
        report = f"""# 装修避坑管家 - 全面性能测试报告

## 测试信息
- **测试时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **测试环境**: 阿里云开发环境 (120.26.201.61:8001)
- **Python版本**: 3.12.8

## 测试概述

本次性能测试包含三个部分：
1. **API性能基准测试** - 测试单个API的响应时间
2. **并发性能测试** - 测试系统在高并发下的表现
3. **负载测试** - 测试系统在不同负载下的性能表现

## 1. API性能基准测试

### 性能要求
- P0 API: 响应时间 ≤ 500ms
- P1 API: 响应时间 ≤ 1000ms
- P2 API: 响应时间 ≤ 1500ms

### 测试结果
| API名称 | 方法 | 端点 | 平均响应时间(ms) | 最小(ms) | 最大(ms) | 成功率 | 状态 |
|---------|------|------|------------------|----------|----------|--------|------|
"""
        
        # API基准测试结果
        if "api_benchmarks" in self.results:
            for result in self.results["api_benchmarks"]:
                status = "✅" if result["success_rate"] >= 80 and result["avg_time_ms"] < 1000 else "⚠️" if result["success_rate"] >= 50 else "❌"
                report += f"| {result['name']} | {result['method']} | {result['endpoint']} | {result['avg_time_ms']:.2f} | {result['min_time_ms']:.2f} | {result['max_time_ms']:.2f} | {result['success_rate']:.1f}% | {status} |\n"
        
        report += f"""
## 2. 并发性能测试

### 测试配置
- 并发线程数: 5
- 每个端点请求数: 20

### 测试结果
| 端点 | 总请求数 | 成功请求数 | 成功率 | 总时间(ms) | 平均响应时间(ms) | 吞吐量(请求/秒) | 状态 |
|------|----------|------------|--------|------------|------------------|-----------------|------|
"""
        
        # 并发测试结果
        if "concurrency_tests" in self.results:
            for result in self.results["concurrency_tests"]:
                status = "✅" if result["success_rate"] >= 90 else "⚠️" if result["success_rate"] >= 70 else "❌"
                report += f"| {result['endpoint']} | {result['num_requests']} | {result['num_requests'] - result['errors']} | {result['success_rate']:.1f}% | {result['total_time_ms']:.2f} | {result['avg_time_ms']:.2f} | {result['requests_per_second']:.2f} | {status} |\n"
        
        report += f"""
## 3. 负载测试

### 测试场景
1. **正常负载**: 5请求/秒，持续30秒
2. **中等负载**: 10请求/秒，持续30秒
3. **高负载**: 20请求/秒，持续30秒

### 测试结果
| 场景名称 | 目标RPS | 实际RPS | 总请求数 | 成功请求数 | 成功率 | 平均响应时间(ms) | P95响应时间(ms) | P99响应时间(ms) | 状态 |
|----------|---------|---------|----------|------------|--------|------------------|-----------------|-----------------|------|
"""
        
        # 负载测试结果
        if "load_tests" in self.results:
            for result in self.results["load_tests"]:
                status = "✅" if result["success_rate"] >= 95 else "⚠️" if result["success_rate"] >= 80 else "❌"
                report += f"| {result['scenario_name']} | {result['target_rps']} | {result['actual_rps']:.2f} | {result['total_requests']} | {result['successful_requests']} | {result['success_rate']:.1f}% | {result['avg_response_time_ms']:.2f} | {result['p95_response_time_ms']:.2f} | {result['p99_response_time_ms']:.2f} | {status} |\n"
        
        report += f"""
## 4. 性能分析

### 发现的问题
"""
        
        # 分析问题
        issues = []
        
        if "api_benchmarks" in self.results:
            for result in self.results["api_benchmarks"]:
                if result["avg_time_ms"] > 1000:
                    issues.append(f"- **{result['name']}** 响应时间过长: {result['avg_time_ms']:.2f}ms (要求: ≤1000ms)")
                if result["success_rate"] < 80:
                    issues.append(f"- **{result['name']}** 成功率过低: {result['success_rate']:.1f}% (要求: ≥80%)")
        
        if "concurrency_tests" in self.results:
            for result in self.results["concurrency_tests"]:
                if result["success_rate"] < 90:
                    issues.append(f"- **{result['endpoint']}** 并发成功率过低: {result['success_rate']:.1f}% (要求: ≥90%)")
                if result["avg_time_ms"] > 2000:
                    issues.append(f"- **{result['endpoint']}** 并发响应时间过长: {result['avg_time_ms']:.2f}ms")
        
        if "load_tests" in self.results:
            for result in self.results["load_tests"]:
                if result["success_rate"] < 95:
                    issues.append(f"- **{result['scenario_name']}** 负载测试成功率过低: {result['success_rate']:.1f}% (要求: ≥95%)")
                if result["avg_response_time_ms"] > 3000:
                    issues.append(f"- **{result['scenario_name']}** 负载测试响应时间过长: {result['avg_response_time_ms']:.2f}ms")
        
        if issues:
            for issue in issues:
                report += f"{issue}\n"
        else:
            report += "✅ 未发现严重性能问题\n"
        
        report += f"""
### 性能建议
"""
        
        # 性能建议
        suggestions = []
        
        if "api_benchmarks" in self.results:
            slow_apis = [r for r in self.results["api_benchmarks"] if r["avg_time_ms"] > 800]
            if slow_apis:
                suggestions.append("- **优化慢API**: 考虑对响应时间超过800ms的API进行优化，如添加缓存、优化数据库查询等")
        
        if "concurrency_tests" in self.results:
            low_concurrency = [r for r in self.results["concurrency_tests"] if r["success_rate"] < 85]
            if low_concurrency:
                suggestions.append("- **提升并发能力**: 对于并发成功率较低的API，考虑优化数据库连接池、增加服务器资源等")
        
        if "load_tests" in self.results:
            high_load_issues = [r for r in self.results["load_tests"] if r["success_rate"] < 90 and r["scenario_name"] == "高负载"]
            if high_load_issues:
                suggestions.append("- **增强高负载处理**: 在高负载场景下系统性能下降，建议进行水平扩展或优化关键路径")
        
        if not suggestions:
            suggestions.append("- **保持当前优化**: 系统性能良好，建议定期监控性能指标")
        
        for suggestion in suggestions:
            report += f"{suggestion}\n"
        
        report += f"""
## 5. 测试结论

### 总体评价
"""
        
        # 总体评价
        total_tests = 0
        passed_tests = 0
        
        if "api_benchmarks" in self.results:
            for result in self.results["api_benchmarks"]:
                total_tests += 1
                if result["success_rate"] >= 80 and result["avg_time_ms"] < 1000:
                    passed_tests += 1
        
        if "concurrency_tests" in self.results:
            for result in self.results["concurrency_tests"]:
                total_tests += 1
                if result["success_rate"] >= 90:
                    passed_tests += 1
        
        if "load_tests" in self.results:
            for result in self.results["load_tests"]:
                total_tests += 1
                if result["success_rate"] >= 95:
                    passed_tests += 1
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        if pass_rate >= 90:
            report += "✅ **优秀** - 系统性能表现优秀，满足所有性能要求\n"
        elif pass_rate >= 70:
            report += "⚠️ **良好** - 系统性能表现良好，部分指标需要优化\n"
        else:
            report += "❌ **需要改进** - 系统性能需要显著改进\n"
        
        report += f"- **总测试项**: {total_tests}\n"
        report += f"- **通过项**: {passed_tests}\n"
        report += f"- **通过率**: {pass_rate:.1f}%\n"
        
        report += f"""
### 后续行动
1. **监控性能指标**: 建议在生产环境部署性能监控
2. **定期性能测试**: 建议每周执行一次性能测试
3. **优化慢API**: 针对发现的慢API进行优化
4. **容量规划**: 根据负载测试结果进行容量规划

---

**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**测试执行人**: 自动化测试脚本
"""
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print_success(f"性能测试报告已生成: {report_file}")
        return report_file
    
    def run_all_tests(self):
        """运行所有性能测试"""
        print_header("开始全面性能测试")
        
        if not self.login():
            print_error("登录失败，无法继续测试")
            return False
        
        try:
            self.run_api_benchmarks()
            self.run_concurrency_tests()
            self.run_load_tests()
            self.generate_report()
            
            print_header("性能测试完成")
            return True
            
        except Exception as e:
            print_error(f"性能测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}装修避坑管家 - 全面性能测试{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    tester = PerformanceTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

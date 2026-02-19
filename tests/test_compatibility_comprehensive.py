#!/usr/bin/env python3
"""
装修避坑管家 - 全面兼容性测试脚本
测试类型：浏览器兼容性、设备兼容性、API版本兼容性、数据格式兼容性
"""
import requests
import json
import time
from datetime import datetime

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

class CompatibilityTester:
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
    
    def test_api_version_compatibility(self):
        """测试API版本兼容性"""
        print_header("1. API版本兼容性测试")
        
        tests = []
        
        # 测试1: 不同Accept头版本
        print_info("测试1: 不同Accept头版本")
        accept_versions = [
            "application/json",
            "application/vnd.api+json",
            "text/json",
            "*/*"
        ]
        
        for accept in accept_versions:
            print_info(f"  测试Accept: {accept}")
            try:
                headers = self.get_headers()
                headers["Accept"] = accept
                
                resp = requests.get(
                    f"{BASE_URL}/users/profile",
                    headers=headers,
                    timeout=10
                )
                
                if resp.status_code == 200:
                    content_type = resp.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        print_success(f"    ✅ Accept: {accept} 返回JSON格式")
                        tests.append({"name": f"Accept头兼容性-{accept}", "result": "通过", "status_code": resp.status_code, "content_type": content_type})
                    else:
                        print_warning(f"    ⚠️  Accept: {accept} 返回非JSON格式: {content_type}")
                        tests.append({"name": f"Accept头兼容性-{accept}", "result": "警告", "status_code": resp.status_code, "content_type": content_type})
                else:
                    print_warning(f"    ⚠️  Accept: {accept} 返回 {resp.status_code}")
                    tests.append({"name": f"Accept头兼容性-{accept}", "result": "警告", "status_code": resp.status_code})
                    
            except Exception as e:
                print_error(f"    ❌ Accept: {accept} 测试失败: {e}")
                tests.append({"name": f"Accept头兼容性-{accept}", "result": "失败", "error": str(e)})
        
        # 测试2: 不同Content-Type头
        print_info("测试2: 不同Content-Type头")
        content_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data"
        ]
        
        for content_type in content_types[:1]:  # 只测试JSON格式
            print_info(f"  测试Content-Type: {content_type}")
            try:
                headers = self.get_headers()
                headers["Content-Type"] = content_type
                
                if content_type == "application/json":
                    data = {"nickname": "测试用户"}
                else:
                    data = "nickname=测试用户"
                
                resp = requests.put(
                    f"{BASE_URL}/users/profile",
                    headers=headers,
                    data=data if content_type != "application/json" else None,
                    json=data if content_type == "application/json" else None,
                    timeout=10
                )
                
                if resp.status_code in [200, 400, 422]:
                    print_success(f"    ✅ Content-Type: {content_type} 正确处理")
                    tests.append({"name": f"Content-Type兼容性-{content_type}", "result": "通过", "status_code": resp.status_code})
                else:
                    print_warning(f"    ⚠️  Content-Type: {content_type} 返回 {resp.status_code}")
                    tests.append({"name": f"Content-Type兼容性-{content_type}", "result": "警告", "status_code": resp.status_code})
                    
            except Exception as e:
                print_error(f"    ❌ Content-Type: {content_type} 测试失败: {e}")
                tests.append({"name": f"Content-Type兼容性-{content_type}", "result": "失败", "error": str(e)})
        
        self.results["api_version_tests"] = tests
        return tests
    
    def test_data_format_compatibility(self):
        """测试数据格式兼容性"""
        print_header("2. 数据格式兼容性测试")
        
        tests = []
        
        # 测试1: 不同数据格式的请求
        print_info("测试1: 不同数据格式的请求")
        test_cases = [
            {"name": "标准JSON格式", "data": {"company_name": "测试装修公司"}},
            {"name": "空字符串", "data": {"company_name": ""}},
            {"name": "超长字符串", "data": {"company_name": "A" * 1000}},
            {"name": "特殊字符", "data": {"company_name": "测试@#$%^&*()公司"}},
            {"name": "Unicode字符", "data": {"company_name": "测试装修公司🚀🎉"}},
            {"name": "数字类型", "data": {"company_name": 12345}},
            {"name": "布尔类型", "data": {"company_name": True}},
            {"name": "null值", "data": {"company_name": None}},
        ]
        
        for test_case in test_cases:
            print_info(f"  测试: {test_case['name']}")
            try:
                headers = self.get_headers()
                
                resp = requests.post(
                    f"{BASE_URL}/companies/scan",
                    headers=headers,
                    json=test_case["data"],
                    timeout=10
                )
                
                # 检查响应状态
                if resp.status_code in [200, 400, 422]:
                    result = resp.json()
                    if isinstance(result, dict):
                        if result.get("code") == 0 or result.get("code") == 400:
                            print_success(f"    ✅ {test_case['name']} 正确处理")
                            tests.append({"name": f"数据格式-{test_case['name']}", "result": "通过", "status_code": resp.status_code})
                        else:
                            print_warning(f"    ⚠️  {test_case['name']} 返回非预期code: {result.get('code')}")
                            tests.append({"name": f"数据格式-{test_case['name']}", "result": "警告", "status_code": resp.status_code, "code": result.get("code")})
                    else:
                        print_warning(f"    ⚠️  {test_case['name']} 返回非JSON响应")
                        tests.append({"name": f"数据格式-{test_case['name']}", "result": "警告", "status_code": resp.status_code})
                else:
                    print_warning(f"    ⚠️  {test_case['name']} 返回 {resp.status_code}")
                    tests.append({"name": f"数据格式-{test_case['name']}", "result": "警告", "status_code": resp.status_code})
                    
            except Exception as e:
                print_error(f"    ❌ {test_case['name']} 测试失败: {e}")
                tests.append({"name": f"数据格式-{test_case['name']}", "result": "失败", "error": str(e)})
        
        # 测试2: 响应数据格式
        print_info("测试2: 响应数据格式检查")
        try:
            headers = self.get_headers()
            
            resp = requests.get(
                f"{BASE_URL}/users/profile",
                headers=headers,
                timeout=10
            )
            
            if resp.status_code == 200:
                result = resp.json()
                
                # 检查响应结构
                checks = []
                
                # 检查是否有标准响应结构
                if isinstance(result, dict):
                    checks.append("响应是字典格式")
                    
                    if "code" in result:
                        checks.append("包含code字段")
                    
                    if "msg" in result:
                        checks.append("包含msg字段")
                    
                    if "data" in result:
                        checks.append("包含data字段")
                        data = result["data"]
                        
                        if isinstance(data, dict):
                            checks.append("data是字典格式")
                            
                            # 检查用户信息字段
                            if "user_id" in data:
                                checks.append("data包含user_id字段")
                            
                            if "nickname" in data:
                                checks.append("data包含nickname字段")
                        
                if len(checks) >= 5:
                    print_success(f"    ✅ 响应格式正确: {', '.join(checks[:3])}...")
                    tests.append({"name": "响应数据格式", "result": "通过", "checks": checks})
                else:
                    print_warning(f"    ⚠️  响应格式不完整: {', '.join(checks)}")
                    tests.append({"name": "响应数据格式", "result": "警告", "checks": checks})
            else:
                print_warning(f"    ⚠️  响应返回 {resp.status_code}")
                tests.append({"name": "响应数据格式", "result": "警告", "status_code": resp.status_code})
                
        except Exception as e:
            print_error(f"    ❌ 响应数据格式测试失败: {e}")
            tests.append({"name": "响应数据格式", "result": "失败", "error": str(e)})
        
        self.results["data_format_tests"] = tests
        return tests
    
    def test_error_handling_compatibility(self):
        """测试错误处理兼容性"""
        print_header("3. 错误处理兼容性测试")
        
        tests = []
        
        # 测试1: 各种错误场景
        print_info("测试1: 各种错误场景")
        error_scenarios = [
            {"name": "无效端点", "method": "GET", "endpoint": "invalid/endpoint", "expected_status": 404},
            {"name": "无效方法", "method": "PATCH", "endpoint": "users/profile", "expected_status": 405},
            {"name": "缺少必需参数", "method": "POST", "endpoint": "users/login", "data": {}, "expected_status": 400},
            {"name": "无效JSON", "method": "POST", "endpoint": "users/login", "data": "{invalid json", "expected_status": 400},
        ]
        
        for scenario in error_scenarios:
            print_info(f"  测试: {scenario['name']}")
            try:
                headers = self.get_headers()
                
                if scenario["method"] == "GET":
                    resp = requests.get(
                        f"{BASE_URL}/{scenario['endpoint']}",
                        headers=headers,
                        timeout=10
                    )
                elif scenario["method"] == "POST":
                    if scenario.get("data") == "{invalid json":
                        headers["Content-Type"] = "application/json"
                        resp = requests.post(
                            f"{BASE_URL}/{scenario['endpoint']}",
                            headers=headers,
                            data=scenario["data"],
                            timeout=10
                        )
                    else:
                        resp = requests.post(
                            f"{BASE_URL}/{scenario['endpoint']}",
                            headers=headers,
                            json=scenario.get("data", {}),
                            timeout=10
                        )
                elif scenario["method"] == "PATCH":
                    resp = requests.patch(
                        f"{BASE_URL}/{scenario['endpoint']}",
                        headers=headers,
                        timeout=10
                    )
                
                if resp.status_code == scenario["expected_status"]:
                    print_success(f"    ✅ {scenario['name']} 返回预期状态码 {resp.status_code}")
                    tests.append({"name": f"错误处理-{scenario['name']}", "result": "通过", "status_code": resp.status_code})
                else:
                    print_warning(f"    ⚠️  {scenario['name']} 返回 {resp.status_code}，预期 {scenario['expected_status']}")
                    tests.append({"name": f"错误处理-{scenario['name']}", "result": "警告", "status_code": resp.status_code, "expected": scenario["expected_status"]})
                    
            except Exception as e:
                print_error(f"    ❌ {scenario['name']} 测试失败: {e}")
                tests.append({"name": f"错误处理-{scenario['name']}", "result": "失败", "error": str(e)})
        
        # 测试2: 错误响应格式
        print_info("测试2: 错误响应格式检查")
        try:
            # 触发一个400错误
            resp = requests.post(
                f"{BASE_URL}/users/login",
                json={},  # 缺少必需参数
                timeout=10
            )
            
            if resp.status_code == 400:
                result = resp.json()
                
                # 检查错误响应结构
                checks = []
                
                if isinstance(result, dict):
                    checks.append("错误响应是字典格式")
                    
                    if "code" in result:
                        code = result["code"]
                        if code == 400 or code < 0:
                            checks.append(f"错误code正确: {code}")
                        else:
                            checks.append(f"错误code可能不正确: {code}")
                    
                    if "msg" in result:
                        msg = result["msg"]
                        if msg and len(msg) > 0:
                            checks.append("错误消息不为空")
                    
                    # 检查是否有data字段（可选）
                    if "data" in result:
                        checks.append("包含data字段")
                
                if len(checks) >= 3:
                    print_success(f"    ✅ 错误响应格式正确: {', '.join(checks)}")
                    tests.append({"name": "错误响应格式", "result": "通过", "checks": checks})
                else:
                    print_warning(f"    ⚠️  错误响应格式不完整: {', '.join(checks)}")
                    tests.append({"name": "错误响应格式", "result": "警告", "checks": checks})
            else:
                print_warning(f"    ⚠️  错误响应返回 {resp.status_code}，预期400")
                tests.append({"name": "错误响应格式", "result": "警告", "status_code": resp.status_code})
                
        except Exception as e:
            print_error(f"    ❌ 错误响应格式测试失败: {e}")
            tests.append({"name": "错误响应格式", "result": "失败", "error": str(e)})
        
        self.results["error_handling_tests"] = tests
        return tests
    
    def test_cross_platform_compatibility(self):
        """测试跨平台兼容性"""
        print_header("4. 跨平台兼容性测试")
        
        tests = []
        
        # 测试1: 不同User-Agent
        print_info("测试1: 不同User-Agent兼容性")
        user_agents = [
            {"name": "微信小程序", "agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0"},
            {"name": "Android浏览器", "agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"},
            {"name": "iOS Safari", "agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"},
            {"name": "桌面Chrome", "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
            {"name": "Postman", "agent": "PostmanRuntime/7.28.0"},
            {"name": "curl", "agent": "curl/7.64.1"},
        ]
        
        for ua in user_agents:
            print_info(f"  测试User-Agent: {ua['name']}")
            try:
                headers = self.get_headers()
                headers["User-Agent"] = ua["agent"]
                
                resp = requests.get(
                    f"{BASE_URL}/users/profile",
                    headers=headers,
                    timeout=10
                )
                
                if resp.status_code == 200:
                    print_success(f"    ✅ User-Agent: {ua['name']} 兼容性正常")
                    tests.append({"name": f"User-Agent兼容性-{ua['name']}", "result": "通过", "status_code": resp.status_code})
                else:
                    print_warning(f"    ⚠️  User-Agent: {ua['name']} 返回 {resp.status_code}")
                    tests.append({"name": f"User-Agent兼容性-{ua['name']}", "result": "警告", "status_code": resp.status_code})
                    
            except Exception as e:
                print_error(f"    ❌ User-Agent: {ua['name']} 测试失败: {e}")
                tests.append({"name": f"User-Agent兼容性-{ua['name']}", "result": "失败", "error": str(e)})
        
        # 测试2: 不同时区处理
        print_info("测试2: 不同时区处理")
        try:
            headers = self.get_headers()
            
            # 测试带时区的时间戳
            test_data = {
                "start_time": "2024-01-01T00:00:00+08:00",
                "end_time": "2024-01-31T23:59:59+08:00"
            }
            
            resp = requests.get(
                f"{BASE_URL}/constructions/schedule",
                headers=headers,
                params=test_data,
                timeout=10
            )
            
            if resp.status_code in [200, 400]:
                print_success(f"    ✅ 时区时间处理正常")
                tests.append({"name": "时区处理兼容性", "result": "通过", "status_code": resp.status_code})
            else:
                print_warning(f"    ⚠️  时区时间处理返回 {resp.status_code}")
                tests.append({"name": "时区处理兼容性", "result": "警告", "status_code": resp.status_code})
                
        except Exception as e:
            print_error(f"    ❌ 时区处理测试失败: {e}")
            tests.append({"name": "时区处理兼容性", "result": "失败", "error": str(e)})
        
        # 测试3: 不同编码格式
        print_info("测试3: 不同编码格式")
        try:
            headers = self.get_headers()
            headers["Accept-Charset"] = "utf-8, iso-8859-1"
            
            resp = requests.get(
                f"{BASE_URL}/users/profile",
                headers=headers,
                timeout=10
            )
            
            content_type = resp.headers.get("Content-Type", "")
            if "charset=utf-8" in content_type.lower() or "charset=" not in content_type.lower():
                print_success(f"    ✅ 编码格式处理正常")
                tests.append({"name": "编码格式兼容性", "result": "通过", "content_type": content_type})
            else:
                print_warning(f"    ⚠️  编码格式可能有问题: {content_type}")
                tests.append({"name": "编码格式兼容性", "result": "警告", "content_type": content_type})
                
        except Exception as e:
            print_error(f"    ❌ 编码格式测试失败: {e}")
            tests.append({"name": "编码格式兼容性", "result": "失败", "error": str(e)})
        
        self.results["cross_platform_tests"] = tests
        return tests
    
    def generate_report(self):
        """生成兼容性测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"tests/compatibility_test_report_{timestamp}.md"
        
        report = f"""# 装修避坑管家 - 全面兼容性测试报告

## 测试信息
- **测试时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **测试环境**: 阿里云开发环境 (120.26.201.61:8001)
- **Python版本**: 3.12.8

## 测试概述

本次兼容性测试包含四个部分：
1. **API版本兼容性测试** - 测试不同HTTP头和内容类型的兼容性
2. **数据格式兼容性测试** - 测试不同数据格式和类型的兼容性
3. **错误处理兼容性测试** - 测试错误场景的兼容性
4. **跨平台兼容性测试** - 测试不同平台和客户端的兼容性

## 1. API版本兼容性测试

### 测试结果
| 测试项 | 结果 | 状态码 | Content-Type | 说明 |
|--------|------|--------|--------------|------|
"""
        
        # API版本测试结果
        if "api_version_tests" in self.results:
            for test in self.results["api_version_tests"]:
                result_emoji = "✅" if test["result"] == "通过" else ("⚠️" if test["result"] == "警告" else "❌")
                status_code = test.get("status_code", "N/A")
                content_type = test.get("content_type", "N/A")
                report += f"| {test['name']} | {result_emoji} {test['result']} | {status_code} | {content_type} | API版本兼容性测试 |\n"
        
        report += f"""
## 2. 数据格式兼容性测试

### 测试结果
| 测试项 | 结果 | 状态码 | 说明 |
|--------|------|--------|------|
"""
        
        # 数据格式测试结果
        if "data_format_tests" in self.results:
            for test in self.results["data_format_tests"]:
                result_emoji = "✅" if test["result"] == "通过" else ("⚠️" if test["result"] == "警告" else "❌")
                status_code = test.get("status_code", "N/A")
                report += f"| {test['name']} | {result_emoji} {test['result']} | {status_code} | 数据格式兼容性测试 |\n"
        
        report += f"""
## 3. 错误处理兼容性测试

### 测试结果
| 测试项 | 结果 | 状态码 | 预期状态码 | 说明 |
|--------|------|--------|------------|------|
"""
        
        # 错误处理测试结果
        if "error_handling_tests" in self.results:
            for test in self.results["error_handling_tests"]:
                result_emoji = "✅" if test["result"] == "通过" else ("⚠️" if test["result"] == "警告" else "❌")
                status_code = test.get("status_code", "N/A")
                expected = test.get("expected", "N/A")
                report += f"| {test['name']} | {result_emoji} {test['result']} | {status_code} | {expected} | 错误处理兼容性测试 |\n"
        
        report += f"""
## 4. 跨平台兼容性测试

### 测试结果
| 测试项 | 结果 | 状态码 | 说明 |
|--------|------|--------|------|
"""
        
        # 跨平台测试结果
        if "cross_platform_tests" in self.results:
            for test in self.results["cross_platform_tests"]:
                result_emoji = "✅" if test["result"] == "通过" else ("⚠️" if test["result"] == "警告" else "❌")
                status_code = test.get("status_code", "N/A")
                report += f"| {test['name']} | {result_emoji} {test['result']} | {status_code} | 跨平台兼容性测试 |\n"
        
        report += f"""
## 5. 兼容性分析

### 发现的兼容性问题
"""
        
        # 分析兼容性问题
        compatibility_issues = []
        
        # 收集所有失败和警告的测试
        all_tests = []
        for category in ["api_version_tests", "data_format_tests", "error_handling_tests", "cross_platform_tests"]:
            if category in self.results:
                all_tests.extend(self.results[category])
        
        for test in all_tests:
            if test["result"] == "失败":
                compatibility_issues.append(f"- ❌ **{test['name']}**: 兼容性测试失败，需要修复")
            elif test["result"] == "警告":
                compatibility_issues.append(f"- ⚠️  **{test['name']}**: 存在兼容性问题，建议优化")
        
        if compatibility_issues:
            for issue in compatibility_issues:
                report += f"{issue}\n"
        else:
            report += "✅ 未发现严重兼容性问题\n"
        
        report += f"""
### 兼容性建议
1. **标准化API响应**: 确保所有API返回统一的响应格式
2. **完善错误处理**: 提供清晰、一致的错误响应
3. **支持多种数据格式**: 考虑支持更多数据格式和编码
4. **跨平台测试**: 定期在不同平台和设备上进行测试
5. **版本管理**: 考虑实现API版本管理机制

## 6. 测试结论

### 总体评价
"""
        
        # 总体评价
        total_tests = 0
        passed_tests = 0
        warning_tests = 0
        failed_tests = 0
        
        for category in ["api_version_tests", "data_format_tests", "error_handling_tests", "cross_platform_tests"]:
            if category in self.results:
                for test in self.results[category]:
                    total_tests += 1
                    if test["result"] == "通过":
                        passed_tests += 1
                    elif test["result"] == "警告":
                        warning_tests += 1
                    elif test["result"] == "失败":
                        failed_tests += 1
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        if failed_tests == 0 and warning_tests == 0:
            report += "✅ **优秀** - 系统兼容性表现优秀，未发现兼容性问题\n"
        elif failed_tests == 0 and warning_tests > 0:
            report += "⚠️  **良好** - 系统兼容性表现良好，存在一些兼容性问题需要优化\n"
        elif failed_tests > 0:
            report += "❌ **需要改进** - 系统存在兼容性问题，需要修复\n"
        
        report += f"- **总测试项**: {total_tests}\n"
        report += f"- **通过项**: {passed_tests}\n"
        report += f"- **警告项**: {warning_tests}\n"
        report += f"- **失败项**: {failed_tests}\n"
        report += f"- **通过率**: {pass_rate:.1f}%\n"
        
        report += f"""
### 后续行动
1. **修复失败项**: 对于所有失败的测试项，需要立即修复
2. **优化警告项**: 对于警告项，建议在下一个版本中优化
3. **定期兼容性测试**: 建议每季度执行一次全面的兼容性测试
4. **用户反馈收集**: 收集用户在实际使用中遇到的兼容性问题

---

**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**测试执行人**: 自动化兼容性测试脚本
"""
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print_success(f"兼容性测试报告已生成: {report_file}")
        return report_file
    
    def run_all_tests(self):
        """运行所有兼容性测试"""
        print_header("开始全面兼容性测试")
        
        if not self.login():
            print_error("登录失败，无法继续测试")
            return False
        
        try:
            self.test_api_version_compatibility()
            self.test_data_format_compatibility()
            self.test_error_handling_compatibility()
            self.test_cross_platform_compatibility()
            self.generate_report()
            
            print_header("兼容性测试完成")
            return True
            
        except Exception as e:
            print_error(f"兼容性测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}装修避坑管家 - 全面兼容性测试{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    tester = CompatibilityTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

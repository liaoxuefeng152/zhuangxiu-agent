#!/usr/bin/env python3
"""
装修避坑管家 - 全面安全测试脚本
测试类型：认证授权测试、数据安全测试、API安全测试、文件上传安全测试
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

class SecurityTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.other_user_token = None
        self.other_user_id = None
        self.results = {}
        
    def login_test_user(self):
        """登录测试用户"""
        print_info("登录测试用户...")
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
            
            print_success(f"测试用户登录成功 (User ID: {self.user_id})")
            return True
        except Exception as e:
            print_error(f"登录失败: {e}")
            return False
    
    def login_other_user(self):
        """登录另一个测试用户（模拟不同用户）"""
        print_info("登录另一个测试用户...")
        try:
            # 使用不同的code模拟另一个用户
            resp = requests.post(
                f"{BASE_URL}/users/login",
                json={"code": "dev_weapp_mock_2"},
                timeout=10
            )
            resp.raise_for_status()
            result = resp.json()
            
            if result.get("code") == 0:
                data = result.get("data", {})
            else:
                data = result
            
            self.other_user_token = data.get("access_token")
            self.other_user_id = data.get("user_id")
            
            if not self.other_user_token:
                print_warning("另一个用户登录失败，使用相同用户继续测试")
                self.other_user_token = self.token
                self.other_user_id = self.user_id
                return False
            
            print_success(f"另一个用户登录成功 (User ID: {self.other_user_id})")
            return True
        except Exception as e:
            print_warning(f"另一个用户登录失败: {e}，使用相同用户继续测试")
            self.other_user_token = self.token
            self.other_user_id = self.user_id
            return False
    
    def get_headers(self, token=None):
        """获取请求头"""
        if token is None:
            token = self.token
        if not token:
            return {}
        return {
            "Authorization": f"Bearer {token}",
            "X-User-Id": str(self.user_id if token == self.token else self.other_user_id)
        }
    
    def test_authentication(self):
        """测试认证机制"""
        print_header("1. 认证机制测试")
        
        tests = []
        
        # 测试1: 无token访问需要认证的接口
        print_info("测试1: 无token访问需要认证的接口")
        try:
            resp = requests.get(
                f"{BASE_URL}/users/profile",
                timeout=10
            )
            if resp.status_code == 401:
                print_success("✅ 无token访问返回401 Unauthorized")
                tests.append({"name": "无token访问", "result": "通过", "status_code": resp.status_code})
            else:
                print_warning(f"⚠️  无token访问返回 {resp.status_code}，期望401")
                tests.append({"name": "无token访问", "result": "警告", "status_code": resp.status_code})
        except Exception as e:
            print_error(f"❌ 无token访问测试失败: {e}")
            tests.append({"name": "无token访问", "result": "失败", "error": str(e)})
        
        # 测试2: 无效token访问
        print_info("测试2: 无效token访问需要认证的接口")
        try:
            headers = {"Authorization": "Bearer invalid_token_123456"}
            resp = requests.get(
                f"{BASE_URL}/users/profile",
                headers=headers,
                timeout=10
            )
            if resp.status_code == 401:
                print_success("✅ 无效token访问返回401 Unauthorized")
                tests.append({"name": "无效token访问", "result": "通过", "status_code": resp.status_code})
            else:
                print_warning(f"⚠️  无效token访问返回 {resp.status_code}，期望401")
                tests.append({"name": "无效token访问", "result": "警告", "status_code": resp.status_code})
        except Exception as e:
            print_error(f"❌ 无效token访问测试失败: {e}")
            tests.append({"name": "无效token访问", "result": "失败", "error": str(e)})
        
        # 测试3: 过期token访问（模拟）
        print_info("测试3: 过期格式token访问")
        try:
            headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2MDAwMDAwMDB9.invalid_signature"}
            resp = requests.get(
                f"{BASE_URL}/users/profile",
                headers=headers,
                timeout=10
            )
            if resp.status_code == 401:
                print_success("✅ 过期格式token访问返回401 Unauthorized")
                tests.append({"name": "过期格式token访问", "result": "通过", "status_code": resp.status_code})
            else:
                print_warning(f"⚠️  过期格式token访问返回 {resp.status_code}，期望401")
                tests.append({"name": "过期格式token访问", "result": "警告", "status_code": resp.status_code})
        except Exception as e:
            print_error(f"❌ 过期格式token访问测试失败: {e}")
            tests.append({"name": "过期格式token访问", "result": "失败", "error": str(e)})
        
        self.results["authentication_tests"] = tests
        return tests
    
    def test_data_isolation(self):
        """测试数据隔离"""
        print_header("2. 数据隔离测试")
        
        tests = []
        
        if not self.token or not self.other_user_token:
            print_error("❌ 需要两个用户token进行数据隔离测试")
            return tests
        
        # 首先为用户A创建一些数据
        print_info("为用户A创建测试数据...")
        try:
            # 创建公司检测记录
            headers = self.get_headers(self.token)
            resp = requests.post(
                f"{BASE_URL}/companies/scan",
                headers=headers,
                json={"company_name": "测试装修公司A"},
                timeout=10
            )
            if resp.status_code == 200:
                result = resp.json()
                if result.get("code") == 0:
                    scan_data = result.get("data", {})
                else:
                    scan_data = result
                user_a_scan_id = scan_data.get("scan_id")
                print_success(f"✅ 为用户A创建公司检测记录 (Scan ID: {user_a_scan_id})")
            else:
                print_warning(f"⚠️  为用户A创建公司检测记录失败: {resp.status_code}")
                user_a_scan_id = "test_scan_1"
        except Exception as e:
            print_warning(f"⚠️  为用户A创建数据失败: {e}")
            user_a_scan_id = "test_scan_1"
        
        # 测试1: 用户B访问用户A的数据
        print_info("测试1: 用户B尝试访问用户A的数据")
        try:
            headers = self.get_headers(self.other_user_token)
            resp = requests.get(
                f"{BASE_URL}/companies/scan/{user_a_scan_id}",
                headers=headers,
                timeout=10
            )
            if resp.status_code in [403, 404]:
                print_success(f"✅ 用户B访问用户A数据返回 {resp.status_code}，数据隔离有效")
                tests.append({"name": "跨用户数据访问", "result": "通过", "status_code": resp.status_code})
            elif resp.status_code == 200:
                print_error(f"❌ 用户B可以访问用户A的数据，数据隔离失效")
                tests.append({"name": "跨用户数据访问", "result": "失败", "status_code": resp.status_code})
            else:
                print_warning(f"⚠️  跨用户访问返回 {resp.status_code}")
                tests.append({"name": "跨用户数据访问", "result": "警告", "status_code": resp.status_code})
        except Exception as e:
            print_error(f"❌ 跨用户数据访问测试失败: {e}")
            tests.append({"name": "跨用户数据访问", "result": "失败", "error": str(e)})
        
        # 测试2: 用户A访问自己的数据
        print_info("测试2: 用户A访问自己的数据")
        try:
            headers = self.get_headers(self.token)
            resp = requests.get(
                f"{BASE_URL}/companies/scans",
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                print_success("✅ 用户A可以访问自己的数据")
                tests.append({"name": "用户访问自己数据", "result": "通过", "status_code": resp.status_code})
            else:
                print_warning(f"⚠️  用户A访问自己数据返回 {resp.status_code}")
                tests.append({"name": "用户访问自己数据", "result": "警告", "status_code": resp.status_code})
        except Exception as e:
            print_error(f"❌ 用户访问自己数据测试失败: {e}")
            tests.append({"name": "用户访问自己数据", "result": "失败", "error": str(e)})
        
        self.results["data_isolation_tests"] = tests
        return tests
    
    def test_sql_injection(self):
        """测试SQL注入防护"""
        print_header("3. SQL注入防护测试")
        
        tests = []
        
        # 测试1: 搜索接口SQL注入测试
        print_info("测试1: 公司搜索接口SQL注入测试")
        sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT username, password FROM users --",
            "' OR 1=1 --",
            "admin' --",
        ]
        
        for payload in sql_injection_payloads:
            print_info(f"  测试payload: {payload}")
            try:
                headers = self.get_headers()
                resp = requests.get(
                    f"{BASE_URL}/companies/search",
                    headers=headers,
                    params={"q": payload},
                    timeout=10
                )
                
                # 检查响应
                if resp.status_code == 400 or resp.status_code == 422:
                    print_success(f"    ✅ payload '{payload}' 被拒绝 (状态码: {resp.status_code})")
                    tests.append({"name": f"SQL注入防护-{payload}", "result": "通过", "status_code": resp.status_code})
                elif resp.status_code == 200:
                    # 检查响应内容是否包含错误或空结果
                    result = resp.json()
                    if isinstance(result, dict) and result.get("code") == 0:
                        data = result.get("data", [])
                        if not data or len(data) == 0:
                            print_success(f"    ✅ payload '{payload}' 返回空结果")
                            tests.append({"name": f"SQL注入防护-{payload}", "result": "通过", "status_code": resp.status_code})
                        else:
                            print_warning(f"    ⚠️  payload '{payload}' 返回了数据，可能存在风险")
                            tests.append({"name": f"SQL注入防护-{payload}", "result": "警告", "status_code": resp.status_code})
                    else:
                        print_success(f"    ✅ payload '{payload}' 返回错误响应")
                        tests.append({"name": f"SQL注入防护-{payload}", "result": "通过", "status_code": resp.status_code})
                else:
                    print_info(f"    ℹ️  payload '{payload}' 返回 {resp.status_code}")
                    tests.append({"name": f"SQL注入防护-{payload}", "result": "信息", "status_code": resp.status_code})
                    
            except Exception as e:
                print_error(f"    ❌ payload '{payload}' 测试失败: {e}")
                tests.append({"name": f"SQL注入防护-{payload}", "result": "失败", "error": str(e)})
        
        # 测试2: 用户输入参数SQL注入测试
        print_info("测试2: 用户信息更新SQL注入测试")
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "'\"><script>alert('xss')</script>",
            "javascript:alert('xss')",
        ]
        
        for payload in xss_payloads[:1]:  # 只测试第一个，避免过多请求
            print_info(f"  测试XSS payload: {payload}")
            try:
                headers = self.get_headers()
                resp = requests.put(
                    f"{BASE_URL}/users/profile",
                    headers=headers,
                    json={"nickname": payload},
                    timeout=10
                )
                
                if resp.status_code == 400 or resp.status_code == 422:
                    print_success(f"    ✅ XSS payload 被拒绝 (状态码: {resp.status_code})")
                    tests.append({"name": f"XSS防护-{payload[:20]}", "result": "通过", "status_code": resp.status_code})
                else:
                    print_info(f"    ℹ️  XSS payload 返回 {resp.status_code}")
                    tests.append({"name": f"XSS防护-{payload[:20]}", "result": "信息", "status_code": resp.status_code})
                    
            except Exception as e:
                print_error(f"    ❌ XSS payload 测试失败: {e}")
                tests.append({"name": f"XSS防护-{payload[:20]}", "result": "失败", "error": str(e)})
        
        self.results["sql_injection_tests"] = tests
        return tests
    
    def test_file_upload_security(self):
        """测试文件上传安全"""
        print_header("4. 文件上传安全测试")
        
        tests = []
        
        # 测试1: 上传非允许格式的文件
        print_info("测试1: 上传非允许格式的文件")
        try:
            headers = self.get_headers()
            
            # 创建临时文件内容（模拟可执行文件）
            file_content = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00\xb8\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x0e\x1f\xba\x0e\x00\xb4\t\xcd!\xb8\x01L\xcd!This program cannot be run in DOS mode."
            
            files = {'file': ('test.exe', file_content, 'application/x-msdownload')}
            
            # 尝试上传到报价单接口
            resp = requests.post(
                f"{BASE_URL}/quotes/upload",
                headers=headers,
                files=files,
                timeout=10
            )
            
            if resp.status_code == 400:
                result = resp.json()
                if "不支持" in str(result) or "格式" in str(result):
                    print_success("✅ 非允许格式文件被拒绝")
                    tests.append({"name": "文件格式校验", "result": "通过", "status_code": resp.status_code})
                else:
                    print_warning(f"⚠️  非允许格式文件返回 {resp.status_code}，但错误信息不明确")
                    tests.append({"name": "文件格式校验", "result": "警告", "status_code": resp.status_code})
            elif resp.status_code == 415:
                print_success("✅ 非允许格式文件返回415 Unsupported Media Type")
                tests.append({"name": "文件格式校验", "result": "通过", "status_code": resp.status_code})
            else:
                print_warning(f"⚠️  非允许格式文件返回 {resp.status_code}")
                tests.append({"name": "文件格式校验", "result": "警告", "status_code": resp.status_code})
                
        except Exception as e:
            print_error(f"❌ 文件格式校验测试失败: {e}")
            tests.append({"name": "文件格式校验", "result": "失败", "error": str(e)})
        
        # 测试2: 上传超大文件
        print_info("测试2: 上传超大文件")
        try:
            headers = self.get_headers()
            
            # 创建超大文件内容（超过10MB）
            file_content = b"A" * (11 * 1024 * 1024)  # 11MB
            
            files = {'file': ('large_file.pdf', file_content, 'application/pdf')}
            
            resp = requests.post(
                f"{BASE_URL}/quotes/upload",
                headers=headers,
                files=files,
                timeout=30
            )
            
            if resp.status_code == 400:
                result = resp.json()
                if "大小" in str(result) or "10MB" in str(result):
                    print_success("✅ 超大文件被拒绝")
                    tests.append({"name": "文件大小校验", "result": "通过", "status_code": resp.status_code})
                else:
                    print_warning(f"⚠️  超大文件返回 {resp.status_code}，但错误信息不明确")
                    tests.append({"name": "文件大小校验", "result": "警告", "status_code": resp.status_code})
            elif resp.status_code == 413:
                print_success("✅ 超大文件返回413 Payload Too Large")
                tests.append({"name": "文件大小校验", "result": "通过", "status_code": resp.status_code})
            else:
                print_warning(f"⚠️  超大文件返回 {resp.status_code}")
                tests.append({"name": "文件大小校验", "result": "警告", "status_code": resp.status_code})
                
        except Exception as e:
            print_error(f"❌ 文件大小校验测试失败: {e}")
            tests.append({"name": "文件大小校验", "result": "失败", "error": str(e)})
        
        # 测试3: 上传恶意文件（包含脚本）
        print_info("测试3: 上传包含脚本的文件")
        try:
            headers = self.get_headers()
            
            # 创建包含脚本的HTML文件
            file_content = b'<html><body><script>alert("malicious")</script></body></html>'
            
            files = {'file': ('malicious.html', file_content, 'text/html')}
            
            resp = requests.post(
                f"{BASE_URL}/quotes/upload",
                headers=headers,
                files=files,
                timeout=10
            )
            
            if resp.status_code == 400 or resp.status_code == 415:
                print_success(f"✅ 恶意文件被拒绝 (状态码: {resp.status_code})")
                tests.append({"name": "恶意文件防护", "result": "通过", "status_code": resp.status_code})
            else:
                print_warning(f"⚠️  恶意文件返回 {resp.status_code}")
                tests.append({"name": "恶意文件防护", "result": "警告", "status_code": resp.status_code})
                
        except Exception as e:
            print_error(f"❌ 恶意文件防护测试失败: {e}")
            tests.append({"name": "恶意文件防护", "result": "失败", "error": str(e)})
        
        self.results["file_upload_tests"] = tests
        return tests
    
    def test_api_security(self):
        """测试API安全"""
        print_header("5. API安全测试")
        
        tests = []
        
        # 测试1: 敏感信息泄露
        print_info("测试1: 检查敏感信息泄露")
        try:
            # 检查错误响应是否包含敏感信息
            headers = {"Authorization": "Bearer invalid_token"}
            resp = requests.get(
                f"{BASE_URL}/users/profile",
                headers=headers,
                timeout=10
            )
            
            response_text = resp.text.lower()
            sensitive_keywords = ["password", "secret", "key", "token", "database", "sql", "exception", "stack trace", "traceback"]
            
            leaked_info = []
            for keyword in sensitive_keywords:
                if keyword in response_text:
                    leaked_info.append(keyword)
            
            if leaked_info:
                print_error(f"❌ 发现敏感信息泄露: {', '.join(leaked_info)}")
                tests.append({"name": "敏感信息泄露", "result": "失败", "leaked_info": leaked_info})
            else:
                print_success("✅ 未发现敏感信息泄露")
                tests.append({"name": "敏感信息泄露", "result": "通过"})
                
        except Exception as e:
            print_error(f"❌ 敏感信息泄露测试失败: {e}")
            tests.append({"name": "敏感信息泄露", "result": "失败", "error": str(e)})
        
        # 测试2: CORS配置检查
        print_info("测试2: CORS配置检查")
        try:
            resp = requests.options(
                f"{BASE_URL}/users/profile",
                headers={"Origin": "https://malicious-site.com"},
                timeout=10
            )
            
            cors_headers = resp.headers.get("Access-Control-Allow-Origin", "")
            if cors_headers == "*":
                print_warning("⚠️  CORS配置允许所有域名，可能存在安全风险")
                tests.append({"name": "CORS配置", "result": "警告", "config": "允许所有域名"})
            elif "malicious-site.com" in cors_headers:
                print_error("❌ CORS配置允许恶意域名")
                tests.append({"name": "CORS配置", "result": "失败", "config": cors_headers})
            else:
                print_success("✅ CORS配置正常")
                tests.append({"name": "CORS配置", "result": "通过", "config": cors_headers})
                
        except Exception as e:
            print_warning(f"⚠️  CORS配置检查失败: {e}")
            tests.append({"name": "CORS配置", "result": "警告", "error": str(e)})
        
        # 测试3: 速率限制检查
        print_info("测试3: 速率限制检查")
        try:
            # 快速发送多个请求
            headers = self.get_headers()
            status_codes = []
            
            for i in range(15):
                resp = requests.get(
                    f"{BASE_URL}/users/profile",
                    headers=headers,
                    timeout=5
                )
                status_codes.append(resp.status_code)
                time.sleep(0.1)  # 稍微延迟
            
            # 检查是否有429状态码
            if 429 in status_codes:
                print_success("✅ 速率限制生效")
                tests.append({"name": "速率限制", "result": "通过", "status_codes": status_codes})
            else:
                print_warning("⚠️  未检测到速率限制")
                tests.append({"name": "速率限制", "result": "警告", "status_codes": status_codes})
                
        except Exception as e:
            print_error(f"❌ 速率限制测试失败: {e}")
            tests.append({"name": "速率限制", "result": "失败", "error": str(e)})
        
        self.results["api_security_tests"] = tests
        return tests
    
    def generate_report(self):
        """生成安全测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"tests/security_test_report_{timestamp}.md"
        
        report = f"""# 装修避坑管家 - 全面安全测试报告

## 测试信息
- **测试时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **测试环境**: 阿里云开发环境 (120.26.201.61:8001)
- **Python版本**: 3.12.8

## 测试概述

本次安全测试包含五个部分：
1. **认证机制测试** - 测试Token认证和授权
2. **数据隔离测试** - 测试用户数据隔离
3. **SQL注入防护测试** - 测试SQL注入和XSS防护
4. **文件上传安全测试** - 测试文件上传安全限制
5. **API安全测试** - 测试API安全配置

## 1. 认证机制测试

### 测试结果
| 测试项 | 结果 | 状态码 | 说明 |
|--------|------|--------|------|
"""
        
        # 认证测试结果
        if "authentication_tests" in self.results:
            for test in self.results["authentication_tests"]:
                result_emoji = "✅" if test["result"] == "通过" else ("⚠️" if test["result"] == "警告" else "❌")
                status_code = test.get("status_code", "N/A")
                report += f"| {test['name']} | {result_emoji} {test['result']} | {status_code} | 认证机制测试 |\n"
        
        report += f"""
## 2. 数据隔离测试

### 测试结果
| 测试项 | 结果 | 状态码 | 说明 |
|--------|------|--------|------|
"""
        
        # 数据隔离测试结果
        if "data_isolation_tests" in self.results:
            for test in self.results["data_isolation_tests"]:
                result_emoji = "✅" if test["result"] == "通过" else ("⚠️" if test["result"] == "警告" else "❌")
                status_code = test.get("status_code", "N/A")
                report += f"| {test['name']} | {result_emoji} {test['result']} | {status_code} | 数据隔离测试 |\n"
        
        report += f"""
## 3. SQL注入防护测试

### 测试结果
| 测试项 | 结果 | 状态码 | 说明 |
|--------|------|--------|------|
"""
        
        # SQL注入测试结果
        if "sql_injection_tests" in self.results:
            for test in self.results["sql_injection_tests"][:10]:  # 只显示前10个
                result_emoji = "✅" if test["result"] == "通过" else ("⚠️" if test["result"] == "警告" else ("ℹ️" if test["result"] == "信息" else "❌"))
                status_code = test.get("status_code", "N/A")
                report += f"| {test['name']} | {result_emoji} {test['result']} | {status_code} | SQL注入防护测试 |\n"
        
        report += f"""
## 4. 文件上传安全测试

### 测试结果
| 测试项 | 结果 | 状态码 | 说明 |
|--------|------|--------|------|
"""
        
        # 文件上传测试结果
        if "file_upload_tests" in self.results:
            for test in self.results["file_upload_tests"]:
                result_emoji = "✅" if test["result"] == "通过" else ("⚠️" if test["result"] == "警告" else "❌")
                status_code = test.get("status_code", "N/A")
                report += f"| {test['name']} | {result_emoji} {test['result']} | {status_code} | 文件上传安全测试 |\n"
        
        report += f"""
## 5. API安全测试

### 测试结果
| 测试项 | 结果 | 说明 |
|--------|------|------|
"""
        
        # API安全测试结果
        if "api_security_tests" in self.results:
            for test in self.results["api_security_tests"]:
                result_emoji = "✅" if test["result"] == "通过" else ("⚠️" if test["result"] == "警告" else "❌")
                report += f"| {test['name']} | {result_emoji} {test['result']} | API安全测试 |\n"
        
        report += f"""
## 6. 安全分析

### 发现的安全问题
"""
        
        # 分析安全问题
        security_issues = []
        
        # 收集所有失败和警告的测试
        all_tests = []
        for category in ["authentication_tests", "data_isolation_tests", "sql_injection_tests", "file_upload_tests", "api_security_tests"]:
            if category in self.results:
                all_tests.extend(self.results[category])
        
        for test in all_tests:
            if test["result"] == "失败":
                security_issues.append(f"- ❌ **{test['name']}**: 测试失败，需要立即修复")
            elif test["result"] == "警告":
                security_issues.append(f"- ⚠️  **{test['name']}**: 存在潜在风险，建议优化")
        
        if security_issues:
            for issue in security_issues:
                report += f"{issue}\n"
        else:
            report += "✅ 未发现严重安全问题\n"
        
        report += f"""
### 安全建议
1. **加强认证机制**: 确保所有需要认证的接口都正确验证Token
2. **完善数据隔离**: 确保用户只能访问自己的数据
3. **输入验证**: 对所有用户输入进行严格的验证和过滤
4. **文件上传限制**: 严格限制上传文件的类型和大小
5. **API安全配置**: 配置合适的CORS和速率限制
6. **敏感信息保护**: 确保错误响应不泄露敏感信息

## 7. 测试结论

### 总体评价
"""
        
        # 总体评价
        total_tests = 0
        passed_tests = 0
        warning_tests = 0
        failed_tests = 0
        
        for category in ["authentication_tests", "data_isolation_tests", "sql_injection_tests", "file_upload_tests", "api_security_tests"]:
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
            report += "✅ **优秀** - 系统安全表现优秀，未发现安全问题\n"
        elif failed_tests == 0 and warning_tests > 0:
            report += "⚠️  **良好** - 系统安全表现良好，存在一些潜在风险需要优化\n"
        elif failed_tests > 0:
            report += "❌ **需要改进** - 系统存在安全漏洞，需要立即修复\n"
        
        report += f"- **总测试项**: {total_tests}\n"
        report += f"- **通过项**: {passed_tests}\n"
        report += f"- **警告项**: {warning_tests}\n"
        report += f"- **失败项**: {failed_tests}\n"
        report += f"- **通过率**: {pass_rate:.1f}%\n"
        
        report += f"""
### 后续行动
1. **立即修复失败项**: 对于所有失败的测试项，需要立即修复
2. **优化警告项**: 对于警告项，建议在下一个版本中优化
3. **定期安全测试**: 建议每月执行一次全面的安全测试
4. **安全监控**: 部署安全监控系统，实时检测安全威胁

---

**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**测试执行人**: 自动化安全测试脚本
"""
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print_success(f"安全测试报告已生成: {report_file}")
        return report_file
    
    def run_all_tests(self):
        """运行所有安全测试"""
        print_header("开始全面安全测试")
        
        if not self.login_test_user():
            print_error("测试用户登录失败，无法继续测试")
            return False
        
        self.login_other_user()
        
        try:
            self.test_authentication()
            self.test_data_isolation()
            self.test_sql_injection()
            self.test_file_upload_security()
            self.test_api_security()
            self.generate_report()
            
            print_header("安全测试完成")
            return True
            
        except Exception as e:
            print_error(f"安全测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}装修避坑管家 - 全面安全测试{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    tester = SecurityTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

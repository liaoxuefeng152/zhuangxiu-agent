#!/usr/bin/env python3
"""
装修避坑管家 - 全功能前后端联调测试
覆盖所有现有功能模块，进行端到端测试

测试环境：
- 前端：本地开发环境（微信小程序）
- 后端：阿里云开发环境（120.26.201.61:8001）
"""
import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

BASE_URL = "http://120.26.201.61:8001/api/v1"

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'

class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.warnings = []
    
    def add_pass(self, msg: str = ""):
        self.passed += 1
        if msg:
            print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")
    
    def add_fail(self, msg: str, error: Exception = None):
        self.failed += 1
        error_msg = f": {str(error)}" if error else ""
        self.errors.append(f"{msg}{error_msg}")
        print(f"{Colors.RED}❌ {msg}{error_msg}{Colors.RESET}")
    
    def add_warning(self, msg: str):
        self.warnings.append(msg)
        print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_section(title: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")

def get_auth_headers(token: str, user_id: int) -> Dict[str, str]:
    """获取认证头"""
    return {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id),
        "Content-Type": "application/json"
    }

def login() -> tuple[Optional[str], Optional[int]]:
    """用户登录"""
    try:
        resp = requests.post(
            f"{BASE_URL}/users/login",
            json={"code": "dev_weapp_mock"},
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        data = result.get("data", {}) if result.get("code") == 0 else result
        token = data.get("access_token")
        user_id = data.get("user_id")
        if not token or not user_id:
            return None, None
        print(f"{Colors.GREEN}✅ 登录成功 (User ID: {user_id}){Colors.RESET}")
        return token, user_id
    except Exception as e:
        print(f"{Colors.RED}❌ 登录失败: {e}{Colors.RESET}")
        return None, None

# ==================== 1. 用户模块测试 ====================
def test_user_module(token: str, user_id: int, result: TestResult):
    """测试用户相关功能"""
    print_section("1. 用户模块测试")
    
    # 1.1 获取用户信息
    try:
        resp = requests.get(
            f"{BASE_URL}/users/profile",
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json().get("data", {}) if resp.json().get("code") == 0 else resp.json()
        result.add_pass("获取用户信息成功")
    except Exception as e:
        result.add_fail("获取用户信息失败", e)
    
    # 1.2 更新用户信息
    try:
        resp = requests.put(
            f"{BASE_URL}/users/profile",
            json={"nickname": "测试用户"},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("更新用户信息成功")
    except Exception as e:
        result.add_warning(f"更新用户信息失败: {e}")

# ==================== 2. 城市模块测试 ====================
def test_city_module(token: str, user_id: int, result: TestResult):
    """测试城市选择功能"""
    print_section("2. 城市模块测试")
    
    # 2.1 选择城市
    try:
        resp = requests.post(
            f"{BASE_URL}/cities/select",
            json={"city_name": "深圳"},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("选择城市成功")
    except Exception as e:
        result.add_fail("选择城市失败", e)
    
    # 2.2 获取城市列表
    try:
        resp = requests.get(
            f"{BASE_URL}/cities/list",
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("获取城市列表成功")
    except Exception as e:
        result.add_warning(f"获取城市列表失败: {e}")

# ==================== 3. 公司检测模块测试 ====================
def test_company_module(token: str, user_id: int, result: TestResult):
    """测试公司检测功能"""
    print_section("3. 公司检测模块测试")
    
    # 3.1 搜索公司
    try:
        resp = requests.get(
            f"{BASE_URL}/companies/search",
            params={"q": "深圳装修公司"},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("搜索公司成功")
    except Exception as e:
        result.add_fail("搜索公司失败", e)
    
    # 3.2 提交公司检测
    scan_id = None
    try:
        resp = requests.post(
            f"{BASE_URL}/companies/scan",
            json={"company_name": "深圳装修公司"},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json().get("data", {}) if resp.json().get("code") == 0 else resp.json()
        scan_id = data.get("id") or data.get("scan_id")
        result.add_pass(f"提交公司检测成功 (Scan ID: {scan_id})")
    except Exception as e:
        result.add_fail("提交公司检测失败", e)
    
    # 3.3 查询检测结果
    if scan_id:
        try:
            resp = requests.get(
                f"{BASE_URL}/companies/scan/{scan_id}",
                headers=get_auth_headers(token, user_id),
                timeout=10
            )
            resp.raise_for_status()
            result.add_pass("查询检测结果成功")
        except Exception as e:
            result.add_warning(f"查询检测结果失败: {e}")
    
    # 3.4 获取检测列表
    try:
        resp = requests.get(
            f"{BASE_URL}/companies/scans",
            params={"page": 1, "page_size": 10},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("获取检测列表成功")
    except Exception as e:
        result.add_fail("获取检测列表失败", e)

# ==================== 4. 报价单模块测试 ====================
def test_quote_module(token: str, user_id: int, result: TestResult):
    """测试报价单分析功能"""
    print_section("4. 报价单模块测试")
    
    # 4.1 上传报价单（模拟）
    quote_id = None
    try:
        # 检查是否有测试文件
        test_file = Path("tests/fixtures/2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png")
        if test_file.exists():
            with open(test_file, 'rb') as f:
                files = {'file': f}
                resp = requests.post(
                    f"{BASE_URL}/quotes/upload",
                    files=files,
                    headers={"Authorization": f"Bearer {token}", "X-User-Id": str(user_id)},
                    timeout=30
                )
                resp.raise_for_status()
                data = resp.json().get("data", {}) if resp.json().get("code") == 0 else resp.json()
                quote_id = data.get("id") or data.get("quote_id")
                result.add_pass(f"上传报价单成功 (Quote ID: {quote_id})")
        else:
            result.add_warning("未找到测试报价单文件，跳过上传测试")
    except Exception as e:
        result.add_warning(f"上传报价单失败: {e}")
    
    # 4.2 查询报价单分析结果
    if quote_id:
        try:
            resp = requests.get(
                f"{BASE_URL}/quotes/quote/{quote_id}",
                headers=get_auth_headers(token, user_id),
                timeout=10
            )
            resp.raise_for_status()
            result.add_pass("查询报价单分析结果成功")
        except Exception as e:
            result.add_warning(f"查询报价单分析结果失败: {e}")
    
    # 4.3 获取报价单列表
    try:
        resp = requests.get(
            f"{BASE_URL}/quotes/list",
            params={"page": 1, "page_size": 10},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("获取报价单列表成功")
    except Exception as e:
        result.add_fail("获取报价单列表失败", e)

# ==================== 5. 合同模块测试 ====================
def test_contract_module(token: str, user_id: int, result: TestResult):
    """测试合同审核功能"""
    print_section("5. 合同模块测试")
    
    # 5.1 上传合同（模拟）
    contract_id = None
    try:
        test_file = Path("tests/fixtures/深圳市住宅装饰装修工程施工合同（半包装修版）.png")
        if test_file.exists():
            with open(test_file, 'rb') as f:
                files = {'file': f}
                resp = requests.post(
                    f"{BASE_URL}/contracts/upload",
                    files=files,
                    headers={"Authorization": f"Bearer {token}", "X-User-Id": str(user_id)},
                    timeout=30
                )
                resp.raise_for_status()
                data = resp.json().get("data", {}) if resp.json().get("code") == 0 else resp.json()
                contract_id = data.get("id") or data.get("contract_id")
                result.add_pass(f"上传合同成功 (Contract ID: {contract_id})")
        else:
            result.add_warning("未找到测试合同文件，跳过上传测试")
    except Exception as e:
        result.add_warning(f"上传合同失败: {e}")
    
    # 5.2 获取合同列表
    try:
        resp = requests.get(
            f"{BASE_URL}/contracts/list",
            params={"page": 1, "page_size": 10},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("获取合同列表成功")
    except Exception as e:
        result.add_fail("获取合同列表失败", e)

# ==================== 6. 施工进度模块测试 ====================
def test_construction_module(token: str, user_id: int, result: TestResult):
    """测试施工进度功能"""
    print_section("6. 施工进度模块测试")
    
    # 6.1 设置开工日期
    try:
        start_date = datetime.now().strftime("%Y-%m-%dT00:00:00")
        resp = requests.post(
            f"{BASE_URL}/constructions/start-date",
            json={"start_date": start_date},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("设置开工日期成功")
    except Exception as e:
        result.add_fail("设置开工日期失败", e)
    
    # 6.2 获取施工进度
    try:
        resp = requests.get(
            f"{BASE_URL}/constructions/schedule",
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json().get("data", {}) if resp.json().get("code") == 0 else resp.json()
        stages = data.get("stages", {})
        result.add_pass(f"获取施工进度成功 (阶段数: {len(stages)})")
    except Exception as e:
        result.add_fail("获取施工进度失败", e)
    
    # 6.3 更新阶段状态
    try:
        resp = requests.put(
            f"{BASE_URL}/constructions/stage-status",
            json={"stage": "S00", "status": "checked"},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("更新阶段状态成功")
    except Exception as e:
        result.add_warning(f"更新阶段状态失败: {e}")

# ==================== 7. 材料核对模块测试 ====================
def test_material_check_module(token: str, user_id: int, result: TestResult):
    """测试材料核对功能"""
    print_section("7. 材料核对模块测试")
    
    # 7.1 获取材料列表
    try:
        resp = requests.get(
            f"{BASE_URL}/material-checks/material-list",
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("获取材料列表成功")
    except Exception as e:
        result.add_warning(f"获取材料列表失败: {e}")
    
    # 7.2 提交材料核对
    try:
        resp = requests.post(
            f"{BASE_URL}/material-checks/submit",
            json={
                "items": [{"material_name": "测试材料", "photo_urls": ["https://mock-oss.example.com/material/test.png"]}],
                "result": "pass"
            },
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("提交材料核对成功")
    except Exception as e:
        result.add_warning(f"提交材料核对失败: {e}")

# ==================== 8. 验收分析模块测试 ====================
def test_acceptance_module(token: str, user_id: int, result: TestResult):
    """测试验收分析功能"""
    print_section("8. 验收分析模块测试")
    
    # 8.1 上传验收照片
    photo_url = None
    try:
        test_file = Path("tests/fixtures/隐蔽工程验收.png")
        if test_file.exists():
            with open(test_file, 'rb') as f:
                files = {'file': f}
                resp = requests.post(
                    f"{BASE_URL}/acceptance/upload-photo",
                    files=files,
                    headers={"Authorization": f"Bearer {token}", "X-User-Id": str(user_id)},
                    timeout=30
                )
                resp.raise_for_status()
                data = resp.json().get("data", {}) if resp.json().get("code") == 0 else resp.json()
                photo_url = data.get("file_url")
                result.add_pass(f"上传验收照片成功")
        else:
            result.add_warning("未找到测试验收照片，跳过上传测试")
    except Exception as e:
        result.add_warning(f"上传验收照片失败: {e}")
    
    # 8.2 提交验收分析
    if photo_url:
        try:
            resp = requests.post(
                f"{BASE_URL}/acceptance/analyze",
                json={"stage": "S01", "file_urls": [photo_url]},
                headers=get_auth_headers(token, user_id),
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json().get("data", {}) if resp.json().get("code") == 0 else resp.json()
            analysis_id = data.get("id") or data.get("analysis_id")
            result.add_pass(f"提交验收分析成功 (Analysis ID: {analysis_id})")
        except Exception as e:
            result.add_warning(f"提交验收分析失败: {e}")
    
    # 8.3 获取验收列表
    try:
        resp = requests.get(
            f"{BASE_URL}/acceptance",
            params={"page": 1, "page_size": 10},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("获取验收列表成功")
    except Exception as e:
        result.add_fail("获取验收列表失败", e)

# ==================== 9. 施工照片模块测试 ====================
def test_construction_photos_module(token: str, user_id: int, result: TestResult):
    """测试施工照片功能"""
    print_section("9. 施工照片模块测试")
    
    # 9.1 获取施工照片列表
    try:
        resp = requests.get(
            f"{BASE_URL}/construction-photos",
            params={"page": 1, "page_size": 20},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json().get("data", {}) if resp.json().get("code") == 0 else resp.json()
        photos = data.get("list", [])
        result.add_pass(f"获取施工照片列表成功 (共{len(photos)}张)")
    except Exception as e:
        result.add_fail("获取施工照片列表失败", e)
    
    # 9.2 获取OSS上传策略
    try:
        resp = requests.get(
            f"{BASE_URL}/oss/upload-policy",
            params={"stage": "material"},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("获取OSS上传策略成功")
    except Exception as e:
        result.add_warning(f"获取OSS上传策略失败: {e}")

# ==================== 10. 消息模块测试 ====================
def test_message_module(token: str, user_id: int, result: TestResult):
    """测试消息中心功能"""
    print_section("10. 消息模块测试")
    
    # 10.1 获取消息列表
    try:
        resp = requests.get(
            f"{BASE_URL}/messages",
            params={"page": 1, "page_size": 50},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json().get("data", {}) if resp.json().get("code") == 0 else resp.json()
        messages = data.get("list", []) if isinstance(data, dict) else data
        if isinstance(messages, list):
            result.add_pass(f"获取消息列表成功 (共{len(messages)}条)")
        else:
            result.add_pass("获取消息列表成功")
    except Exception as e:
        result.add_fail("获取消息列表失败", e)
    
    # 10.2 获取未读消息数
    try:
        resp = requests.get(
            f"{BASE_URL}/messages/unread-count",
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("获取未读消息数成功")
    except Exception as e:
        result.add_fail("获取未读消息数失败", e)
    
    # 10.3 标记全部已读
    try:
        resp = requests.put(
            f"{BASE_URL}/messages/read-all",
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("标记全部已读成功")
    except Exception as e:
        result.add_warning(f"标记全部已读失败: {e}")

# ==================== 11. 支付模块测试 ====================
def test_payment_module(token: str, user_id: int, result: TestResult):
    """测试支付功能"""
    print_section("11. 支付模块测试")
    
    # 11.1 获取订单列表
    try:
        resp = requests.get(
            f"{BASE_URL}/payments/orders",
            params={"page": 1, "page_size": 10},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("获取订单列表成功")
    except Exception as e:
        result.add_fail("获取订单列表失败", e)

# ==================== 12. 数据管理模块测试 ====================
def test_data_manage_module(token: str, user_id: int, result: TestResult):
    """测试数据管理功能"""
    print_section("12. 数据管理模块测试")
    
    # 12.1 获取报告列表
    try:
        resp = requests.get(
            f"{BASE_URL}/reports",
            params={"page": 1, "page_size": 10},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("获取报告列表成功")
    except Exception as e:
        result.add_warning(f"获取报告列表失败: {e}")

# ==================== 13. 材料库模块测试 ====================
def test_material_library_module(token: str, user_id: int, result: TestResult):
    """测试材料库功能"""
    print_section("13. 材料库模块测试")
    
    # 13.1 搜索材料
    try:
        resp = requests.get(
            f"{BASE_URL}/material-library/search",
            params={"keyword": "防水涂料"},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("搜索材料成功")
    except Exception as e:
        result.add_warning(f"搜索材料失败: {e}")
    
    # 13.2 获取常用材料
    try:
        resp = requests.get(
            f"{BASE_URL}/material-library/common",
            params={"category": "防水"},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("获取常用材料成功")
    except Exception as e:
        result.add_warning(f"获取常用材料失败: {e}")

# ==================== 14. 意见反馈模块测试 ====================
def test_feedback_module(token: str, user_id: int, result: TestResult):
    """测试意见反馈功能"""
    print_section("14. 意见反馈模块测试")
    
    # 14.1 提交反馈
    try:
        resp = requests.post(
            f"{BASE_URL}/feedback",
            json={"content": "测试反馈内容"},
            headers=get_auth_headers(token, user_id),
            timeout=10
        )
        resp.raise_for_status()
        result.add_pass("提交反馈成功")
    except Exception as e:
        result.add_warning(f"提交反馈失败: {e}")

# ==================== 主函数 ====================
def main():
    """执行所有测试"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}装修避坑管家 - 全功能前后端联调测试{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    # 登录
    token, user_id = login()
    if not token or not user_id:
        print(f"{Colors.RED}❌ 登录失败，无法继续测试{Colors.RESET}")
        return 1
    
    # 创建测试结果对象
    result = TestResult("全功能测试")
    
    # 执行所有模块测试
    test_user_module(token, user_id, result)
    test_city_module(token, user_id, result)
    test_company_module(token, user_id, result)
    test_quote_module(token, user_id, result)
    test_contract_module(token, user_id, result)
    test_construction_module(token, user_id, result)
    test_material_check_module(token, user_id, result)
    test_acceptance_module(token, user_id, result)
    test_construction_photos_module(token, user_id, result)
    test_message_module(token, user_id, result)
    test_payment_module(token, user_id, result)
    test_data_manage_module(token, user_id, result)
    test_material_library_module(token, user_id, result)
    test_feedback_module(token, user_id, result)
    
    # 输出测试结果汇总
    print_section("测试结果汇总")
    print(f"{Colors.BOLD}总测试数: {result.passed + result.failed}{Colors.RESET}")
    print(f"{Colors.GREEN}通过: {result.passed}{Colors.RESET}")
    print(f"{Colors.RED}失败: {result.failed}{Colors.RESET}")
    
    if result.errors:
        print(f"\n{Colors.RED}失败详情:{Colors.RESET}")
        for error in result.errors:
            print(f"  ❌ {error}")
    
    if result.warnings:
        print(f"\n{Colors.YELLOW}警告:{Colors.RESET}")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")
    
    # 计算通过率
    total = result.passed + result.failed
    if total > 0:
        pass_rate = (result.passed / total) * 100
        print(f"\n{Colors.BOLD}通过率: {pass_rate:.1f}%{Colors.RESET}")
    
    return 0 if result.failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

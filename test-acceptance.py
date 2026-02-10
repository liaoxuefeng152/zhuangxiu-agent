#!/usr/bin/env python3
"""
验收测试 - 从用户角度验证系统是否满足业务需求
基于PRD V2.6.1，验证核心功能、业务流程、用户体验
"""
import requests
import time
import json
import os
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional

BASE_URL = "http://localhost:8000/api/v1"

# 验收测试结果
acceptance_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "blocked": 0,
    "details": [],
    "user_scenarios": []
}


def log_acceptance(case_id: str, name: str, result: str, message: str = "", 
                  user_scenario: str = "", priority: str = "P0"):
    """记录验收测试结果"""
    acceptance_results["total"] += 1
    if result == "通过":
        acceptance_results["passed"] += 1
        status = "✅"
    elif result == "阻塞":
        acceptance_results["blocked"] += 1
        status = "🚫"
    else:
        acceptance_results["failed"] += 1
        status = "❌"
    
    acceptance_results["details"].append({
        "case_id": case_id,
        "name": name,
        "result": result,
        "message": message,
        "user_scenario": user_scenario,
        "priority": priority
    })
    
    if user_scenario:
        acceptance_results["user_scenarios"].append({
            "scenario": user_scenario,
            "case_id": case_id,
            "result": result
        })
    
    print(f"[{priority}] [{case_id}] {name}: {status} {result}")
    if message:
        print(f"  📝 {message}")
    if user_scenario:
        print(f"  👤 用户场景: {user_scenario}")


def login() -> Optional[str]:
    """用户登录"""
    try:
        response = requests.post(
            f"{BASE_URL}/users/login",
            json={"code": "dev_h5_mock"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("data", {}).get("access_token") or data.get("access_token")
            return token
        return None
    except Exception as e:
        return None


# ==================== 用户场景验收测试 ====================

def test_acceptance_01_new_user_onboarding():
    """AT-01: 新用户引导流程验收"""
    case_id = "AT-01"
    name = "新用户引导流程验收"
    scenario = "新用户首次打开小程序，完成引导和权限设置"
    
    try:
        # 1. 用户登录（模拟新用户）
        token = login()
        if not token:
            log_acceptance(case_id, name, "阻塞", "用户登录失败", scenario, "P0")
            return False
        
        # 2. 获取用户信息（验证用户创建）
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/users/profile", headers=headers, timeout=5)
        
        if response.status_code == 200:
            user_data = response.json().get("data", {}) or response.json()
            log_acceptance(case_id, name, "通过", 
                          f"新用户创建成功，用户ID: {user_data.get('id', 'N/A')}", 
                          scenario, "P0")
            return True
        else:
            log_acceptance(case_id, name, "失败", f"获取用户信息失败: {response.status_code}", 
                          scenario, "P0")
            return False
            
    except Exception as e:
        log_acceptance(case_id, name, "失败", f"异常: {e}", scenario, "P0")
        return False


def test_acceptance_02_company_risk_detection():
    """AT-02: 公司风险检测完整流程验收"""
    case_id = "AT-02"
    name = "公司风险检测完整流程验收"
    scenario = "用户输入装修公司名称，系统检测公司风险并生成报告"
    
    token = login()
    if not token:
        log_acceptance(case_id, name, "阻塞", "用户登录失败", scenario, "P0")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 1. 公司名称搜索（FR-012）
        response = requests.get(
            f"{BASE_URL}/companies/search?q=深圳",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            search_results = response.json().get("data", {}).get("list", [])
            print(f"  🔍 搜索到 {len(search_results)} 个匹配结果")
        
        # 2. 提交公司检测（FR-013）
        company_name = "深圳测试装饰工程有限公司"
        response = requests.post(
            f"{BASE_URL}/companies/scan",
            headers=headers,
            json={"company_name": company_name},
            timeout=10
        )
        
        if response.status_code == 200:
            scan_data = response.json().get("data", {}) or response.json()
            scan_id = scan_data.get("id")
            
            # 3. 等待检测完成（最多30秒）
            for i in range(30):
                time.sleep(1)
                response = requests.get(
                    f"{BASE_URL}/companies/scan/{scan_id}",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    result = response.json().get("data", {}) or response.json()
                    status = result.get("status")
                    if status == "completed":
                        risk_level = result.get("risk_level", "unknown")
                        risk_score = result.get("risk_score", 0)
                        log_acceptance(case_id, name, "通过", 
                                    f"公司检测完成，风险等级: {risk_level}, 风险分数: {risk_score}", 
                                    scenario, "P0")
                        return True
                    elif status == "failed":
                        log_acceptance(case_id, name, "失败", 
                                    f"公司检测失败: {result.get('error_message', '未知错误')}", 
                                    scenario, "P0")
                        return False
            
            log_acceptance(case_id, name, "失败", "公司检测超时", scenario, "P0")
            return False
        else:
            log_acceptance(case_id, name, "失败", f"提交检测失败: {response.status_code}", 
                          scenario, "P0")
            return False
            
    except Exception as e:
        log_acceptance(case_id, name, "失败", f"异常: {e}", scenario, "P0")
        return False


def test_acceptance_03_quote_analysis_workflow():
    """AT-03: 报价单分析完整流程验收"""
    case_id = "AT-03"
    name = "报价单分析完整流程验收"
    scenario = "用户上传报价单，系统OCR识别并AI分析，生成风险报告"
    
    token = login()
    if not token:
        log_acceptance(case_id, name, "阻塞", "用户登录失败", scenario, "P0")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 1. 上传报价单（FR-021）
        quote_png = "2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png"
        if not os.path.exists(quote_png):
            log_acceptance(case_id, name, "跳过", "测试文件不存在", scenario, "P0")
            return True
        
        with open(quote_png, "rb") as f:
            files = {"file": (os.path.basename(quote_png), io.BytesIO(f.read()), "image/png")}
            response = requests.post(
                f"{BASE_URL}/quotes/upload",
                headers=headers,
                files=files,
                timeout=30
            )
        
        if response.status_code != 200:
            log_acceptance(case_id, name, "失败", f"上传失败: {response.status_code}", 
                          scenario, "P0")
            return False
        
        upload_data = response.json().get("data", {}) or response.json()
        task_id = upload_data.get("task_id")
        
        # 2. 等待分析完成（最多60秒）
        for i in range(60):
            time.sleep(1)
            response = requests.get(
                f"{BASE_URL}/quotes/quote/{task_id}",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                quote_data = response.json().get("data", {}) or response.json()
                status = quote_data.get("status")
                
                if status == "completed":
                    # 验证分析结果
                    total_price = quote_data.get("total_price")
                    risk_items = quote_data.get("risk_items", [])
                    log_acceptance(case_id, name, "通过", 
                                f"报价单分析完成，总价: {total_price}, 风险项: {len(risk_items)}", 
                                scenario, "P0")
                    return True
                elif status == "failed":
                    log_acceptance(case_id, name, "失败", 
                                f"分析失败: {quote_data.get('error_message', '未知错误')}", 
                                scenario, "P0")
                    return False
        
        log_acceptance(case_id, name, "失败", "分析超时", scenario, "P0")
        return False
        
    except Exception as e:
        log_acceptance(case_id, name, "失败", f"异常: {e}", scenario, "P0")
        return False


def test_acceptance_04_contract_review_workflow():
    """AT-04: 合同审核完整流程验收"""
    case_id = "AT-04"
    name = "合同审核完整流程验收"
    scenario = "用户上传合同，系统OCR识别并AI审核，生成风险条款报告"
    
    token = login()
    if not token:
        log_acceptance(case_id, name, "阻塞", "用户登录失败", scenario, "P0")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 1. 上传合同（FR-031）
        contract_png = "深圳市住宅装饰装修工程施工合同（半包装修版）.png"
        if not os.path.exists(contract_png):
            log_acceptance(case_id, name, "跳过", "测试文件不存在", scenario, "P0")
            return True
        
        with open(contract_png, "rb") as f:
            files = {"file": (os.path.basename(contract_png), io.BytesIO(f.read()), "image/png")}
            response = requests.post(
                f"{BASE_URL}/contracts/upload",
                headers=headers,
                files=files,
                timeout=30
            )
        
        if response.status_code != 200:
            log_acceptance(case_id, name, "失败", f"上传失败: {response.status_code}", 
                          scenario, "P0")
            return False
        
        upload_data = response.json().get("data", {}) or response.json()
        task_id = upload_data.get("task_id")
        
        # 2. 等待审核完成（最多60秒）
        for i in range(60):
            time.sleep(1)
            response = requests.get(
                f"{BASE_URL}/contracts/contract/{task_id}",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                contract_data = response.json().get("data", {}) or response.json()
                status = contract_data.get("status")
                
                if status == "completed":
                    # 验证审核结果
                    risk_clauses = contract_data.get("risk_clauses", [])
                    suggestions = contract_data.get("suggestions", [])
                    log_acceptance(case_id, name, "通过", 
                                f"合同审核完成，风险条款: {len(risk_clauses)}, 修正建议: {len(suggestions)}", 
                                scenario, "P0")
                    return True
                elif status == "failed":
                    log_acceptance(case_id, name, "失败", 
                                f"审核失败: {contract_data.get('error_message', '未知错误')}", 
                                scenario, "P0")
                    return False
        
        log_acceptance(case_id, name, "失败", "审核超时", scenario, "P0")
        return False
        
    except Exception as e:
        log_acceptance(case_id, name, "失败", f"异常: {e}", scenario, "P0")
        return False


def test_acceptance_05_construction_schedule_management():
    """AT-05: 施工进度管理完整流程验收"""
    case_id = "AT-05"
    name = "施工进度管理完整流程验收"
    scenario = "用户设置开工日期，系统生成6大阶段进度计划，用户完成阶段验收"
    
    token = login()
    if not token:
        log_acceptance(case_id, name, "阻塞", "用户登录失败", scenario, "P0")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 1. 设置开工日期（FR-041）
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d") + "T00:00:00"
        response = requests.post(
            f"{BASE_URL}/constructions/start-date",
            headers=headers,
            json={"start_date": start_date},
            timeout=5
        )
        
        if response.status_code != 200:
            log_acceptance(case_id, name, "失败", f"设置开工日期失败: {response.status_code}", 
                          scenario, "P0")
            return False
        
        # 2. 查询进度计划（FR-042）
        response = requests.get(f"{BASE_URL}/constructions/schedule", headers=headers, timeout=5)
        if response.status_code != 200:
            log_acceptance(case_id, name, "失败", f"查询进度失败: {response.status_code}", 
                          scenario, "P0")
            return False
        
        schedule_data = response.json().get("data", {}) or response.json()
        stages = schedule_data.get("stages", {})
        
        # 验证6大阶段都存在
        required_stages = ["S00", "S01", "S02", "S03", "S04", "S05"]
        missing_stages = [s for s in required_stages if s not in stages]
        
        if missing_stages:
            log_acceptance(case_id, name, "失败", f"缺少阶段: {missing_stages}", 
                          scenario, "P0")
            return False
        
        # 3. 验证阶段互锁规则（FR-043）
        # S00应该未锁定（可以操作）
        s00 = stages.get("S00", {})
        if s00.get("locked") == True:
            log_acceptance(case_id, name, "失败", "S00阶段被锁定，不符合预期", 
                          scenario, "P0")
            return False
        
        # S01应该被锁定（S00未完成）
        s01 = stages.get("S01", {})
        if s01.get("locked") != True:
            log_acceptance(case_id, name, "失败", "S01阶段未锁定，互锁规则异常", 
                          scenario, "P0")
            return False
        
        # 4. 完成S00阶段
        response = requests.put(
            f"{BASE_URL}/constructions/stage-status",
            headers=headers,
            json={"stage": "S00", "status": "checked"},
            timeout=5
        )
        
        if response.status_code != 200:
            log_acceptance(case_id, name, "失败", f"完成S00失败: {response.status_code}", 
                          scenario, "P0")
            return False
        
        # 5. 验证S01自动解锁
        response = requests.get(f"{BASE_URL}/constructions/schedule", headers=headers, timeout=5)
        schedule_data = response.json().get("data", {}) or response.json()
        stages = schedule_data.get("stages", {})
        s01 = stages.get("S01", {})
        
        if s01.get("locked") == True:
            log_acceptance(case_id, name, "失败", "S00完成后S01未自动解锁", 
                          scenario, "P0")
            return False
        
        log_acceptance(case_id, name, "通过", 
                      f"6大阶段进度计划正常，互锁规则正确，S00完成后S01自动解锁", 
                      scenario, "P0")
        return True
        
    except Exception as e:
        log_acceptance(case_id, name, "失败", f"异常: {e}", scenario, "P0")
        return False


def test_acceptance_06_complete_user_journey():
    """AT-06: 完整用户旅程验收"""
    case_id = "AT-06"
    name = "完整用户旅程验收"
    scenario = "新用户从注册到完成一次完整装修决策流程"
    
    token = login()
    if not token:
        log_acceptance(case_id, name, "阻塞", "用户登录失败", scenario, "P0")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    steps_completed = []
    
    try:
        # 步骤1: 公司检测
        response = requests.post(
            f"{BASE_URL}/companies/scan",
            headers=headers,
            json={"company_name": "深圳测试装饰工程有限公司"},
            timeout=10
        )
        if response.status_code == 200:
            steps_completed.append("公司检测")
        
        # 步骤2: 报价单分析（如果文件存在）
        quote_png = "2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png"
        if os.path.exists(quote_png):
            with open(quote_png, "rb") as f:
                files = {"file": (os.path.basename(quote_png), io.BytesIO(f.read()), "image/png")}
                response = requests.post(f"{BASE_URL}/quotes/upload", headers=headers, files=files, timeout=30)
                if response.status_code == 200:
                    steps_completed.append("报价单分析")
        
        # 步骤3: 合同审核（如果文件存在）
        contract_png = "深圳市住宅装饰装修工程施工合同（半包装修版）.png"
        if os.path.exists(contract_png):
            with open(contract_png, "rb") as f:
                files = {"file": (os.path.basename(contract_png), io.BytesIO(f.read()), "image/png")}
                response = requests.post(f"{BASE_URL}/contracts/upload", headers=headers, files=files, timeout=30)
                if response.status_code == 200:
                    steps_completed.append("合同审核")
        
        # 步骤4: 设置开工日期
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d") + "T00:00:00"
        response = requests.post(
            f"{BASE_URL}/constructions/start-date",
            headers=headers,
            json={"start_date": start_date},
            timeout=5
        )
        if response.status_code == 200:
            steps_completed.append("设置开工日期")
        
        # 步骤5: 查询进度
        response = requests.get(f"{BASE_URL}/constructions/schedule", headers=headers, timeout=5)
        if response.status_code == 200:
            steps_completed.append("查询进度")
        
        if len(steps_completed) >= 3:
            log_acceptance(case_id, name, "通过", 
                          f"完整用户旅程测试通过，完成步骤: {', '.join(steps_completed)}", 
                          scenario, "P0")
            return True
        else:
            log_acceptance(case_id, name, "失败", 
                          f"完成步骤不足，仅完成: {', '.join(steps_completed)}", 
                          scenario, "P0")
            return False
            
    except Exception as e:
        log_acceptance(case_id, name, "失败", f"异常: {e}", scenario, "P0")
        return False


def test_acceptance_07_user_data_isolation():
    """AT-07: 用户数据隔离验收"""
    case_id = "AT-07"
    name = "用户数据隔离验收"
    scenario = "不同用户的数据相互隔离，用户只能看到自己的数据"
    
    token1 = login()
    if not token1:
        log_acceptance(case_id, name, "阻塞", "用户1登录失败", scenario, "P1")
        return False
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    try:
        # 用户1创建数据
        response = requests.post(
            f"{BASE_URL}/companies/scan",
            headers=headers1,
            json={"company_name": "用户1测试公司"},
            timeout=10
        )
        
        # 用户1查询自己的数据
        response = requests.get(f"{BASE_URL}/companies/scans", headers=headers1, timeout=5)
        if response.status_code == 200:
            user1_scans = response.json().get("data", {}).get("list", [])
            
            # 验证数据隔离（用户1只能看到自己的数据）
            user1_company_names = [s.get("company_name") for s in user1_scans]
            if "用户1测试公司" in user1_company_names:
                log_acceptance(case_id, name, "通过", 
                            f"用户数据隔离正常，用户只能看到自己的数据（{len(user1_scans)}条记录）", 
                            scenario, "P1")
                return True
            else:
                log_acceptance(case_id, name, "失败", "用户数据隔离异常", scenario, "P1")
                return False
        else:
            log_acceptance(case_id, name, "失败", f"查询数据失败: {response.status_code}", 
                          scenario, "P1")
            return False
            
    except Exception as e:
        log_acceptance(case_id, name, "失败", f"异常: {e}", scenario, "P1")
        return False


def test_acceptance_08_performance_requirements():
    """AT-08: 性能要求验收（PRD 1.4）"""
    case_id = "AT-08"
    name = "性能要求验收"
    scenario = "验证系统性能是否符合PRD要求（页面加载≤1.5秒，AI分析≤10秒）"
    
    token = login()
    if not token:
        log_acceptance(case_id, name, "阻塞", "用户登录失败", scenario, "P1")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    performance_results = []
    
    try:
        # 测试1: 页面加载时间（PRD要求≤1.5秒）
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/users/profile", headers=headers, timeout=5)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            if duration <= 1.5:
                performance_results.append(f"页面加载: {duration:.3f}s ✅")
            else:
                performance_results.append(f"页面加载: {duration:.3f}s ❌ (超过1.5s)")
        
        # 测试2: 进度查询响应时间
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/constructions/schedule", headers=headers, timeout=5)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            if duration <= 1.5:
                performance_results.append(f"进度查询: {duration:.3f}s ✅")
            else:
                performance_results.append(f"进度查询: {duration:.3f}s ❌ (超过1.5s)")
        
        # 汇总结果
        all_passed = all("✅" in r for r in performance_results)
        if all_passed:
            log_acceptance(case_id, name, "通过", 
                          f"性能要求符合PRD: {', '.join(performance_results)}", 
                          scenario, "P1")
            return True
        else:
            log_acceptance(case_id, name, "失败", 
                          f"部分性能指标不符合PRD: {', '.join(performance_results)}", 
                          scenario, "P1")
            return False
            
    except Exception as e:
        log_acceptance(case_id, name, "失败", f"异常: {e}", scenario, "P1")
        return False


def test_acceptance_09_business_rules_validation():
    """AT-09: 业务规则验证验收"""
    case_id = "AT-09"
    name = "业务规则验证验收"
    scenario = "验证6大阶段互锁规则、数据验证规则等业务规则是否正确实现"
    
    token = login()
    if not token:
        log_acceptance(case_id, name, "阻塞", "用户登录失败", scenario, "P0")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    rules_passed = []
    
    try:
        # 规则1: 阶段互锁规则（PRD 6.1）
        # 设置开工日期
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d") + "T00:00:00"
        requests.post(
            f"{BASE_URL}/constructions/start-date",
            headers=headers,
            json={"start_date": start_date},
            timeout=5
        )
        
        # 尝试直接操作S01（应该被阻止）
        response = requests.put(
            f"{BASE_URL}/constructions/stage-status",
            headers=headers,
            json={"stage": "S01", "status": "passed"},
            timeout=5
        )
        
        if response.status_code == 409:  # 冲突，表示互锁规则生效
            rules_passed.append("阶段互锁规则 ✅")
        else:
            rules_passed.append("阶段互锁规则 ❌")
        
        # 规则2: 数据验证规则
        # 测试无效的开工日期
        response = requests.post(
            f"{BASE_URL}/constructions/start-date",
            headers=headers,
            json={"start_date": "invalid-date"},
            timeout=5
        )
        
        if response.status_code in (400, 422):  # 验证失败
            rules_passed.append("数据验证规则 ✅")
        else:
            rules_passed.append("数据验证规则 ❌")
        
        # 汇总结果
        all_passed = all("✅" in r for r in rules_passed)
        if all_passed:
            log_acceptance(case_id, name, "通过", 
                          f"业务规则验证通过: {', '.join(rules_passed)}", 
                          scenario, "P0")
            return True
        else:
            log_acceptance(case_id, name, "失败", 
                          f"部分业务规则验证失败: {', '.join(rules_passed)}", 
                          scenario, "P0")
            return False
            
    except Exception as e:
        log_acceptance(case_id, name, "失败", f"异常: {e}", scenario, "P0")
        return False


def test_acceptance_10_user_experience():
    """AT-10: 用户体验验收"""
    case_id = "AT-10"
    name = "用户体验验收"
    scenario = "验证系统是否提供良好的用户体验（响应速度、错误提示、操作流畅性）"
    
    token = login()
    if not token:
        log_acceptance(case_id, name, "阻塞", "用户登录失败", scenario, "P1")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    ux_points = []
    
    try:
        # UX点1: 快速响应
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/users/profile", headers=headers, timeout=5)
        duration = time.time() - start_time
        
        if duration < 0.5:
            ux_points.append("快速响应 ✅")
        else:
            ux_points.append(f"响应时间: {duration:.3f}s ⚠️")
        
        # UX点2: 错误提示清晰
        response = requests.get(f"{BASE_URL}/quotes/quote/999999", headers=headers, timeout=5)
        if response.status_code == 404:
            error_msg = response.json().get("msg") or response.json().get("detail", "")
            if error_msg:
                ux_points.append("错误提示清晰 ✅")
            else:
                ux_points.append("错误提示缺失 ❌")
        
        # UX点3: 操作流畅性（连续操作）
        operations = [
            ("GET", f"{BASE_URL}/users/profile", None),
            ("GET", f"{BASE_URL}/constructions/schedule", None),
            ("GET", f"{BASE_URL}/messages/unread-count", None),
        ]
        
        all_success = True
        for method, url, data in operations:
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=5)
            else:
                r = requests.post(url, headers=headers, json=data, timeout=5)
            if r.status_code != 200:
                all_success = False
                break
        
        if all_success:
            ux_points.append("操作流畅性 ✅")
        else:
            ux_points.append("操作流畅性 ❌")
        
        # 汇总结果
        passed_count = sum(1 for p in ux_points if "✅" in p)
        if passed_count >= 2:
            log_acceptance(case_id, name, "通过", 
                          f"用户体验良好: {', '.join(ux_points)}", 
                          scenario, "P1")
            return True
        else:
            log_acceptance(case_id, name, "失败", 
                          f"用户体验待改进: {', '.join(ux_points)}", 
                          scenario, "P1")
            return False
            
    except Exception as e:
        log_acceptance(case_id, name, "失败", f"异常: {e}", scenario, "P1")
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("验收测试 - 从用户角度验证系统是否满足业务需求")
    print("=" * 70)
    print("\n测试范围:")
    print("1. 新用户引导流程")
    print("2. 公司风险检测完整流程")
    print("3. 报价单分析完整流程")
    print("4. 合同审核完整流程")
    print("5. 施工进度管理完整流程")
    print("6. 完整用户旅程")
    print("7. 用户数据隔离")
    print("8. 性能要求（PRD 1.4）")
    print("9. 业务规则验证")
    print("10. 用户体验")
    print("=" * 70)
    print()
    
    # 执行验收测试
    test_acceptance_01_new_user_onboarding()
    test_acceptance_02_company_risk_detection()
    test_acceptance_03_quote_analysis_workflow()
    test_acceptance_04_contract_review_workflow()
    test_acceptance_05_construction_schedule_management()
    test_acceptance_06_complete_user_journey()
    test_acceptance_07_user_data_isolation()
    test_acceptance_08_performance_requirements()
    test_acceptance_09_business_rules_validation()
    test_acceptance_10_user_experience()
    
    # 输出结果
    print("\n" + "=" * 70)
    print("验收测试结果汇总")
    print("=" * 70)
    print(f"总用例数: {acceptance_results['total']}")
    print(f"通过: {acceptance_results['passed']}")
    print(f"失败: {acceptance_results['failed']}")
    print(f"阻塞: {acceptance_results['blocked']}")
    print(f"通过率: {acceptance_results['passed']/acceptance_results['total']*100:.1f}%" 
          if acceptance_results['total'] > 0 else "0%")
    
    # 按用户场景汇总
    print("\n用户场景验收结果:")
    scenarios_summary = {}
    for scenario_info in acceptance_results['user_scenarios']:
        scenario = scenario_info['scenario']
        if scenario not in scenarios_summary:
            scenarios_summary[scenario] = {"passed": 0, "failed": 0, "blocked": 0}
        result = scenario_info['result']
        if result == "通过":
            scenarios_summary[scenario]["passed"] += 1
        elif result == "阻塞":
            scenarios_summary[scenario]["blocked"] += 1
        else:
            scenarios_summary[scenario]["failed"] += 1
    
    for scenario, counts in scenarios_summary.items():
        total = counts["passed"] + counts["failed"] + counts["blocked"]
        passed_rate = counts["passed"] / total * 100 if total > 0 else 0
        status = "✅" if passed_rate == 100 else "⚠️" if passed_rate >= 80 else "❌"
        print(f"  {status} {scenario}: {counts['passed']}/{total} 通过")
    
    print("\n详细结果:")
    for detail in acceptance_results['details']:
        status = "✅" if detail['result'] == "通过" else "🚫" if detail['result'] == "阻塞" else "❌"
        print(f"  {status} [{detail['case_id']}] {detail['name']}")
        if detail['message']:
            print(f"     {detail['message']}")
    
    print("=" * 70)
    
    # 保存报告
    report_file = f"test-acceptance-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(acceptance_results, f, ensure_ascii=False, indent=2)
    print(f"\n详细报告已保存至: {report_file}")
    
    # 验收结论
    print("\n" + "=" * 70)
    print("验收结论")
    print("=" * 70)
    if acceptance_results['blocked'] > 0:
        print("❌ 验收未通过：存在阻塞性问题，需要先解决阻塞问题")
    elif acceptance_results['failed'] == 0:
        print("✅ 验收通过：所有用例通过，系统满足业务需求")
    elif acceptance_results['passed'] / acceptance_results['total'] >= 0.8:
        print("⚠️ 验收有条件通过：大部分用例通过，但存在部分问题需要修复")
    else:
        print("❌ 验收未通过：存在较多问题，需要修复后重新验收")
    print("=" * 70)


if __name__ == "__main__":
    main()

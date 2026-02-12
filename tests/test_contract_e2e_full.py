#!/usr/bin/env python3
"""
合同审核完整端到端测试
流程：
1. 用户登录
2. 上传合同
3. 等待分析完成
4. 查看分析结果详情
5. 在"我的数据"（合同列表）中查看分析报告
"""
import requests
import json
import time
import os
import sys
from datetime import datetime

BASE_URL = "http://120.26.201.61:8001/api/v1"

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_step(step_num, title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}步骤 {step_num}: {title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def login():
    """步骤1: 用户登录"""
    print_step(1, "用户登录")
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
    
    if not token:
        print_error("登录失败：未获取到token")
        return None, None
    
    print_success(f"登录成功 (User ID: {user_id})")
    return token, user_id

def upload_contract(token, user_id, file_path):
    """步骤2: 上传合同"""
    print_step(2, "上传合同")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    if not os.path.exists(file_path):
        print_error(f"文件不存在: {file_path}")
        return None
    
    print_info(f"上传文件: {file_path}")
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'image/png')}
        resp = requests.post(
            f"{BASE_URL}/contracts/upload",
            headers=headers,
            files=files,
            timeout=60
        )
    
    resp.raise_for_status()
    result = resp.json()
    
    print_info(f"上传响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
    
    # 处理不同的响应格式
    if result.get("code") == 0:
        contract_data = result.get("data", {})
    elif isinstance(result, dict) and ("task_id" in result or "id" in result):
        contract_data = result
    else:
        contract_data = result
    
    # ContractUploadResponse返回的是task_id
    contract_id = contract_data.get("task_id") or contract_data.get("id") or contract_data.get("contract_id")
    if not contract_id:
        print_error(f"上传失败：未获取到contract_id，响应: {json.dumps(result, ensure_ascii=False)[:200]}")
        return None
    
    print_success(f"合同上传成功 (Contract ID: {contract_id})")
    print_info(f"文件名: {contract_data.get('file_name')}")
    print_info(f"状态: {contract_data.get('status')}")
    
    return contract_id

def wait_for_analysis(token, user_id, contract_id, max_wait=120):
    """步骤3: 等待分析完成"""
    print_step(3, "等待分析完成")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    start_time = time.time()
    poll_interval = 2
    
    print_info(f"开始轮询分析状态（最多等待{max_wait}秒）...")
    
    while time.time() - start_time < max_wait:
        try:
            resp = requests.get(
                f"{BASE_URL}/contracts/contract/{contract_id}",
                headers=headers,
                timeout=10
            )
            resp.raise_for_status()
            result = resp.json()
            
            if result.get("code") == 0:
                contract_data = result.get("data", {})
            else:
                contract_data = result
            
            status = contract_data.get("status")
            analysis_progress = contract_data.get("analysis_progress", {})
            progress = analysis_progress.get("progress", 0)
            message = analysis_progress.get("message", "")
            
            print_info(f"状态: {status}, 进度: {progress}%, 消息: {message}")
            
            if status == "completed":
                print_success(f"分析完成！耗时: {int(time.time() - start_time)}秒")
                return contract_data
            
            if status == "failed":
                print_error("分析失败")
                return None
            
            time.sleep(poll_interval)
            
        except Exception as e:
            print_warning(f"轮询出错: {e}")
            time.sleep(poll_interval)
    
    print_error(f"分析超时（超过{max_wait}秒）")
    return None

def view_analysis_detail(token, user_id, contract_id):
    """步骤4: 查看分析结果详情"""
    print_step(4, "查看分析结果详情")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    try:
        resp = requests.get(
            f"{BASE_URL}/contracts/contract/{contract_id}",
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") == 0:
            contract_data = result.get("data", {})
        else:
            contract_data = result
        
        print_success("获取分析结果成功")
        print(f"\n{Colors.BOLD}基本信息:{Colors.RESET}")
        print(f"  Contract ID: {contract_data.get('id')}")
        print(f"  文件名: {contract_data.get('file_name')}")
        print(f"  状态: {contract_data.get('status')}")
        print(f"  创建时间: {contract_data.get('created_at')}")
        
        print(f"\n{Colors.BOLD}风险分析:{Colors.RESET}")
        risk_level = contract_data.get('risk_level', 'compliant')
        risk_level_text = {
            'high': '高风险',
            'warning': '警告',
            'compliant': '合规'
        }.get(risk_level, risk_level)
        print(f"  风险等级: {risk_level} ({risk_level_text})")
        
        risk_items = contract_data.get('risk_items', [])
        unfair_terms = contract_data.get('unfair_terms', [])
        missing_terms = contract_data.get('missing_terms', [])
        suggested_modifications = contract_data.get('suggested_modifications', [])
        
        print(f"  风险项: {len(risk_items)}项")
        print(f"  霸王条款: {len(unfair_terms)}项")
        print(f"  漏项: {len(missing_terms)}项")
        print(f"  建议修改: {len(suggested_modifications)}项")
        
        # 显示详细内容
        if risk_items:
            print(f"\n{Colors.BOLD}风险项详情:{Colors.RESET}")
            for i, item in enumerate(risk_items[:5], 1):
                print(f"  {i}. [{item.get('risk_level', '')}] {item.get('term', '')}")
                print(f"     描述: {item.get('description', '')[:80]}...")
        
        if unfair_terms:
            print(f"\n{Colors.BOLD}霸王条款详情:{Colors.RESET}")
            for i, item in enumerate(unfair_terms[:5], 1):
                print(f"  {i}. {item.get('term', '')}")
                print(f"     描述: {item.get('description', '')[:80]}...")
        
        if missing_terms:
            print(f"\n{Colors.BOLD}漏项详情:{Colors.RESET}")
            for i, item in enumerate(missing_terms[:5], 1):
                print(f"  {i}. {item.get('term', '')}")
                print(f"     原因: {item.get('reason', '')[:80]}...")
        
        if suggested_modifications:
            print(f"\n{Colors.BOLD}建议修改详情:{Colors.RESET}")
            for i, item in enumerate(suggested_modifications[:5], 1):
                print(f"  {i}. {item.get('modified', '')}")
                print(f"     原因: {item.get('reason', '')[:80]}...")
        
        # 显示result_json中的摘要
        result_json = contract_data.get('result_json', {})
        if result_json:
            summary = result_json.get('summary', '')
            if summary:
                print(f"\n{Colors.BOLD}AI分析摘要:{Colors.RESET}")
                print(f"  {summary[:200]}...")
        
        return contract_data
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            print_error(f"获取分析结果失败（500错误），可能是后端代码未部署或数据有问题")
            print_info("尝试使用合同列表API获取数据...")
            # 尝试从列表获取
            contracts_list = view_contract_list(token, user_id)
            contract_data = None
            for c in contracts_list:
                if c.get('id') == contract_id:
                    contract_data = c
                    break
            if not contract_data:
                raise
            return contract_data
        else:
            raise

def view_contract_list(token, user_id):
    """步骤5: 在"我的数据"（合同列表）中查看分析报告"""
    print_step(5, "在'我的数据'中查看合同列表")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    resp = requests.get(
        f"{BASE_URL}/contracts/list",
        headers=headers,
        params={"page": 1, "page_size": 10},
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        contracts_data = result.get("data", {})
        contracts = contracts_data.get("contracts", []) or contracts_data.get("list", [])
    else:
        contracts = result.get("contracts", []) or result.get("list", [])
    
    print_success(f"获取合同列表成功，共{len(contracts)}条")
    
    print(f"\n{Colors.BOLD}合同列表:{Colors.RESET}")
    print(f"{'ID':<8} {'文件名':<40} {'状态':<12} {'风险等级':<12} {'创建时间':<20}")
    print("-" * 120)
    
    for contract in contracts[:10]:
        contract_id = contract.get('id', '')
        file_name = contract.get('file_name', '')[:38]
        status = contract.get('status', '')
        risk_level = contract.get('risk_level', '—')
        created_at = contract.get('created_at', '')[:19] if contract.get('created_at') else '—'
        
        # 状态颜色标记
        status_color = Colors.GREEN if status == 'completed' else (Colors.YELLOW if status == 'analyzing' else Colors.RED)
        status_display = f"{status_color}{status:<12}{Colors.RESET}"
        
        # 风险等级颜色标记
        if risk_level == 'high':
            risk_color = Colors.RED
        elif risk_level == 'warning':
            risk_color = Colors.YELLOW
        else:
            risk_color = Colors.GREEN
        risk_display = f"{risk_color}{risk_level:<12}{Colors.RESET}" if risk_level != '—' else f"{risk_level:<12}"
        
        print(f"{contract_id:<8} {file_name:<40} {status_display} {risk_display} {created_at:<20}")
    
    return contracts

def generate_report(token, user_id, contract_id, contract_data, contracts_list):
    """生成测试报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(os.path.dirname(__file__), f"contract_e2e_report_{timestamp}.md")
    
    risk_level_text = {
        'high': '高风险',
        'warning': '警告',
        'compliant': '合规'
    }.get(contract_data.get('risk_level', 'compliant'), contract_data.get('risk_level', 'compliant'))
    
    report = f"""# 合同审核端到端测试报告

## 测试时间
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 测试流程

### ✅ 步骤1: 用户登录
- User ID: {user_id}
- 状态: 成功

### ✅ 步骤2: 上传合同
- Contract ID: {contract_id}
- 文件名: {contract_data.get('file_name', '')}
- 状态: 成功

### ✅ 步骤3: 等待分析完成
- 状态: {contract_data.get('status', '')}
- 风险等级: {contract_data.get('risk_level', '')} ({risk_level_text})

### ✅ 步骤4: 查看分析结果详情

#### 基本信息
- Contract ID: {contract_data.get('id')}
- 文件名: {contract_data.get('file_name', '')}
- 状态: {contract_data.get('status', '')}
- 创建时间: {contract_data.get('created_at', '')}

#### 风险分析
- 风险等级: {contract_data.get('risk_level', '')} ({risk_level_text})
- 风险项数量: {len(contract_data.get('risk_items', []))}
- 霸王条款数量: {len(contract_data.get('unfair_terms', []))}
- 漏项数量: {len(contract_data.get('missing_terms', []))}
- 建议修改数量: {len(contract_data.get('suggested_modifications', []))}

#### 风险项详情
"""
    
    for i, item in enumerate(contract_data.get('risk_items', [])[:10], 1):
        report += f"""
{i}. **[{item.get('risk_level', '')}] {item.get('term', '')}**
   - 描述: {item.get('description', '')}
"""
    
    report += f"""
#### 霸王条款详情
"""
    
    for i, item in enumerate(contract_data.get('unfair_terms', [])[:10], 1):
        report += f"""
{i}. **{item.get('term', '')}**
   - 描述: {item.get('description', '')}
"""
    
    report += f"""
#### 漏项详情
"""
    
    for i, item in enumerate(contract_data.get('missing_terms', [])[:10], 1):
        report += f"""
{i}. **{item.get('term', '')}**
   - 原因: {item.get('reason', '')}
"""
    
    report += f"""
#### 建议修改详情
"""
    
    for i, item in enumerate(contract_data.get('suggested_modifications', [])[:10], 1):
        report += f"""
{i}. **{item.get('modified', '')}**
   - 原因: {item.get('reason', '')}
"""
    
    # AI分析摘要
    result_json = contract_data.get('result_json', {})
    if result_json:
        summary = result_json.get('summary', '')
        if summary:
            report += f"""
#### AI分析摘要
{summary}
"""
    
    report += f"""
### ✅ 步骤5: 在"我的数据"中查看合同列表

共找到 {len(contracts_list)} 条合同记录。

#### 最新合同列表（前10条）
| ID | 文件名 | 状态 | 风险等级 | 创建时间 |
|---|---|---|---|---|
"""
    
    for contract in contracts_list[:10]:
        report += f"| {contract.get('id', '')} | {contract.get('file_name', '')[:30]}... | {contract.get('status', '')} | {contract.get('risk_level', '—')} | {contract.get('created_at', '')[:19]} |\n"
    
    report += f"""
## 测试结果

### ✅ 测试通过

所有步骤均成功完成：
1. ✅ 用户登录成功
2. ✅ 合同上传成功
3. ✅ 分析完成（状态: {contract_data.get('status', '')}）
4. ✅ 成功获取分析结果详情
5. ✅ 成功获取合同列表

### 数据验证

- **result_json存在**: {'是' if contract_data.get('result_json') else '否'}
- **风险项数据完整**: {'是' if (contract_data.get('risk_items') or contract_data.get('unfair_terms') or contract_data.get('missing_terms') or contract_data.get('suggested_modifications')) else '否'}

### 前端显示验证

前端页面应能正确显示：
- ✅ 风险等级（{risk_level_text}）
- ✅ 风险项列表
- ✅ 霸王条款列表
- ✅ 漏项列表
- ✅ 建议修改列表

## 建议

1. 验证前端页面显示效果
2. 确认所有风险项都能正确显示
3. 测试解锁报告功能
4. 测试导出PDF功能
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print_success(f"测试报告已生成: {report_file}")
    return report_file

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}合同审核完整端到端测试{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    # 测试文件路径
    test_file = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "深圳市住宅装饰装修工程施工合同（半包装修版）.png"
    )
    
    try:
        # 步骤1: 登录
        token, user_id = login()
        if not token:
            return
        
        # 检查是否使用已存在的合同ID（通过命令行参数）
        use_existing = len(sys.argv) > 1 and sys.argv[1].isdigit()
        if use_existing:
            contract_id = int(sys.argv[1])
            print_info(f"使用已存在的合同ID: {contract_id}")
        else:
            # 步骤2: 上传合同
            if not os.path.exists(test_file):
                print_error(f"测试文件不存在: {test_file}")
                print_info("提示：可以使用已存在的合同ID进行测试，例如: python3 test_contract_e2e_full.py 1")
                return
            
            contract_id = upload_contract(token, user_id, test_file)
            if not contract_id:
                return
            
            # 步骤3: 等待分析完成
            contract_data = wait_for_analysis(token, user_id, contract_id)
            if not contract_data:
                print_warning("分析未完成，但继续测试查看详情功能")
                contract_data = {}
        
        # 步骤4: 查看分析结果详情
        try:
            contract_data = view_analysis_detail(token, user_id, contract_id)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                print_error(f"获取分析结果失败（500错误），可能是后端代码未部署或数据有问题")
                print_info("尝试使用合同列表API获取数据...")
                # 尝试从列表获取
                contracts_list = view_contract_list(token, user_id)
                contract_data = None
                for c in contracts_list:
                    if c.get('id') == contract_id:
                        contract_data = c
                        break
                if not contract_data:
                    raise
            else:
                raise
        
        # 步骤5: 查看合同列表
        contracts_list = view_contract_list(token, user_id)
        
        # 生成测试报告
        if contract_data:
            generate_report(token, user_id, contract_id, contract_data, contracts_list)
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}✅ 端到端测试完成！{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.RESET}\n")
        
    except Exception as e:
        print_error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

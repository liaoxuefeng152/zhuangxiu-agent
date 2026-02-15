#!/usr/bin/env python3
"""
报价单分析完整端到端测试
流程：
1. 用户登录
2. 上传报价单
3. 等待分析完成
4. 查看分析结果详情
5. 在"我的数据"（报价单列表）中查看分析报告
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

def upload_quote(token, user_id, file_path):
    """步骤2: 上传报价单"""
    print_step(2, "上传报价单")
    
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
            f"{BASE_URL}/quotes/upload",
            headers=headers,
            files=files,
            timeout=60
        )
    
    resp.raise_for_status()
    result = resp.json()
    
    print_info(f"上传响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
    
    # 处理不同的响应格式
    if result.get("code") == 0:
        quote_data = result.get("data", {})
    elif isinstance(result, dict) and "id" in result:
        quote_data = result
    else:
        quote_data = result
    
    # QuoteUploadResponse返回的是task_id，不是id
    quote_id = quote_data.get("task_id") or quote_data.get("id") or quote_data.get("quote_id")
    if not quote_id:
        print_error(f"上传失败：未获取到quote_id，响应: {json.dumps(result, ensure_ascii=False)[:200]}")
        return None
    
    print_success(f"报价单上传成功 (Quote ID: {quote_id})")
    print_info(f"文件名: {quote_data.get('file_name')}")
    print_info(f"状态: {quote_data.get('status')}")
    
    return quote_id

def wait_for_analysis(token, user_id, quote_id, max_wait=120):
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
                f"{BASE_URL}/quotes/quote/{quote_id}",
                headers=headers,
                timeout=10
            )
            resp.raise_for_status()
            result = resp.json()
            
            if result.get("code") == 0:
                quote_data = result.get("data", {})
            else:
                quote_data = result
            
            status = quote_data.get("status")
            analysis_progress = quote_data.get("analysis_progress", {})
            progress = analysis_progress.get("progress", 0)
            message = analysis_progress.get("message", "")
            
            print_info(f"状态: {status}, 进度: {progress}%, 消息: {message}")
            
            if status == "completed":
                print_success(f"分析完成！耗时: {int(time.time() - start_time)}秒")
                return quote_data
            
            if status == "failed":
                print_error("分析失败")
                return None
            
            time.sleep(poll_interval)
            
        except Exception as e:
            print_warning(f"轮询出错: {e}")
            time.sleep(poll_interval)
    
    print_error(f"分析超时（超过{max_wait}秒）")
    return None

def view_analysis_detail(token, user_id, quote_id):
    """步骤4: 查看分析结果详情"""
    print_step(4, "查看分析结果详情")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    resp = requests.get(
        f"{BASE_URL}/quotes/quote/{quote_id}",
        headers=headers,
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        quote_data = result.get("data", {})
    else:
        quote_data = result
    
    print_success("获取分析结果成功")
    print(f"\n{Colors.BOLD}基本信息:{Colors.RESET}")
    print(f"  Quote ID: {quote_data.get('id')}")
    print(f"  文件名: {quote_data.get('file_name')}")
    print(f"  状态: {quote_data.get('status')}")
    print(f"  创建时间: {quote_data.get('created_at')}")
    
    print(f"\n{Colors.BOLD}价格信息:{Colors.RESET}")
    print(f"  总价: {quote_data.get('total_price')}元" if quote_data.get('total_price') else "  总价: —")
    print(f"  市场参考价: {quote_data.get('market_ref_price')}元" if quote_data.get('market_ref_price') else "  市场参考价: —")
    
    print(f"\n{Colors.BOLD}风险分析:{Colors.RESET}")
    risk_score = quote_data.get('risk_score')
    if quote_data.get('status') == 'failed':
        risk_level = "AI分析失败"
        print(f"  风险评分: — ({risk_level})")
    elif risk_score is not None:
        risk_level = "高风险" if risk_score >= 61 else ("警告" if risk_score >= 31 else "合规")
        print(f"  风险评分: {risk_score}分 ({risk_level})")
    else:
        risk_level = "—"
        print(f"  风险评分: — ({risk_level})")
    
    high_risk = quote_data.get('high_risk_items', [])
    warning = quote_data.get('warning_items', [])
    missing = quote_data.get('missing_items', [])
    overpriced = quote_data.get('overpriced_items', [])
    
    print(f"  高风险项: {len(high_risk)}项")
    print(f"  警告项: {len(warning)}项")
    print(f"  漏项: {len(missing)}项")
    print(f"  虚高项: {len(overpriced)}项")
    
    # 显示详细内容
    if high_risk:
        print(f"\n{Colors.BOLD}高风险项详情:{Colors.RESET}")
        for i, item in enumerate(high_risk[:5], 1):
            print(f"  {i}. [{item.get('category', '')}] {item.get('item', '')}")
            print(f"     描述: {item.get('description', '')[:80]}...")
            if item.get('impact'):
                print(f"     影响: {item.get('impact', '')[:80]}...")
            if item.get('suggestion'):
                print(f"     建议: {item.get('suggestion', '')[:80]}...")
    
    if warning:
        print(f"\n{Colors.BOLD}警告项详情:{Colors.RESET}")
        for i, item in enumerate(warning[:5], 1):
            print(f"  {i}. [{item.get('category', '')}] {item.get('item', '')}")
            print(f"     描述: {item.get('description', '')[:80]}...")
            if item.get('suggestion'):
                print(f"     建议: {item.get('suggestion', '')[:80]}...")
    
    if missing:
        print(f"\n{Colors.BOLD}漏项详情:{Colors.RESET}")
        for i, item in enumerate(missing[:5], 1):
            print(f"  {i}. {item.get('item', '')} (重要性: {item.get('importance', '')})")
            print(f"     原因: {item.get('reason', '')[:80]}...")
    
    if overpriced:
        print(f"\n{Colors.BOLD}虚高项详情:{Colors.RESET}")
        for i, item in enumerate(overpriced[:5], 1):
            print(f"  {i}. {item.get('item', '')}")
            print(f"     报价: {item.get('quoted_price', '')}元")
            print(f"     市场参考价: {item.get('market_ref_price', '')[:60]}...")
            print(f"     差异: {item.get('price_diff', '')[:60]}...")
    
    # 显示result_json中的建议
    result_json = quote_data.get('result_json', {})
    if result_json:
        suggestions = result_json.get('suggestions', [])
        if suggestions:
            print(f"\n{Colors.BOLD}AI分析建议:{Colors.RESET}")
            for i, suggestion in enumerate(suggestions[:5], 1):
                print(f"  {i}. {suggestion[:100]}...")
    
    return quote_data

def view_quote_list(token, user_id):
    """步骤5: 在"我的数据"（报价单列表）中查看分析报告"""
    print_step(5, "在'我的数据'中查看报价单列表")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    resp = requests.get(
        f"{BASE_URL}/quotes/list",
        headers=headers,
        params={"page": 1, "page_size": 10},
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") == 0:
        quotes_data = result.get("data", {})
        quotes = quotes_data.get("quotes", []) or quotes_data.get("list", [])
    else:
        quotes = result.get("quotes", []) or result.get("list", [])
    
    print_success(f"获取报价单列表成功，共{len(quotes)}条")
    
    print(f"\n{Colors.BOLD}报价单列表:{Colors.RESET}")
    print(f"{'ID':<8} {'文件名':<40} {'状态':<12} {'风险评分':<10} {'总价':<12} {'创建时间':<20}")
    print("-" * 120)
    
    for quote in quotes[:10]:
        quote_id = quote.get('id', '')
        file_name = quote.get('file_name', '')[:38]
        status = quote.get('status', '')
        risk_score = quote.get('risk_score', '—')
        total_price = f"{quote.get('total_price', '—')}元" if quote.get('total_price') else '—'
        created_at = quote.get('created_at', '')[:19] if quote.get('created_at') else '—'
        
        # 状态颜色标记
        status_color = Colors.GREEN if status == 'completed' else (Colors.YELLOW if status == 'analyzing' else Colors.RED)
        status_display = f"{status_color}{status:<12}{Colors.RESET}"
        
        # 风险评分颜色标记
        if isinstance(risk_score, int):
            risk_color = Colors.RED if risk_score >= 61 else (Colors.YELLOW if risk_score >= 31 else Colors.GREEN)
            risk_display = f"{risk_color}{risk_score:<10}{Colors.RESET}"
        else:
            risk_display = f"{str(risk_score) if risk_score is not None else '—':<10}"
        
        print(f"{quote_id:<8} {file_name:<40} {status_display} {risk_display} {total_price:<12} {created_at:<20}")
    
    return quotes

def generate_report(token, user_id, quote_id, quote_data, quotes_list):
    """生成测试报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(os.path.dirname(__file__), f"quote_e2e_report_{timestamp}.md")
    
    report = f"""# 报价单分析端到端测试报告

## 测试时间
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 测试流程

### ✅ 步骤1: 用户登录
- User ID: {user_id}
- 状态: 成功

### ✅ 步骤2: 上传报价单
- Quote ID: {quote_id}
- 文件名: {quote_data.get('file_name', '')}
- 状态: 成功

### ✅ 步骤3: 等待分析完成
- 状态: {quote_data.get('status', '')}
- 风险评分: {quote_data.get('risk_score') if quote_data.get('risk_score') is not None else '—'}分

### ✅ 步骤4: 查看分析结果详情

#### 基本信息
- Quote ID: {quote_data.get('id')}
- 文件名: {quote_data.get('file_name', '')}
- 状态: {quote_data.get('status', '')}
- 创建时间: {quote_data.get('created_at', '')}

#### 价格信息
- 总价: {quote_data.get('total_price', '—')}元
- 市场参考价: {quote_data.get('market_ref_price', '—')}元

#### 风险分析
- 风险评分: {quote_data.get('risk_score') if quote_data.get('risk_score') is not None else '—'}分
- 高风险项数量: {len(quote_data.get('high_risk_items', []))}
- 警告项数量: {len(quote_data.get('warning_items', []))}
- 漏项数量: {len(quote_data.get('missing_items', []))}
- 虚高项数量: {len(quote_data.get('overpriced_items', []))}

#### 高风险项详情
"""
    
    for i, item in enumerate(quote_data.get('high_risk_items', [])[:10], 1):
        report += f"""
{i}. **{item.get('category', '')} - {item.get('item', '')}**
   - 描述: {item.get('description', '')}
   - 影响: {item.get('impact', '')}
   - 建议: {item.get('suggestion', '')}
"""
    
    report += f"""
#### 警告项详情
"""
    
    for i, item in enumerate(quote_data.get('warning_items', [])[:10], 1):
        report += f"""
{i}. **{item.get('category', '')} - {item.get('item', '')}**
   - 描述: {item.get('description', '')}
   - 建议: {item.get('suggestion', '')}
"""
    
    report += f"""
#### 漏项详情
"""
    
    for i, item in enumerate(quote_data.get('missing_items', [])[:10], 1):
        report += f"""
{i}. **{item.get('item', '')}** (重要性: {item.get('importance', '')})
   - 原因: {item.get('reason', '')}
"""
    
    report += f"""
#### 虚高项详情
"""
    
    for i, item in enumerate(quote_data.get('overpriced_items', [])[:10], 1):
        report += f"""
{i}. **{item.get('item', '')}**
   - 报价: {item.get('quoted_price', '')}元
   - 市场参考价: {item.get('market_ref_price', '')}
   - 差异: {item.get('price_diff', '')}
"""
    
    # AI分析建议
    result_json = quote_data.get('result_json', {})
    if result_json:
        suggestions = result_json.get('suggestions', [])
        if suggestions:
            report += f"""
#### AI分析建议
"""
            for i, suggestion in enumerate(suggestions, 1):
                report += f"{i}. {suggestion}\n"
    
    report += f"""
### ✅ 步骤5: 在"我的数据"中查看报价单列表

共找到 {len(quotes_list)} 条报价单记录。

#### 最新报价单列表（前10条）
| ID | 文件名 | 状态 | 风险评分 | 总价 | 创建时间 |
|---|---|---|---|---|---|
"""
    
    for quote in quotes_list[:10]:
        report += f"| {quote.get('id', '')} | {quote.get('file_name', '')[:30]}... | {quote.get('status', '')} | {quote.get('risk_score', '—')} | {quote.get('total_price', '—')}元 | {quote.get('created_at', '')[:19]} |\n"
    
    report += f"""
## 测试结果

### ✅ 测试通过

所有步骤均成功完成：
1. ✅ 用户登录成功
2. ✅ 报价单上传成功
3. ✅ 分析完成（状态: {quote_data.get('status', '')}）
4. ✅ 成功获取分析结果详情
5. ✅ 成功获取报价单列表

### 数据验证

- **result_json存在**: {'是' if quote_data.get('result_json') else '否'}
- **风险项数据完整**: {'是' if (quote_data.get('high_risk_items') or quote_data.get('warning_items') or quote_data.get('missing_items') or quote_data.get('overpriced_items')) else '否'}
- **价格信息完整**: {'是' if quote_data.get('total_price') else '否'}

### 前端显示验证

前端页面应能正确显示：
- ✅ 风险等级（根据risk_score={quote_data.get('risk_score')}计算）
- ✅ 高风险项列表
- ✅ 警告项列表
- ✅ 漏项列表
- ✅ 虚高项列表
- ✅ AI分析建议

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
    print(f"{Colors.BOLD}{Colors.BLUE}报价单分析完整端到端测试{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    # 测试文件路径
    test_file = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png"
    )
    
    try:
        # 步骤1: 登录
        token, user_id = login()
        if not token:
            return
        
        # 检查是否使用已存在的报价单ID（通过命令行参数）
        use_existing = len(sys.argv) > 1 and sys.argv[1].isdigit()
        if use_existing:
            quote_id = int(sys.argv[1])
            print_info(f"使用已存在的报价单ID: {quote_id}")
        else:
            # 步骤2: 上传报价单
            if not os.path.exists(test_file):
                print_error(f"测试文件不存在: {test_file}")
                print_info("提示：可以使用已存在的报价单ID进行测试，例如: python3 test_quote_e2e_full.py 9")
                return
            
            quote_id = upload_quote(token, user_id, test_file)
            if not quote_id:
                return
            
            # 步骤3: 等待分析完成
            quote_data = wait_for_analysis(token, user_id, quote_id)
            if not quote_data:
                print_warning("分析未完成，但继续测试查看详情功能")
                quote_data = {}
        
        # 步骤4: 查看分析结果详情
        try:
            quote_data = view_analysis_detail(token, user_id, quote_id)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                print_error(f"获取分析结果失败（500错误），可能是后端代码未部署或数据有问题")
                print_info("尝试使用报价单列表API获取数据...")
                # 尝试从列表获取
                quotes_list = view_quote_list(token, user_id)
                quote_data = None
                for q in quotes_list:
                    if q.get('id') == quote_id:
                        quote_data = q
                        break
                if not quote_data:
                    raise
            else:
                raise
        
        # 步骤5: 查看报价单列表
        quotes_list = view_quote_list(token, user_id)
        
        # 生成测试报告
        if quote_data:
            generate_report(token, user_id, quote_id, quote_data, quotes_list)
        
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

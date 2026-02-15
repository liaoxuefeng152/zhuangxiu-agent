#!/usr/bin/env python3
"""
消息提醒功能 端到端测试
覆盖：消息列表、未读数、创建消息、单条已读、全部已读、提醒计划、用户提醒设置
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://120.26.201.61:8001/api/v1"

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_step(step_num, title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}步骤 {step_num}: {title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def _headers(token, user_id):
    return {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id),
        "Content-Type": "application/json"
    }

def login():
    """用户登录"""
    print_step(1, "用户登录")
    resp = requests.post(
        f"{BASE_URL}/users/login",
        json={"code": "dev_weapp_mock"},
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    data = result.get("data", result) if result.get("code") == 0 else result
    token = data.get("access_token")
    user_id = data.get("user_id")
    if not token or not user_id:
        print_error("登录失败：未获取到 token 或 user_id")
        return None, None
    print_success(f"登录成功 (User ID: {user_id})")
    return token, user_id

def test_message_list(token, user_id):
    """消息列表"""
    print_step(2, "消息列表查询")
    resp = requests.get(
        f"{BASE_URL}/messages",
        headers=_headers(token, user_id),
        params={"page": 1, "page_size": 10},
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        print_error(f"消息列表失败: {result.get('msg', result)}")
        return None, []
    data = result.get("data", {})
    lst = data.get("list", [])
    total = data.get("total", 0)
    print_success(f"消息列表成功，共 {total} 条")
    print_info(f"当前页返回 {len(lst)} 条")
    return data, lst

def test_unread_count(token, user_id):
    """未读消息数"""
    print_step(3, "未读消息数")
    resp = requests.get(
        f"{BASE_URL}/messages/unread-count",
        headers=_headers(token, user_id),
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        print_error(f"未读数失败: {result.get('msg', result)}")
        return None
    count = result.get("data", {}).get("count", 0)
    print_success(f"未读数量: {count}")
    return count

def test_create_message(token, user_id):
    """创建测试消息"""
    print_step(4, "创建测试消息")
    payload = {
        "category": "progress",
        "title": "E2E测试-施工提醒",
        "content": "测试消息内容",
        "summary": "测试摘要"
    }
    resp = requests.post(
        f"{BASE_URL}/messages",
        headers=_headers(token, user_id),
        json=payload,
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        print_error(f"创建消息失败: {result.get('msg', result)}")
        return None
    msg = result.get("data", {})
    msg_id = msg.get("id")
    print_success(f"创建消息成功 (ID: {msg_id})")
    return msg_id

def test_mark_single_read(token, user_id, msg_id):
    """单条消息标记已读"""
    print_step(5, "单条消息标记已读")
    resp = requests.put(
        f"{BASE_URL}/messages/{msg_id}/read",
        headers=_headers(token, user_id),
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        print_error(f"标记已读失败: {result.get('msg', result)}")
        return False
    print_success(f"消息 {msg_id} 已标记为已读")
    return True

def test_mark_all_read(token, user_id):
    """全部已读"""
    print_step(6, "全部已读")
    resp = requests.put(
        f"{BASE_URL}/messages/read-all",
        headers=_headers(token, user_id),
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        print_error(f"全部已读失败: {result.get('msg', result)}")
        return False
    print_success("全部已读成功")
    return True

def test_reminder_schedule(token, user_id):
    """提醒计划"""
    print_step(7, "提醒计划")
    today = datetime.now().strftime("%Y-%m-%d")
    resp = requests.get(
        f"{BASE_URL}/constructions/reminder-schedule",
        headers=_headers(token, user_id),
        params={"date": today},
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        print_error(f"提醒计划失败: {result.get('msg', result)}")
        return None
    lst = result.get("data", {}).get("list", [])
    print_success(f"提醒计划查询成功 (date={today})")
    if lst:
        print_info(f"今日有 {len(lst)} 条提醒")
    else:
        print_warning("今日无提醒（可能无施工进度或阶段日期）")
    return lst

def test_get_user_settings(token, user_id):
    """获取用户设置"""
    print_step(8, "获取用户设置")
    resp = requests.get(
        f"{BASE_URL}/users/settings",
        headers=_headers(token, user_id),
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        print_error(f"获取设置失败: {result.get('msg', result)}")
        return None
    settings = result.get("data", {})
    rd = settings.get("reminder_days_before", 3)
    print_success(f"获取设置成功，提醒提前天数: {rd}")
    return settings

def test_update_user_settings(token, user_id, reminder_days_before=5):
    """更新用户提醒设置"""
    print_step(9, "更新用户提醒设置")
    resp = requests.put(
        f"{BASE_URL}/users/settings",
        headers=_headers(token, user_id),
        params={"reminder_days_before": reminder_days_before},
        timeout=10
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        print_error(f"更新设置失败: {result.get('msg', result)}")
        return False
    print_success(f"提醒提前天数已更新为 {reminder_days_before} 天")
    return True

def run_e2e():
    report = []
    token, user_id = login()
    if not token or not user_id:
        report.append(("登录", False, "未获取 token/user_id"))
        return report

    report.append(("登录", True, "OK"))

    # 2. 消息列表
    try:
        _, lst = test_message_list(token, user_id)
        report.append(("消息列表", True, f"共 {len(lst)} 条"))
    except Exception as e:
        report.append(("消息列表", False, str(e)))

    # 3. 未读数
    try:
        count = test_unread_count(token, user_id)
        report.append(("未读数", True, f"count={count}"))
    except Exception as e:
        report.append(("未读数", False, str(e)))

    # 4. 创建消息
    msg_id = None
    try:
        msg_id = test_create_message(token, user_id)
        report.append(("创建消息", msg_id is not None, "OK" if msg_id else "失败"))
    except Exception as e:
        report.append(("创建消息", False, str(e)))

    # 5. 单条已读
    if msg_id:
        try:
            ok = test_mark_single_read(token, user_id, msg_id)
            report.append(("单条已读", ok, "OK" if ok else "失败"))
        except Exception as e:
            report.append(("单条已读", False, str(e)))
    else:
        report.append(("单条已读", None, "跳过(无消息ID)"))

    # 6. 全部已读
    try:
        ok = test_mark_all_read(token, user_id)
        report.append(("全部已读", ok, "OK" if ok else "失败"))
    except Exception as e:
        report.append(("全部已读", False, str(e)))

    # 7. 提醒计划
    try:
        lst = test_reminder_schedule(token, user_id)
        report.append(("提醒计划", True, f"{len(lst)} 条" if lst is not None else "无数据"))
    except Exception as e:
        report.append(("提醒计划", False, str(e)))

    # 8. 获取设置
    try:
        settings = test_get_user_settings(token, user_id)
        report.append(("获取用户设置", settings is not None, "OK" if settings else "失败"))
    except Exception as e:
        report.append(("获取用户设置", False, str(e)))

    # 9. 更新设置
    try:
        ok = test_update_user_settings(token, user_id, 5)
        report.append(("更新用户设置", ok, "OK" if ok else "失败"))
    except Exception as e:
        report.append(("更新用户设置", False, str(e)))

    return report

def main():
    print(f"\n{Colors.BOLD}消息提醒功能 端到端测试{Colors.RESET}")
    print(f"BASE_URL: {BASE_URL}\n")

    try:
        report = run_e2e()
    except Exception as e:
        print_error(f"测试异常: {e}")
        report = [("异常", False, str(e))]

    # 报告
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}测试报告{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

    passed = sum(1 for _, ok, _ in report if ok is True)
    failed = sum(1 for _, ok, _ in report if ok is False)
    skipped = sum(1 for _, ok, _ in report if ok is None)

    for name, ok, detail in report:
        if ok is True:
            status = f"{Colors.GREEN}通过{Colors.RESET}"
        elif ok is False:
            status = f"{Colors.RED}失败{Colors.RESET}"
        else:
            status = f"{Colors.YELLOW}跳过{Colors.RESET}"
        print(f"  {name}: {status} - {detail}")

    print(f"\n总计: {passed} 通过, {failed} 失败, {skipped} 跳过")
    print()

    # 写入报告文件
    with open("tests/report_message_reminder_e2e.txt", "w", encoding="utf-8") as f:
        f.write("消息提醒功能 端到端测试报告\n")
        f.write("=" * 50 + "\n")
        f.write(f"时间: {datetime.now().isoformat()}\n")
        f.write(f"BASE_URL: {BASE_URL}\n\n")
        for name, ok, detail in report:
            s = "通过" if ok is True else ("失败" if ok is False else "跳过")
            f.write(f"{name}: {s} - {detail}\n")
        f.write(f"\n总计: {passed} 通过, {failed} 失败, {skipped} 跳过\n")

    print_info("报告已写入 tests/report_message_reminder_e2e.txt")

    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    import sys
    main()

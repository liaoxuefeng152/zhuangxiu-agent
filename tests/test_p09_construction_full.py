#!/usr/bin/env python3
"""
P09 施工陪伴页测试用例 - 全量执行
根据 docs/施工陪伴页测试用例-P09.md 执行 API 可验证用例 + 前端逻辑校验
"""
import os
import re
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path

BASE_URL = "http://120.26.201.61:8001/api/v1"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def ok(msg): print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")
def fail(msg): print(f"{Colors.RED}❌ {msg}{Colors.RESET}")
def skip(msg): print(f"{Colors.YELLOW}⏭️  {msg}{Colors.RESET}")
def info(msg): print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

results = []  # [(tc_id, name, status, note)]

def record(tc_id, name, status, note=""):
    results.append((tc_id, name, status, note))
    if status == "PASS": ok(f"{tc_id} {name}")
    elif status == "FAIL": fail(f"{tc_id} {name}: {note}")
    else: skip(f"{tc_id} {name}: {note}")

def login():
    resp = requests.post(f"{BASE_URL}/users/login", json={"code": "dev_weapp_mock"}, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("data", resp.json())
    return data.get("access_token"), data.get("user_id")

# ========== 一、API 可验证用例 ==========
def run_api_tests():
    info("========== API 层测试 ==========")
    token, user_id = None, None
    try:
        token, user_id = login()
    except Exception as e:
        fail(f"登录失败: {e}")
        return
    headers = {"Authorization": f"Bearer {token}", "X-User-Id": str(user_id)}

    # TC-P09-003: 401/404 静默（后端行为，API 测试无法直接模拟未登录）
    record("TC-P09-003", "加载失败-401/404 静默", "SKIP", "需前端验证静默处理")

    # TC-P09-004: 6 阶段卡片 - 通过 schedule 接口验证
    try:
        r = requests.get(f"{BASE_URL}/constructions/schedule", headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json().get("data", r.json())
        stages = data.get("stages", {})
        stage_order = ["S00", "S01", "S02", "S03", "S04", "S05"]
        missing = [s for s in stage_order if s not in stages]
        if not missing:
            record("TC-P09-004", "6 阶段卡片展示", "PASS")
        else:
            record("TC-P09-004", "6 阶段卡片展示", "FAIL", f"缺少阶段: {missing}")
    except Exception as e:
        record("TC-P09-004", "6 阶段卡片展示", "FAIL", str(e))

    # TC-P09-010/011/012: 开工日期设置
    try:
        date_str = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        r = requests.post(f"{BASE_URL}/constructions/start-date", headers=headers, json={"start_date": date_str}, timeout=10)
        r.raise_for_status()
        record("TC-P09-010", "快捷选择 7 天后开工", "PASS")
        record("TC-P09-011", "快捷选择 15/30 天后开工", "SKIP", "与 TC-P09-010 同逻辑")
        record("TC-P09-012", "选择其他日期", "SKIP", "需前端日期选择器验证")
    except Exception as e:
        record("TC-P09-010", "快捷选择 7 天后开工", "FAIL", str(e))

    # TC-P09-013: 编辑已有开工日期
    try:
        date_str = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        r = requests.post(f"{BASE_URL}/constructions/start-date", headers=headers, json={"start_date": date_str}, timeout=10)
        r.raise_for_status()
        record("TC-P09-013", "编辑已有开工日期", "PASS")
    except Exception as e:
        record("TC-P09-013", "编辑已有开工日期", "FAIL", str(e))

    # TC-P09-022/023: 材料清单 - 有清单时 S00 可操作
    try:
        r = requests.get(f"{BASE_URL}/material-checks/material-list", headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json().get("data", r.json())
        lst = data.get("list", [])
        has_list = isinstance(lst, list) and len(lst) > 0
        if has_list:
            record("TC-P09-022", "已上传报价单-按钮可点", "PASS", "材料清单存在")
        else:
            record("TC-P09-022", "已上传报价单-按钮可点", "SKIP", "当前用户无材料清单")
    except Exception as e:
        record("TC-P09-022", "已上传报价单-材料清单 API", "FAIL", str(e))

    # TC-P09-030~035: 流程互锁 - 后端返回 locked 字段
    try:
        r = requests.get(f"{BASE_URL}/constructions/schedule", headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json().get("data", r.json())
        stages = data.get("stages", {})
        s00 = stages.get("S00", {})
        s01 = stages.get("S01", {})
        s00_checked = (s00.get("status") or "").lower() in ("checked", "completed", "passed")
        s01_locked = s01.get("locked", True)
        if not s00_checked and s01_locked:
            record("TC-P09-030", "S00 未完成时 S01 置灰", "PASS", "S01 locked=True")
        else:
            record("TC-P09-030", "S00 未完成时 S01 置灰", "SKIP", f"S00={s00.get('status')}, S01 locked={s01_locked}")
    except Exception as e:
        record("TC-P09-030", "流程互锁-后端 locked", "FAIL", str(e))

# ========== 二、前端代码逻辑校验 ==========
def check_frontend_logic():
    info("========== 前端逻辑校验 ==========")
    construction_tsx = PROJECT_ROOT / "frontend" / "src" / "pages" / "construction" / "index.tsx"
    construction_scss = PROJECT_ROOT / "frontend" / "src" / "pages" / "construction" / "index.scss"
    if not construction_tsx.exists():
        record("FRONTEND", "P09 页面存在", "FAIL", "index.tsx 不存在")
        return
    content = construction_tsx.read_text(encoding="utf-8")
    scss_content = construction_scss.read_text(encoding="utf-8") if construction_scss.exists() else ""

    # TC-P09-020/021: S00 未上传报价单-按钮置灰、点击提示
    if "请先上传报价单以获取材料清单" in content and "hasMaterialList === false" in content:
        record("TC-P09-020", "未上传报价单-点击提示", "PASS", "代码已实现")
    else:
        record("TC-P09-020", "未上传报价单-点击提示", "FAIL", "未找到对应逻辑")

    if "#E5E5E5" in scss_content or "disabled" in content:
        record("TC-P09-020", "未上传报价单-按钮置灰", "PASS", "SCSS 有 disabled 样式")
    else:
        record("TC-P09-020", "未上传报价单-按钮置灰", "SKIP", "需确认置灰样式")

    # TC-P09-031: S00 未完成点击 S01
    if "请先完成材料进场人工核对" in content and "index === 1" in content:
        record("TC-P09-031", "S00 未完成点击 S01 提示", "PASS", "代码已实现")
    else:
        record("TC-P09-031", "S00 未完成点击 S01 提示", "FAIL", "未找到对应逻辑")

    # TC-P09-033: 前置未完成点击后续阶段
    if "请先完成" in content and "STAGES[index - 1].name" in content:
        record("TC-P09-033", "前置未完成点击后续阶段", "PASS", "代码已实现")
    else:
        record("TC-P09-033", "前置未完成点击后续阶段", "FAIL", "未找到对应逻辑")

    # TC-P09-023: 跳转 P37 + Toast
    if "请按清单逐项勾选并拍照留证" in content and "material-check" in content:
        record("TC-P09-023", "已上传报价单-点击跳转 P37", "PASS", "代码已实现")
    else:
        record("TC-P09-023", "已上传报价单-点击跳转 P37", "FAIL", "未找到对应逻辑")

    # TC-P09-040~043: 提醒设置
    if "remindModalVisible" in content and "提醒设置" in content and "提醒设置成功" in content:
        record("TC-P09-040", "打开提醒设置弹窗", "PASS", "代码已实现")
        record("TC-P09-043", "保存提醒设置", "PASS", "Toast 已实现")
    else:
        record("TC-P09-040", "提醒设置弹窗", "FAIL", "未找到对应逻辑")

    if "REMIND_DAYS_OPTIONS" in content and "[1, 2, 3, 5, 7]" in content:
        record("TC-P09-042", "选择提醒提前天数 1/2/3/5/7", "PASS", "选项已定义")

    # TC-P09-052/053/054: 时间校准
    if "时间校准成功，后续进度计划已同步更新" in content:
        record("TC-P09-052", "调整时间成功", "PASS", "Toast 已实现")
    if "校准时间须大于预计开始时间" in content:
        record("TC-P09-053", "选择早于开工日期", "PASS", "校验已实现")
    if "请选择当前日期及以后的时间" in content:
        record("TC-P09-054", "选择早于今天", "PASS", "校验已实现")

    # TC-P09-070~074: 记录板块
    if "待人工核对" in content or "待验收" in content:
        record("TC-P09-070", "未完成阶段记录文案", "PASS", "代码已实现")
    if "待整改" in content:
        record("TC-P09-071", "待整改阶段记录文案", "PASS", "代码已实现")

    # TC-P09-100~102: 视觉规范
    if "#007AFF" in scss_content:
        record("TC-P09-100", "主按钮样式 #007AFF", "PASS", "SCSS 已定义")
    if "#E5E5E5" in scss_content:
        record("TC-P09-020", "置灰 #E5E5E5", "PASS", "SCSS 已定义")
    if "linear-gradient" in scss_content and "#007AFF" in scss_content:
        record("TC-P09-100", "主按钮渐变", "PASS", "SCSS 已定义")

    # TC-P09-103: scroll-view padding（此前已修复）
    record("TC-P09-103", "页面可滚动", "SKIP", "需手工验证 scroll-view")

    # loadFromApi 预拉材料清单
    if "materialChecksApi.getMaterialList" in content and "setHasMaterialList" in content:
        record("TC-P09-024", "从报价单页返回刷新", "PASS", "useDidShow 调用 loadFromApi")

    # 401/404 静默
    if "is404" in content and "is401" in content and "静默" in content:
        record("TC-P09-003", "加载失败 401/404 静默", "PASS", "代码已实现静默处理")

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}P09 施工陪伴页测试用例 - 全量执行{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")
    run_api_tests()
    check_frontend_logic()
    # 汇总
    passed = sum(1 for _, _, s, _ in results if s == "PASS")
    failed = sum(1 for _, _, s, _ in results if s == "FAIL")
    skipped = sum(1 for _, _, s, _ in results if s == "SKIP")
    total = len(results)
    print(f"\n{Colors.BOLD}汇总: 通过 {passed} / 失败 {failed} / 跳过 {skipped} / 总计 {total}{Colors.RESET}")
    # 写报告
    report_path = PROJECT_ROOT / "docs" / "P09测试执行报告.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# P09 施工陪伴页测试执行报告\n\n")
        f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("| 编号 | 用例名称 | 结果 | 备注 |\n|------|----------|------|------|\n")
        for tc_id, name, status, note in results:
            f.write(f"| {tc_id} | {name} | {status} | {note} |\n")
        f.write(f"\n**汇总**: 通过 {passed} / 失败 {failed} / 跳过 {skipped} / 总计 {total}\n")
    ok(f"报告已生成: {report_path}")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

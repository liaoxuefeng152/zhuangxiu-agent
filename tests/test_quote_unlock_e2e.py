#!/usr/bin/env python3
"""
装修报价分析 + 立即解锁9.9 + 支付成功 → 报告详情/我的数据 端到端测试

流程：
1. 登录
2. 上传报价单
3. 等待 AI 分析完成（明确输出：AI分析是否成功）
4. 创建报告解锁订单（立即解锁 9.9）
5. 确认支付
6. 校验：报告在 GET /reports（我的数据）中，且可访问报告详情

环境：请求阿里云开发环境 http://120.26.201.61:8001/api/v1
"""
import requests
import time
import os
import sys
from pathlib import Path

BASE_URL = "http://120.26.201.61:8001/api/v1"
# 测试用报价单图片（若不存在可传已存在的 quote_id：python test_quote_unlock_e2e.py <quote_id>）
FIXTURE_QUOTE = Path(__file__).resolve().parent / "fixtures" / "2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png"
# 可选：小图加快测试
FIXTURE_QUOTE_ALT = Path(__file__).resolve().parent / "fixtures" / "quote_sample.png"

def auth_headers(token: str, user_id: int):
    return {"Authorization": f"Bearer {token}", "X-User-Id": str(user_id)}

def login():
    r = requests.post(f"{BASE_URL}/users/login", json={"code": "dev_weapp_mock"}, timeout=10)
    r.raise_for_status()
    data = r.json().get("data") or r.json()
    token = data.get("access_token")
    user_id = data.get("user_id")
    if not token or not user_id:
        raise RuntimeError("登录失败：未获取 token 或 user_id")
    print("[1/6] 登录成功")
    return token, user_id

def upload_quote(token: str, user_id: int, file_path: Path) -> int:
    if not file_path.exists():
        raise FileNotFoundError(f"测试文件不存在: {file_path}")
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, "image/png")}
        r = requests.post(
            f"{BASE_URL}/quotes/upload",
            headers=auth_headers(token, user_id),
            files=files,
            timeout=60,
        )
    r.raise_for_status()
    raw = r.json()
    data = raw.get("data") if raw.get("code") == 0 else raw
    quote_id = data.get("task_id") or data.get("id") or data.get("quote_id")
    if not quote_id:
        raise RuntimeError(f"上传成功但未返回 quote_id，响应: {raw}")
    print(f"[2/6] 上传报价单成功 (quote_id={quote_id})")
    return int(quote_id)

def wait_for_analysis(token: str, user_id: int, quote_id: int, max_wait: int = 120) -> dict:
    """轮询直到 status=completed 或超时。返回当次 GET 的 quote 数据。若接口 500 则返回空 dict 并继续后续步骤。"""
    start = time.time()
    last_status = None
    while time.time() - start < max_wait:
        try:
            r = requests.get(
                f"{BASE_URL}/quotes/quote/{quote_id}",
                headers=auth_headers(token, user_id),
                timeout=10,
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 500:
                if time.time() - start < 30:
                    time.sleep(5)
                    continue
                print("[3/6] 查询分析结果接口返回 500，跳过轮询，继续后续解锁与我的数据校验")
                return {}
            raise
        raw = r.json()
        data = raw.get("data") if raw.get("code") == 0 else raw
        status = data.get("status")
        last_status = status
        progress = (data.get("analysis_progress") or {}).get("progress", 0)
        if status == "completed":
            print(f"[3/6] AI 分析完成（耗时约 {int(time.time() - start)} 秒）")
            return data
        if status == "failed":
            print("[3/6] AI 分析失败（status=failed）")
            return data
        time.sleep(3)
    print(f"[3/6] 等待 AI 分析超时（{max_wait}s），最后状态: {last_status}")
    return {}

def create_unlock_order(token: str, user_id: int, quote_id: int) -> tuple:
    """创建报告解锁订单，返回 (order_id, status)。"""
    r = requests.post(
        f"{BASE_URL}/payments/create",
        headers={**auth_headers(token, user_id), "Content-Type": "application/json"},
        json={
            "order_type": "report_single",
            "resource_type": "quote",
            "resource_id": quote_id,
        },
        timeout=10,
    )
    r.raise_for_status()
    raw = r.json()
    data = raw.get("data") if raw.get("code") == 0 else raw
    status = data.get("status")
    order_id = data.get("order_id") or 0
    if status == "completed" and (not order_id or order_id == 0):
        print("[4/6] 创建解锁订单成功（会员免费，无需支付）")
        return 0, "completed"
    if order_id and order_id > 0:
        print(f"[4/6] 创建解锁订单成功 (order_id={order_id})")
        return int(order_id), status
    raise RuntimeError(f"创建订单返回异常: {data}")

def confirm_paid(token: str, user_id: int, order_id: int):
    if not order_id or order_id <= 0:
        return
    r = requests.post(
        f"{BASE_URL}/payments/confirm-paid",
        headers={**auth_headers(token, user_id), "Content-Type": "application/json"},
        json={"order_id": order_id},
        timeout=10,
    )
    r.raise_for_status()
    print("[5/6] 确认支付成功")

def get_reports_list(token: str, user_id: int) -> list:
    r = requests.get(
        f"{BASE_URL}/reports",
        params={"page": 1, "page_size": 50},
        headers=auth_headers(token, user_id),
        timeout=10,
    )
    r.raise_for_status()
    raw = r.json()
    data = raw.get("data") if raw.get("code") == 0 else raw
    return data.get("list", [])

def main():
    print("\n" + "=" * 60)
    print("装修报价分析 → 立即解锁9.9 → 支付成功 → 报告详情/我的数据")
    print("=" * 60 + "\n")

    token, user_id = login()

    if len(sys.argv) > 1 and sys.argv[1].strip().isdigit():
        quote_id = int(sys.argv[1].strip())
        print(f"[2/6] 使用已有 quote_id={quote_id}，跳过上传")
        quote_data = wait_for_analysis(token, user_id, quote_id)
    else:
        path = FIXTURE_QUOTE if FIXTURE_QUOTE.exists() else FIXTURE_QUOTE_ALT
        quote_id = upload_quote(token, user_id, path)
        quote_data = wait_for_analysis(token, user_id, quote_id)

    # ----- AI 分析结论 -----
    status = quote_data.get("status")
    risk_score = quote_data.get("risk_score")
    has_risk_items = bool(
        quote_data.get("high_risk_items")
        or quote_data.get("warning_items")
        or quote_data.get("missing_items")
        or quote_data.get("overpriced_items")
    )
    result_json = quote_data.get("result_json")
    ai_success = (
        status == "completed"
        and (risk_score is not None or has_risk_items or (result_json and (result_json.get("suggestions") or result_json.get("high_risk_items"))))
    )
    print("\n" + "-" * 60)
    if ai_success:
        print("【AI 分析】结论: 成功")
        print(f"  - status: {status}")
        print(f"  - risk_score: {risk_score}")
        print(f"  - 有风险/建议数据: {has_risk_items or bool(result_json)}")
    else:
        print("【AI 分析】结论: 未成功或数据不完整")
        print(f"  - status: {status}")
        print(f"  - risk_score: {risk_score}")
        print(f"  - 有风险项: {has_risk_items}, result_json 存在: {bool(result_json)}")
    print("-" * 60 + "\n")

    order_id, order_status = create_unlock_order(token, user_id, quote_id)
    confirm_paid(token, user_id, order_id)

    reports = get_reports_list(token, user_id)
    in_list = any(
        (item.get("type") == "quote" and item.get("id") == quote_id)
        for item in reports
    )
    print("[6/6] 我的数据（GET /reports）:")
    if in_list:
        print("  ✅ 生成的报告在「我的数据」中")
    else:
        print("  ❌ 未在「我的数据」中找到本单报价报告")
    quote_items = [i for i in reports if i.get("type") == "quote"]
    print(f"  报价单类报告共 {len(quote_items)} 条；当前 quote_id={quote_id} 在列表中: {in_list}")

    # 再次拉取报告详情，确认已解锁
    try:
        r = requests.get(
            f"{BASE_URL}/quotes/quote/{quote_id}",
            headers=auth_headers(token, user_id),
            timeout=10,
        )
        r.raise_for_status()
        detail = (r.json().get("data") or r.json()) if r.ok else {}
    except Exception:
        detail = {}
    is_unlocked = detail.get("is_unlocked", False)
    print(f"  报告详情 is_unlocked: {is_unlocked}")

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"  AI 分析是否成功: {'是' if ai_success else '否'}")
    print(f"  报告是否在我的数据中: {'是' if in_list else '否'}")
    print(f"  报告是否已解锁: {'是' if is_unlocked else '否'}")
    print("=" * 60 + "\n")

    if not in_list or not ai_success:
        sys.exit(1)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except FileNotFoundError as e:
        print(f"错误: {e}")
        print("用法: python test_quote_unlock_e2e.py [quote_id]")
        print("  不传 quote_id 时需存在 fixtures 下的报价单图片")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

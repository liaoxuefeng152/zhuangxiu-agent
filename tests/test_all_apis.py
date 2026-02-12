#!/usr/bin/env python3
"""
全接口测试脚本 - 测试所有 API 端点
用法: python tests/test_all_apis.py [BASE_URL] [--skip-health] [--retry-health]
  BASE_URL: 默认 http://127.0.0.1:8000（若 localhost 报 Connection reset 可改用 127.0.0.1）
  --skip-health: 跳过健康检查，直接测 API
  --retry-health: 健康检查失败时重试 3 次（间隔 2 秒），用于等待后端启动
"""
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import quote

args = [a for a in sys.argv[1:] if not a.startswith("--")]
skip_health = "--skip-health" in sys.argv
retry_health = "--retry-health" in sys.argv
BASE = (args[0] if args else "http://127.0.0.1:8000").rstrip("/")
API = f"{BASE}/api/v1"

results = []


def req(method: str, url: str, data=None, headers=None, is_json=True):
    h = dict(headers) if headers else {}
    if is_json and data is not None:
        h["Content-Type"] = "application/json"
    body = json.dumps(data).encode() if data is not None and is_json else data
    r = Request(url, data=body, headers=h, method=method)
    try:
        with urlopen(r, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode()) if "application/json" in resp.headers.get("Content-Type", "") else resp.read()
    except HTTPError as e:
        try:
            body = e.read().decode()
            return e.code, json.loads(body) if body.strip().startswith("{") else {"detail": body}
        except Exception:
            return e.code, {"detail": str(e)}
    except URLError as e:
        if isinstance(e.reason, HTTPError):
            try:
                he = e.reason
                body = he.read().decode()
                return he.code, json.loads(body) if body.strip().startswith("{") else {"detail": body}
            except Exception:
                return getattr(e.reason, "code", 500), {"detail": str(e.reason)}
        err = str(e.reason) if hasattr(e, "reason") else str(e)
        if "timed out" in err.lower() or "timeout" in err.lower():
            raise SystemExit(
                f"连接超时: {url}\n"
                "  1. 确认后端已启动: docker-compose -f docker-compose.dev.yml up -d\n"
                "  2. 查看后端日志: docker logs decoration-backend-dev"
            )
        raise SystemExit(f"连接失败: {e}")
    except (TimeoutError, OSError) as e:
        if "timed out" not in str(e).lower() and "timeout" not in str(e).lower():
            raise
        raise SystemExit(
            f"请求超时，无法连接 {url}\n"
            "  1. 确认后端已启动: docker-compose -f docker-compose.dev.yml up -d\n"
            "  2. 查看后端日志: docker logs decoration-backend-dev\n"
            "  3. 可尝试: python3 tests/test_all_apis.py http://127.0.0.1:8000"
        )


def test(name: str, method: str, path: str, data=None, token=None, user_id=None, expect_ok=True, expect_401_ok=False, expect_404_ok=False):
    url = f"{API}{path}" if path.startswith("/") else f"{API}/{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if user_id is not None:
        headers["X-User-Id"] = str(user_id)
    if "X-User-Id" in headers and "user_id" in str(data or ""):
        pass
    status, body = req(method, url, data, headers)
    ok = 200 <= status < 300 or (expect_401_ok and status == 401) or (expect_404_ok and status == 404) or (not expect_ok and status in (400, 404))
    results.append((name, status, ok, body))
    return status, body


def main():
    print("=" * 60)
    print("装修避坑管家 - 全接口测试")
    print(f"BASE: {BASE} | API: {API}")
    print("=" * 60)

    # 0. 健康检查
    if not skip_health:
        last_err = None
        for attempt in range(3 if retry_health else 1):
            try:
                r = urlopen(f"{BASE}/health", timeout=10)
                print(f"[OK] 健康检查: {r.status}")
                last_err = None
                break
            except Exception as e:
                last_err = e
                if retry_health and attempt < 2:
                    print(f"  健康检查尝试 {attempt + 1}/3 失败，2 秒后重试...")
                    time.sleep(2)
        if last_err is not None:
            print(f"[FAIL] 健康检查: {last_err}")
            print("  提示 1: 先启动后端: docker compose -f docker-compose.dev.yml up -d")
            print("  提示 2: 若用 localhost 报 Connection reset，可改用: python3 tests/test_all_apis.py http://127.0.0.1:8000")
            print("  提示 3: 若后端已启动仍失败，可跳过健康检查: python3 tests/test_all_apis.py --skip-health")
            print("  提示 4: 查看后端日志: docker logs decoration-backend-dev")
            sys.exit(1)

    # 1. 登录 (dev_h5_mock 需 DEBUG=True)
    status, body = test("POST /users/login", "POST", "/users/login", {"code": "dev_h5_mock"}, expect_401_ok=True)
    token = None
    user_id = None
    if status == 200:
        token = body.get("access_token") or (body.get("data") or {}).get("access_token")
        user_id = body.get("user_id") or (body.get("data") or {}).get("user_id")
    if not token:
        print("[WARN] 登录失败，将跳过需认证接口（请确保 DEBUG=True）")
    else:
        print(f"[OK] 登录成功 user_id={user_id}")

    auth = {"token": token, "user_id": user_id} if token else {}

    # 1.5 造测试数据（报价单、合同、公司扫描）
    seed_ids = {}
    if token:
        status_seed, body_seed = test("POST /dev/seed", "POST", "/dev/seed", expect_404_ok=True, **auth)
        if status_seed == 200 and isinstance(body_seed, dict):
            seed_ids = body_seed.get("data", body_seed)

    quote_id = seed_ids.get("quote_id", 1)
    contract_id = seed_ids.get("contract_id", 1)
    scan_id = seed_ids.get("scan_id", 1)

    # 2. 用户
    test("GET /users/profile", "GET", "/users/profile", **auth)
    test("PUT /users/profile", "PUT", "/users/profile", {"nickname": "测试"}, **auth)

    # 3. 公司
    test("GET /companies/search?q=装修公司&limit=5", "GET", "/companies/search?q=%E8%A3%85%E4%BF%AE%E5%85%AC%E5%8F%B8&limit=5", **auth)
    status_scan, body_scan = test("POST /companies/scan", "POST", "/companies/scan", {"company_name": "测试装修公司"}, **auth)
    if status_scan == 200 and isinstance(body_scan, dict):
        scan_id = body_scan.get("id") or body_scan.get("data", {}).get("id") or scan_id
    test(f"GET /companies/scan/{scan_id}", "GET", f"/companies/scan/{scan_id}", **auth)
    test("GET /companies/scans", "GET", "/companies/scans?page=1&page_size=10", **auth)

    # 4. 报价单
    test("GET /quotes/list", "GET", "/quotes/list?page=1&page_size=10", **auth)
    test("GET /quotes/quote/1", "GET", "/quotes/quote/1", expect_ok=False, **auth)

    # 5. 合同
    test("GET /contracts/list", "GET", "/contracts/list?page=1&page_size=10", **auth)
    test(f"GET /contracts/contract/{contract_id}", "GET", f"/contracts/contract/{contract_id}", **auth)

    # 6. 用户设置
    test("GET /users/settings", "GET", "/users/settings", **auth)
    test("PUT /users/settings", "PUT", "/users/settings", {"reminder_days_before": 3}, **auth)

    # 7. 施工进度
    test("GET /constructions/schedule", "GET", "/constructions/schedule", expect_404_ok=True, **auth)
    test("POST /constructions/start-date", "POST", "/constructions/start-date", {"start_date": "2030-01-15T00:00:00"}, **auth)
    test("GET /constructions/schedule", "GET", "/constructions/schedule", **auth)
    test("PUT /constructions/stage-status", "PUT", "/constructions/stage-status", {"stage": "S00", "status": "pending"}, **auth)
    test("PUT /constructions/stage-calibrate", "PUT", "/constructions/stage-calibrate", {"stage": "S01", "manual_start_date": "2030-01-20T00:00:00"}, **auth)
    test("GET /constructions/reminder-schedule", "GET", "/constructions/reminder-schedule?date=2030-01-12", **auth)
    test("DELETE /constructions/schedule", "DELETE", "/constructions/schedule", **auth)

    # 8. 消息
    test("GET /messages", "GET", "/messages?page=1&page_size=10", **auth)
    test("GET /messages/unread-count", "GET", "/messages/unread-count", **auth)
    test("POST /messages", "POST", "/messages", {"category": "system", "title": "测试通知", "content": "内容"}, **auth)
    test("PUT /messages/read-all", "PUT", "/messages/read-all", **auth)

    # 9. 反馈
    test("POST /feedback", "POST", "/feedback", {"content": "测试反馈内容"}, **auth)

    # 10. 施工照片
    test("GET /construction-photos", "GET", "/construction-photos", **auth)

    # 11. 验收
    test("GET /acceptance", "GET", "/acceptance?page=1&page_size=10", **auth)
    test("GET /acceptance/1", "GET", "/acceptance/1", expect_404_ok=True, **auth)
    test("POST /acceptance/1/mark-rectify", "POST", "/acceptance/1/mark-rectify", expect_404_ok=True, **auth)
    test("POST /acceptance/1/request-recheck", "POST", "/acceptance/1/request-recheck", {"rectified_photo_urls": []}, expect_404_ok=True, **auth)

    # 12. 报告导出
    test("GET /reports/export-pdf company", "GET", f"/reports/export-pdf?report_type=company&resource_id={scan_id}", **auth)
    test("GET /reports/export-pdf acceptance", "GET", "/reports/export-pdf?report_type=acceptance&resource_id=1", expect_404_ok=True, **auth)

    # 13. 城市
    test("GET /cities/hot", "GET", "/cities/hot", **auth)
    test("GET /cities/list", "GET", "/cities/list", **auth)
    test("GET /cities/list province", "GET", "/cities/list?province=" + quote("广东"), **auth)
    test("POST /cities/select", "POST", "/cities/select", {"city_name": "深圳市"}, **auth)
    test("GET /cities/current", "GET", "/cities/current", **auth)

    # 14. AI 监理咨询
    test("GET /consultation/quota", "GET", "/consultation/quota", **auth)
    test("GET /consultation/sessions", "GET", "/consultation/sessions", **auth)

    # 15. 数据管理
    test("GET /users/data/recycle", "GET", "/users/data/recycle", **auth)

    # 16. 材料进场人工核对 P37
    test("GET /material-checks/material-list", "GET", "/material-checks/material-list", **auth)
    test("GET /material-checks/latest", "GET", "/material-checks/latest", **auth)
    test("POST /material-checks/submit", "POST", "/material-checks/submit", {
        "result": "fail",
        "problem_note": "测试未通过原因不少于十字",
        "items": [{"material_name": "测试材料", "spec_brand": "", "quantity": "1", "photo_urls": []}],
    }, **auth)

    # 17. 申诉与特殊申请
    test("POST /appeals/acceptance/1", "POST", "/appeals/acceptance/1", {"reason": "测试申诉", "images": []}, expect_404_ok=True, **auth)
    test("GET /appeals/acceptance", "GET", "/appeals/acceptance?page=1&page_size=10", **auth)
    test("POST /appeals/special", "POST", "/appeals/special", {"application_type": "exemption", "content": "测试自主装修豁免申请内容不少于十字", "images": []}, **auth)
    test("GET /appeals/special", "GET", "/appeals/special?page=1&page_size=10", **auth)

    # 18. 支付/订单
    test("GET /payments/orders", "GET", "/payments/orders?page=1&page_size=10", **auth)
    test("GET /payments/order/1", "GET", "/payments/order/1", expect_404_ok=True, **auth)

    # 汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    ok_count = sum(1 for _, _, ok, _ in results if ok)
    for name, status, ok, body in results:
        symbol = "✓" if ok else "✗"
        brief = ""
        if isinstance(body, dict) and "detail" in body:
            d = body["detail"]
            brief = f" - {str(d)[:60]}" if isinstance(d, str) else ""
        elif isinstance(body, dict) and "msg" in body:
            brief = f" - {body.get('msg','')}"
        print(f"  [{symbol}] {name} -> {status}{brief}")
    print(f"\n通过: {ok_count}/{len(results)}")
    sys.exit(0 if ok_count == len(results) else 1)


if __name__ == "__main__":
    main()

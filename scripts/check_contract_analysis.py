#!/usr/bin/env python3
"""
检查指定合同的分析结果（是否 AI 分析成功）。
用法（在项目根目录）:
  python scripts/check_contract_analysis.py <contract_id>
  python scripts/check_contract_analysis.py 87
  API_BASE=http://120.26.201.61:8001 python scripts/check_contract_analysis.py 87

用自己的 token 查自己账号下的合同（任选一种方式）:
  1) 环境变量: ACCESS_TOKEN=xxx USER_ID=1 python scripts/check_contract_analysis.py 87
  2) 在项目根 .env 或 backend/.env 中增加:
     CHECK_ACCESS_TOKEN=你的JWT
     CHECK_USER_ID=1
  3) 在 scripts/.env.local 中增加上述两行（该文件已 gitignore，仅本地使用）
"""
import os
import sys
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

# 从 .env 加载配置（可选）
def _load_dotenv():
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(ROOT, ".env"))
        load_dotenv(os.path.join(ROOT, "backend", ".env"))
        load_dotenv(os.path.join(SCRIPTS_DIR, ".env.local"))
    except ImportError:
        pass

_load_dotenv()

BASE_URL = os.environ.get("API_BASE", "http://120.26.201.61:8001").rstrip("/") + "/api/v1"


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/check_contract_analysis.py <contract_id>")
        sys.exit(1)
    contract_id = sys.argv[1].strip()
    if not contract_id.isdigit():
        print("contract_id 需为数字")
        sys.exit(1)

    token = os.environ.get("CHECK_ACCESS_TOKEN") or os.environ.get("ACCESS_TOKEN")
    user_id = os.environ.get("CHECK_USER_ID") or os.environ.get("USER_ID", "1")
    if not token:
        r = requests.post(f"{BASE_URL}/users/login", json={"code": "dev_weapp_mock"}, timeout=10)
        if r.status_code != 200:
            print(f"登录失败: {r.status_code} {r.text[:200]}")
            sys.exit(2)
        data = r.json()
        token = data.get("access_token") or (data.get("data") or {}).get("access_token")
        if not token:
            print("登录响应中无 access_token")
            sys.exit(2)
        user_id = str(data.get("user_id") or (data.get("data") or {}).get("user_id") or 1)

    headers = {"Authorization": f"Bearer {token}", "X-User-Id": str(user_id)}
    resp = requests.get(f"{BASE_URL}/contracts/contract/{contract_id}", headers=headers, timeout=10)
    if resp.status_code == 404:
        print(f"合同不存在或无权访问: id={contract_id}")
        sys.exit(3)
    if resp.status_code != 200:
        print(f"请求失败: {resp.status_code} {resp.text[:300]}")
        sys.exit(3)

    out = resp.json()
    if out.get("code") == 0 and "data" in out:
        c = out["data"]
    else:
        c = out

    status = c.get("status")
    risk_level = c.get("risk_level")
    is_unlocked = c.get("is_unlocked", False)
    risk_items = c.get("risk_items") or []
    unfair_terms = c.get("unfair_terms") or []
    missing_terms = c.get("missing_terms") or []
    suggested = c.get("suggested_modifications") or []
    result_json = c.get("result_json")
    file_name = c.get("file_name")
    created_at = c.get("created_at")

    print("========== 合同分析检查 ==========")
    print(f"  合同ID: {contract_id}")
    print(f"  文件名: {file_name}")
    print(f"  状态: {status}")
    print(f"  创建时间: {created_at}")
    print(f"  风险等级: {risk_level}")
    print(f"  已解锁: {is_unlocked}")
    print(f"  风险条款数: {len(risk_items)}")
    print(f"  不公平条款数: {len(unfair_terms)}")
    print(f"  缺失条款数: {len(missing_terms)}")
    print(f"  修改建议数: {len(suggested)}")
    print(f"  result_json 存在: {result_json is not None and isinstance(result_json, dict)}")
    if result_json and isinstance(result_json, dict):
        print(f"  result_json.summary: {(result_json.get('summary') or '')[:100]}...")
    print("==================================")

    if status == "completed" and (risk_items or unfair_terms or missing_terms or (result_json and isinstance(result_json, dict))):
        print("结论: AI 分析已成功完成。")
    elif status == "completed":
        print("结论: 状态为 completed，但无风险/建议数据，可能分析结果为空或仅 summary。")
    elif status == "analyzing":
        print("结论: 仍在分析中，请稍后再查。")
    elif status == "failed":
        print("结论: 分析失败。")
    else:
        print(f"结论: 当前状态为 {status}，请根据上方数据判断。")


if __name__ == "__main__":
    main()

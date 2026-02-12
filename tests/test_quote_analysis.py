#!/usr/bin/env python3
"""
测试报价单分析：用项目根目录的报价单 .md 调用后端 /dev/analyze-quote-text，验证扣子/DeepSeek 是否正常返回。
用法：在项目根目录执行
  python3 tests/test_quote_analysis.py
  python3 tests/test_quote_analysis.py  path/to/报价单.md
"""
import os
import sys
import json
import httpx

# 项目根目录
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FILE = os.path.join(ROOT, "2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.md")
BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000/api/v1")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE
    if not os.path.isfile(path):
        print(f"文件不存在: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"已读取: {path}，长度 {len(text)} 字符")

    # 登录
    r = httpx.post(
        f"{BASE}/users/login",
        json={"code": "dev_h5_mock"},
        timeout=15.0,
    )
    if r.status_code != 200:
        print(f"登录失败: {r.status_code} {r.text[:300]}")
        sys.exit(2)
    data = r.json()
    token = data.get("access_token") or (data.get("data") or {}).get("access_token")
    if not token:
        print("登录响应中无 access_token:", data)
        sys.exit(2)
    print("登录成功")

    # 调用分析（总价从文档中可知约 62000）
    payload = {"text": text, "total_price": 62000.0}
    r2 = httpx.post(
        f"{BASE}/dev/analyze-quote-text",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=120.0,
    )
    if r2.status_code != 200:
        print(f"分析请求失败: {r2.status_code}")
        print(r2.text[:800])
        sys.exit(3)

    result = r2.json()
    print("\n========== 报价单分析结果 ==========")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n========== 简要 ==========")
    print("风险评分:", result.get("risk_score"))
    print("高风险项数量:", len(result.get("high_risk_items") or []))
    print("警告项数量:", len(result.get("warning_items") or []))
    print("漏项数量:", len(result.get("missing_items") or []))
    print("虚高项数量:", len(result.get("overpriced_items") or []))
    if result.get("suggestions"):
        print("建议:", result["suggestions"][:3])
    print("测试通过，分析功能正常返回。")


if __name__ == "__main__":
    main()

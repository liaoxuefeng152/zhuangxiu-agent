#!/usr/bin/env python3
"""
测试合同分析：用项目根目录的合同文本调用后端 /dev/analyze-contract-text，验证扣子/DeepSeek 是否正常返回。
用法：在项目根目录执行
  python3 tests/test_contract_analysis.py                          # 使用默认路径
  python3 tests/test_contract_analysis.py  path/to/合同.md         # 指定文件
"""
import os
import sys
import json
import httpx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 默认合同文件名（可把「深圳市住宅装饰装修工程施工合同（半包装修版）」放到项目根目录并改名或传路径）
DEFAULT_FILE = os.path.join(ROOT, "深圳市住宅装饰装修工程施工合同（半包装修版）.md")
BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000/api/v1")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE
    if not os.path.isfile(path):
        print(f"文件不存在: {path}")
        print("请把合同文件放到 tests/fixtures/，或执行: python3 tests/test_contract_analysis.py  path/to/合同.md")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"已读取: {path}，长度 {len(text)} 字符")

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

    r2 = httpx.post(
        f"{BASE}/dev/analyze-contract-text",
        json={"text": text},
        headers={"Authorization": f"Bearer {token}"},
        timeout=120.0,
    )
    if r2.status_code != 200:
        print(f"分析请求失败: {r2.status_code}")
        print(r2.text[:800])
        sys.exit(3)

    result = r2.json()
    print("\n========== 合同分析结果 ==========")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n========== 简要 ==========")
    print("风险等级:", result.get("risk_level"))
    print("风险项数量:", len(result.get("risk_items") or []))
    print("不公平条款数量:", len(result.get("unfair_terms") or []))
    print("缺失条款数量:", len(result.get("missing_terms") or []))
    print("修改建议数量:", len(result.get("suggested_modifications") or []))
    if result.get("summary"):
        print("总评:", result["summary"][:200])
    print("测试完成。")


if __name__ == "__main__":
    main()

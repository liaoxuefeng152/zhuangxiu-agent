#!/usr/bin/env python3
"""
材料核对「核对通过」流程 - 前后端联调测试
流程: 登录 -> 上传验收照片(使用 tests/fixtures 图片) -> 提交材料核对
用法: python tests/test_material_check_e2e.py [API_BASE] [图片路径]
  默认: API=http://120.26.201.61:8001  图片=tests/fixtures/装修知识库导入与验证 (1).png
"""
import json
import os
import sys

# 支持直接运行 python tests/test_material_check_e2e.py
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FIXTURES = os.path.join(_SCRIPT_DIR, "fixtures")
_MATERIAL_PNG = "装修知识库导入与验证 (1).png"
DEFAULT_IMAGE = os.path.join(_FIXTURES, _MATERIAL_PNG)

try:
    import requests
except ImportError:
    print("请安装: pip install requests")
    sys.exit(1)

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://120.26.201.61:8001").rstrip("/")
API = f"{BASE}/api/v1"
IMAGE_PATH = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_IMAGE


def main():
    print("=" * 60)
    print("材料核对「核对通过」前后端联调测试")
    print(f"后端 API: {API}")
    print(f"上传图片: {IMAGE_PATH}")
    print("=" * 60)

    if not os.path.isfile(IMAGE_PATH):
        print(f"\n[FAIL] 图片不存在: {IMAGE_PATH}")
        sys.exit(1)
    print(f"\n图片大小: {os.path.getsize(IMAGE_PATH)} bytes")

    # 1. 登录
    print("\n1. 登录 (dev_h5_mock)...")
    try:
        r = requests.post(
            f"{API}/users/login",
            json={"code": "dev_h5_mock"},
            timeout=15,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"  [FAIL] 登录请求失败: {e}")
        sys.exit(1)

    login_res = r.json()
    token = login_res.get("access_token") or (login_res.get("data") or {}).get("access_token")
    user_id = login_res.get("user_id") or (login_res.get("data") or {}).get("user_id")
    if not token:
        print(f"  [FAIL] 登录失败，无 token: {login_res}")
        sys.exit(1)
    print(f"  [OK] user_id={user_id}")

    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id),
    }

    # 2. 上传验收照片 (使用真实图片)
    print("\n2. 上传验收照片...")
    try:
        with open(IMAGE_PATH, "rb") as f:
            files = {"file": (os.path.basename(IMAGE_PATH), f, "image/png")}
            r = requests.post(
                f"{API}/acceptance/upload-photo",
                params={"access_token": token, "user_id": user_id},
                headers=headers,
                files=files,
                timeout=30,
            )
        r.raise_for_status()
    except requests.RequestException as e:
        body = e.response.text if hasattr(e, "response") and e.response is not None else str(e)
        print(f"  [FAIL] 上传失败: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"  HTTP {e.response.status_code}: {body[:300]}")
        sys.exit(1)

    upload_res = r.json()
    data = upload_res.get("data") or upload_res
    file_url = data.get("file_url")
    if not file_url:
        print(f"  [FAIL] 未返回 file_url: {upload_res}")
        sys.exit(1)
    print(f"  [OK] file_url={file_url[:80]}...")

    # 3. 提交材料核对 (通过)
    print("\n3. 提交材料核对 (pass)...")
    try:
        r = requests.post(
            f"{API}/material-checks/submit",
            json={
                "items": [{"material_name": "材料进场核对", "photo_urls": [file_url]}],
                "result": "pass",
            },
            headers=headers,
            timeout=15,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        body = e.response.text if hasattr(e, "response") and e.response is not None else str(e)
        print(f"  [FAIL] 提交失败: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"  HTTP {e.response.status_code}: {body[:300]}")
        sys.exit(1)

    submit_res = r.json()
    print(f"  [OK] 提交成功: {submit_res.get('msg', submit_res)}")

    print("\n" + "=" * 60)
    print("材料核对「核对通过」前后端联调测试 - 全部通过")
    print("=" * 60)


if __name__ == "__main__":
    main()

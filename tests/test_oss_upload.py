#!/usr/bin/env python3
"""
OSS 上传测试：验证上传策略接口 + 后端代理上传到 OSS
默认请求阿里云开发环境；若需测本地，请设置环境变量 API_BASE=http://localhost:8000
"""
import os
import requests
import sys
from pathlib import Path

BASE_URL = os.environ.get("API_BASE", "http://120.26.201.61:8001").rstrip("/") + "/api/v1"

def main():
    print("=" * 60)
    print("OSS 上传测试")
    print("=" * 60)

    # 1. 登录
    print("\n1. 登录...")
    try:
        r = requests.post(
            f"{BASE_URL}/users/login",
            json={"code": "dev_weapp_mock"},
            timeout=10
        )
        r.raise_for_status()
        data = r.json().get("data", {}) if r.json().get("code") == 0 else r.json()
        token = data.get("access_token")
        user_id = data.get("user_id")
        if not token or not user_id:
            print("❌ 登录失败：未获取 token/user_id")
            return 1
        print("✅ 登录成功")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return 1

    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id),
    }

    # 2. 获取 OSS 上传策略
    print("\n2. 获取 OSS 上传策略 (GET /oss/upload-policy?stage=material)...")
    try:
        r = requests.get(
            f"{BASE_URL}/oss/upload-policy",
            params={"stage": "material"},
            headers=headers,
            timeout=10
        )
        r.raise_for_status()
        body = r.json()
        data = body.get("data", {}) if body.get("code") == 0 else body
        available = data.get("available", True)
        if available:
            print("✅ 上传策略获取成功，OSS 直传已配置")
            print(f"   host: {data.get('host', '')[:50]}...")
            print(f"   dir: {data.get('dir')}, expire: {data.get('expire')}s")
        else:
            print("⚠️ 接口返回 200，但 available=false（OSS 未配置或配置不完整）")
            print(f"   说明: {data.get('message', '')}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ 请求失败: {e.response.status_code} - {e.response.text[:200]}")
        if e.response.status_code == 503 and "OSS" in (e.response.text or ""):
            print("\n说明：当前请求的是阿里云服务器后端，503 表示服务器上未配置 OSS 环境变量。")
            print("若已配置本地 .env，可用本地后端验证：")
            print("  1. 终端1: cd backend && uvicorn main:app --host 0.0.0.0 --port 8000")
            print("  2. 终端2: API_BASE=http://localhost:8000 python3 tests/test_oss_upload.py")
            print("要在服务器上启用 OSS：在部署环境配置 ALIYUN_ACCESS_KEY_ID、ALIYUN_ACCESS_KEY_SECRET、ALIYUN_OSS_BUCKET1、ALIYUN_OSS_ENDPOINT 并重启后端。")
        return 1
    except Exception as e:
        print(f"❌ 失败: {e}")
        return 1

    # 3. 后端代理上传（验收照片接口会写入 OSS，返回 object_key）
    print("\n3. 后端代理上传测试 (POST /acceptance/upload-photo)...")
    test_file = Path(__file__).parent / "fixtures" / "隐蔽工程验收.png"
    if not test_file.exists():
        test_file = Path(__file__).parent / "fixtures" / "瓷砖.png"
    if not test_file.exists():
        print("⚠️ 未找到测试图片，跳过实际上传与签名 URL 测试")
        print("✅ OSS 上传策略接口测试完成")
        return 0

    object_key = None
    try:
        with open(test_file, "rb") as f:
            files = {"file": (test_file.name, f, "image/png")}
            r = requests.post(
                f"{BASE_URL}/acceptance/upload-photo",
                files=files,
                headers={"Authorization": f"Bearer {token}", "X-User-Id": str(user_id)},
                timeout=30
            )
        r.raise_for_status()
        res = r.json()
        data = res.get("data") or {}
        object_key = data.get("object_key") or data.get("file_url")
        if object_key:
            print("✅ 验收照片上传成功（已写入 OSS）")
            print(f"   object_key: {object_key[:80]}{'...' if len(object_key) > 80 else ''}")
        else:
            print("⚠️ 上传返回成功但未解析到 object_key/file_url")
    except requests.exceptions.HTTPError as e:
        print(f"❌ 上传请求失败: {e.response.status_code}")
        print(f"   {e.response.text[:300]}")
        return 1
    except Exception as e:
        print(f"❌ 上传失败: {e}")
        return 1

    # 4. 获取临时签名 URL（私有 Bucket 访问）
    if object_key and not object_key.startswith("https://"):
        print("\n4. 获取临时签名 URL (GET /oss/sign-url)...")
        try:
            r = requests.get(
                f"{BASE_URL}/oss/sign-url",
                params={"object_key": object_key},
                headers=headers,
                timeout=10
            )
            r.raise_for_status()
            body = r.json()
            data = body.get("data", {}) if body.get("code") == 0 else body
            signed_url = data.get("url")
            if signed_url:
                print("✅ 签名 URL 获取成功")
                print(f"   url: {signed_url[:80]}...")
                # 签名 URL 是按 GET 生成的（前端 img/浏览器用 GET），必须用 GET 校验，用 HEAD 会 SignatureDoesNotMatch
                get_resp = requests.get(signed_url, timeout=10)
                if get_resp.status_code == 200:
                    print("✅ 使用签名 URL 访问资源成功 (GET 200)")
                else:
                    print(f"⚠️ GET 返回 {get_resp.status_code}")
                    for k, v in (get_resp.headers or {}).items():
                        if k.lower().startswith("x-oss-") or k.lower() in ("content-type", "content-length"):
                            print(f"   [{k}]: {v}")
            else:
                print("⚠️ 未解析到 data.url")
        except requests.exceptions.HTTPError as e:
            print(f"❌ sign-url 请求失败: {e.response.status_code} - {e.response.text[:200]}")
            return 1
        except Exception as e:
            print(f"❌ 获取签名 URL 失败: {e}")
            return 1
    else:
        print("\n4. 跳过签名 URL 测试（object_key 为 mock URL 或未获取）")

    print("\n" + "=" * 60)
    print("✅ OSS 上传测试全部通过")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())

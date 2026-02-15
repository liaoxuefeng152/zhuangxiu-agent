#!/usr/bin/env python3
"""
装修避坑管家 - 微信小程序 UI 自动化测试（Minium）

运行前提：
  1. 安装: pip install minium
  2. 微信开发者工具打开 frontend 项目（先 npm run build:weapp 编译），
     设置 -> 安全设置 -> 开启「服务端口」
  3. 本脚本在项目根目录执行: python tests/ui/run_ui_tests.py

若未开开发者工具或未安装 minium，将跳过执行并提示，退出码 0。
"""
from __future__ import annotations

import os
import sys

# 项目根目录
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def check_minium():
    try:
        import minium  # noqa: F401
        return True
    except ImportError:
        return False


def run_ui_tests():
    if not check_minium():
        print("=" * 60)
        print("UI 自动化测试（Minium）")
        print("=" * 60)
        print("未检测到 minium，请先安装：")
        print("  pip install minium")
        print("然后重新运行: python tests/ui/run_ui_tests.py")
        print("=" * 60)
        return 0

    import minium

    # 连接配置：默认连接本地开发者工具
    conf = {
        "project_path": os.path.join(ROOT, "frontend"),
        "dev_tool_path": "",  # 留空使用默认
        "debug_mode": "warn",
        "enable_app_log": False,
    }
    # macOS 上若 Minium 找不到 IDE，显式指定开发者工具 CLI 路径
    if sys.platform == "darwin":
        _cli = "/Applications/wechatwebdevtools.app/Contents/MacOS/cli"
        if os.path.isfile(_cli):
            conf["dev_tool_path"] = _cli
    # 若 frontend 编译产物在 dist，Minium 可能需指定 miniprogram_root
    if os.path.isdir(os.path.join(ROOT, "frontend", "dist")):
        conf.setdefault("miniprogram_root", "dist")

    try:
        mini = minium.Minium(conf)
        # 验证连接：获取系统信息
        _ = mini.get_system_info()
        print("[连接] 已连接微信开发者工具")
    except Exception as e:
        print("=" * 60)
        print("UI 自动化测试（Minium）")
        print("=" * 60)
        print("无法连接微信开发者工具，请确认：")
        print("  1. 已打开微信开发者工具并导入 frontend 项目")
        print("  2. 设置 -> 安全设置 -> 已开启「服务端口」（Connection refused 多为未开启此项）")
        print("  3. 若为 macOS 且未指定路径，脚本会自动使用 /Applications/wechatwebdevtools.app")
        print("错误信息:", e)
        print("=" * 60)
        return 0

    passed = 0
    failed = 0

    def _navigate_and_check(path: str, name: str) -> bool:
        try:
            mini.navigate_to(path)
            mini.sleep(1)
            page = mini.get_current_page()
            return page is not None
        except Exception:
            return False

    for path, name, case_id in [
        ("/pages/index/index", "首页", "UI-HOME-01"),
        ("/pages/profile/index", "我的", "UI-PROFILE-01"),
        ("/pages/construction/index", "施工陪伴", "UI-CONST-01"),
        ("/pages/company-scan/index", "公司检测", "UI-COMPANY-01"),
        ("/pages/quote-upload/index", "报价单", "UI-QUOTE-01"),
        ("/pages/contract-upload/index", "合同上传", "UI-CONTRACT-01"),
        ("/pages/message/index", "消息中心", "UI-MSG-01"),
        ("/pages/data-manage/index", "数据管理", "UI-DATA-01"),
    ]:
        if _navigate_and_check(path, name):
            passed += 1
            print(f"[通过] {case_id} 进入{name}页")
        else:
            failed += 1
            print(f"[失败] {case_id} 进入{name}页")

    try:
        mini.shutdown()
    except Exception:
        try:
            mini.close()
        except Exception:
            pass

    print("")
    print("=" * 60)
    print(f"UI 自动化测试结果: 通过 {passed}, 失败 {failed}")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_ui_tests())

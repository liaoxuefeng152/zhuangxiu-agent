"""将项目根目录加入 sys.path，以便直接运行 python tests/xxx.py 时能 from tests import ..."""
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
if _root not in sys.path:
    sys.path.insert(0, _root)


def _ensure_path():
    """供其他脚本调用：确保项目根在 sys.path 中"""
    if _root not in sys.path:
        sys.path.insert(0, _root)

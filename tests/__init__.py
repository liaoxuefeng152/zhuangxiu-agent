# tests package
import os

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, "fixtures")


def fixture_path(name: str) -> str:
    """返回测试数据文件路径"""
    return os.path.join(FIXTURES_DIR, name)


# 常用测试文件快捷名
QUOTE_PNG = "2026年深圳住宅装修真实报价单（89㎡三室一厅，半包，中档品质）.png"
CONTRACT_PNG = "深圳市住宅装饰装修工程施工合同（半包装修版）.png"
MATERIAL_PNG = "装修知识库导入与验证 (1).png"

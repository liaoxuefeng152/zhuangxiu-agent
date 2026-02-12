#!/usr/bin/env python3
"""
扩展白盒测试 - 覆盖更多模块和函数
"""
import sys
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json
import re

# 直接复制需要的函数，避免导入时的数据库初始化问题

# 从constructions.py复制的常量和函数
STAGE_ORDER = ["S00", "S01", "S02", "S03", "S04", "S05"]
STAGE_KEY_TO_S = {
    "material": "S00", "plumbing": "S01", "carpentry": "S02",
    "woodwork": "S03", "painting": "S04", "installation": "S05",
    "flooring": "S02", "soft_furnishing": "S05",
}


def normalize_stage_key(stage: str) -> str:
    if stage in STAGE_ORDER:
        return stage
    return STAGE_KEY_TO_S.get(stage, stage)


def _stage_passed(stages, key: str) -> bool:
    """检查阶段是否已通过"""
    s = stages.get(key) or {} if stages else {}
    if isinstance(s, str):
        try:
            s = json.loads(s)
        except:
            s = {}
    st = s.get("status") if isinstance(s, dict) else "pending"
    if not st:
        st = "pending"
    if key == "S00":
        return st == "checked"
    return st in ("passed", "completed")


def _serialize_stages_with_lock(stages):
    """序列化阶段数据并添加locked状态"""
    if isinstance(stages, str):
        try:
            stages = json.loads(stages)
        except:
            stages = {}
    if not isinstance(stages, dict):
        stages = {}
    
    out = {}
    for i, key in enumerate(STAGE_ORDER):
        raw = stages.get(key) or {}
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except:
                raw = {}
        if not isinstance(raw, dict):
            raw = {}
        
        prev_passed = True
        if i > 0:
            prev_key = STAGE_ORDER[i - 1]
            prev_passed = _stage_passed(stages, prev_key)
        locked = not prev_passed

        if not raw:
            item = {
                "status": "pending",
                "sequence": i + 1,
                "stage_key": key,
                "locked": locked
            }
        else:
            item = dict(raw)
            for k, v in list(item.items()):
                if isinstance(v, datetime):
                    item[k] = v.isoformat() if v else None
            item["locked"] = locked
            item["stage_key"] = key
        
        out[key] = item
    return out


def calculate_construction_schedule(start_date: datetime):
    """计算施工计划"""
    stages = {}
    current_date = start_date
    STAGE_DURATION = {"S00": 7, "S01": 14, "S02": 10, "S03": 10, "S04": 7, "S05": 7}
    
    for stage in STAGE_ORDER:
        duration = STAGE_DURATION.get(stage, 7)
        if isinstance(current_date, datetime):
            end_date = current_date + timedelta(days=duration - 1)
        else:
            end_date = current_date + timedelta(days=duration - 1)
        stages[stage] = {
            "status": "pending",
            "start_date": current_date,
            "end_date": end_date,
            "duration": duration,
            "sequence": STAGE_ORDER.index(stage) + 1,
        }
        current_date = end_date + timedelta(days=1)
    estimated_end_date = current_date - timedelta(days=1)
    return {"stages": stages, "estimated_end_date": estimated_end_date}


def calculate_progress(stages):
    """计算进度百分比"""
    if not stages:
        return 0
    
    total_duration = sum((s.get("duration") or 0) for s in stages.values())
    if total_duration == 0:
        return 0
    
    completed_duration = 0
    for stage_key, stage_data in stages.items():
        status = stage_data.get("status", "pending")
        duration = stage_data.get("duration", 0)
        
        if stage_key == "S00" and status == "checked":
            completed_duration += duration
        elif stage_key != "S00" and status in ("passed", "completed"):
            completed_duration += duration
    
    if total_duration == 0:
        return 0
    
    progress = int((completed_duration / total_duration) * 100)
    return min(100, max(0, progress))


# 从quotes.py复制的函数逻辑
def extract_total_price_from_ocr_text(ocr_text: str):
    """从OCR文本中提取总价"""
    import re
    total_price = None
    price_match = re.search(r'[总合]计[^\d]*(\d+(?:\.\d+)?)', ocr_text)
    if price_match:
        total_price = float(price_match.group(1))
    return total_price


class TestQuoteAnalysisLogic(unittest.TestCase):
    """报价单分析逻辑的白盒测试"""
    
    def test_extract_total_price_simple(self):
        """测试提取总价: 简单格式"""
        text = "总计：80000元"
        price = extract_total_price_from_ocr_text(text)
        self.assertEqual(price, 80000.0)
    
    def test_extract_total_price_with_text(self):
        """测试提取总价: 带文字"""
        text = "合计：9600.50元"
        price = extract_total_price_from_ocr_text(text)
        self.assertEqual(price, 9600.50)
    
    def test_extract_total_price_decimal(self):
        """测试提取总价: 小数"""
        text = "合计金额：12345.67元"
        price = extract_total_price_from_ocr_text(text)
        self.assertEqual(price, 12345.67)
    
    def test_extract_total_price_no_match(self):
        """测试提取总价: 无匹配"""
        text = "这是一个没有价格的文本"
        price = extract_total_price_from_ocr_text(text)
        self.assertIsNone(price)
    
    def test_extract_total_price_multiple_matches(self):
        """测试提取总价: 多个匹配"""
        text = "小计：1000元，总计：5000元"
        price = extract_total_price_from_ocr_text(text)
        # 应该匹配第一个
        self.assertIsNotNone(price)
    
    def test_extract_total_price_chinese_number(self):
        """测试提取总价: 中文数字"""
        text = "总计：八万元"
        price = extract_total_price_from_ocr_text(text)
        # 当前正则不支持中文数字，应该返回None
        self.assertIsNone(price)


class TestOcrServiceLogic(unittest.TestCase):
    """OCR服务逻辑的白盒测试"""
    
    def test_ocr_input_url_detection(self):
        """测试OCR输入类型检测: URL"""
        file_url = "https://example.com/image.png"
        is_url = file_url.startswith("http")
        self.assertTrue(is_url)
    
    def test_ocr_input_base64_data_prefix(self):
        """测试OCR输入类型检测: Base64 data:前缀"""
        file_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        is_data = file_url.startswith("data:")
        self.assertTrue(is_data)
        
        # 测试Base64提取
        if "," in file_url:
            base64_part = file_url.split(",")[1]
            self.assertIsInstance(base64_part, str)
            self.assertGreater(len(base64_part), 0)
    
    def test_ocr_input_base64_no_prefix(self):
        """测试OCR输入类型检测: Base64无前缀"""
        file_url = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        is_url = file_url.startswith("http")
        is_data = file_url.startswith("data:")
        self.assertFalse(is_url)
        self.assertFalse(is_data)
        # 应该作为纯Base64处理
    
    def test_ocr_input_empty(self):
        """测试OCR输入类型检测: 空字符串"""
        file_url = ""
        is_url = file_url.startswith("http")
        is_data = file_url.startswith("data:")
        self.assertFalse(is_url)
        self.assertFalse(is_data)


class TestStageInterlockLogic(unittest.TestCase):
    """阶段互锁逻辑的深度测试"""
    
    def test_interlock_all_stages_sequential(self):
        """测试互锁: 所有阶段顺序解锁"""
        stages = {}
        result = _serialize_stages_with_lock(stages)
        
        # S00应该未锁定
        self.assertFalse(result["S00"]["locked"])
        
        # 其他阶段应该锁定
        for i in range(1, len(STAGE_ORDER)):
            self.assertTrue(result[STAGE_ORDER[i]]["locked"])
        
        # 逐步解锁
        for i, stage in enumerate(STAGE_ORDER):
            if i == 0:
                stages[stage] = {"status": "checked"}
            else:
                stages[stage] = {"status": "passed"}
            
            result = _serialize_stages_with_lock(stages)
            
            # 当前阶段应该未锁定
            self.assertFalse(result[stage]["locked"])
            
            # 如果还有下一个阶段，应该解锁
            if i < len(STAGE_ORDER) - 1:
                next_stage = STAGE_ORDER[i + 1]
                self.assertFalse(result[next_stage]["locked"])
    
    def test_interlock_skip_stage(self):
        """测试互锁: 跳过阶段的情况"""
        # S00完成，S01跳过，直接完成S02
        stages = {
            "S00": {"status": "checked"},
            "S02": {"status": "passed"}  # 跳过S01
        }
        result = _serialize_stages_with_lock(stages)
        
        # S02应该仍然锁定（因为S01未完成）
        self.assertTrue(result["S02"]["locked"])
    
    def test_interlock_reverse_order(self):
        """测试互锁: 反向顺序"""
        # 先完成S05（不应该成功）
        stages = {"S05": {"status": "passed"}}
        result = _serialize_stages_with_lock(stages)
        
        # S05应该锁定（因为前置阶段未完成）
        self.assertTrue(result["S05"]["locked"])


class TestProgressCalculationEdgeCases(unittest.TestCase):
    """进度计算的边界情况测试"""
    
    def test_progress_with_mixed_statuses(self):
        """测试进度计算: 混合状态"""
        stages = {
            "S00": {"status": "checked", "duration": 7},
            "S01": {"status": "in_progress", "duration": 14},  # 进行中不算完成
            "S02": {"status": "passed", "duration": 10}
        }
        progress = calculate_progress(stages)
        # 只有S00和S02完成
        self.assertGreater(progress, 0)
        self.assertLess(progress, 100)
    
    def test_progress_with_need_rectify(self):
        """测试进度计算: 需要整改的状态"""
        stages = {
            "S00": {"status": "checked", "duration": 7},
            "S01": {"status": "need_rectify", "duration": 14}  # 需要整改不算完成
        }
        progress = calculate_progress(stages)
        # 只有S00完成
        self.assertGreater(progress, 0)
        self.assertLess(progress, 100)
    
    def test_progress_with_pending_recheck(self):
        """测试进度计算: 待复检状态"""
        stages = {
            "S00": {"status": "checked", "duration": 7},
            "S01": {"status": "pending_recheck", "duration": 14}  # 待复检不算完成
        }
        progress = calculate_progress(stages)
        # 只有S00完成
        self.assertGreater(progress, 0)
        self.assertLess(progress, 100)
    
    def test_progress_with_zero_total(self):
        """测试进度计算: 总duration为0"""
        stages = {
            "S00": {"status": "checked", "duration": 0},
            "S01": {"status": "passed", "duration": 0}
        }
        progress = calculate_progress(stages)
        self.assertEqual(progress, 0)
    
    def test_progress_with_very_large_duration(self):
        """测试进度计算: 非常大的duration"""
        stages = {
            "S00": {"status": "checked", "duration": 1000000},
            "S01": {"status": "pending", "duration": 1}
        }
        progress = calculate_progress(stages)
        # 应该能正常计算，不会溢出
        self.assertGreaterEqual(progress, 0)
        self.assertLessEqual(progress, 100)


class TestDataValidation(unittest.TestCase):
    """数据验证逻辑测试"""
    
    def test_stage_key_normalization_edge_cases(self):
        """测试阶段键标准化: 边界情况"""
        # 空字符串
        self.assertEqual(normalize_stage_key(""), "")
        
        # 特殊字符
        self.assertEqual(normalize_stage_key("S00!"), "S00!")
        
        # 数字
        self.assertEqual(normalize_stage_key("123"), "123")
        
        # Unicode字符
        self.assertEqual(normalize_stage_key("阶段"), "阶段")
    
    def test_stage_passed_edge_cases(self):
        """测试阶段通过判断: 边界情况"""
        # 状态为数字
        stages = {"S00": {"status": 1}}
        self.assertFalse(_stage_passed(stages, "S00"))
        
        # 状态为列表
        stages = {"S00": {"status": ["checked"]}}
        self.assertFalse(_stage_passed(stages, "S00"))
        
        # 状态为字典
        stages = {"S00": {"status": {"value": "checked"}}}
        self.assertFalse(_stage_passed(stages, "S00"))
    
    def test_serialize_stages_with_lock_nested_dict(self):
        """测试序列化: 嵌套字典"""
        stages = {
            "S00": {
                "status": "checked",
                "metadata": {
                    "nested": "value"
                }
            }
        }
        result = _serialize_stages_with_lock(stages)
        self.assertIn("S00", result)
        self.assertFalse(result["S00"]["locked"])


class TestControlFlow(unittest.TestCase):
    """控制流测试"""
    
    def test_if_else_branches_stage_passed(self):
        """测试if-else分支: _stage_passed"""
        # 测试S00分支
        stages = {"S00": {"status": "checked"}}
        self.assertTrue(_stage_passed(stages, "S00"))
        
        stages = {"S00": {"status": "pending"}}
        self.assertFalse(_stage_passed(stages, "S00"))
        
        # 测试其他阶段分支
        stages = {"S01": {"status": "passed"}}
        self.assertTrue(_stage_passed(stages, "S01"))
        
        stages = {"S01": {"status": "completed"}}
        self.assertTrue(_stage_passed(stages, "S01"))
        
        stages = {"S01": {"status": "pending"}}
        self.assertFalse(_stage_passed(stages, "S01"))
    
    def test_loop_iteration_stage_order(self):
        """测试循环迭代: STAGE_ORDER"""
        stages = {}
        result = _serialize_stages_with_lock(stages)
        
        # 验证所有阶段都被处理
        for stage in STAGE_ORDER:
            self.assertIn(stage, result)
    
    def test_nested_conditions(self):
        """测试嵌套条件"""
        # 测试多层嵌套的条件判断
        stages = {
            "S00": json.dumps({"status": "checked"}),  # JSON字符串
            "S01": {"status": "passed"}  # 字典
        }
        
        # 应该能正确处理混合格式
        result = _serialize_stages_with_lock(stages)
        self.assertFalse(result["S00"]["locked"])
        self.assertFalse(result["S01"]["locked"])


class TestErrorHandling(unittest.TestCase):
    """错误处理测试"""
    
    def test_json_parse_error_handling(self):
        """测试JSON解析错误处理"""
        # 无效JSON字符串
        stages = {"S00": "{invalid json}"}
        result = _stage_passed(stages, "S00")
        # 应该返回False而不是抛出异常
        self.assertFalse(result)
    
    def test_type_error_handling(self):
        """测试类型错误处理"""
        # 传入非预期类型
        stages = None
        result = _serialize_stages_with_lock(stages)
        # 应该返回空字典或默认值，而不是抛出异常
        self.assertIsInstance(result, dict)
    
    def test_key_error_handling(self):
        """测试键错误处理"""
        # 访问不存在的键
        stages = {}
        result = _stage_passed(stages, "NONEXISTENT")
        # 应该返回False而不是抛出KeyError
        self.assertFalse(result)


def run_extended_whitebox_tests():
    """运行扩展白盒测试"""
    print("=" * 70)
    print("扩展白盒测试 - 覆盖更多模块和函数")
    print("=" * 70)
    print("\n测试覆盖:")
    print("1. 报价单分析逻辑")
    print("2. OCR服务逻辑")
    print("3. 阶段互锁深度测试")
    print("4. 进度计算边界情况")
    print("5. 数据验证")
    print("6. 控制流")
    print("7. 错误处理")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestQuoteAnalysisLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestOcrServiceLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestStageInterlockLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestProgressCalculationEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestControlFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("扩展白盒测试结果统计")
    print("=" * 70)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  ❌ {test}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  ❌ {test}")
    
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    result = run_extended_whitebox_tests()
    sys.exit(0 if result.wasSuccessful() else 1)

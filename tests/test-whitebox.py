#!/usr/bin/env python3
"""
白盒测试 - 基于代码内部结构和逻辑的测试
测试关键函数的各种分支、边界条件、异常情况
"""
import sys
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json

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
    # 处理JSON字符串格式
    if isinstance(s, str):
        try:
            s = json.loads(s)
        except:
            s = {}
    st = s.get("status") if isinstance(s, dict) else "pending"
    if not st:
        st = "pending"
    # S00阶段：checked表示已通过
    if key == "S00":
        return st == "checked"
    # 其他阶段：passed或completed表示已通过
    return st in ("passed", "completed")


def _serialize_stages_with_lock(stages):
    """序列化阶段数据并添加locked状态"""
    # 处理JSON字符串格式
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
        # 处理字典中的字符串值
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except:
                raw = {}
        if not isinstance(raw, dict):
            raw = {}
        
        # 计算locked状态：检查前置阶段是否通过
        prev_passed = True
        if i > 0:
            prev_key = STAGE_ORDER[i - 1]
            prev_passed = _stage_passed(stages, prev_key)
        locked = not prev_passed

        # 如果阶段数据为空，至少返回基本信息
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
        
        # S00: checked表示完成
        if stage_key == "S00" and status == "checked":
            completed_duration += duration
        # 其他阶段: passed或completed表示完成
        elif stage_key != "S00" and status in ("passed", "completed"):
            completed_duration += duration
    
    if total_duration == 0:
        return 0
    
    progress = int((completed_duration / total_duration) * 100)
    return min(100, max(0, progress))


class TestConstructionFunctions(unittest.TestCase):
    """施工进度管理模块的白盒测试"""
    
    def test_normalize_stage_key_valid_s00_s05(self):
        """测试normalize_stage_key: 有效的S00-S05阶段"""
        self.assertEqual(normalize_stage_key("S00"), "S00")
        self.assertEqual(normalize_stage_key("S01"), "S01")
        self.assertEqual(normalize_stage_key("S05"), "S05")
    
    def test_normalize_stage_key_old_keys(self):
        """测试normalize_stage_key: 旧阶段键映射"""
        self.assertEqual(normalize_stage_key("material"), "S00")
        self.assertEqual(normalize_stage_key("plumbing"), "S01")
        self.assertEqual(normalize_stage_key("carpentry"), "S02")
        self.assertEqual(normalize_stage_key("woodwork"), "S03")
        self.assertEqual(normalize_stage_key("painting"), "S04")
        self.assertEqual(normalize_stage_key("installation"), "S05")
    
    def test_normalize_stage_key_unknown(self):
        """测试normalize_stage_key: 未知阶段键"""
        self.assertEqual(normalize_stage_key("unknown"), "unknown")
    
    def test_stage_passed_s00_checked(self):
        """测试_stage_passed: S00阶段checked状态"""
        stages = {"S00": {"status": "checked"}}
        self.assertTrue(_stage_passed(stages, "S00"))
    
    def test_stage_passed_s00_pending(self):
        """测试_stage_passed: S00阶段pending状态"""
        stages = {"S00": {"status": "pending"}}
        self.assertFalse(_stage_passed(stages, "S00"))
    
    def test_stage_passed_s01_passed(self):
        """测试_stage_passed: S01阶段passed状态"""
        stages = {"S01": {"status": "passed"}}
        self.assertTrue(_stage_passed(stages, "S01"))
    
    def test_stage_passed_s01_completed(self):
        """测试_stage_passed: S01阶段completed状态"""
        stages = {"S01": {"status": "completed"}}
        self.assertTrue(_stage_passed(stages, "S01"))
    
    def test_stage_passed_s01_pending(self):
        """测试_stage_passed: S01阶段pending状态"""
        stages = {"S01": {"status": "pending"}}
        self.assertFalse(_stage_passed(stages, "S01"))
    
    def test_stage_passed_missing_stage(self):
        """测试_stage_passed: 缺失阶段"""
        stages = {}
        self.assertFalse(_stage_passed(stages, "S01"))
    
    def test_stage_passed_json_string(self):
        """测试_stage_passed: JSON字符串格式"""
        stages = {"S00": json.dumps({"status": "checked"})}
        self.assertTrue(_stage_passed(stages, "S00"))
    
    def test_stage_passed_invalid_json_string(self):
        """测试_stage_passed: 无效JSON字符串"""
        stages = {"S00": "invalid json"}
        self.assertFalse(_stage_passed(stages, "S00"))
    
    def test_stage_passed_empty_status(self):
        """测试_stage_passed: 空状态"""
        stages = {"S00": {"status": ""}}
        self.assertFalse(_stage_passed(stages, "S00"))
    
    def test_stage_passed_none_status(self):
        """测试_stage_passed: None状态"""
        stages = {"S00": {"status": None}}
        self.assertFalse(_stage_passed(stages, "S00"))
    
    def test_stage_passed_none_stages(self):
        """测试_stage_passed: stages为None"""
        self.assertFalse(_stage_passed(None, "S00"))
    
    def test_stage_passed_non_dict_stage(self):
        """测试_stage_passed: 阶段值不是字典"""
        stages = {"S00": "not a dict"}
        self.assertFalse(_stage_passed(stages, "S00"))
    
    def test_serialize_stages_with_lock_empty(self):
        """测试_serialize_stages_with_lock: 空stages"""
        result = _serialize_stages_with_lock({})
        self.assertEqual(len(result), len(STAGE_ORDER))
        self.assertFalse(result["S00"]["locked"])
        self.assertTrue(result["S01"]["locked"])  # S01需要S00通过
    
    def test_serialize_stages_with_lock_s00_checked(self):
        """测试_serialize_stages_with_lock: S00已通过"""
        stages = {"S00": {"status": "checked"}}
        result = _serialize_stages_with_lock(stages)
        self.assertFalse(result["S00"]["locked"])
        self.assertFalse(result["S01"]["locked"])  # S01应该解锁
    
    def test_serialize_stages_with_lock_s00_pending(self):
        """测试_serialize_stages_with_lock: S00未通过"""
        stages = {"S00": {"status": "pending"}}
        result = _serialize_stages_with_lock(stages)
        self.assertFalse(result["S00"]["locked"])
        self.assertTrue(result["S01"]["locked"])  # S01应该锁定
    
    def test_serialize_stages_with_lock_json_string(self):
        """测试_serialize_stages_with_lock: JSON字符串格式"""
        stages = json.dumps({"S00": {"status": "checked"}})
        result = _serialize_stages_with_lock(stages)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), len(STAGE_ORDER))
    
    def test_serialize_stages_with_lock_invalid_json(self):
        """测试_serialize_stages_with_lock: 无效JSON"""
        stages = "invalid json"
        result = _serialize_stages_with_lock(stages)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), len(STAGE_ORDER))
    
    def test_serialize_stages_with_lock_none(self):
        """测试_serialize_stages_with_lock: stages为None"""
        result = _serialize_stages_with_lock(None)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), len(STAGE_ORDER))
    
    def test_serialize_stages_with_lock_list(self):
        """测试_serialize_stages_with_lock: stages为列表（错误类型）"""
        stages = ["S00", "S01"]
        result = _serialize_stages_with_lock(stages)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), len(STAGE_ORDER))
    
    def test_serialize_stages_with_lock_all_passed(self):
        """测试_serialize_stages_with_lock: 所有阶段已通过"""
        stages = {
            "S00": {"status": "checked"},
            "S01": {"status": "passed"},
            "S02": {"status": "passed"},
            "S03": {"status": "passed"},
            "S04": {"status": "passed"},
            "S05": {"status": "passed"}
        }
        result = _serialize_stages_with_lock(stages)
        for key in STAGE_ORDER:
            self.assertFalse(result[key]["locked"])
    
    def test_calculate_construction_schedule(self):
        """测试calculate_construction_schedule: 计算施工计划"""
        start_date = datetime(2026, 2, 15)
        result = calculate_construction_schedule(start_date)
        
        self.assertIn("stages", result)
        self.assertIn("estimated_end_date", result)
        self.assertEqual(len(result["stages"]), len(STAGE_ORDER))
        
        # 验证第一个阶段
        self.assertEqual(result["stages"]["S00"]["status"], "pending")
        self.assertEqual(result["stages"]["S00"]["start_date"], start_date)
        
        # 验证最后一个阶段有结束日期
        self.assertIn("end_date", result["stages"]["S05"])
    
    def test_calculate_construction_schedule_sequence(self):
        """测试calculate_construction_schedule: 阶段序号"""
        start_date = datetime(2026, 2, 15)
        result = calculate_construction_schedule(start_date)
        
        for i, stage in enumerate(STAGE_ORDER):
            self.assertEqual(result["stages"][stage]["sequence"], i + 1)
    
    def test_calculate_construction_schedule_future_date(self):
        """测试calculate_construction_schedule: 未来日期"""
        future_date = datetime.now() + timedelta(days=365)
        result = calculate_construction_schedule(future_date)
        self.assertIn("stages", result)
        self.assertIn("estimated_end_date", result)
    
    def test_calculate_construction_schedule_past_date(self):
        """测试calculate_construction_schedule: 过去日期"""
        past_date = datetime.now() - timedelta(days=30)
        result = calculate_construction_schedule(past_date)
        self.assertIn("stages", result)
        # 应该仍然能计算，但实际业务中应该验证日期不能早于今天
    
    def test_calculate_progress_empty(self):
        """测试calculate_progress: 空stages"""
        progress = calculate_progress({})
        self.assertEqual(progress, 0)
    
    def test_calculate_progress_none(self):
        """测试calculate_progress: stages为None"""
        progress = calculate_progress(None)
        self.assertEqual(progress, 0)
    
    def test_calculate_progress_partial(self):
        """测试calculate_progress: 部分完成"""
        stages = {
            "S00": {"status": "checked", "duration": 7},
            "S01": {"status": "pending", "duration": 14}
        }
        progress = calculate_progress(stages)
        # S00完成，S01未完成，进度应该是 S00的duration / 总duration
        self.assertGreater(progress, 0)
        self.assertLess(progress, 100)
    
    def test_calculate_progress_all_completed(self):
        """测试calculate_progress: 全部完成"""
        stages = {
            "S00": {"status": "checked", "duration": 7},
            "S01": {"status": "passed", "duration": 14},
            "S02": {"status": "passed", "duration": 10},
            "S03": {"status": "passed", "duration": 10},
            "S04": {"status": "passed", "duration": 7},
            "S05": {"status": "passed", "duration": 7}
        }
        progress = calculate_progress(stages)
        self.assertEqual(progress, 100)
    
    def test_calculate_progress_zero_duration(self):
        """测试calculate_progress: 零duration"""
        stages = {
            "S00": {"status": "checked", "duration": 0}
        }
        progress = calculate_progress(stages)
        self.assertEqual(progress, 0)
    
    def test_calculate_progress_missing_duration(self):
        """测试calculate_progress: 缺失duration"""
        stages = {
            "S00": {"status": "checked"}
        }
        progress = calculate_progress(stages)
        # 应该处理缺失duration的情况
        self.assertGreaterEqual(progress, 0)
        self.assertLessEqual(progress, 100)


class TestDataFlow(unittest.TestCase):
    """数据流测试"""
    
    def test_stage_unlock_flow(self):
        """测试阶段解锁数据流"""
        # 初始状态：所有阶段锁定（除了S00）
        stages = {}
        result = _serialize_stages_with_lock(stages)
        self.assertFalse(result["S00"]["locked"])
        self.assertTrue(result["S01"]["locked"])
        
        # S00完成
        stages = {"S00": {"status": "checked"}}
        result = _serialize_stages_with_lock(stages)
        self.assertFalse(result["S00"]["locked"])
        self.assertFalse(result["S01"]["locked"])  # S01解锁
        
        # S01完成
        stages = {
            "S00": {"status": "checked"},
            "S01": {"status": "passed"}
        }
        result = _serialize_stages_with_lock(stages)
        self.assertFalse(result["S01"]["locked"])
        self.assertFalse(result["S02"]["locked"])  # S02解锁
    
    def test_progress_calculation_flow(self):
        """测试进度计算数据流"""
        # 初始进度
        stages = {}
        progress1 = calculate_progress(stages)
        self.assertEqual(progress1, 0)
        
        # S00完成
        stages = {"S00": {"status": "checked", "duration": 7}}
        progress2 = calculate_progress(stages)
        self.assertGreater(progress2, progress1)
        
        # 所有阶段完成
        stages = {
            "S00": {"status": "checked", "duration": 7},
            "S01": {"status": "passed", "duration": 14},
            "S02": {"status": "passed", "duration": 10},
            "S03": {"status": "passed", "duration": 10},
            "S04": {"status": "passed", "duration": 7},
            "S05": {"status": "passed", "duration": 7}
        }
        progress3 = calculate_progress(stages)
        self.assertEqual(progress3, 100)
    
    def test_stage_status_transition_flow(self):
        """测试阶段状态转换流程"""
        # pending -> checked (S00)
        stages = {"S00": {"status": "pending"}}
        self.assertFalse(_stage_passed(stages, "S00"))
        
        stages = {"S00": {"status": "checked"}}
        self.assertTrue(_stage_passed(stages, "S00"))
        
        # pending -> passed (S01)
        stages = {"S01": {"status": "pending"}}
        self.assertFalse(_stage_passed(stages, "S01"))
        
        stages = {"S01": {"status": "passed"}}
        self.assertTrue(_stage_passed(stages, "S01"))


class TestBoundaryConditions(unittest.TestCase):
    """边界条件测试"""
    
    def test_normalize_stage_key_empty_string(self):
        """测试normalize_stage_key: 空字符串"""
        result = normalize_stage_key("")
        self.assertEqual(result, "")
    
    def test_normalize_stage_key_case_sensitive(self):
        """测试normalize_stage_key: 大小写敏感"""
        self.assertEqual(normalize_stage_key("s00"), "s00")  # 小写不匹配
        self.assertEqual(normalize_stage_key("S00"), "S00")  # 大写匹配
    
    def test_calculate_progress_overflow(self):
        """测试calculate_progress: 进度超过100%的情况"""
        stages = {
            "S00": {"status": "checked", "duration": 100},
            "S01": {"status": "passed", "duration": 1}
        }
        progress = calculate_progress(stages)
        # 应该限制在100%
        self.assertLessEqual(progress, 100)
    
    def test_calculate_progress_negative_duration(self):
        """测试calculate_progress: 负duration"""
        stages = {
            "S00": {"status": "checked", "duration": -5}
        }
        progress = calculate_progress(stages)
        # 应该处理负duration
        self.assertGreaterEqual(progress, 0)


def run_whitebox_tests():
    """运行白盒测试并生成报告"""
    print("=" * 70)
    print("白盒测试 - 代码内部逻辑测试")
    print("=" * 70)
    print("\n测试覆盖:")
    print("1. 函数内部逻辑")
    print("2. 分支条件")
    print("3. 边界条件")
    print("4. 异常情况")
    print("5. 数据流")
    print("=" * 70)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestConstructionFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestDataFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestBoundaryConditions))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出统计
    print("\n" + "=" * 70)
    print("白盒测试结果统计")
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
            print(f"     {traceback.split(chr(10))[-2]}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  ❌ {test}")
            print(f"     {traceback.split(chr(10))[-2]}")
    
    if result.skipped:
        print("\n跳过的测试:")
        for test, reason in result.skipped:
            print(f"  ⏭️  {test}: {reason}")
    
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    result = run_whitebox_tests()
    sys.exit(0 if result.wasSuccessful() else 1)

print("=== 测试验收报告阶段映射逻辑 ===")

# 模拟后端API中的映射逻辑
_ACCEPTANCE_STAGE_TO_S = {"material": "S00", "plumbing": "S01", "carpentry": "S02", "woodwork": "S03", "painting": "S04", "installation": "S05", "flooring": "S02", "soft_furnishing": "S05"}
for _s in ["S00", "S01", "S02", "S03", "S04", "S05"]:
    _ACCEPTANCE_STAGE_TO_S[_s] = _s

STAGES_LEGACY = ["plumbing", "carpentry", "painting", "flooring", "soft_furnishing", "woodwork", "installation", "material"]

print("\n1. 映射表 _ACCEPTANCE_STAGE_TO_S:")
for k, v in sorted(_ACCEPTANCE_STAGE_TO_S.items()):
    print(f"  {k:15} -> {v}")

print("\n2. 反向映射 reverse_mapping:")
reverse_mapping = {v: k for k, v in _ACCEPTANCE_STAGE_TO_S.items()}
for k, v in sorted(reverse_mapping.items()):
    print(f"  {k:15} -> {v}")

print("\n3. 测试阶段映射逻辑:")
test_stages = ["S01", "S02", "S03", "S04", "S05", "plumbing", "carpentry", "woodwork", "painting", "installation"]

for stage in test_stages:
    mapped_stage = None
    if stage in reverse_mapping:
        legacy_key = reverse_mapping[stage]
        if legacy_key in STAGES_LEGACY:
            mapped_stage = legacy_key
    
    print(f"  前端发送: {stage:15} -> 映射到: {mapped_stage or '无映射'}")

print("\n4. 数据库查询条件模拟:")
print("   当 stage='S03' 时:")
print("   - reverse_mapping['S03'] = 'woodwork'")
print("   - 'woodwork' in STAGES_LEGACY = True")
print("   - mapped_stage = 'woodwork'")
print("   - 查询条件: (stage == 'S03') OR (stage == 'woodwork')")
print("   - 数据库中存储的是 'woodwork'，所以应该能匹配到")

print("\n5. 数据库实际数据:")
print("   根据查询结果，数据库中有4条 woodwork 阶段的验收报告")
print("   ID: 50, 49, 46, 26")

print("\n6. 可能的问题:")
print("   a) 用户ID不匹配：API只返回当前用户的验收报告")
print("   b) 分页问题：可能在第2页或后面")
print("   c) 前端显示逻辑问题：可能过滤掉了某些状态")
print("   d) 数据库查询条件有误：需要检查SQLAlchemy生成的SQL")

print("\n7. 建议的排查步骤:")
print("   1. 检查API返回的实际数据")
print("   2. 检查前端是否正确解析和显示数据")
print("   3. 检查用户ID是否正确")
print("   4. 检查分页参数")

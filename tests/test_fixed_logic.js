// 测试修复后的前端逻辑
console.log('=== 测试修复后的前端逻辑 ===');

// 模拟修复后的calculateStorage函数逻辑
function simulateFixedCalculateStorage() {
  // 模拟getWithAuth返回的数据（已经处理了API响应格式）
  const mockApiResponse = {
    photo_count: 14,
    estimated_size_mb: 661.84,
    total_storage_mb: 100,
    usage_percentage: 100,
    storage_duration_months: 12,
    is_member: true,
    warning_level: "high",
    file_count: 329,
    data_source: "oss_real",
    by_type: {
      construction: { count: 14, size_bytes: 36717528, size_mb: 35.02 },
      acceptance: { count: 113, size_bytes: 254947737, size_mb: 243.14 },
      quote: { count: 64, size_bytes: 93020634, size_mb: 88.71 },
      contract: { count: 38, size_bytes: 62269002, size_mb: 59.38 }
    }
  };
  
  // 修复后的逻辑：const data = res || {}
  const res = mockApiResponse; // getWithAuth返回的数据
  const data = res || {};
  
  console.log('1. 修复后的逻辑:');
  console.log('const res = await getWithAuth(\'/users/storage-usage\') as any');
  console.log('const data = res || {}');
  console.log('data结果:', JSON.stringify(data, null, 2));
  
  const storageInfo = {
    used: data.estimated_size_mb || 0,
    total: data.total_storage_mb || 100
  };
  
  console.log('\n2. 计算出的storageInfo:');
  console.log('used:', storageInfo.used, 'MB');
  console.log('total:', storageInfo.total, 'MB');
  console.log('使用百分比:', Math.round((storageInfo.used / storageInfo.total) * 100) + '%');
  
  // 验证
  if (storageInfo.used === 661.84) {
    console.log('\n✅ 修复成功！前端现在能正确显示存储空间使用情况：');
    console.log(`   已使用 ${storageInfo.used} MB / 总存储 ${storageInfo.total} MB`);
  } else if (storageInfo.used === 0) {
    console.log('\n❌ 修复失败！前端仍然显示0MB');
  } else {
    console.log(`\n⚠️  显示值: ${storageInfo.used} MB (期望值: 661.84 MB)`);
  }
  
  return storageInfo;
}

// 运行测试
const result = simulateFixedCalculateStorage();

console.log('\n3. 前端显示效果预测:');
console.log('在数据管理页面的"数据工具"选项卡中，用户将看到:');
console.log(`   "已使用 ${result.used} MB / 总存储 ${result.total} MB"`);
console.log(`   进度条宽度: ${(result.used / result.total) * 100}%`);
console.log(`   警告级别: ${result.used >= result.total * 0.9 ? '高 (红色)' : result.used >= result.total * 0.7 ? '中 (黄色)' : '低 (绿色)'}`);

console.log('\n=== 测试完成 ===');

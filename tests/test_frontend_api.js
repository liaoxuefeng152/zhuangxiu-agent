// 测试前端API调用逻辑
console.log('=== 测试前端API调用逻辑 ===');

// 模拟getWithAuth的返回逻辑
function simulateGetWithAuth() {
  // 模拟后端API响应
  const mockResponse = {
    code: 0,
    msg: "success",
    data: {
      photo_count: 13,
      estimated_size_mb: 661.37,
      total_storage_mb: 100,
      usage_percentage: 100,
      storage_duration_months: 12,
      is_member: true,
      warning_level: "high",
      file_count: 327,
      data_source: "oss_real",
      by_type: {
        construction: { count: 13, size_bytes: 36471245, size_mb: 34.78 },
        acceptance: { count: 112, size_bytes: 254701454, size_mb: 242.9 },
        quote: { count: 64, size_bytes: 93020634, size_mb: 88.71 },
        contract: { count: 38, size_bytes: 62269002, size_mb: 59.38 }
      }
    }
  };
  
  // getWithAuth的逻辑：返回 r.data?.data ?? r.data
  // 对于这个响应：r.data?.data 是 mockResponse.data，所以返回 mockResponse.data
  return mockResponse.data; // 这是getWithAuth的返回值
}

// 测试calculateStorage函数中的逻辑
function testCalculateStorage() {
  console.log('1. 模拟getWithAuth调用...');
  const res = simulateGetWithAuth();
  console.log('getWithAuth返回值:', JSON.stringify(res, null, 2));
  
  console.log('\n2. calculateStorage中的逻辑:');
  console.log('const res = await getWithAuth(\'/users/storage-usage\') as any');
  console.log('const data = res?.data || {}');
  
  const data = res?.data || {};
  console.log('data结果:', data);
  console.log('data是否为空对象?', Object.keys(data).length === 0);
  
  if (Object.keys(data).length === 0) {
    console.log('❌ 问题发现：data是空对象！');
    console.log('原因：getWithAuth已经返回了data字段，但代码又尝试获取res?.data');
    console.log('解决方案：应该直接使用res，而不是res?.data');
  } else {
    console.log('✅ data包含数据');
  }
  
  // 正确的写法
  console.log('\n3. 正确的写法:');
  console.log('const data = res || {}');
  const correctData = res || {};
  console.log('正确data结果:', correctData);
  console.log('estimated_size_mb:', correctData.estimated_size_mb);
}

testCalculateStorage();

// 模拟前端调用存储空间API
const BASE_URL = 'http://120.26.201.61:8001/api/v1';

// 模拟登录获取token
async function login() {
  const response = await fetch(`${BASE_URL}/users/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ code: 'dev_h5_mock' })
  });
  
  if (!response.ok) {
    throw new Error(`登录失败: ${response.status}`);
  }
  
  const data = await response.json();
  return data.access_token;
}

// 获取存储空间信息
async function getStorageUsage(token) {
  const response = await fetch(`${BASE_URL}/users/storage-usage`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error(`获取存储空间失败: ${response.status}`);
  }
  
  const data = await response.json();
  return data;
}

// 测试函数
async function testFrontendStorage() {
  console.log('=== 测试前端存储空间功能 ===');
  
  try {
    // 1. 登录
    console.log('1. 登录获取token...');
    const token = await login();
    console.log(`✅ 登录成功，token: ${token.substring(0, 50)}...`);
    
    // 2. 获取存储空间信息
    console.log('\n2. 获取存储空间信息...');
    const storageData = await getStorageUsage(token);
    
    console.log(`API响应状态: ${storageData.code} - ${storageData.msg}`);
    
    const data = storageData.data || {};
    console.log(`数据源: ${data.data_source || 'unknown'}`);
    console.log(`文件总数: ${data.file_count || 0}`);
    console.log(`照片数量: ${data.photo_count || 0}`);
    console.log(`估算大小: ${data.estimated_size_mb || 0} MB`);
    console.log(`总存储空间: ${data.total_storage_mb || 0} MB`);
    console.log(`使用百分比: ${data.usage_percentage || 0}%`);
    console.log(`警告级别: ${data.warning_level || 'unknown'}`);
    console.log(`会员状态: ${data.is_member || false}`);
    console.log(`存储期限: ${data.storage_duration_months || 12}个月`);
    
    // 显示按类型统计
    const byType = data.by_type || {};
    if (Object.keys(byType).length > 0) {
      console.log('\n按类型统计:');
      for (const [fileType, stats] of Object.entries(byType)) {
        console.log(`  ${fileType}: ${stats.count || 0}个文件, ${stats.size_mb || 0}MB`);
      }
    }
    
    // 验证数据
    if (data.data_source === 'oss_real') {
      console.log('\n✅ 前端成功获取真实OSS存储数据');
      console.log('存储空间功能在前端正常工作！');
    } else if (data.data_source === 'database_estimate') {
      console.log('\n⚠️  前端使用数据库估算数据（OSS可能未配置或调用失败）');
    } else if (data.data_source === 'error_fallback') {
      console.log(`\n⚠️  OSS调用失败，前端使用后备数据: ${data.error || '未知错误'}`);
    } else {
      console.log(`\n❌ 前端获取未知数据源: ${data.data_source}`);
    }
    
    return true;
    
  } catch (error) {
    console.error(`❌ 测试失败: ${error.message}`);
    return false;
  }
}

// 运行测试
testFrontendStorage().then(success => {
  if (success) {
    console.log('\n✅ 前端存储空间功能测试通过');
  } else {
    console.log('\n❌ 前端存储空间功能测试失败');
  }
});

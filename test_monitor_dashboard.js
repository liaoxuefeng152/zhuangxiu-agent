// 测试监控仪表板数据加载
const https = require('https');

const API_BASE = 'https://lakeli.top/api/v1/monitor';

function testAPI(endpoint) {
  return new Promise((resolve, reject) => {
    const req = https.get(`${API_BASE}/${endpoint}`, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          console.log(`✅ ${endpoint}: 状态码 ${res.statusCode}`);
          console.log(`   数据: ${JSON.stringify(jsonData.data).substring(0, 100)}...`);
          resolve(jsonData);
        } catch (error) {
          console.log(`❌ ${endpoint}: JSON解析失败`);
          reject(error);
        }
      });
    });
    
    req.on('error', (error) => {
      console.log(`❌ ${endpoint}: 请求失败 - ${error.message}`);
      reject(error);
    });
    
    req.setTimeout(5000, () => {
      req.destroy();
      console.log(`❌ ${endpoint}: 请求超时`);
      reject(new Error('请求超时'));
    });
  });
}

async function runTests() {
  console.log('🚀 开始测试监控仪表板API...\n');
  
  try {
    // 测试所有API端点
    await testAPI('metrics');
    await testAPI('status');
    await testAPI('backup/status');
    await testAPI('overview');
    
    console.log('\n✅ 所有API测试通过！');
    console.log('\n📊 监控仪表板现在应该能够正常显示数据：');
    console.log('   1. 系统指标（CPU、内存、磁盘使用率）');
    console.log('   2. 服务状态（数据库、Redis、OSS、API）');
    console.log('   3. 备份状态（最近备份、备份文件数）');
    console.log('   4. 业务指标（用户数、订单数）');
    console.log('\n🌐 访问地址：https://lakeli.top/monitor_dashboard.html');
    
  } catch (error) {
    console.log('\n❌ 测试失败：', error.message);
    process.exit(1);
  }
}

runTests();

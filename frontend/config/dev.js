module.exports = {
  // 开发环境配置
  env: {
    TARO_APP_MODE: 'dev',
    TARO_APP_API_BASE_URL: process.env.TARO_APP_API_BASE_URL || 'http://localhost:8000/api/v1'
  }
}

module.exports = {
  // 开发环境配置
  env: {
    TARO_APP_MODE: 'dev',
    // 默认连阿里云 dev 环境（直连后端 8001）；走 Nginx 可改 dev.lakeli.top
    TARO_APP_API_BASE_URL: process.env.TARO_APP_API_BASE_URL || 'http://120.26.201.61:8001/api/v1'
  }
}

/**
 * 环境配置
 * 支持多环境配置管理
 */

export interface EnvConfig {
  apiBaseUrl: string;
  apiTimeout: number;
  enableCache: boolean;
  debugMode: boolean;
}

const getEnvConfig = (): EnvConfig => {
  // 优先使用环境变量 TARO_APP_API_BASE_URL（.env.development / .env.production）
  const apiBaseUrl =
    process.env.TARO_APP_API_BASE_URL ||
    (process.env.NODE_ENV === 'production' ? 'https://your-domain.com/api/v1' : 'http://localhost:8000/api/v1')

  const common = {
    apiBaseUrl,
    apiTimeout: parseInt(process.env.API_TIMEOUT || '30000'),
    enableCache: process.env.ENABLE_CACHE !== 'false',
    debugMode: process.env.NODE_ENV !== 'production'
  }

  if (process.env.TARO_ENV === 'weapp' || process.env.TARO_ENV === 'h5') {
    return { ...common, apiTimeout: parseInt(process.env.API_TIMEOUT || '30000') }
  }

  return {
    ...common,
    apiTimeout: process.env.NODE_ENV === 'production' ? 30000 : 60000
  }
}

export const env = getEnvConfig()

export default env

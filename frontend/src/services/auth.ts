/**
 * 认证服务
 * 处理Token存储、过期检查和自动清理
 */

export interface TokenPayload {
  user_id: number;
  openid: string;
  exp: number;
}

export class TokenManager {
  /**
   * 设置Token
   */
  static setToken(token: string) {
    if (process.env.TARO_ENV === 'weapp') {
      // 小程序环境：使用本地存储
      Taro.setStorageSync('access_token', token)
    } else {
      // H5环境：使用HttpOnly Cookie
      document.cookie = `access_token=${token}; path=/; secure; HttpOnly; SameSite=Strict`
    }
  }

  /**
   * 获取Token
   */
  static getToken(): string | null {
    if (process.env.TARO_ENV === 'weapp') {
      return Taro.getStorageSync('access_token') || null
    } else {
      const match = document.cookie.match(/access_token=([^;]+)/)
      return match ? match[1] : null
    }
  }

  /**
   * 清除Token
   */
  static clearToken() {
    if (process.env.TARO_ENV === 'weapp') {
      Taro.removeStorageSync('access_token')
    } else {
      document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
    }
  }

  /**
   * 检查Token是否过期
   */
  static isTokenExpired(): boolean {
    const token = this.getToken()
    if (!token) return true

    try {
      const payload = this.decodeToken(token)
      if (!payload || !payload.exp) return true

      // Token过期时间（秒）转换为毫秒
      const expTime = payload.exp * 1000
      const now = Date.now()

      // 提前5分钟判定为过期，给续约留出时间
      return expTime - now < 300000 // 5分钟
    } catch (error) {
      console.error('Token解码失败:', error)
      return true
    }
  }

  /**
   * 解码Token
   */
  static decodeToken(token: string): TokenPayload | null {
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
      return JSON.parse(jsonPayload)
    } catch (error) {
      console.error('Token解码失败:', error)
      return null
    }
  }

  /**
   * 获取用户ID
   */
  static getUserId(): number | null {
    const token = this.getToken()
    if (!token) return null

    try {
      const payload = this.decodeToken(token)
      return payload?.user_id || null
    } catch (error) {
      return null
    }
  }

  /**
   * 获取OpenID
   */
  static getOpenid(): string | null {
    const token = this.getToken()
    if (!token) return null

    try {
      const payload = this.decodeToken(token)
      return payload?.openid || null
    } catch (error) {
      return null
    }
  }
}

export default TokenManager

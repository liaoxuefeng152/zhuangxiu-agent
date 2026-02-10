/**
 * 认证工具函数
 * 提供登录状态检查、登录跳转等功能
 */
import Taro from '@tarojs/taro'

/**
 * 检查用户是否已登录
 */
export function isLoggedIn(): boolean {
  const token = Taro.getStorageSync('access_token')
  return !!token
}

/**
 * 获取当前用户的Token
 */
export function getToken(): string | null {
  return Taro.getStorageSync('access_token') || null
}

/**
 * 获取当前用户的ID
 */
export function getUserId(): number | null {
  const userId = Taro.getStorageSync('user_id')
  return userId ? Number(userId) : null
}

/**
 * 检查登录状态，如果未登录则提示并跳转
 * @param showModal 是否显示确认弹窗（默认true）
 * @param redirectTo 跳转目标（默认"我的"页面）
 * @returns 是否已登录
 */
export function checkLogin(
  showModal: boolean = true,
  redirectTo: 'profile' | 'home' = 'profile'
): boolean {
  if (isLoggedIn()) {
    return true
  }

  if (showModal) {
    Taro.showModal({
      title: '需要登录',
      content: '此功能需要登录，是否前往登录？',
      confirmText: '去登录',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          if (redirectTo === 'profile') {
            Taro.switchTab({ url: '/pages/profile/index' })
          } else {
            Taro.switchTab({ url: '/pages/index/index' })
          }
        }
      }
    })
  }

  return false
}

/**
 * 清除登录信息
 */
export function clearLogin(): void {
  Taro.removeStorageSync('access_token')
  Taro.removeStorageSync('user_id')
}

/**
 * 保存登录信息
 */
export function saveLogin(token: string, userId: number | string): void {
  Taro.setStorageSync('access_token', token)
  Taro.setStorageSync('user_id', String(userId))
}

/**
 * 检查Token是否过期（简单检查，实际过期由后端401判断）
 * @returns 是否可能过期（true表示可能过期，需要重新登录）
 */
export function isTokenExpired(): boolean {
  const token = getToken()
  if (!token) return true

  try {
    // JWT Token格式：header.payload.signature
    const parts = token.split('.')
    if (parts.length !== 3) return true

    // 解码payload
    const payload = JSON.parse(
      decodeURIComponent(
        atob(parts[1])
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
    )

    // 检查过期时间（exp是秒级时间戳）
    if (payload.exp) {
      const expTime = payload.exp * 1000 // 转换为毫秒
      const now = Date.now()
      // 提前5分钟判定为过期
      return expTime - now < 300000
    }

    return false
  } catch (error) {
    console.error('Token解析失败:', error)
    return true
  }
}

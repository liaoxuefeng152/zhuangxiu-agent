/**
 * API服务层 - 封装所有后端API请求
 */
import Taro from '@tarojs/taro'
import axios, { AxiosInstance, AxiosResponse } from 'axios'
import store from '../store'
import { setNetworkError } from '../store/slices/networkSlice'
import { env } from '../config/env'

// API 基础配置：统一从 env 读取
const BASE_URL = env.apiBaseUrl

// 创建axios实例
const instance: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    // 添加token
    const token = Taro.getStorageSync('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加用户ID
    const userId = Taro.getStorageSync('user_id')
    if (userId) {
      config.headers['X-User-Id'] = userId
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：兼容两种后端格式
// 1) { code: 0, msg, data }  2) 直接返回数据 { access_token, id, ... }
instance.interceptors.response.use(
  (response: AxiosResponse) => {
    const body = response.data as any
    const code = body?.code
    const msg = body?.msg
    const data = body?.data

    // 格式1：标准 ApiResponse，code=0 表示成功
    if (code === 0) {
      return data
    }

    // 格式2：直接返回数据（如 login、profile、scan 等 response_model）
    if (code === undefined && body && typeof body === 'object' && !body.error_id) {
      return body
    }

    // 业务错误
    Taro.showToast({
      title: msg || body?.detail || '请求失败',
      icon: 'none',
      duration: 2000
    })

    return Promise.reject(new Error(msg || '请求失败'))
  },
  (error) => {
    // HTTP错误
    let message = '网络请求失败'

    if (error.response) {
      const { status } = error.response

      switch (status) {
        case 401:
          message = '登录已过期，请重新登录'
          // 清除token和用户信息
          Taro.removeStorageSync('access_token')
          Taro.removeStorageSync('user_id')
          
          // 检查是否已完成引导，如果已完成则跳转到首页，否则跳转到引导页
          const hasOnboarded = Taro.getStorageSync('onboarding_completed') || Taro.getStorageSync('has_onboarded')
          if (hasOnboarded) {
            // 已完成引导，跳转到首页，用户可以在"我的"页面重新登录
            Taro.reLaunch({ url: '/pages/index/index' })
            // 延迟显示提示，避免与页面跳转冲突
            setTimeout(() => {
              Taro.showModal({
                title: '登录已过期',
                content: '您的登录已过期，请前往"我的"页面重新登录',
                showCancel: false,
                confirmText: '知道了'
              })
            }, 500)
          } else {
            // 未完成引导，跳转到引导页
            Taro.reLaunch({ url: '/pages/onboarding/index' })
          }
          break
        case 403:
          message = '无权限访问'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = `请求错误: ${status}`
      }
    } else if (error.request) {
      message = '网络连接失败，请检查网络'
      store.dispatch(setNetworkError(true))
      try {
        const inst = Taro.getCurrentInstance()
        const from = inst.router?.path
          ? `${inst.router.path}${inst.router.params && Object.keys(inst.router.params).length
            ? '?' + Object.entries(inst.router.params).map(([k, v]) => `${k}=${v}`).join('&')
            : ''}`
          : ''
        Taro.redirectTo({
          url: '/pages/network-error/index' + (from ? '?from=' + encodeURIComponent(from) : '')
        })
      } catch (_) {
        Taro.showToast({ title: message, icon: 'none', duration: 2000 })
      }
      return Promise.reject(error)
    }

    Taro.showToast({
      title: message,
      icon: 'none',
      duration: 2000
    })

    return Promise.reject(error)
  }
)

/**
 * 用户相关API
 */
export const userApi = {
  // 微信登录
  login: (code: string) => {
    return instance.post('/users/login', { code })
  },

  // 获取用户信息
  getProfile: () => {
    return instance.get('/users/profile')
  },

  // 更新用户信息
  updateProfile: (data: { nickname?: string, avatar_url?: string }) => {
    return instance.put('/users/profile', data)
  }
}

/**
 * 公司检测相关API
 */
export const companyApi = {
  // 扫描公司
  scan: (companyName: string) => {
    return instance.post('/companies/scan', { company_name: companyName })
  },

  // 获取扫描结果
  getResult: (scanId: number) => {
    return instance.get(`/companies/scan/${scanId}`)
  },

  // 获取扫描列表
  getList: (params?: { page?: number, page_size?: number }) => {
    return instance.get('/companies/scans', { params })
  },

  // 公司名称模糊搜索 (FR-012)
  search: (keyword: string, limit?: number) => {
    return instance.get('/companies/search', { params: { q: keyword, limit: limit || 5 } })
  }
}

/**
 * 报价单相关API
 */
export const quoteApi = {
  // 上传报价单
  upload: (filePath: string, fileName: string) => {
    return new Promise((resolve, reject) => {
      const token = Taro.getStorageSync('access_token')
      const userId = Taro.getStorageSync('user_id')
      const header: Record<string, string> = { 'X-User-Id': String(userId || '') }
      if (token) header.Authorization = `Bearer ${token}`
      Taro.uploadFile({
        url: `${BASE_URL}/quotes/upload`,
        filePath,
        name: 'file',
        header,
        success: (res) => {
          try {
            const data = JSON.parse(res.data)
            resolve(data)
          } catch (error) {
            reject(error)
          }
        },
        fail: reject
      })
    })
  },

  // 获取分析结果
  getAnalysis: (quoteId: number) => {
    return instance.get(`/quotes/quote/${quoteId}`)
  },

  // 获取报价单列表
  getList: (params?: { page?: number, page_size?: number }) => {
    return instance.get('/quotes/list', { params })
  }
}

/**
 * 合同相关API
 */
export const contractApi = {
  // 上传合同
  upload: (filePath: string, fileName: string) => {
    return new Promise((resolve, reject) => {
      const token = Taro.getStorageSync('access_token')
      const userId = Taro.getStorageSync('user_id')
      const header: Record<string, string> = { 'X-User-Id': String(userId || '') }
      if (token) header.Authorization = `Bearer ${token}`
      Taro.uploadFile({
        url: `${BASE_URL}/contracts/upload`,
        filePath,
        name: 'file',
        header,
        success: (res) => {
          try {
            const data = JSON.parse(res.data)
            resolve(data)
          } catch (error) {
            reject(error)
          }
        },
        fail: reject
      })
    })
  },

  // 获取分析结果
  getAnalysis: (contractId: number) => {
    return instance.get(`/contracts/contract/${contractId}`)
  },

  // 获取合同列表
  getList: (params?: { page?: number, page_size?: number }) => {
    return instance.get('/contracts/list', { params })
  }
}

/**
 * 施工进度相关API
 */
export const constructionApi = {
  // 获取进度计划
  getSchedule: () => {
    return instance.get('/constructions/schedule')
  },

  // 设置开工日期
  setStartDate: (startDate: string) => {
    return instance.post('/constructions/start-date', { start_date: startDate })
  },

  // 更新阶段状态
  updateStageStatus: (stage: string, status: string) => {
    return instance.put('/constructions/stage-status', { stage, status })
  },

  // 校准阶段验收时间（后续阶段顺延，提醒联动）
  calibrateStageEnd: (stage: string, endDate: string) => {
    return instance.post('/constructions/calibrate', { stage, end_date: endDate })
  },

  // 重置进度
  resetSchedule: () => {
    return instance.delete('/constructions/schedule')
  }
}

/**
 * 订单支付相关API
 */
export const paymentApi = {
  // 创建订单
  createOrder: (data: { order_type: string, resource_type: string, resource_id: number }) => {
    return instance.post('/payments/create', data)
  },

  // 发起支付
  pay: (orderId: number) => {
    return instance.post('/payments/pay', { order_id: orderId })
  },

  // 获取订单列表
  getOrders: (params?: { page?: number, page_size?: number }) => {
    return instance.get('/payments/orders', { params })
  },

  // 获取订单详情
  getOrder: (orderId: number) => {
    return instance.get(`/payments/order/${orderId}`)
  }
}

/**
 * 消息中心 API
 */
export const messageApi = {
  getList: (params?: { category?: string; page?: number; page_size?: number }) => {
    return instance.get('/messages', { params })
  },
  getUnreadCount: () => instance.get('/messages/unread-count'),
  markRead: (msgId: number) => instance.put(`/messages/${msgId}/read`),
  markAllRead: () => instance.put('/messages/read-all')
}

/**
 * 意见反馈 API
 */
export const feedbackApi = {
  submit: (content: string, images?: string[]) => {
    return instance.post('/feedback', { content, images })
  }
}

/**
 * 施工照片 API
 */
export const constructionPhotoApi = {
  upload: (filePath: string, stage: string) => {
    return new Promise((resolve, reject) => {
      const token = Taro.getStorageSync('access_token')
      const userId = Taro.getStorageSync('user_id')
      const header: Record<string, string> = {}
      if (token) header.Authorization = `Bearer ${token}`
      if (userId) header['X-User-Id'] = userId
      Taro.uploadFile({
        url: `${BASE_URL}/construction-photos/upload?stage=${encodeURIComponent(stage)}`,
        filePath,
        name: 'file',
        header,
        success: (res) => {
          try {
            const data = JSON.parse(res.data)
            resolve(data?.data ?? data)
          } catch { reject(new Error('解析失败')) }
        },
        fail: reject
      })
    })
  },
  getList: (stage?: string) => instance.get('/construction-photos', { params: stage ? { stage } : {} }),
  delete: (photoId: number) => instance.delete(`/construction-photos/${photoId}`),
  move: (photoId: number, stage: string) => instance.put(`/construction-photos/${photoId}/move`, { stage })
}

/**
 * 验收分析 API
 */
export const acceptanceApi = {
  uploadPhoto: (filePath: string) => {
    return new Promise((resolve, reject) => {
      const token = Taro.getStorageSync('access_token')
      const userId = Taro.getStorageSync('user_id')
      const header: Record<string, string> = { 'X-User-Id': String(userId || '') }
      if (token) header.Authorization = `Bearer ${token}`
      Taro.uploadFile({
        url: `${BASE_URL}/acceptance/upload-photo`,
        filePath,
        name: 'file',
        header,
        success: (res) => {
          try {
            const data = JSON.parse(res.data)
            resolve(data?.data ?? data)
          } catch { reject(new Error('解析失败')) }
        },
        fail: reject
      })
    })
  },
  analyze: (stage: string, fileUrls: string[]) => instance.post('/acceptance/analyze', { stage, file_urls: fileUrls }),
  getResult: (analysisId: number) => instance.get(`/acceptance/${analysisId}`),
  getList: (params?: { stage?: string; page?: number; page_size?: number }) => {
    return instance.get('/acceptance', { params })
  }
}

/**
 * 报告导出 API
 */
export const reportApi = {
  getExportPdfUrl: (reportType: string, resourceId: number) =>
    `${BASE_URL}/reports/export-pdf?report_type=${reportType}&resource_id=${resourceId}`,
  downloadPdf: (reportType: string, resourceId: number, filename?: string) => {
    return new Promise((resolve, reject) => {
      const token = Taro.getStorageSync('access_token')
      const userId = Taro.getStorageSync('user_id')
      const header: Record<string, string> = { 'X-User-Id': String(userId || '') }
      if (token) header.Authorization = `Bearer ${token}`
      Taro.downloadFile({
        url: `${BASE_URL}/reports/export-pdf?report_type=${reportType}&resource_id=${resourceId}`,
        header,
        success: (res) => {
          if (res.statusCode === 200) {
            Taro.saveFile({ tempFilePath: res.tempFilePath }).then((saveRes) => resolve(saveRes.savedFilePath)).catch(reject)
          } else reject(new Error('导出失败'))
        },
        fail: reject
      })
    })
  }
}

export default instance

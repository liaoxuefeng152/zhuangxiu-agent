/**
 * API服务层 - 封装所有后端API请求
 */
import Taro from '@tarojs/taro'
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

// API基础配置
const BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://your-domain.com/api/v1'
  : 'http://localhost:8000/api/v1'

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

// 响应拦截器
instance.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, msg, data } = response.data

    // 成功响应
    if (code === 0) {
      return data
    }

    // 业务错误
    Taro.showToast({
      title: msg || '请求失败',
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
          // 清除token并跳转登录页
          Taro.removeStorageSync('access_token')
          Taro.removeStorageSync('user_id')
          Taro.reLaunch({ url: '/pages/onboarding/index' })
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
  }
}

/**
 * 报价单相关API
 */
export const quoteApi = {
  // 上传报价单
  upload: (filePath: string, fileName: string) => {
    return new Promise((resolve, reject) => {
      Taro.uploadFile({
        url: `${BASE_URL}/quotes/upload`,
        filePath,
        name: 'file',
        header: {
          'X-User-Id': Taro.getStorageSync('user_id')
        },
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
      Taro.uploadFile({
        url: `${BASE_URL}/contracts/upload`,
        filePath,
        name: 'file',
        header: {
          'X-User-Id': Taro.getStorageSync('user_id')
        },
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

export default instance

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

/** Taro.uploadFile 等非 axios 请求需手动带上的鉴权 header */
const getAuthHeaders = (): Record<string, string> => {
  const h: Record<string, string> = {}
  const token = Taro.getStorageSync('access_token')
  const userId = Taro.getStorageSync('user_id')
  if (token) h['Authorization'] = `Bearer ${token}`
  if (userId) h['X-User-Id'] = String(userId)
  return h
}

/** 微信小程序 uploadFile 可能不传自定义 header，将鉴权放入 URL query 作为备用 */
const appendAuthQuery = (url: string): string => {
  const token = Taro.getStorageSync('access_token')
  const userId = Taro.getStorageSync('user_id')
  const params = new URLSearchParams()
  if (token) params.set('access_token', token)
  if (userId) params.set('user_id', String(userId))
  const qs = params.toString()
  return qs ? `${url}${url.includes('?') ? '&' : '?'}${qs}` : url
}

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
    // HTTP错误：优先使用后端返回的 detail/msg
    const backendMsg = error.response?.data?.detail ?? error.response?.data?.msg
    const detailStr = typeof backendMsg === 'string' ? backendMsg : (Array.isArray(backendMsg) && backendMsg[0]?.msg ? backendMsg[0].msg : null)
    let message = detailStr || '网络请求失败'

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
          message = detailStr || '无权限访问'
          break
        case 404:
          message = detailStr || '请求的资源不存在'
          break
        case 500:
          message = detailStr || '服务器内部错误'
          break
        default:
          message = detailStr || `请求错误: ${status}`
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
      Taro.uploadFile({
        url: appendAuthQuery(`${BASE_URL}/quotes/upload`),
        filePath,
        name: 'file',
        header: getAuthHeaders(),
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
        url: appendAuthQuery(`${BASE_URL}/contracts/upload`),
        filePath,
        name: 'file',
        header: getAuthHeaders(),
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
 * 材料进场核对相关API
 */
export const materialsApi = {
  /** 材料进场核对通过（简化接口，无留证） */
  verify: () => instance.post('/materials/verify', {}),
}

/**
 * 材料进场人工核对 P37（FR-019~FR-023，支持留证）
 */
export const materialChecksApi = {
  getMaterialList: () => instance.get('/material-checks/material-list'),
  /** 提交核对结果，pass 需 items 每项至少1张照片，fail 需 problem_note≥10字 */
  submit: (data: { items: Array<{ material_name: string; spec_brand?: string; quantity?: string; photo_urls: string[] }>; result: 'pass' | 'fail'; problem_note?: string }) =>
    instance.post('/material-checks/submit', data),
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
 * 推荐：uploadDirect（后端签名+前端直传 OSS）
 * 备用：upload（经后端代理上传）
 */
export const constructionPhotoApi = {
  /** 获取 OSS 直传 policy（后端签名） */
  getUploadPolicy: (stage: string) =>
    instance.get('/oss/upload-policy', { params: { stage } }),

  /** 直传 OSS 后注册照片 */
  register: (stage: string, key: string) =>
    instance.post('/construction-photos/register', { stage, key }),

  /**
   * 后端签名 + 前端直传 OSS（阿里云最佳实践）
   * 失败时自动回退到 upload 代理上传
   */
  uploadDirect: async (filePath: string, stage: string): Promise<{ file_url: string; id?: number }> => {
    try {
      const policyRes = await instance.get('/oss/upload-policy', { params: { stage } }) as any
      const { host, policy, OSSAccessKeyId, signature, dir } = policyRes
      const ext = (filePath.split('.').pop() || 'jpg').toLowerCase().replace('jpeg', 'jpg') || 'jpg'
      const key = `${dir}${Date.now()}_${Math.floor(Math.random() * 10000)}.${ext}`
      return new Promise((resolve, reject) => {
        Taro.uploadFile({
          url: host,
          filePath,
          name: 'file',
          formData: {
            key,
            policy,
            OSSAccessKeyId,
            Signature: signature,
            success_action_status: '200'
          },
          success: async (res) => {
            if (res.statusCode >= 200 && res.statusCode < 300) {
              try {
                const reg = await instance.post('/construction-photos/register', { stage, key }) as any
                resolve(reg?.file_url ? reg : { file_url: `${host}/${key}` } as any)
              } catch (e) {
                reject(e)
              }
            } else {
              reject(new Error(typeof res.data === 'string' ? res.data : `上传失败 ${res.statusCode}`))
            }
          },
          fail: reject
        })
      })
    } catch (e) {
      return constructionPhotoApi.upload(filePath, stage) as Promise<{ file_url: string }>
    }
  },

  /** 经后端代理上传（备用） */
  upload: (filePath: string, stage: string) => {
    return new Promise((resolve, reject) => {
      const url = appendAuthQuery(`${BASE_URL}/construction-photos/upload?stage=${encodeURIComponent(stage)}`)
      Taro.uploadFile({
        url,
        filePath,
        name: 'file',
        header: getAuthHeaders(),
        success: (res) => {
          if (res.statusCode < 200 || res.statusCode >= 300) {
            try {
              const errData = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
              const msg = errData?.detail || errData?.msg || `上传失败 ${res.statusCode}`
              reject(new Error(typeof msg === 'string' ? msg : msg[0]?.msg || '上传失败'))
            } catch {
              reject(new Error(`上传失败 ${res.statusCode}`))
            }
            return
          }
          try {
            const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
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
      Taro.uploadFile({
        url: appendAuthQuery(`${BASE_URL}/acceptance/upload-photo`),
        filePath,
        name: 'file',
        header: getAuthHeaders(),
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
      const baseUrl = `${BASE_URL}/reports/export-pdf?report_type=${reportType}&resource_id=${resourceId}`
      Taro.downloadFile({
        url: appendAuthQuery(baseUrl),
        header: getAuthHeaders(),
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

/**
 * API服务层 - 封装所有后端API请求
 */
import Taro from '@tarojs/taro'
import axios, { AxiosInstance, AxiosResponse } from 'axios'
import mpAdapter from 'axios-miniprogram-adapter'
import store from '../store'
import { setNetworkError } from '../store/slices/networkSlice'
import { logout } from '../store/slices/userSlice'
import { env } from '../config/env'

// API 基础配置：统一从 env 读取
const BASE_URL = env.apiBaseUrl

/** 统一获取 token：兼容 key 为 token 或 access_token */
const getStoredToken = (): string => {
  return (Taro.getStorageSync('token') as string) || (Taro.getStorageSync('access_token') as string) || ''
}

/** 登录成功后调用，写入 storage 并设置到 axios 实例，确保后续请求立即带鉴权 */
export function setAuthToken(token: string, userId: string | number) {
  Taro.setStorageSync('token', token)
  Taro.setStorageSync('access_token', token)
  Taro.setStorageSync('user_id', userId)
  Taro.setStorageSync('login_fresh_at', Date.now())
  _setInstanceAuth(token, userId)
}

/** 登出或 401 时调用，清除 storage 与实例上的鉴权 */
export function clearAuthToken() {
  Taro.removeStorageSync('token')
  Taro.removeStorageSync('access_token')
  Taro.removeStorageSync('user_id')
  _setInstanceAuth(null, null)
}

function _setInstanceAuth(token: string | null, userId: string | number | null) {
  if (typeof instance === 'undefined') return
  const h = (instance as any).defaults?.headers
  if (!h) return
  h.common = h.common || {}
  if (token) {
    h.common['Authorization'] = `Bearer ${token}`
    h.common['X-User-Id'] = userId != null ? String(userId) : ''
  } else {
    delete h.common['Authorization']
    delete h.common['X-User-Id']
  }
}

/** Taro.uploadFile 等非 axios 请求需手动带上的鉴权 header（微信小程序可能不传 header，URL query 为备用） */
export const getAuthHeaders = (): Record<string, string> => {
  const h: Record<string, string> = { 'Content-Type': 'application/json' }
  const token = getStoredToken()
  const userId = Taro.getStorageSync('user_id')
  if (token) h['Authorization'] = `Bearer ${token}`
  if (userId != null && userId !== '' && String(userId).trim() !== '') {
    h['X-User-Id'] = String(userId).trim()
  }
  return h
}

/** Taro.request 返回后若 401 则清除 token、跳转登录（与 axios 响应拦截器一致） */
function handleTaro401() {
  clearAuthToken()
  try { store.dispatch(logout()) } catch (_) {}
  const hasOnboarded = Taro.getStorageSync('onboarding_completed') || Taro.getStorageSync('has_onboarded')
  if (hasOnboarded) {
    Taro.reLaunch({ url: '/pages/index/index' })
    setTimeout(() => {
      Taro.showModal({
        title: '登录已过期',
        content: '您的登录已过期或需要重新验证，请重新登录后继续使用',
        showCancel: true,
        cancelText: '知道了',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) Taro.switchTab({ url: '/pages/profile/index' })
        }
      })
    }, 500)
  } else {
    Taro.reLaunch({ url: '/pages/onboarding/index' })
  }
}

/** 小程序下 axios 可能不传 header，用 Taro.request 发 GET 并带鉴权，供报告/数据管理/施工照片等页使用 */
export function getWithAuth(path: string, params?: Record<string, string | number | undefined>): Promise<any> {
  let url = path.startsWith('http') ? path : `${BASE_URL}${path}`
  if (params && Object.keys(params).length > 0) {
    const qs = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== '') qs.set(k, String(v)) })
    const str = qs.toString()
    if (str) url += (url.includes('?') ? '&' : '?') + str
  }
  return Taro.request({
    url,
    method: 'GET',
    header: getAuthHeaders()
  }).then((r) => {
    if (r.statusCode === 401) {
      handleTaro401()
      return Promise.reject(new Error('未授权'))
    }
    if (r.statusCode >= 400) {
      const err = new Error((r.data as any)?.detail || (r.data as any)?.msg || `请求失败 ${r.statusCode}`) as any
      err.statusCode = r.statusCode
      err.response = { status: r.statusCode }
      return Promise.reject(err)
    }
    return (r.data as any)?.data ?? r.data
  })
}

/** POST 带鉴权（小程序下避免 axios 不传 header 导致 401） */
export function postWithAuth(path: string, data?: Record<string, any>): Promise<any> {
  const url = path.startsWith('http') ? path : `${BASE_URL}${path}`
  return Taro.request({
    url,
    method: 'POST',
    header: getAuthHeaders(),
    data: data ?? {}
  }).then((r) => {
    if (r.statusCode === 401) {
      handleTaro401()
      return Promise.reject(new Error('未授权'))
    }
    if (r.statusCode >= 400) {
      const err = new Error((r.data as any)?.detail || (r.data as any)?.msg || `请求失败 ${r.statusCode}`) as any
      err.statusCode = r.statusCode
      err.response = { status: r.statusCode, data: r.data }
      // 对于 403 等业务错误，返回原始响应数据以便前端处理
      if (r.statusCode === 403 && r.data && typeof r.data === 'object') {
        return r.data
      }
      return Promise.reject(err)
    }
    return (r.data as any)?.data ?? r.data
  })
}

/** PUT 带鉴权 */
export function putWithAuth(path: string, data?: Record<string, any>): Promise<any> {
  const url = path.startsWith('http') ? path : `${BASE_URL}${path}`
  return Taro.request({
    url,
    method: 'PUT',
    header: getAuthHeaders(),
    data: data ?? {}
  }).then((r) => {
    if (r.statusCode === 401) {
      handleTaro401()
      return Promise.reject(new Error('未授权'))
    }
    if (r.statusCode >= 400) {
      const err = new Error((r.data as any)?.detail || (r.data as any)?.msg || `请求失败 ${r.statusCode}`) as any
      err.statusCode = r.statusCode
      err.response = { status: r.statusCode }
      return Promise.reject(err)
    }
    return (r.data as any)?.data ?? r.data
  })
}

/** DELETE 带鉴权 */
export function deleteWithAuth(path: string): Promise<any> {
  const url = path.startsWith('http') ? path : `${BASE_URL}${path}`
  return Taro.request({
    url,
    method: 'DELETE',
    header: getAuthHeaders()
  }).then((r) => {
    if (r.statusCode === 401) {
      handleTaro401()
      return Promise.reject(new Error('未授权'))
    }
    if (r.statusCode >= 400) {
      const err = new Error((r.data as any)?.detail || (r.data as any)?.msg || `请求失败 ${r.statusCode}`) as any
      err.statusCode = r.statusCode
      err.response = { status: r.statusCode }
      return Promise.reject(err)
    }
    return (r.data as any)?.data ?? r.data
  })
}

/** 微信小程序 uploadFile 可能不传自定义 header，将鉴权放入 URL query 作为备用 */
const appendAuthQuery = (url: string): string => {
  const token = Taro.getStorageSync('access_token')
  const userId = Taro.getStorageSync('user_id')
  return appendAuthToUrl(url, token, userId)
}

/** 使用显式 token/userId 拼鉴权 URL（避免 uploadFile 时读 storage 竞态） */
const appendAuthToUrl = (url: string, token?: string | null, userId?: string | number | null): string => {
  const params = new URLSearchParams()
  if (token) params.set('access_token', token)
  if (userId != null && userId !== '' && String(userId).trim() !== '') params.set('user_id', String(userId).trim())
  const qs = params.toString()
  return qs ? `${url}${url.includes('?') ? '&' : '?'}${qs}` : url
}

/** 使用显式 token/userId 构建鉴权 header */
const buildAuthHeaders = (token?: string | null, userId?: string | number | null): Record<string, string> => {
  const h: Record<string, string> = {}
  if (token) h['Authorization'] = `Bearer ${token}`
  if (userId != null && userId !== '' && String(userId).trim() !== '') h['X-User-Id'] = String(userId).trim()
  return h
}

// 微信小程序无 xhr/fetch，需使用适配器
const axiosConfig: Parameters<typeof axios.create>[0] = {
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
}
if (process.env.TARO_ENV === 'weapp') {
  axiosConfig.adapter = mpAdapter as any
}
// V2.6.2修复：确保headers始终是对象（微信小程序要求）
if (!axiosConfig.headers || typeof axiosConfig.headers !== 'object') {
  axiosConfig.headers = { 'Content-Type': 'application/json' }
}
const instance: AxiosInstance = axios.create(axiosConfig)

// 请求拦截器 - 紧急修复：确保拦截器被正确注册和执行
console.log('[API初始化] 开始注册请求拦截器')
instance.interceptors.request.use(
  (config) => {
    console.log('[请求拦截器] 被调用', config.url, 'method:', config.method)
    
    // P0紧急修复：确保headers始终是对象（微信小程序要求）
    // 必须确保headers是普通对象，不能是undefined/null/其他类型
    if (!config.headers || typeof config.headers !== 'object' || Array.isArray(config.headers)) {
      console.log('[请求拦截器] headers不是对象，重新创建', typeof config.headers)
      config.headers = {}
    }
    // 确保headers是普通对象（不是类实例，如AxiosHeaders）
    // 使用 Object.getOwnPropertyNames 和 Object.getOwnPropertyDescriptor 来安全地转换
    if (config.headers && (config.headers.constructor !== Object || config.headers.constructor.name === 'AxiosHeaders')) {
      console.log('[请求拦截器] headers不是普通对象，转换', config.headers.constructor?.name || 'unknown')
      const headersObj: Record<string, string> = {}
      // 使用 Object.keys 和 Object.getOwnPropertyDescriptor 安全地复制所有属性
      const keys = Object.keys(config.headers)
      for (const key of keys) {
        const value = (config.headers as any)[key]
        if (value != null) {
          headersObj[key] = String(value)
        }
      }
      config.headers = headersObj
    }
    // 确保Content-Type存在
    if (!config.headers['Content-Type'] && !config.headers['content-type']) {
      config.headers['Content-Type'] = 'application/json'
    }

    // 统一从 storage 获取 token（兼容 key：token / access_token）
    const token = getStoredToken()
    const userId = Taro.getStorageSync('user_id')
    
    // 强制输出调试日志（无论环境）
    console.log('[请求拦截器]', config.url, 'token:', token ? `存在(${token.substring(0, 20)}...)` : '不存在', 'userId:', userId || '无')
    
    // 添加token（关键修复：确保总是添加）
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('[请求拦截器] 已添加Authorization header')
    } else {
      // token不存在时，清除可能存在的旧token
      delete config.headers.Authorization
      console.warn('[请求拦截器] ⚠️ token不存在，无法添加Authorization header')
    }

    // 添加用户ID
    if (userId != null && userId !== '' && String(userId).trim() !== '') {
      config.headers['X-User-Id'] = String(userId).trim()
      console.log('[请求拦截器] 已添加X-User-Id header:', userId)
    } else {
      delete config.headers['X-User-Id']
    }

    // P0紧急修复：最终检查，确保headers是普通对象且包含必要字段
    if (!config.headers || typeof config.headers !== 'object' || Array.isArray(config.headers) || config.headers.constructor !== Object) {
      console.error('[请求拦截器] ⚠️ headers仍然不是普通对象，强制重建')
      const safeHeaders: Record<string, string> = {
        'Content-Type': config.headers?.['Content-Type'] || config.headers?.['content-type'] || 'application/json'
      }
      if (token) safeHeaders.Authorization = `Bearer ${token}`
      if (userId != null && userId !== '' && String(userId).trim() !== '') {
        safeHeaders['X-User-Id'] = String(userId).trim()
      }
      config.headers = safeHeaders
    } else {
      // 即使headers是对象，也要确保token被正确设置
      if (token && !config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${token}`
        console.log('[请求拦截器] 补充添加Authorization header')
      }
      if (userId != null && userId !== '' && String(userId).trim() !== '' && !config.headers['X-User-Id']) {
        config.headers['X-User-Id'] = String(userId).trim()
      }
    }

    // 最终验证：确保headers是普通对象
    if (!config.headers || typeof config.headers !== 'object' || Array.isArray(config.headers)) {
      config.headers = {}
    }
    if (config.headers.constructor !== Object) {
      const finalHeaders: Record<string, string> = {}
      for (const key in config.headers) {
        if (config.headers.hasOwnProperty(key)) {
          finalHeaders[key] = String(config.headers[key])
        }
      }
      config.headers = finalHeaders
    }

    // 调试日志：验证headers（开发环境）
    if (process.env.NODE_ENV === 'development' && config.headers.Authorization) {
      console.log('[请求拦截器] 已添加Authorization header')
    }

    return config
  },
  (error) => {
    console.error('[请求拦截器错误]', error)
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
        case 401: {
          message = '登录已过期，请重新登录'
          const config = error.config as any
          const skip401Handler = config?.skip401Handler === true
          const url = config?.url || ''
          
          // 检查是否为获取用户信息的API（/users/profile）
          const isProfileApi = url.includes('/users/profile')
          
          // 若刚登录成功不久（30秒内），可能是页面预加载或竞态，暂不清除避免误杀
          const freshAt = Taro.getStorageSync('login_fresh_at') as number | string
          const now = Date.now()
          const recentlyLoggedIn = freshAt && (now - Number(freshAt)) < 30000
          
          // V2.6.8优化：对于获取用户信息的API，如果用户未登录，静默处理不显示错误
          if (skip401Handler || recentlyLoggedIn || isProfileApi) {
            if (recentlyLoggedIn) Taro.removeStorageSync('login_fresh_at')
            // 静默处理，不显示错误信息
            const silentError = new Error('请稍后重试')
            ;(silentError as any).isSilent = true
            ;(silentError as any).isProfileApi = isProfileApi
            return Promise.reject(silentError)
          }
          
          // 清除 token 与实例鉴权，后端可能因过期或 SECRET_KEY 变更而拒绝
          clearAuthToken()
          try { store.dispatch(logout()) } catch (_) {}
          
          const hasOnboarded = Taro.getStorageSync('onboarding_completed') || Taro.getStorageSync('has_onboarded')
          if (hasOnboarded) {
            Taro.reLaunch({ url: '/pages/index/index' })
            setTimeout(() => {
              Taro.showModal({
                title: '登录已过期',
                content: '您的登录已过期或需要重新验证，请重新登录后继续使用',
                showCancel: true,
                cancelText: '知道了',
                confirmText: '去登录',
                success: (res) => {
                  if (res.confirm) Taro.switchTab({ url: '/pages/profile/index' })
                }
              })
            }, 500)
          } else {
            Taro.reLaunch({ url: '/pages/onboarding/index' })
          }
          break
        }
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
  // 获取进度计划（后台拉取，401 时仅静默失败不弹「登录已过期」）
  getSchedule: () => {
    return instance.get('/constructions/schedule', { skip401Handler: true } as any)
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
 * 材料进场核对相关API（已废弃，请使用 constructionApi.updateStageStatus）
 * @deprecated 使用 constructionApi.updateStageStatus('S00', 'checked') 替代
 */
export const materialsApi = {
  /** 材料进场核对通过（已废弃，请使用 constructionApi.updateStageStatus('S00', 'checked')） */
  verify: () => {
    console.warn('materialsApi.verify 已废弃，请使用 constructionApi.updateStageStatus')
    return instance.put('/constructions/stage-status', { stage: 'S00', status: 'checked' })
  },
}

/**
 * 材料进场人工核对 P37（FR-019~FR-023，支持留证）
 */
export const materialChecksApi = {
  /** 使用 getWithAuth 避免微信小程序 axios 不传 header 导致 401 */
  getMaterialList: () => getWithAuth('/material-checks/material-list'),
  /** 提交核对结果，pass 需 items 每项至少1张照片，fail 需 problem_note≥10字 */
  submit: (data: { items: Array<{ material_name: string; spec_brand?: string; quantity?: string; photo_urls: string[] }>; result: 'pass' | 'fail'; problem_note?: string }) => {
    // 使用 postWithAuth 避免微信小程序 axios 不传 header 导致 401（与 getMaterialList 一致）
    const token = getStoredToken()
    if (!token) {
      return Promise.reject(new Error('登录已失效，请重新登录'))
    }
    return postWithAuth('/material-checks/submit', data)
  },
}

/**
 * 材料库API（V2.6.2优化：材料库建设）
 */
export const materialLibraryApi = {
  /** 搜索材料库 */
  search: (keyword: string, category?: string, cityCode?: string) => 
    instance.get('/material-library/search', { params: { keyword, category, city_code: cityCode } }),
  /** 获取常用材料列表 */
  getCommon: (category?: string) => 
    instance.get('/material-library/common', { params: { category } }),
  /** 智能匹配材料（从报价单材料名称匹配材料库） */
  match: (materialNames: string[], cityCode?: string) => 
    instance.post('/material-library/match', { material_names: materialNames, city_code: cityCode }),
}

/**
 * 订单支付相关API - 修复：确保每个请求都带上认证信息
 */
export const paymentApi = {
  // 创建订单（报告解锁：resource_type=company|quote|contract|acceptance, resource_id=scanId；会员：order_type=member_month|member_season|member_year，无需 resource）
  createOrder: (data: {
    order_type: string
    resource_type?: string
    resource_id?: number
  }) => {
    // 确保token存在，如果不存在则抛出明确错误
    const token = getStoredToken()
    if (!token) {
      return Promise.reject(new Error('请先登录'))
    }
    return postWithAuth('/payments/create', data)
  },

  // 发起支付（获取微信支付参数，生产环境调起 wx.requestPayment）
  pay: (orderId: number) => {
    const token = getStoredToken()
    if (!token) {
      return Promise.reject(new Error('请先登录'))
    }
    return postWithAuth('/payments/pay', { order_id: orderId })
  },

  // 确认支付成功（开发/联调：模拟支付成功；生产应由微信回调处理）
  confirmPaid: (orderId: number) => {
    const token = getStoredToken()
    if (!token) {
      return Promise.reject(new Error('请先登录'))
    }
    return postWithAuth('/payments/confirm-paid', { order_id: orderId })
  },

  getOrders: (params?: { page?: number; page_size?: number }) => {
    const token = getStoredToken()
    if (!token) return Promise.reject(new Error('请先登录'))
    return getWithAuth('/payments/orders', params as Record<string, string | number | undefined>)
  },

  getOrder: (orderId: number) => {
    const token = getStoredToken()
    if (!token) {
      return Promise.reject(new Error('请先登录'))
    }
    return getWithAuth(`/payments/order/${orderId}`)
  }
}

/**
 * 消息中心 API
 */
export const messageApi = {
  getList: (params?: { category?: string; page?: number; page_size?: number }) => {
    return getWithAuth('/messages', params as any)
  },
  getUnreadCount: () => getWithAuth('/messages/unread-count'),
  markRead: (msgId: number) => putWithAuth(`/messages/${msgId}/read`, {}),
  markAllRead: () => putWithAuth('/messages/read-all', {}),
  delete: (msgId: number) => deleteWithAuth(`/messages/${msgId}`)
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

  /** 经后端代理上传（微信小程序 uploadFile 带 Token 走此路径；URL + formData 双通道鉴权） */
  upload: (filePath: string, stage: string) => {
    return new Promise((resolve, reject) => {
      const base = (BASE_URL || '').replace(/\/$/, '')
      const url = appendAuthQuery(`${base}/construction-photos/upload?stage=${encodeURIComponent(stage)}`)
      const token = Taro.getStorageSync('access_token')
      const userId = Taro.getStorageSync('user_id')
      const formData: Record<string, string> = {}
      if (token) formData['access_token'] = token
      if (userId != null && String(userId).trim() !== '') formData['user_id'] = String(userId).trim()
      Taro.uploadFile({
        url,
        filePath,
        name: 'file',
        formData,
        header: getAuthHeaders(),
        success: (res) => {
          if (res.statusCode < 200 || res.statusCode >= 300) {
            let msg = `上传失败 ${res.statusCode}`
            try {
              const errData = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
              const d = errData?.detail ?? errData?.msg
              if (typeof d === 'string' && d) msg = d
              else if (Array.isArray(d) && d[0]?.msg) msg = d[0].msg
              if (res.statusCode === 401) msg = '请先登录'
            } catch { /* keep default msg */ }
            reject(new Error(msg))
            return
          }
          try {
            const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
            const out = data?.data ?? data
            resolve(out?.file_url ? out : { file_url: out })
          } catch {
            reject(new Error('解析失败'))
          }
        },
        fail: (err) => reject(err instanceof Error ? err : new Error(err?.errMsg || '网络请求失败'))
      })
    })
  },
  getList: (stage?: string) => {
    // V2.6.2修复：确保headers正确设置
    const params = stage ? { stage } : {}
    // 不设置headers，让拦截器自动添加认证信息
    return instance.get('/construction-photos', { params })
  },
  delete: (photoId: number) => deleteWithAuth(`/construction-photos/${photoId}`),
  move: (photoId: number, stage: string) => instance.put(`/construction-photos/${photoId}/move`, { stage })
}

/**
 * 验收分析 API
 * uploadPhoto 支持传入 auth，微信小程序 uploadFile 可能不传 header，URL query 为唯一可靠方式
 */
export const acceptanceApi = {
  uploadPhoto: (filePath: string, auth?: { token: string; userId?: string | number }) => {
    const token = auth?.token ?? getStoredToken()
    const userId = auth?.userId ?? Taro.getStorageSync('user_id')
    const url = appendAuthToUrl(`${BASE_URL}/acceptance/upload-photo`, token, userId)
    const headers = auth ? buildAuthHeaders(token, userId) : getAuthHeaders()
    // 微信 uploadFile 可能不传 header/query，formData 最可靠
    const formData: Record<string, string> = {}
    if (token) formData['access_token'] = token
    if (userId != null && userId !== '' && String(userId).trim() !== '') formData['user_id'] = String(userId).trim()
    return new Promise((resolve, reject) => {
      Taro.uploadFile({
        url,
        filePath,
        name: 'file',
        formData,
        header: headers,
        success: (res) => {
          if (res.statusCode < 200 || res.statusCode >= 300) {
            try {
              const errData = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
              const d = errData?.detail ?? errData?.msg
              const msg = typeof d === 'string' ? d : (Array.isArray(d) && d[0]?.msg ? d[0].msg : `上传失败 ${res.statusCode}`)
              reject(new Error(res.statusCode === 401 ? '请先登录' : msg))
            } catch {
              reject(new Error(`上传失败 ${res.statusCode}`))
            }
            return
          }
          try {
            const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
            const out = data?.data ?? data
            // 返回完整 out（含 object_key、file_url），供 analyze 使用 object_key 避免 URL 过期
            resolve(out && (out.file_url || out.object_key) ? out : {})
          } catch { reject(new Error('解析失败')) }
        },
        fail: (err) => reject(err instanceof Error ? err : new Error(err?.errMsg || '网络请求失败'))
      })
    })
  },
  analyze: (stage: string, fileUrls: string[]) =>
    postWithAuth('/acceptance/analyze', { stage, file_urls: fileUrls }),
  getResult: (analysisId: number) => getWithAuth(`/acceptance/${analysisId}`),
  getList: (params?: { stage?: string; page?: number; page_size?: number }) => {
    const p = params || {}
    const query: Record<string, string | number | undefined> = {}
    if (p.stage != null) query.stage = p.stage
    if (p.page != null) query.page = p.page
    if (p.page_size != null) query.page_size = p.page_size
    return getWithAuth('/acceptance', query)
  },
  requestRecheck: (analysisId: number, rectifiedPhotoUrls: string[]) =>
    postWithAuth(`/acceptance/${analysisId}/request-recheck`, { rectified_photo_urls: rectifiedPhotoUrls }),
  markPassed: (analysisId: number, confirmPhotoUrls: string[], confirmNote: string) =>
    postWithAuth(`/acceptance/${analysisId}/mark-passed`, { confirm_photo_urls: confirmPhotoUrls, confirm_note: confirmNote })
}

/**
 * AI监理咨询 API (P36)
 */
export const consultationApi = {
  createSession: (params: { acceptance_analysis_id?: number; stage?: string }) =>
    postWithAuth('/consultation/session', params),
  sendMessage: (sessionId: number, content: string, images?: string[]) =>
    postWithAuth('/consultation/message', { session_id: sessionId, content: content || undefined, images: images?.length ? images : undefined })
}

/**
 * 报告导出 API
 */
export const pointsApi = {
  /** 分享奖励积分 */
  shareReward: (shareType: string, resourceType?: string, resourceId?: number) =>
    postWithAuth('/points/share-reward', {
      share_type: shareType,
      resource_type: resourceType,
      resource_id: resourceId
    }),
  /** 获取积分记录 */
  getRecords: (page: number = 1, pageSize: number = 20) =>
    getWithAuth('/points/records', { page, page_size: pageSize }),
  /** 获取积分汇总 */
  getSummary: () => getWithAuth('/points/summary')
}

export const reportApi = {
  getExportPdfUrl: (reportType: string, resourceId: number) =>
    `${BASE_URL}/reports/export-pdf?report_type=${reportType}&resource_id=${resourceId}`,
  downloadPdf: (reportType: string, resourceId: number, filename?: string) => {
    return new Promise((resolve, reject) => {
      const baseUrl = `${BASE_URL}/reports/export-pdf?report_type=${reportType}&resource_id=${resourceId}`
      // 鉴权放URL：小程序downloadFile部分环境不传自定义header，必须用query
      const url = appendAuthQuery(baseUrl)
      Taro.downloadFile({
        url,
        header: getAuthHeaders(),
        success: (res) => {
          if (res.statusCode === 200) {
            const filePath = res.tempFilePath
            Taro.openDocument({ filePath, fileType: 'pdf' })
              .then(() => resolve(filePath))
              .catch((e) => {
                Taro.saveFile({ tempFilePath: filePath }).then((s) => resolve(s.savedFilePath)).catch(() => resolve(filePath))
              })
          } else if (res.statusCode === 403) {
            reject(new Error('请先解锁报告'))
          } else if (res.statusCode === 401) {
            reject(new Error('请先登录'))
          } else if (res.statusCode === 404) {
            reject(new Error('报告不存在'))
          } else {
            reject(new Error(`导出失败(${res.statusCode})`))
          }
        },
        fail: (err) => reject(err?.errMsg ? new Error(err.errMsg) : err)
      })
    })
  }
}

/**
 * 邀请系统 API（V2.6.8新增）
 */
export const invitationsApi = {
  /** 创建邀请 */
  createInvitation: (data?: { invitee_phone?: string; invitee_nickname?: string }) =>
    postWithAuth('/invitations/create', data || {}),

  /** 检查邀请状态 */
  checkInvitationStatus: () =>
    getWithAuth('/invitations/status'),

  /** 获取免费解锁权益列表 */
  getFreeUnlockEntitlements: () =>
    getWithAuth('/invitations/entitlements'),

  /** 使用免费解锁权益 */
  useFreeUnlock: (reportType: string, reportId: number) =>
    postWithAuth('/invitations/use-free-unlock', { report_type: reportType, report_id: reportId }),

  /** 检查邀请码（新用户注册时调用） */
  checkInvitationCode: (invitationCode: string) =>
    postWithAuth('/invitations/check-invitation-code?invitation_code=' + encodeURIComponent(invitationCode), {})
}

/**
 * AI设计师 API（新增：首页悬浮头像功能）
 */
export const designerApi = {
  /** AI设计师咨询（单次，向后兼容） */
  consult: (question: string, context?: string) =>
    postWithAuth('/designer/consult', { question, context }),

  /** AI设计师服务健康检查 */
  healthCheck: () =>
    getWithAuth('/designer/health'),

  /** 创建新的聊天session（支持多轮对话） */
  createChatSession: (initialQuestion?: string) =>
    postWithAuth('/designer/sessions', { initial_question: initialQuestion }),

  /** 发送消息到聊天session（支持图片URL） */
  sendChatMessage: (sessionId: string, message: string, imageUrls?: string[]) =>
    postWithAuth('/designer/chat', { session_id: sessionId, message, image_urls: imageUrls }),

  /** 上传户型图到AI设计师 */
  uploadImage: (filePath: string, fileName: string) => {
    return new Promise((resolve, reject) => {
      // 获取认证信息
      const token = getStoredToken()
      const userId = Taro.getStorageSync('user_id')
      
      // 构建URL和header
      const url = appendAuthToUrl(`${BASE_URL}/designer/upload-image`, token, userId)
      const headers = buildAuthHeaders(token, userId)
      
      // 微信小程序uploadFile可能不传header，使用formData作为备用
      const formData: Record<string, string> = {}
      if (token) formData['access_token'] = token
      if (userId != null && userId !== '' && String(userId).trim() !== '') {
        formData['user_id'] = String(userId).trim()
      }
      
      Taro.uploadFile({
        url,
        filePath,
        name: 'file',
        formData,
        header: headers,
        success: (res) => {
          if (res.statusCode < 200 || res.statusCode >= 300) {
            let msg = `上传失败 ${res.statusCode}`
            try {
              const errData = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
              const d = errData?.detail ?? errData?.msg
              if (typeof d === 'string' && d) msg = d
              else if (Array.isArray(d) && d[0]?.msg) msg = d[0].msg
              if (res.statusCode === 401) msg = '请先登录'
            } catch { /* keep default msg */ }
            reject(new Error(msg))
            return
          }
          try {
            const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
            const out = data?.data ?? data
            resolve(out?.image_url ? out : { image_url: out })
          } catch {
            reject(new Error('解析失败'))
          }
        },
        fail: (err) => reject(err instanceof Error ? err : new Error(err?.errMsg || '网络请求失败'))
      })
    })
  },

  /** 获取聊天session详情 */
  getChatSession: (sessionId: string) =>
    getWithAuth(`/designer/sessions/${sessionId}`),

  /** 获取用户的所有聊天session */
  listChatSessions: () =>
    getWithAuth('/designer/sessions'),

  /** 清空聊天session的历史记录 */
  clearChatHistory: (sessionId: string) =>
    postWithAuth('/designer/clear', { session_id: sessionId }),

  /** 删除聊天session */
  deleteChatSession: (sessionId: string) =>
    deleteWithAuth(`/designer/sessions/${sessionId}`)
}

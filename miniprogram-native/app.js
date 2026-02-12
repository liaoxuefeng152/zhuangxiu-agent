/**
 * 装修决策Agent - 全局逻辑
 * 网络请求封装、权限校验、全局状态管理、异常兜底
 *
 * 微信开发者工具本地调试：
 * - 保持 API_BASE 为 http://localhost:8000/api/v1，并确保本机已启动后端（如 docker-compose -f docker-compose.dev.yml up -d）
 * - 在开发者工具中勾选「不校验合法域名、web-view（调试用）」
 * - 不需要改项目根目录的 .env（后端用 Docker 开发时 compose 会覆盖环境变量）
 */

// API 配置：本地调试用 localhost；真机/体验版改为你的后端域名
const API_BASE = 'http://localhost:8000/api/v1'

// 6大阶段核心配置（流程互锁用）
const STAGES = {
  S00: { name: '材料进场核对', cycle: 3, prev: null },
  S01: { name: '隐蔽工程', cycle: 7, prev: 'S00' },
  S02: { name: '泥瓦工', cycle: 10, prev: 'S01' },
  S03: { name: '木工', cycle: 7, prev: 'S02' },
  S04: { name: '油漆', cycle: 7, prev: 'S03' },
  S05: { name: '安装收尾', cycle: 5, prev: 'S04' }
}

App({
  globalData: {
    userInfo: null,
    userId: null,
    token: null,
    startDate: null,
    stageStatus: {},
    remindDays: 3,
    remindEnabled: true,
    hasMessageUnread: false,
    stageRedDots: {}
  },

  onLaunch() {
    this._initStorage()
    // 无 token 时尝试静默登录（开发/体验版用模拟 code，正式版用 wx.login）
    if (!this.globalData.token) this._trySilentLogin()
    this._checkNetwork()
    this._checkOnboarding()
  },

  _checkOnboarding() {
    if (!wx.getStorageSync('onboarding_completed')) {
      wx.redirectTo({ url: '/pages/p01_onboarding/p01_onboarding' })
    }
  },

  onShow() {
    // 从本地恢复全局状态
    const startDate = wx.getStorageSync('construction_start_date')
    const stageStatus = wx.getStorageSync('stage_status') || {}
    const remindDays = wx.getStorageSync('remind_days') || 3
    const remindEnabled = wx.getStorageSync('remind_enabled') !== false

    this.globalData.startDate = startDate || null
    this.globalData.stageStatus = stageStatus
    this.globalData.remindDays = remindDays
    this.globalData.remindEnabled = remindEnabled
  },

  _initStorage() {
    const token = wx.getStorageSync('access_token')
    const userId = wx.getStorageSync('user_id')
    const userInfo = wx.getStorageSync('user_info')

    if (token) this.globalData.token = token
    if (userId) this.globalData.userId = userId
    if (userInfo) this.globalData.userInfo = userInfo
  },

  /**
   * 静默登录：开发/体验版用 dev_weapp_mock 模拟用户，正式版用 wx.login 的 code
   * 便于在微信开发者工具里模拟真实用户测试
   */
  _trySilentLogin() {
    const envVersion = (wx.getAccountInfoSync && wx.getAccountInfoSync().miniProgram) ? wx.getAccountInfoSync().miniProgram.envVersion : 'release'
    const isDev = envVersion === 'develop' || envVersion === 'trial'

    if (isDev) {
      // 开发者工具 / 体验版：后端 DEBUG 时接受 dev_weapp_mock，直接拿模拟 token
      wx.request({
        url: API_BASE + '/users/login',
        method: 'POST',
        header: { 'Content-Type': 'application/json' },
        data: { code: 'dev_weapp_mock' },
        success: (res) => {
          if (res.statusCode === 200 && res.data && (res.data.access_token || res.data.data && res.data.data.access_token)) {
            const d = res.data.data || res.data
            const token = d.access_token
            const userId = d.user_id
            const userInfo = { nickname: d.nickname, avatar_url: d.avatar_url, is_member: d.is_member }
            wx.setStorageSync('access_token', token)
            wx.setStorageSync('user_id', userId)
            wx.setStorageSync('user_info', userInfo)
            this.globalData.token = token
            this.globalData.userId = userId
            this.globalData.userInfo = userInfo
          }
        }
      })
      return
    }

    // 正式版：用微信 code 换 token
    wx.login({
      success: (loginRes) => {
        if (!loginRes.code) return
        wx.request({
          url: API_BASE + '/users/login',
          method: 'POST',
          header: { 'Content-Type': 'application/json' },
          data: { code: loginRes.code },
          success: (res) => {
            if (res.statusCode === 200 && res.data && (res.data.access_token || res.data.data && res.data.data.access_token)) {
              const d = res.data.data || res.data
              wx.setStorageSync('access_token', d.access_token)
              wx.setStorageSync('user_id', d.user_id)
              wx.setStorageSync('user_info', { nickname: d.nickname, avatar_url: d.avatar_url, is_member: d.is_member })
              this.globalData.token = d.access_token
              this.globalData.userId = d.user_id
              this.globalData.userInfo = { nickname: d.nickname, avatar_url: d.avatar_url, is_member: d.is_member }
            }
          }
        })
      }
    })
  },

  _checkNetwork() {
    wx.getNetworkType({
      success: (res) => {
        if (res.networkType === 'none') {
          wx.redirectTo({ url: '/pages/p33_network_error/p33_network_error' })
        }
      }
    })
  },

  /**
   * 网络请求封装
   * @param {Object} opts - 同 wx.request，额外支持 url 相对路径
   */
  request(opts) {
    const url = opts.url.startsWith('http') ? opts.url : `${API_BASE}${opts.url.startsWith('/') ? '' : '/'}${opts.url}`
    const header = {
      'Content-Type': 'application/json',
      ...opts.header
    }
    const token = this.globalData.token || wx.getStorageSync('access_token')
    if (token) header['Authorization'] = `Bearer ${token}`

    const userId = this.globalData.userId || wx.getStorageSync('user_id')
    if (userId) header['X-User-Id'] = String(userId)

    return new Promise((resolve, reject) => {
      wx.request({
        ...opts,
        url,
        header,
        success: (res) => {
          const { statusCode, data } = res
          if (statusCode >= 200 && statusCode < 300) {
            const code = data?.code
            const msg = data?.msg
            const body = data?.data

            if (code === 0 || code === undefined) {
              resolve(body !== undefined ? body : data)
              return
            }
            if (code === 403) {
              wx.showToast({ title: msg || '权限不足', icon: 'none' })
              reject(new Error('403'))
              return
            }
            if (code === 409) {
              wx.showToast({ title: msg || '流程互锁，请先完成前置阶段', icon: 'none' })
              reject(new Error('409'))
              return
            }
            wx.showToast({ title: msg || '请求失败', icon: 'none' })
            reject(new Error(msg || '请求失败'))
            return
          }

          if (statusCode === 401) {
            wx.removeStorageSync('access_token')
            wx.removeStorageSync('user_id')
            this.globalData.token = null
            this.globalData.userId = null
            wx.showToast({ title: '登录已过期', icon: 'none' })
          }

          if (statusCode >= 500 || statusCode === 0) {
            wx.redirectTo({
              url: '/pages/p33_network_error/p33_network_error?from=' + encodeURIComponent(getCurrentPages().pop()?.route || '')
            })
          }
          reject(new Error(data?.msg || `HTTP ${statusCode}`))
        },
        fail: (err) => {
          wx.redirectTo({
            url: '/pages/p33_network_error/p33_network_error?from=' + encodeURIComponent(getCurrentPages().pop()?.route || '')
          })
          reject(err)
        }
      })
    })
  },

  /**
   * 权限校验：是否有前置阶段通过
   */
  canAccessStage(stageId) {
    const stage = STAGES[stageId]
    if (!stage || !stage.prev) return true
    const prevStatus = this.globalData.stageStatus[stage.prev]
    const passed = prevStatus === '已核对' || prevStatus === '已通过'
    return !!passed
  },

  /**
   * 获取阶段状态
   */
  getStageStatus(stageId) {
    return this.globalData.stageStatus[stageId] || (stageId === 'S00' ? '待人工核对' : '待验收')
  },

  /**
   * 设置阶段状态并持久化
   */
  setStageStatus(stageId, status) {
    this.globalData.stageStatus[stageId] = status
    wx.setStorageSync('stage_status', this.globalData.stageStatus)
  },

  /**
   * 消除阶段红点
   */
  clearStageRedDot(stageId) {
    const dots = wx.getStorageSync('stage_red_dots') || this.globalData.stageRedDots || {}
    delete dots[stageId]
    this.globalData.stageRedDots = dots
    this.globalData.hasMessageUnread = Object.keys(dots).length > 0
    wx.setStorageSync('stage_red_dots', dots)
    wx.setStorageSync('has_message_unread', Object.keys(dots).length > 0)
  },

  /**
   * Toast 防重复（3秒内不重复）
   */
  _lastToast = 0
  toast(title, icon = 'none') {
    const now = Date.now()
    if (now - this._lastToast < 3000) return
    this._lastToast = now
    wx.showToast({ title, icon, duration: 3000 })
  }
})

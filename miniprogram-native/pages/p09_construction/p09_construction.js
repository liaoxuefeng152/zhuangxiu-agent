const { STAGES, STAGE_NAMES } = require('../../utils/config')
const app = getApp()
const DEFAULT_S00_STATUS = '待人工核对'
const DEFAULT_STAGE_STATUS = '待验收'

function formatDate(d) {
  if (!d) return ''
  const t = d instanceof Date ? d : new Date(d)
  return t.getFullYear() + '-' + String(t.getMonth() + 1).padStart(2, '0') + '-' + String(t.getDate()).padStart(2, '0')
}

function addDays(d, n) {
  const t = d instanceof Date ? new Date(d) : new Date(d)
  t.setDate(t.getDate() + n)
  return t
}

Page({
  data: {
    startDate: null,
    pickerDate: '',
    progressPercent: 0,
    delayTip: '',
    remindTip: '',
    stageList: [],
    remindDays: 3
  },

  onLoad(options) {
    const today = formatDate(new Date())
    this.setData({ pickerDate: today })
    const existingStatus = wx.getStorageSync('stage_status')
    if (
      !existingStatus ||
      typeof existingStatus !== 'object' ||
      Object.keys(existingStatus).length === 0
    ) {
      this._resetStageStatus()
    }
    this._loadData()
    const stage = options.stage
    if (stage) {
      wx.nextTick(() => this._scrollToStage(stage))
    }
  },

  onShow() {
    this._loadData()
  },

  _loadData() {
    const startDate = wx.getStorageSync('construction_start_date') || null
    const stageStatus = wx.getStorageSync('stage_status') || app.globalData.stageStatus || {}
    const remindDays = wx.getStorageSync('remind_days') || 3
    const dots = wx.getStorageSync('stage_red_dots') || {}
    const icons = ['📦', '🔌', '🧱', '🪵', '🎨', '🔧']

    let passedCount = 0
    const statusMap = { '已核对': 1, '已通过': 1, '待整改': 0.5, '验收中': 0.5, '核对中': 0.5 }

    const stageList = STAGES.map((s, i) => {
      const status = stageStatus[s.id] || (s.id === 'S00' ? DEFAULT_S00_STATUS : DEFAULT_STAGE_STATUS)
      const prev = s.id === 'S00' ? null : STAGES[i - 1]
      const prevStatus = prev ? stageStatus[prev.id] : null
      const passed = prevStatus === '已核对' || prevStatus === '已通过'
      const locked = s.id !== 'S00' && !passed

      if (status === '已核对' || status === '已通过') passedCount++

      let expectedStart = ''
      let expectedEnd = ''
      let planTime = ''
      if (startDate) {
        let start = new Date(startDate)
        for (let j = 0; j < i; j++) start = addDays(start, STAGES[j].cycle)
        const end = addDays(start, s.cycle)
        expectedStart = formatDate(start)
        expectedEnd = formatDate(end)
        planTime = expectedStart + '~' + formatDate(end)
      }

      let statusClass = 'pending'
      if (status === '已核对' || status === '已通过') statusClass = 'done'
      else if (status === '待整改' || status === '验收中') statusClass = 'fixing'

      const progress = statusMap[status] ? statusMap[status] * 100 : (locked ? 0 : 10)

      return {
        id: s.id,
        name: s.name,
        fullName: STAGE_NAMES[s.id] || s.name,
        icon: icons[i],
        statusText: status,
        statusClass,
        locked,
        hasRedDot: !!dots[s.id],
        expectedStart,
        expectedEnd,
        planTime,
        progress: Math.min(progress, 100),
        recordText: s.id === 'S00' ? '材料记录：' + status : '验收记录：' + status,
        recordExpanded: false
      }
    })

    const progressPercent = STAGES.length ? Math.round((passedCount / STAGES.length) * 100) : 0
    const delayTip = ''
    const remindTip = ''

    this.setData({
      startDate,
      progressPercent,
      delayTip,
      remindTip,
      stageList,
      remindDays
    })
  },

  _scrollToStage(stageId) {
    // 可后续用 scroll-into-view 实现
  },

  onDateChange(e) {
    const val = e.detail.value
    this.setData({ showDatePicker: false })
    if (!val) return
    wx.setStorageSync('construction_start_date', val)
    app.globalData.startDate = val
    this._resetStageStatus()
    this.setData({ startDate: val })
    this._loadData()
    wx.showToast({ title: '进度计划更新成功', icon: 'none' })
  },

  _resetStageStatus() {
    const stageStatus = {}
    STAGES.forEach(stage => {
      stageStatus[stage.id] = stage.id === 'S00' ? DEFAULT_S00_STATUS : DEFAULT_STAGE_STATUS
    })
    wx.setStorageSync('stage_status', stageStatus)
    app.globalData.stageStatus = stageStatus
  },

  onRemindSetting() {
    wx.navigateTo({ url: '/pages/p19_account_setting/p19_account_setting' })
  },

  onAICheck(e) {
    const id = e.currentTarget.dataset.id
    const item = this.data.stageList.find(s => s.id === id)
    if (item && item.locked && id !== 'S00') {
      wx.showToast({ title: '请先完成前置阶段', icon: 'none' })
      return
    }
    wx.navigateTo({
      url: '/pages/p30_acceptance/p30_acceptance?stage=' + id
    })
  },

  onPhoto(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: '/pages/p15_photo/p15_photo?stage=' + id
    })
  },

  onGuide(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: (id === 'S00' ? '材料核对' : '验收') + '指引',
      content: '请确保拍摄清晰、完整。具体标准详见验收/核对指引弹窗。',
      showCancel: false
    })
  },

  onUpdateStatus(e) {
    const id = e.currentTarget.dataset.id
    wx.showActionSheet({
      itemList: ['待开始', '进行中', '已完成'],
      success: (res) => {
        const statuses = ['待开始', '进行中', '已完成']
        const status = statuses[res.tapIndex]
        if (status === '已完成') {
          const item = this.data.stageList.find(s => s.id === id)
          const passStatus = id === 'S00' ? '已核对' : '已通过'
          if (item && item.statusText !== passStatus) {
            wx.showToast({ title: '请先完成AI验收/核对', icon: 'none' })
            return
          }
        }
        const stageStatus = wx.getStorageSync('stage_status') || {}
        const passStatus = id === 'S00' ? '已核对' : '已通过'
        stageStatus[id] = status === '已完成' ? passStatus : status
        wx.setStorageSync('stage_status', stageStatus)
        getApp().globalData.stageStatus = stageStatus
        this._loadData()
        wx.showToast({ title: '状态已更新', icon: 'none' })
      }
    })
  },

  onCalibrateTime(e) {
    wx.showToast({ title: '时间校准功能开发中', icon: 'none' })
  },

  onToggleRecord(e) {
    const id = e.currentTarget.dataset.id
    const list = this.data.stageList.map(s => {
      if (s.id === id) s.recordExpanded = !s.recordExpanded
      return s
    })
    this.setData({ stageList: list })
  },

  onViewDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/p30_acceptance/p30_acceptance?stage=' + id })
  },

  onMarkFix(e) {
    const id = e.currentTarget.dataset.id
    const stageStatus = wx.getStorageSync('stage_status') || {}
    stageStatus[id] = '待整改'
    wx.setStorageSync('stage_status', stageStatus)
    getApp().globalData.stageStatus = stageStatus
    this._loadData()
    wx.showToast({ title: '已标记为待整改', icon: 'none' })
  },

  onRecheck() {
    wx.showToast({ title: '请上传整改后照片申请复检', icon: 'none' })
  },

  onRecordReason() {
    wx.showToast({ title: '记录原因功能开发中', icon: 'none' })
  },

  onShare() {
    wx.navigateTo({ url: '/pages/p32_share/p32_share?type=progress' })
  }
})

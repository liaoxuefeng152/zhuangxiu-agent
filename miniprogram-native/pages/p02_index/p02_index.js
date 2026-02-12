const { STAGES, STAGE_NAMES } = require('../../utils/config')

Page({
  data: {
    banners: [
      { id: 1, title: '6大阶段介绍', bg: 'bg1' },
      { id: 2, title: '智能提醒功能', bg: 'bg2' },
      { id: 3, title: '会员权益', bg: 'bg3' }
    ],
    stages: [],
    hasMessageUnread: false
  },

  onLoad() {
    this._loadStageRedDots()
    this._buildStages()
  },

  onShow() {
    const dots = wx.getStorageSync('stage_red_dots') || {}
    const hasMessageUnread = Object.keys(dots).length > 0 || wx.getStorageSync('has_message_unread')
    this.setData({ hasMessageUnread: !!hasMessageUnread })
    this._buildStages()
  },

  _loadStageRedDots() {
    const dots = wx.getStorageSync('stage_red_dots') || {}
    const hasMessageUnread = Object.keys(dots).length > 0 || wx.getStorageSync('has_message_unread')
    this.setData({ hasMessageUnread: !!hasMessageUnread })
  },

  _buildStages() {
    const dots = wx.getStorageSync('stage_red_dots') || {}
    const icons = ['📦', '🔌', '🧱', '🪵', '🎨', '🔧']
    const stages = STAGES.map((s, i) => ({
      id: s.id,
      name: s.name,
      icon: icons[i],
      hasRedDot: !!dots[s.id]
    }))
    this.setData({ stages })
  },

  onMessage() {
    wx.setStorageSync('has_message_unread', false)
    this.setData({ hasMessageUnread: false })
    wx.navigateTo({ url: '/pages/p14_message/p14_message' })
  },

  onBannerTap(e) {
    wx.navigateTo({ url: '/pages/p16_guide/p16_guide' })
  },

  onGridTap(e) {
    const path = e.currentTarget.dataset.path
    if (path) wx.navigateTo({ url: path })
  },

  onAICheck() {
    const startDate = wx.getStorageSync('construction_start_date')
    if (!startDate) {
      wx.showModal({
        title: '设置开工日期',
        content: '请先设置开工日期，以便为您规划6大阶段进度',
        confirmText: '去设置',
        success: (res) => {
          if (res.confirm) wx.switchTab({ url: '/pages/p09_construction/p09_construction' })
        }
      })
      return
    }
    wx.switchTab({ url: '/pages/p09_construction/p09_construction' })
  },

  onStageTap(e) {
    const stageId = e.currentTarget.dataset.id
    const app = getApp()
    app.clearStageRedDot && app.clearStageRedDot(stageId)
    wx.setStorageSync('has_message_unread', false)
    this.setData({ hasMessageUnread: false })
    wx.switchTab({
      url: '/pages/p09_construction/p09_construction?stage=' + stageId
    })
  },

  onMemberCard() {
    wx.navigateTo({ url: '/pages/p27_report_unlock/p27_report_unlock' })
  }
})

Page({
  data: {
    remindEnabled: true,
    remindDayIndex: 2,
    remindDayOptions: [
      { value: 1, label: '1天' },
      { value: 2, label: '2天' },
      { value: 3, label: '3天' },
      { value: 5, label: '5天' },
      { value: 7, label: '7天' }
    ],
    redDotEnabled: true
  },

  onLoad() {
    this._loadSettings()
  },

  onShow() {
    this._loadSettings()
  },

  _loadSettings() {
    const remindEnabled = wx.getStorageSync('remind_enabled')
    const remindDays = wx.getStorageSync('remind_days') || 3
    const redDotEnabled = wx.getStorageSync('red_dot_enabled')
    const options = this.data.remindDayOptions
    let remindDayIndex = options.findIndex(o => o.value === remindDays)
    if (remindDayIndex < 0) remindDayIndex = 2
    this.setData({
      remindEnabled: remindEnabled !== false,
      remindDayIndex: remindDayIndex >= 0 ? remindDayIndex : 2,
      redDotEnabled: redDotEnabled !== false
    })
  },

  _syncToApp() {
    const app = getApp()
    if (app.globalData) {
      app.globalData.remindEnabled = this.data.remindEnabled
      app.globalData.remindDays = this.data.remindDayOptions[this.data.remindDayIndex].value
    }
  },

  onRemindSwitch(e) {
    const v = e.detail.value
    wx.setStorageSync('remind_enabled', v)
    this.setData({ remindEnabled: v })
    this._syncToApp()
    wx.showToast({ title: '设置已更新', icon: 'none' })
  },

  onRemindDaysChange(e) {
    const i = parseInt(e.detail.value, 10)
    const val = this.data.remindDayOptions[i].value
    wx.setStorageSync('remind_days', val)
    this.setData({ remindDayIndex: i })
    this._syncToApp()
    wx.showToast({ title: '设置已更新', icon: 'none' })
  },

  onRedDotSwitch(e) {
    const v = e.detail.value
    wx.setStorageSync('red_dot_enabled', v)
    this.setData({ redDotEnabled: v })
    wx.showToast({ title: '设置已更新', icon: 'none' })
  },

  onLogout() {
    wx.showModal({
      title: '确认退出',
      content: '退出后需重新登录',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorageSync()
          getApp().globalData = { stageStatus: {}, startDate: null }
          wx.reLaunch({ url: '/pages/p01_onboarding/p01_onboarding' })
        }
      }
    })
  }
})

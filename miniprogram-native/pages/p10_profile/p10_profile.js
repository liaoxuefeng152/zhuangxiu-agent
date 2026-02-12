Page({
  data: {
    userInfo: {},
    memberText: '普通用户'
  },

  onLoad() {
    this._loadUser()
  },

  onShow() {
    this._loadUser()
  },

  _loadUser() {
    const userInfo = wx.getStorageSync('user_info') || {}
    const expire = wx.getStorageSync('member_expire') || ''
    const isMember = !!expire && new Date(expire) > new Date()
    const memberText = isMember ? '6大阶段全解锁会员' : '普通用户'
    this.setData({ userInfo, memberText })
  },

  onMember() {
    wx.navigateTo({ url: '/pages/p26_membership/p26_membership' })
  },

  onReport() {
    wx.navigateTo({ url: '/pages/p18_report_list/p18_report_list' })
  },

  onPhotos() {
    wx.navigateTo({ url: '/pages/p28_photos/p28_photos' })
  },

  onOrder() {
    wx.navigateTo({ url: '/pages/p24_order_list/p24_order_list' })
  },

  onCalendar() {
    wx.navigateTo({ url: '/pages/p29_calendar/p29_calendar' })
  },

  onDataMgmt() {
    wx.navigateTo({ url: '/pages/p20_data_mgmt/p20_data_mgmt' })
  },

  onAccount() {
    wx.navigateTo({ url: '/pages/p19_account_setting/p19_account_setting' })
  },

  onPrivacy() {
    wx.navigateTo({ url: '/pages/p17_privacy/p17_privacy' })
  },

  onGuide() {
    wx.navigateTo({ url: '/pages/p16_guide/p16_guide' })
  },

  onFeedback() {
    wx.navigateTo({ url: '/pages/p22_feedback/p22_feedback' })
  }
})

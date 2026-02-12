const SHARE_TYPES = {
  progress: { icon: '📊', title: '装修进度', desc: '6大阶段进度一览' },
  report: { icon: '📄', title: '验收报告', desc: 'AI验收结果' },
  member: { icon: '👑', title: '会员权益', desc: '6大阶段全解锁' }
}

Page({
  data: {
    shareData: { icon: '📊', title: '分享', desc: '装修避坑管家' },
    shareType: 'progress'
  },

  onLoad(options) {
    const type = options.type || 'progress'
    const title = options.title || ''
    const desc = options.desc || ''
    const data = SHARE_TYPES[type] || SHARE_TYPES.progress
    if (title) data.title = title
    if (desc) data.desc = desc
    this.setData({ shareData: data, shareType: type })
  },

  onShareAppMessage() {
    return {
      title: this.data.shareData.title,
      path: '/pages/p02_index/p02_index'
    }
  },

  onShareTimeline() {
    return {
      title: this.data.shareData.title
    }
  },

  onShareFriend() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage']
    })
    wx.showToast({ title: '点击右上角分享给好友', icon: 'none', duration: 2500 })
  },

  onShareMoments() {
    wx.showToast({ title: '点击右上角分享到朋友圈', icon: 'none', duration: 2500 })
  },

  onSaveImage() {
    wx.showModal({
      title: '保存图片',
      content: '小程序码需后端生成，请使用右上角分享',
      showCancel: false
    })
  }
})

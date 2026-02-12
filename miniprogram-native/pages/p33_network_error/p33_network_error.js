Page({
  data: {
    from: ''
  },

  onLoad(options) {
    this.setData({ from: options.from || '' })
  },

  onRetry() {
    wx.getNetworkType({
      success: (res) => {
        if (res.networkType === 'none') {
          wx.showToast({ title: '网络仍异常', icon: 'none' })
        } else {
          const from = decodeURIComponent(this.data.from || '')
          const tabPages = ['p02_index', 'p09_construction', 'p10_profile']
          const isTab = tabPages.some(p => from.includes(p))
          const url = from ? '/' + from : '/pages/p02_index/p02_index'
          if (isTab) {
            wx.switchTab({ url })
          } else if (from) {
            wx.redirectTo({
              url,
              fail: () => wx.switchTab({ url: '/pages/p02_index/p02_index' })
            })
          } else {
            wx.switchTab({ url: '/pages/p02_index/p02_index' })
          }
        }
      }
    })
  },

  onGoHome() {
    wx.switchTab({ url: '/pages/p02_index/p02_index' })
  }
})

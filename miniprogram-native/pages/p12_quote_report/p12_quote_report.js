Page({
  data: { leakCount: 3, highCount: 2, saveAmount: '1200' },

  onShare() {
    wx.navigateTo({ url: '/pages/p32_share/p32_share?type=report' })
  }
})

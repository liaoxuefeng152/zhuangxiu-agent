Page({
  data: { problemCount: 2, fixCount: 5 },

  onShare() {
    wx.navigateTo({ url: '/pages/p32_share/p32_share?type=report' })
  }
})

Page({
  data: {
    companyName: '待检测公司',
    status: '在业',
    riskLevel: '低风险',
    score: 85
  },

  onLoad(options) {
    if (options.name) {
      this.setData({ companyName: decodeURIComponent(options.name) })
    }
  },

  onShare() {
    wx.navigateTo({ url: '/pages/p32_share/p32_share?type=report&title=公司风险报告' })
  }
})

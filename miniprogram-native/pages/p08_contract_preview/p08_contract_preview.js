Page({
  data: {
    riskLevel: '中风险',
    riskClass: 'mid',
    riskDesc: '2项问题条款 + 1项高危条款',
    fixCount: 5,
    items: [
      { pos: '第3条第2款', text: '付款节点不明确' },
      { pos: '第5条', text: '违约责任不对等' }
    ]
  },

  onUnlock() {
    wx.navigateTo({ url: '/pages/p27_report_unlock/p27_report_unlock?type=contract' })
  }
})

Page({
  data: {
    riskLevel: '中风险',
    riskClass: 'mid',
    riskDesc: '3项漏项 + 2项虚高',
    saveAmount: '1200',
    risks: [
      { name: '水电改造报价偏高', save: 500 },
      { name: '辅材未列明细', save: 300 }
    ]
  },

  onUnlock() {
    wx.navigateTo({ url: '/pages/p27_report_unlock/p27_report_unlock?type=quote' })
  }
})

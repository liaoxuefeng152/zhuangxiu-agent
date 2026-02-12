Page({
  data: { reports: [] },

  onLoad() {
    const unlocked = wx.getStorageSync('unlocked_reports') || []
    const names = { quote: '报价分析', contract: '合同审核', company: '公司风险' }
    const reports = unlocked.map((t, i) => ({
      id: i,
      type: t,
      name: names[t] || t,
      time: new Date().toLocaleDateString(),
      unlocked: true
    }))
    this.setData({ reports })
  },

  onReportTap(e) {
    const item = e.currentTarget.dataset.item
    const routes = { quote: '/pages/p12_quote_report/p12_quote_report', contract: '/pages/p13_contract_report/p13_contract_report', company: '/pages/p11_company_report/p11_company_report' }
    const url = routes[item.type]
    if (url) wx.navigateTo({ url })
  },

  onGoGen() {
    wx.switchTab({ url: '/pages/p02_index/p02_index' })
  }
})

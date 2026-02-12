const REPORT_NAMES = {
  quote: '报价单分析报告',
  contract: '合同审核报告',
  company: '公司风险报告',
  acceptance: '验收报告'
}

Page({
  data: {
    reportType: 'quote',
    reportName: '报价单分析报告',
    unlockType: 'single'
  },

  onLoad(options) {
    const type = options.type || options.report || 'quote'
    const name = REPORT_NAMES[type] || options.title || '完整报告'
    this.setData({ reportType: type, reportName: name })
  },

  onSelectType(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ unlockType: type })
  },

  onViewMember() {
    wx.navigateTo({ url: '/pages/p26_membership/p26_membership' })
  },

  onConfirm() {
    const isMember = !!wx.getStorageSync('member_expire') && new Date(wx.getStorageSync('member_expire')) > new Date()
    if (isMember) {
      wx.showToast({ title: '会员已免费解锁', icon: 'success' })
      setTimeout(() => wx.navigateBack(), 1500)
      return
    }
    if (this.data.unlockType === 'member') {
      wx.navigateTo({ url: '/pages/p26_membership/p26_membership' })
      return
    }
    wx.showModal({
      title: '支付模拟',
      content: '开发环境无支付，是否模拟解锁成功？',
      success: (res) => {
        if (res.confirm) {
          const unlocked = wx.getStorageSync('unlocked_reports') || []
          if (!unlocked.includes(this.data.reportType)) {
            unlocked.push(this.data.reportType)
            wx.setStorageSync('unlocked_reports', unlocked)
          }
          const orders = wx.getStorageSync('orders') || []
          orders.unshift({
            id: 'ord' + Date.now(),
            no: 'ORD' + Date.now(),
            type: 'report',
            name: this.data.reportName + '解锁',
            amount: '9.9',
            status: 'paid',
            createTime: Date.now()
          })
          wx.setStorageSync('orders', orders)
          wx.showToast({ title: '解锁成功', icon: 'success' })
          setTimeout(() => wx.navigateBack(), 1500)
        }
      }
    })
  }
})

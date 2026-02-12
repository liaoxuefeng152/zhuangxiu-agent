function formatTime(ts) {
  const d = new Date(ts)
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0') + ' ' + String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0')
}

Page({
  data: {
    order: null
  },

  onLoad(options) {
    const id = options.id
    const orders = wx.getStorageSync('orders') || []
    const order = orders.find(o => o.id === id)
    if (order) {
      const statusMap = { pending: { text: '待支付', class: 'pending' }, paid: { text: '已支付', class: 'paid' }, refund: { text: '已退款', class: 'refund' } }
      const s = statusMap[order.status] || {}
      this.setData({
        order: {
          ...order,
          typeName: order.type === 'member' ? '会员开通' : '报告解锁',
          statusText: s.text,
          statusClass: s.class,
          timeText: formatTime(order.createTime || order.time || Date.now())
        }
      })
    }
  },

  onPay() {
    wx.showToast({ title: '请使用真实环境支付', icon: 'none' })
  },

  onViewBenefit() {
    const o = this.data.order
    if (o && o.type === 'member') {
      wx.navigateTo({ url: '/pages/p26_membership/p26_membership' })
    } else {
      wx.navigateBack()
    }
  },

  onBack() {
    wx.navigateBack()
  }
})

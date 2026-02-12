const TABS = [
  { id: 'all', name: '全部' },
  { id: 'pending', name: '待支付' },
  { id: 'paid', name: '已支付' },
  { id: 'refund', name: '已退款' },
  { id: 'expired', name: '已过期' }
]

function genOrderNo() {
  return 'ORD' + Date.now().toString(36).toUpperCase()
}

Page({
  data: {
    tabs: TABS,
    currentTab: 'all',
    currentTabName: '全部',
    orders: [],
    filteredOrders: []
  },

  onLoad() {
    this._loadOrders()
  },

  onShow() {
    this._loadOrders()
  },

  _loadOrders() {
    let orders = wx.getStorageSync('orders') || []
    if (!Array.isArray(orders)) orders = []
    const tab = this.data.currentTab
    let filtered = orders
    if (tab !== 'all') {
      filtered = orders.filter(o => o.status === tab)
    }
    const withExtra = filtered.map(o => {
      const statusMap = {
        pending: { text: '待支付', class: 'pending' },
        paid: { text: '已支付', class: 'paid' },
        refund: { text: '已退款', class: 'refund' },
        expired: { text: '已过期', class: 'refund' }
      }
      const s = statusMap[o.status] || { text: o.status, class: '' }
      return {
        ...o,
        statusText: s.text,
        statusClass: s.class,
        typeName: o.type === 'member' ? '会员开通' : '报告解锁'
      }
    })
    const tabItem = TABS.find(t => t.id === tab)
    this.setData({
      orders,
      filteredOrders: withExtra,
      currentTabName: tabItem ? tabItem.name : '全部'
    })
  },

  onTabTap(e) {
    const id = e.currentTarget.dataset.id
    this.setData({ currentTab: id })
    this._loadOrders()
  },

  onOrderTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/p25_order_detail/p25_order_detail?id=' + id })
  },

  onGoOrder() {
    wx.navigateTo({ url: '/pages/p27_report_unlock/p27_report_unlock' })
  }
})

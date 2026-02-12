const PACKAGES = [
  { id: 'month', price: '29.9', unit: '月', desc: '1个月有效期', badge: '' },
  { id: 'quarter', price: '69.9', unit: '季', desc: '3个月有效期', badge: '' },
  { id: 'year', price: '199', unit: '年', desc: '12个月有效期', badge: '性价比首选' }
]

Page({
  data: {
    isMember: false,
    memberExpire: '',
    memberDays: 0,
    packages: PACKAGES,
    selectedPkg: 'year',
    selectedPrice: '199',
    selectedUnit: '年'
  },

  onLoad() {
    this._loadMember()
  },

  onShow() {
    this._loadMember()
  },

  _loadMember() {
    const expire = wx.getStorageSync('member_expire') || ''
    const isMember = !!expire && new Date(expire) > new Date()
    const now = new Date()
    const end = expire ? new Date(expire) : now
    const memberDays = isMember ? Math.ceil((end - now) / 86400000) : 0
    const memberExpire = expire ? expire.slice(0, 10) + ' 至 ' + expire.slice(0, 10) : ''
    const pkg = this.data.packages.find(p => p.id === this.data.selectedPkg) || PACKAGES[2]
    this.setData({
      isMember,
      memberExpire,
      memberDays,
      selectedPrice: pkg.price,
      selectedUnit: pkg.unit
    })
  },

  onSelectPkg(e) {
    const id = e.currentTarget.dataset.id
    const pkg = PACKAGES.find(p => p.id === id) || PACKAGES[2]
    this.setData({
      selectedPkg: id,
      selectedPrice: pkg.price,
      selectedUnit: pkg.unit
    })
  },

  onSubscribe() {
    const { selectedPkg } = this.data
    wx.showModal({
      title: '会员开通',
      content: '开发环境暂无法调用微信支付，是否模拟开通成功？',
      success: (res) => {
        if (res.confirm) this._onPaySuccess(selectedPkg)
      }
    })
  },

  _onPaySuccess(pkgId) {
    const units = { month: 1, quarter: 3, year: 12 }
    const months = units[pkgId] || 12
    const d = new Date()
    d.setMonth(d.getMonth() + months)
    const expire = d.toISOString().slice(0, 10)
    wx.setStorageSync('member_expire', expire)
    const orders = wx.getStorageSync('orders') || []
    orders.unshift({
      id: 'ord' + Date.now(),
      no: 'ORD' + Date.now(),
      type: 'member',
      name: '会员开通-' + (months === 1 ? '月卡' : months === 3 ? '季卡' : '年卡'),
      amount: this.data.selectedPrice,
      status: 'paid',
      createTime: Date.now()
    })
    wx.setStorageSync('orders', orders)
    wx.showToast({ title: '开通成功', icon: 'success' })
    this._loadMember()
  }
})

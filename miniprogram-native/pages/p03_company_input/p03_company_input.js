const MOCK_MATCHES = [
  { name: '某某装饰有限公司', region: '北京' },
  { name: '某某家装', region: '北京' }
]

Page({
  data: {
    keyword: '',
    matches: []
  },

  onInput(e) {
    const v = e.detail.value.trim()
    const matches = v.length >= 3 ? this._mockMatch(v) : []
    this.setData({ keyword: v, matches })
  },

  _mockMatch(kw) {
    return MOCK_MATCHES.filter(m => m.name.includes(kw) || m.region.includes(kw))
  },

  onSelectMatch(e) {
    const name = e.currentTarget.dataset.name
    this.setData({ keyword: name, matches: [] })
  },

  onDetect() {
    if (this.data.keyword.length < 3) {
      wx.showToast({ title: '请输入有效公司名称', icon: 'none' })
      return
    }
    wx.redirectTo({
      url: '/pages/p04_scanning/p04_scanning?type=company&name=' + encodeURIComponent(this.data.keyword)
    })
  }
})

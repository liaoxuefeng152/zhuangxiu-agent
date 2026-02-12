Page({
  data: {
    keyword: '',
    selectedCity: '',
    hotCities: ['北京', '上海', '广州', '深圳', '杭州', '成都']
  },

  onSearch(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSelectCity(e) {
    const city = e.currentTarget.dataset.city
    this.setData({ selectedCity: city })
  },

  onConfirm() {
    const city = this.data.selectedCity
    if (!city) return
    wx.setStorageSync('current_city', city)
    wx.showToast({ title: '已切换至' + city, icon: 'success' })
    setTimeout(() => wx.navigateBack(), 1000)
  }
})

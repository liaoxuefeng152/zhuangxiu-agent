Page({
  data: {},

  onSwiperChange() {},

  onStart() {
    wx.setStorageSync('onboarding_completed', true)
    wx.reLaunch({ url: '/pages/p02_index/p02_index' })
  }
})

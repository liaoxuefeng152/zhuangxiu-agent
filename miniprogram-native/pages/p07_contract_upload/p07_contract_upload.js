Page({
  onUpload() {
    wx.chooseImage({
      count: 1,
      success: () => {
        wx.redirectTo({ url: '/pages/p04_scanning/p04_scanning?type=contract' })
      }
    })
  },
  onExample() {
    wx.showModal({ title: '合同示例', content: '住建局官方范本', showCancel: false })
  }
})

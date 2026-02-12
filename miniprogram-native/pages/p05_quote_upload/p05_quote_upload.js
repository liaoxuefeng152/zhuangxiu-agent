Page({
  data: { uploading: false, progress: 0 },

  onUpload() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['pdf', 'jpg', 'png'],
      success: () => {
        this.setData({ uploading: true })
        let p = 0
        const t = setInterval(() => {
          p += 20
          this.setData({ progress: p })
          if (p >= 100) {
            clearInterval(t)
            wx.redirectTo({ url: '/pages/p04_scanning/p04_scanning?type=quote' })
          }
        }, 200)
      }
    })
  },

  onExample() {
    wx.showModal({
      title: '示例',
      content: '规范报价单示例图',
      showCancel: false
    })
  }
})

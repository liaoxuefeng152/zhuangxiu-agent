Page({
  data: {
    context: '验收问题咨询',
    input: ''
  },

  onLoad(options) {
    if (options.stage) {
      this.setData({ context: options.stage + '验收问题' })
    }
  },

  onInput(e) {
    this.setData({ input: e.detail.value })
  },

  onSend() {
    const text = this.data.input.trim()
    if (!text) return
    wx.showToast({ title: '已发送', icon: 'none' })
    this.setData({ input: '' })
  }
})

Page({
  data: { input: '' },

  onInput(e) {
    this.setData({ input: e.detail.value })
  },

  onSend() {
    const text = this.data.input.trim()
    if (!text) return
    wx.showToast({ title: '消息已发送', icon: 'none' })
    this.setData({ input: '' })
  }
})

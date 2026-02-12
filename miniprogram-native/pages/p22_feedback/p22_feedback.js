Page({
  data: {
    types: [
      { value: 'bug', label: '功能BUG' },
      { value: 'suggest', label: '操作建议' },
      { value: 'privacy', label: '隐私异议' }
    ],
    typeIndex: 0,
    content: '',
    canSubmit: false
  },

  onTypeChange(e) {
    this.setData({ typeIndex: parseInt(e.detail.value, 10) })
  },

  onContentInput(e) {
    const content = e.detail.value
    this.setData({ content, canSubmit: content.length >= 10 })
  },

  onSubmit() {
    if (!this.data.canSubmit) return
    wx.showToast({ title: '反馈提交成功', icon: 'success' })
    setTimeout(() => wx.navigateBack(), 1500)
  }
})

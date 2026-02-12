Page({
  data: {
    orderNo: '',
    amount: '',
    reasons: [
      { value: '1', label: '不需要了' },
      { value: '2', label: '报告不准确' },
      { value: '3', label: '功能不符合预期' }
    ],
    reasonIndex: 0,
    desc: ''
  },

  onLoad(options) {
    this.setData({
      orderNo: options.no || '',
      amount: options.amount || ''
    })
  },

  onReasonChange(e) {
    this.setData({ reasonIndex: parseInt(e.detail.value, 10) })
  },

  onDescInput(e) {
    this.setData({ desc: e.detail.value })
  },

  onSubmit() {
    wx.showToast({ title: '申请已提交', icon: 'success' })
    setTimeout(() => wx.navigateBack(), 1500)
  }
})

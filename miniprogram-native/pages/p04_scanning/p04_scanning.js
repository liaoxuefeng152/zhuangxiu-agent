const REDIRECT = {
  company: '/pages/p11_company_report/p11_company_report',
  quote: '/pages/p06_quote_preview/p06_quote_preview',
  contract: '/pages/p08_contract_preview/p08_contract_preview',
  acceptance: '/pages/p30_acceptance/p30_acceptance'
}

Page({
  data: {
    loadingText: '正在处理...',
    progress: 0,
    type: 'acceptance',
    stage: 'S00',
    name: ''
  },

  onLoad(options) {
    const type = options.type || 'acceptance'
    const stage = options.stage || 'S00'
    const name = options.name || ''
    const texts = {
      company: '正在核验工商信息，检测中...',
      quote: '正在分析报价单...',
      contract: '正在审核合同...',
      acceptance: '正在生成【' + stage + '】验收报告...'
    }
    this.setData({ type, stage, name, loadingText: texts[type] || texts.acceptance })
    this._mockProgress()
  },

  _mockProgress() {
    let p = 0
    const timer = setInterval(() => {
      p += 10
      this.setData({
        progress: Math.min(p, 100),
        loadingText: this.data.loadingText.replace(/\d+%/, p + '%')
      })
      if (p >= 100) {
        clearInterval(timer)
        let url = REDIRECT[this.data.type] || REDIRECT.acceptance
        if (this.data.type === 'company' && this.data.name) {
          url += '?name=' + encodeURIComponent(this.data.name)
        } else if (this.data.type === 'acceptance') {
          url += '?stage=' + this.data.stage
        }
        wx.redirectTo({ url })
      }
    }, 300)
  }
})

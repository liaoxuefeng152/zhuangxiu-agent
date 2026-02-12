const { STAGES, STAGE_NAMES } = require('../../utils/config')

Page({
  data: {
    stageStats: [],
    aiSummary: '',
    photoCount: 0,
    reportCount: 0,
    completeStages: 0
  },

  onLoad() {
    this._loadStats()
  },

  onShow() {
    this._loadStats()
  },

  _loadStats() {
    const stageStatus = wx.getStorageSync('stage_status') || {}
    let photoCount = 0
    const stages = ['S00', 'S01', 'S02', 'S03', 'S04', 'S05']
    stages.forEach(s => {
      const list = wx.getStorageSync('photos_' + s) || []
      photoCount += list.length
    })

    const stageStats = STAGES.map(s => {
      const status = stageStatus[s.id]
      const percent = (status === '已核对' || status === '已通过') ? 100 : 30
      return {
        id: s.id,
        name: s.name,
        percent
      }
    })

    const completeStages = stageStats.filter(s => s.percent === 100).length
    const reportCount = completeStages
    const aiSummary = completeStages >= 6
      ? '装修已全部完成，恭喜！所有阶段验收通过。'
      : completeStages > 0
        ? `已完成 ${completeStages}/6 阶段，继续加油！`
        : '设置开工日期后开始记录进度。'

    this.setData({
      stageStats,
      aiSummary,
      photoCount,
      reportCount,
      completeStages
    })
  },

  onGenReport() {
    wx.showToast({ title: '报告生成中...', icon: 'loading', duration: 2000 })
    setTimeout(() => {
      wx.showToast({ title: '报告已生成', icon: 'success' })
    }, 1500)
  }
})

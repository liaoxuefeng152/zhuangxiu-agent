const { STAGE_NAMES } = require('../../utils/config')
const app = getApp()

// 模拟验收项（按阶段）
const MOCK_ITEMS = {
  S00: [
    { name: '材料清单核对', standard: '清单与实物逐一核对', pass: true },
    { name: '品牌规格确认', standard: '与合同约定一致', pass: true }
  ],
  S01: [
    { name: '水电布线间距', standard: '间距≥30cm', pass: true },
    { name: '防水高度', standard: '≥1.8m无漏刷', pass: false },
    { name: '线管固定', standard: '固定牢固无松动', pass: true }
  ],
  S02: [
    { name: '地砖平整度', standard: '2m内误差≤2mm', pass: true },
    { name: '空鼓率', standard: '≤5%', pass: true }
  ],
  S03: [
    { name: '吊顶平整', standard: '接缝严密', pass: true },
    { name: '柜体安装', standard: '牢固垂直', pass: true }
  ],
  S04: [
    { name: '墙面平整', standard: '无凹凸裂缝', pass: true },
    { name: '涂料均匀', standard: '无色差流挂', pass: true }
  ],
  S05: [
    { name: '五金安装', standard: '牢固可用', pass: true },
    { name: '洁具密封', standard: '无渗漏', pass: true }
  ]
}

Page({
  data: {
    stage: 'S00',
    stageName: '',
    loading: true,
    loadingText: '正在生成验收报告...',
    progress: 0,
    report: null,
    canAddPhoto: true
  },

  onLoad(options) {
    const stage = options.stage || 'S00'
    const stageName = STAGE_NAMES[stage] || (stage === 'S00' ? '材料进场核对' : '阶段验收')
    wx.setNavigationBarTitle({
      title: stage === 'S00' ? '材料台账' : stageName + '验收报告'
    })
    this.setData({ stage, stageName })
    this._mockLoadReport(stage)
  },

  _mockLoadReport(stage) {
    const items = MOCK_ITEMS[stage] || MOCK_ITEMS.S01
    const passCount = items.filter(i => i.pass).length
    const failCount = items.length - passCount
    const failItems = items.filter(i => !i.pass)
    let statusText = '已通过'
    let statusClass = 'pass'
    if (failCount > 0) {
      statusText = '待整改'
      statusClass = 'fail'
    } else if (passCount === 0) {
      statusText = '待验收'
      statusClass = 'pending'
    }

    const report = {
      statusText,
      statusClass,
      checkTime: new Date().toISOString().slice(0, 10),
      totalCount: items.length,
      passCount,
      failCount,
      items,
      failItems,
      fixSuggestion: failItems.length
        ? '请按验收标准整改后重新拍照申请复检。'
        : '验收合格，可进行下一阶段。',
      photos: []
    }

    let progress = 0
    const timer = setInterval(() => {
      progress += 20
      this.setData({
        loadingText: progress < 100 ? 'AI正在分析...' + progress + '%' : '分析完成',
        progress: Math.min(progress, 100)
      })
      if (progress >= 100) {
        clearInterval(timer)
        this.setData({
          loading: false,
          report,
          progress: 100
        })
        this._syncStageStatus(report)
      }
    }, 300)
  },

  _syncStageStatus(report) {
    if (!report) return
    const stageId = this.data.stage
    const stageStatus = wx.getStorageSync('stage_status') || {}
    let finalStatus = report.statusText
    if (report.statusText === '已通过') {
      finalStatus = stageId === 'S00' ? '已核对' : '已通过'
    } else if (report.statusText === '待整改') {
      finalStatus = '待整改'
    }
    stageStatus[stageId] = finalStatus
    wx.setStorageSync('stage_status', stageStatus)
    app.globalData.stageStatus = stageStatus
  },

  onItemTap(e) {
    const item = e.currentTarget.dataset.item
    wx.showModal({
      title: item.name,
      content: '标准：' + item.standard + '\n结果：' + (item.pass ? '合格' : '不合格'),
      showCancel: false
    })
  },

  onMarkFix() {
    const stageStatus = wx.getStorageSync('stage_status') || {}
    stageStatus[this.data.stage] = '待整改'
    wx.setStorageSync('stage_status', stageStatus)
    getApp().globalData.stageStatus = stageStatus
    wx.showToast({ title: '已标记为待整改', icon: 'none' })
  },

  onRecheck() {
    wx.navigateTo({
      url: '/pages/p15_photo/p15_photo?stage=' + this.data.stage + '&recheck=1'
    })
  },

  onPhotoPreview(e) {
    const url = e.currentTarget.dataset.url
    if (url) wx.previewImage({ urls: [url], current: url })
  },

  onAddPhoto() {
    wx.navigateTo({
      url: '/pages/p15_photo/p15_photo?stage=' + this.data.stage
    })
  },

  onBack() {
    wx.navigateBack()
  }
})

const { STAGE_NAMES } = require('../../utils/config')

const TABS = [
  { id: 'all', name: '全部' },
  { id: 'S00', name: '材料进场' },
  { id: 'S01', name: '隐蔽工程' },
  { id: 'S02', name: '泥瓦工' },
  { id: 'S03', name: '木工' },
  { id: 'S04', name: '油漆' },
  { id: 'S05', name: '安装收尾' }
]

function formatTime(ts) {
  const d = new Date(ts)
  const m = d.getMonth() + 1
  const day = d.getDate()
  return m + '/' + day
}

Page({
  data: {
    tabs: TABS,
    currentTab: 'all',
    currentTabName: '全部',
    photoList: [],
    previewUrls: [],
    batchMode: false,
    selectAll: false,
    selected: []
  },

  onLoad() {
    this._loadPhotos()
  },

  onShow() {
    this._loadPhotos()
  },

  _loadPhotos() {
    const tab = this.data.currentTab
    let list = []
    if (tab === 'all') {
      const stages = ['S00', 'S01', 'S02', 'S03', 'S04', 'S05']
      stages.forEach(s => {
        const stored = wx.getStorageSync('photos_' + s) || []
        list = list.concat(stored.map(i => ({ ...i, stage: s })))
      })
    } else {
      list = (wx.getStorageSync('photos_' + tab) || []).map(i => ({ ...i, stage: tab }))
    }
    list.sort((a, b) => (b.time || 0) - (a.time || 0))
    const withTime = list.map(i => ({
      ...i,
      timeText: formatTime(i.time || i.path),
      selected: !!i.selected
    }))
    const previewUrls = list.map(i => i.path).filter(Boolean)
    const tabItem = TABS.find(t => t.id === tab)
    this.setData({
      photoList: withTime,
      previewUrls,
      currentTabName: tabItem ? tabItem.name : '全部'
    })
  },

  onTabTap(e) {
    const id = e.currentTarget.dataset.id
    this.setData({ currentTab: id, batchMode: false })
    this._loadPhotos()
  },

  onPhotoTap(e) {
    if (this.data.batchMode) {
      this.onSelectPhoto(e)
    } else {
      this.onPreview(e)
    }
  },

  onPreview(e) {
    const url = e.currentTarget.dataset.url
    const urls = this.data.previewUrls
    if (url && urls && urls.length) {
      wx.previewImage({ urls, current: url })
    }
  },

  onSelectPhoto(e) {
    const i = e.currentTarget.dataset.index
    const list = this.data.photoList.map((item, idx) => {
      if (idx === i) item.selected = !item.selected
      return item
    })
    const selected = list.filter(item => item.selected)
    this.setData({
      photoList: list,
      selected,
      selectAll: selected.length === list.length
    })
  },

  onGoPhoto() {
    const stage = this.data.currentTab === 'all' ? 'S00' : this.data.currentTab
    wx.navigateTo({ url: '/pages/p15_photo/p15_photo?stage=' + stage })
  },

  onToggleBatch() {
    this.setData({
      batchMode: !this.data.batchMode,
      selectAll: false,
      selected: []
    })
  },

  onToggleSelectAll() {
    const selectAll = !this.data.selectAll
    const selected = selectAll ? this.data.photoList.map((_, i) => i) : []
    this.setData({ selectAll, selected })
  },

  onBatchDel() {
    const { selected, currentTab } = this.data
    if (!selected.length) {
      wx.showToast({ title: '请先选择照片', icon: 'none' })
      return
    }
    wx.showModal({
      title: '确认删除',
      content: '删除后不可恢复',
      success: (res) => {
        if (res.confirm) {
          this._deletePhotos(selected, currentTab)
          this.setData({ batchMode: false, selected: [], selectAll: false })
          this._loadPhotos()
          wx.showToast({ title: '已删除', icon: 'none' })
        }
      }
    })
  },

  _deletePhotos(items, tab) {
    const paths = new Set(items.map(i => i.path).filter(Boolean))
    const stages = tab === 'all' ? ['S00','S01','S02','S03','S04','S05'] : [tab]
    stages.forEach(s => {
      const key = 'photos_' + s
      let stored = wx.getStorageSync(key) || []
      stored = stored.filter(i => !paths.has(i.path))
      wx.setStorageSync(key, stored)
    })
  },

  onBatchExport() {
    wx.showToast({ title: '导出功能开发中', icon: 'none' })
  }
})

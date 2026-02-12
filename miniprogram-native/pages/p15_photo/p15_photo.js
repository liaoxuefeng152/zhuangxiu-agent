const { STAGE_NAMES } = require('../../utils/config')

const GUIDE_BY_STAGE = {
  S00: ['请拍摄材料清单', '拍摄实物与清单对比照', '确保清晰完整'],
  S01: ['水电走线全景', '防水高度特写', '线管固定细节'],
  S02: ['地砖平整度', '空鼓检测部位', '接缝处理'],
  S03: ['吊顶接缝', '柜体安装', '垂直度'],
  S04: ['墙面平整', '涂料均匀度', '无色差'],
  S05: ['五金安装', '洁具密封', '整体效果']
}

const SCENE_TIP_BY_STAGE = {
  S00: '材料核对拍摄：请拍摄材料清单+实物对比照',
  S01: '隐蔽工程验收：请拍摄水电/防水等关键部位',
  S02: '泥瓦工验收：请拍摄地砖/墙面等',
  S03: '木工验收：请拍摄吊顶/柜体等',
  S04: '油漆验收：请拍摄墙面涂料等',
  S05: '安装收尾验收：请拍摄五金/洁具等'
}

const DEFAULT_GUIDE = ['拍摄清晰完整', '包含关键部位', '避免逆光']

Page({
  data: {
    stage: 'S00',
    sceneTip: '请拍摄施工相关照片',
    guideItems: DEFAULT_GUIDE,
    showGuide: true,
    photos: [],
    recheck: false
  },

  onLoad(options) {
    const stage = options.stage || 'S00'
    const recheck = options.recheck === '1'
    const sceneTip = SCENE_TIP_BY_STAGE[stage] || '请拍摄施工相关照片'
    const guideItems = GUIDE_BY_STAGE[stage] || DEFAULT_GUIDE
    const title = recheck ? '复检拍照' : '拍照留证'
    wx.setNavigationBarTitle({ title })
    this.setData({
      stage,
      sceneTip,
      guideItems,
      recheck
    })
  },

  onCloseGuide() {
    this.setData({ showGuide: false })
  },

  onChooseAlbum() {
    const remain = 9 - this.data.photos.length
    if (remain <= 0) {
      wx.showToast({ title: '最多选择9张照片', icon: 'none' })
      return
    }
    wx.chooseImage({
      count: remain,
      sourceType: ['album'],
      sizeType: ['compressed'],
      success: (res) => this._addPhotos(res.tempFilePaths),
      fail: (err) => {
        if (err.errMsg && (err.errMsg.includes('auth') || err.errMsg.includes('deny'))) {
          this._showPermissionGuide()
        } else {
          wx.showToast({ title: '选择失败', icon: 'none' })
        }
      }
    })
  },

  onTakePhoto() {
    const remain = 9 - this.data.photos.length
    if (remain <= 0) {
      wx.showToast({ title: '最多选择9张照片', icon: 'none' })
      return
    }
    wx.chooseImage({
      count: Math.min(remain, 9),
      sourceType: ['camera'],
      sizeType: ['compressed'],
      success: (res) => this._addPhotos(res.tempFilePaths),
      fail: (err) => {
        if (err.errMsg && (err.errMsg.includes('auth') || err.errMsg.includes('deny'))) {
          this._showPermissionGuide()
        } else {
          wx.showToast({ title: '拍照失败', icon: 'none' })
        }
      }
    })
  },

  _addPhotos(paths) {
    const photos = [...this.data.photos, ...paths].slice(0, 9)
    this.setData({ photos })
  },

  onDelPhoto(e) {
    const i = e.currentTarget.dataset.index
    const photos = this.data.photos.filter((_, idx) => idx !== i)
    this.setData({ photos })
  },

  onConfirm() {
    const { photos, stage, recheck } = this.data
    if (!photos.length) {
      wx.showToast({ title: '请至少选择1张照片', icon: 'none' })
      return
    }
    this._savePhotos(stage, photos)
    if (recheck) {
      wx.showToast({ title: '申诉材料已提交', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
      return
    }
    wx.redirectTo({
      url: '/pages/p04_scanning/p04_scanning?type=acceptance&stage=' + stage
    })
  },

  _savePhotos(stage, paths) {
    const key = 'photos_' + stage
    const stored = wx.getStorageSync(key) || []
    const list = stored.concat(paths.map(p => ({ path: p, time: Date.now() })))
    wx.setStorageSync(key, list.slice(-50))
  },

  _showPermissionGuide() {
    wx.showModal({
      title: '需要相册/相机权限',
      content: '请在设置中开启相册和相机权限，以便拍照留证',
      confirmText: '去设置',
      success: (res) => {
        if (res.confirm) wx.openSetting()
      }
    })
  }
})

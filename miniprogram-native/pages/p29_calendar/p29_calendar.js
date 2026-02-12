Page({
  data: {
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1,
    weekdays: ['日', '一', '二', '三', '四', '五', '六'],
    days: [],
    startDate: null
  },

  onLoad() {
    this.setData({ startDate: wx.getStorageSync('construction_start_date') })
    this._buildDays()
  },

  _buildDays() {
    const { year, month } = this.data
    const first = new Date(year, month - 1, 1)
    const last = new Date(year, month, 0)
    const pad = first.getDay()
    const total = last.getDate()
    const today = new Date()
    const days = []
    for (let i = 0; i < pad; i++) days.push({ date: '', isToday: false, hasNode: false })
    for (let d = 1; d <= total; d++) {
      const d2 = new Date(year, month - 1, d)
      days.push({
        date: d,
        isToday: d2.toDateString() === today.toDateString(),
        hasNode: false
      })
    }
    this.setData({ days })
  },

  onPrevMonth() {
    let { year, month } = this.data
    if (month === 1) { year--; month = 12 } else month--
    this.setData({ year, month })
    this._buildDays()
  },

  onNextMonth() {
    let { year, month } = this.data
    if (month === 12) { year++; month = 1 } else month++
    this.setData({ year, month })
    this._buildDays()
  }
})

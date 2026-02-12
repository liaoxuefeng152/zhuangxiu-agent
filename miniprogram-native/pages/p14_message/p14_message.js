const TABS = [
  { id: 'remind', name: '施工提醒' },
  { id: 'report', name: '报告通知' },
  { id: 'system', name: '系统消息' }
]

Page({
  data: {
    tabs: TABS,
    currentTab: 'remind',
    msgList: []
  },

  onLoad() {
    wx.setStorageSync('has_message_unread', false)
    this._loadMessages()
  },

  _loadMessages() {
    const msgs = wx.getStorageSync('messages') || []
    const tab = this.data.currentTab
    let list = msgs
    if (tab === 'remind') list = msgs.filter(m => m.type === 'remind')
    else if (tab === 'report') list = msgs.filter(m => m.type === 'report')
    else list = msgs.filter(m => m.type === 'system')
    const icons = { remind: '🔔', report: '📄', system: '⚙' }
    const withIcon = list.map(m => ({ ...m, icon: icons[m.type] || '📩' }))
    this.setData({ msgList: withIcon })
  },

  onTabTap(e) {
    const id = e.currentTarget.dataset.id
    this.setData({ currentTab: id })
    this._loadMessages()
  },

  onMsgTap(e) {
    const item = e.currentTarget.dataset.item
    if (item.action) {
      wx.navigateTo({ url: item.action })
    }
  }
})

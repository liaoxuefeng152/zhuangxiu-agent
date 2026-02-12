const fs = require('fs')
const path = require('path')

const PAGES = [
  ['p01_onboarding', '引导页'],
  ['p02_index', '首页'],
  ['p03_company_input', '公司检测'],
  ['p04_scanning', '检测中'],
  ['p05_quote_upload', '报价上传'],
  ['p06_quote_preview', '报价预览'],
  ['p07_contract_upload', '合同上传'],
  ['p08_contract_preview', '合同预览'],
  ['p09_construction', '施工陪伴'],
  ['p10_profile', '我的'],
  ['p11_company_report', '公司报告'],
  ['p12_quote_report', '报价报告'],
  ['p13_contract_report', '合同报告'],
  ['p14_message', '消息中心'],
  ['p15_photo', '拍照'],
  ['p16_guide', '使用指南'],
  ['p17_privacy', '隐私保障'],
  ['p18_report_list', '我的报告'],
  ['p19_account_setting', '账户设置'],
  ['p20_data_mgmt', '数据管理'],
  ['p21_recycle', '回收站'],
  ['p22_feedback', '意见反馈'],
  ['p23_customer', '在线客服'],
  ['p24_order_list', '我的订单'],
  ['p25_order_detail', '订单详情'],
  ['p26_membership', '会员权益'],
  ['p27_report_unlock', '报告解锁'],
  ['p28_photos', '施工照片'],
  ['p29_calendar', '装修日历'],
  ['p30_acceptance', '阶段验收'],
  ['p32_share', '分享'],
  ['p33_network_error', '网络异常'],
  ['p34_refund', '退款申请'],
  ['p35_city', '选择城市'],
  ['p36_ai_consult', 'AI监理咨询']
]

const root = path.join(__dirname, '..')

PAGES.forEach(([pageId, title]) => {
  const dir = path.join(root, 'pages', pageId)
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })

  const wxml = `<view class="stub">
  <text class="stub-title">{{title}}</text>
  <text class="stub-desc">开发中</text>
</view>`

  const wxss = `.stub {
  padding: 80rpx 40rpx;
  text-align: center;
}
.stub-title { font-size: 36rpx; font-weight: bold; color: #333; display: block; margin-bottom: 20rpx; }
.stub-desc { font-size: 28rpx; color: #999; }`

  const js = `Page({
  data: { title: '${title}' },
  onLoad() {
    wx.setNavigationBarTitle && wx.setNavigationBarTitle({ title: '${title}' })
  }
})`

  const json = JSON.stringify({ usingComponents: {}, navigationBarTitleText: title }, null, 2)

  fs.writeFileSync(path.join(dir, `${pageId}.wxml`), wxml)
  fs.writeFileSync(path.join(dir, `${pageId}.wxss`), wxss)
  fs.writeFileSync(path.join(dir, `${pageId}.js`), js)
  fs.writeFileSync(path.join(dir, `${pageId}.json`), json)
})

console.log('Stub pages created:', PAGES.length)

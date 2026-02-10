const config = {
  pages: [
    'pages/onboarding/index',
    'pages/index/index',
    'pages/company-scan/index',
    'pages/scan-progress/index',
    'pages/quote-upload/index',
    'pages/contract-upload/index',
    'pages/report-detail/index',
    'pages/report-unlock/index',
    'pages/report-list/index',
    'pages/construction/index',
    'pages/profile/index',
    'pages/payment/index',
    'pages/supervision/index',
    'pages/guide/index',
    'pages/settings/index',
    'pages/neutral-statement/index',
    'pages/account-notify/index',
    'pages/about/index',
    'pages/feedback/index',
    'pages/contact/index',
    'pages/photo/index',
    'pages/photo-gallery/index',
    'pages/acceptance/index',
    'pages/material-check/index',
    'pages/progress-share/index',
    'pages/message/index',
    'pages/order-list/index',
    'pages/order-detail/index',
    'pages/membership/index',
    'pages/history/index',
    'pages/network-error/index',
    'pages/refund/index',
    'pages/city-picker/index',
    'pages/data-manage/index',
    'pages/recycle-bin/index',
    'pages/calendar/index',
    'pages/privacy/index',
    'pages/ai-supervision/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#fff',
    navigationBarTitleText: '装修避坑管家',
    navigationBarTextStyle: 'black',
    backgroundColor: '#f5f5f5'
  },
  tabBar: {
    color: '#8C8C8C',
    selectedColor: '#1677FF',
    backgroundColor: '#fff',
    borderStyle: 'black',
    list: [
      {
        pagePath: 'pages/index/index',
        text: '首页',
        iconPath: 'assets/tabbar/home.png',
        selectedIconPath: 'assets/tabbar/home-active.png'
      },
      {
        pagePath: 'pages/construction/index',
        text: '施工陪伴',
        iconPath: 'assets/tabbar/construction.png',
        selectedIconPath: 'assets/tabbar/construction-active.png'
      },
      {
        pagePath: 'pages/profile/index',
        text: '我的',
        iconPath: 'assets/tabbar/profile.png',
        selectedIconPath: 'assets/tabbar/profile-active.png'
      }
    ]
  },
  permission: {
    'scope.userLocation': {
      desc: '你的位置信息将用于获取本地装修公司信息'
    }
  },
  requiredPrivateInfos: ['getLocation'],
  usingComponents: {},
  lazyCodeLoading: 'requiredComponents'
}

export default config

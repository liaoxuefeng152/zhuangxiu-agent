import React, { useState, useEffect } from 'react'
import { View, Text, Swiper, SwiperItem, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useDispatch, useSelector } from 'react-redux'
import './index.scss'

/**
 * 首页 - 装修决策Agent
 */
const Index: React.FC = () => {
  const dispatch = useDispatch()
  const { userInfo } = useSelector((state: any) => state.user)

  const [currentIndex, setCurrentIndex] = useState(0)
  const [swiperList] = useState([
    {
      id: 1,
      image: '/assets/banner1.png',
      title: '花30万装修，不该靠运气',
      subtitle: 'AI帮你避坑',
      action: 'guide'
    },
    {
      id: 2,
      image: '/assets/banner2.png',
      title: '装修公司靠谱吗？',
      subtitle: '10秒AI核验',
      action: 'company'
    },
    {
      id: 3,
      image: '/assets/banner3.png',
      title: '报价单/合同藏陷阱？',
      subtitle: 'AI逐条分析',
      action: 'upload'
    }
  ])

  useEffect(() => {
    // 检查是否需要显示公司检测提醒
    const hasCompanyScan = Taro.getStorageSync('has_company_scan')
    if (!hasCompanyScan) {
      // 显示提示
      Taro.showModal({
        title: '温馨提示',
        content: '建议先检测装修公司风险，再上传报价单或合同',
        confirmText: '去检测',
        cancelText: '跳过',
        success: (res) => {
          if (res.confirm) {
            Taro.navigateTo({ url: '/pages/company-scan/index' })
          }
        }
      })
    }
  }, [])

  // 检测公司
  const handleScanCompany = () => {
    Taro.navigateTo({
      url: '/pages/company-scan/index'
    })
  }

  // 上传报价单
  const handleUploadQuote = () => {
    const hasCompanyScan = Taro.getStorageSync('has_company_scan')
    if (!hasCompanyScan) {
      Taro.showModal({
        title: '温馨提示',
        content: '建议先检测装修公司风险，再上传报价单',
        confirmText: '去检测',
        cancelText: '继续上传',
        success: (res) => {
          if (res.confirm) {
            Taro.navigateTo({ url: '/pages/company-scan/index' })
          } else {
            Taro.navigateTo({ url: '/pages/quote-upload/index' })
          }
        }
      })
    } else {
      Taro.navigateTo({
        url: '/pages/quote-upload/index'
      })
    }
  }

  // 上传合同
  const handleUploadContract = () => {
    const hasCompanyScan = Taro.getStorageSync('has_company_scan')
    if (!hasCompanyScan) {
      Taro.showModal({
        title: '温馨提示',
        content: '建议先检测装修公司风险，再上传合同',
        confirmText: '去检测',
        cancelText: '继续上传',
        success: (res) => {
          if (res.confirm) {
            Taro.navigateTo({ url: '/pages/company-scan/index' })
          } else {
            Taro.navigateTo({ url: '/pages/contract-upload/index' })
          }
        }
      })
    } else {
      Taro.navigateTo({
        url: '/pages/contract-upload/index'
      })
    }
  }

  // 快捷入口点击
  const handleQuickAction = (type: string) => {
    switch (type) {
      case 'construction':
        Taro.navigateTo({ url: '/pages/construction/index' })
        break
      case 'photo':
        Taro.navigateTo({ url: '/pages/photo/index' })
        break
      case 'report':
        Taro.navigateTo({ url: '/pages/report-list/index' })
        break
      case 'supervision':
        Taro.navigateTo({ url: '/pages/supervision/index' })
        break
    }
  }

  // 轮播图点击
  const handleSwiperClick = (action: string) => {
    switch (action) {
      case 'guide':
        Taro.navigateTo({ url: '/pages/guide/index' })
        break
      case 'company':
        handleScanCompany()
        break
      case 'upload':
        Taro.showActionSheet({
          itemList: ['上传报价单', '上传合同'],
          success: (res) => {
            if (res.tapIndex === 0) {
              handleUploadQuote()
            } else if (res.tapIndex === 1) {
              handleUploadContract()
            }
          }
        })
        break
    }
  }

  return (
    <View className='index-page'>
      {/* 头部 */}
      <View className='header'>
        <Text className='title'>装修决策Agent</Text>
        <View className='message-icon' onClick={() => Taro.navigateTo({ url: '/pages/message/index' })}>
          <Image src='/assets/message.png' className='icon' />
          {hasNewMessage && <View className='dot' />}
        </View>
      </View>

      {/* 轮播图 */}
      <View className='swiper-container'>
        <Swiper
          className='swiper'
          indicatorDots
          autoplay
          interval={3000}
          circular
          current={currentIndex}
          onChange={(e) => setCurrentIndex(e.detail.current)}
        >
          {swiperList.map((item) => (
            <SwiperItem key={item.id}>
              <View className='swiper-item' onClick={() => handleSwiperClick(item.action)}>
                <Image src={item.image} className='swiper-image' mode='aspectFill' />
                <View className='swiper-content'>
                  <Text className='swiper-title'>{item.title}</Text>
                  <Text className='swiper-subtitle'>{item.subtitle}</Text>
                </View>
              </View>
            </SwiperItem>
          ))}
        </Swiper>
      </View>

      {/* 主功能按钮 */}
      <View className='main-actions'>
        <View className='action-btn primary' onClick={handleScanCompany}>
          <Text className='btn-text'>输入公司名称，检测是否跑路/有纠纷</Text>
        </View>
        <View className='action-btn secondary' onClick={handleUploadQuote}>
          <Text className='btn-text'>上传报价单，AI自动查漏项与虚高</Text>
        </View>
        <View className='action-btn secondary' onClick={handleUploadContract}>
          <Text className='btn-text'>上传合同，AI高亮霸王条款与陷阱</Text>
        </View>
      </View>

      {/* 快捷入口 */}
      <View className='quick-actions'>
        <View className='quick-item' onClick={() => handleQuickAction('construction')}>
          <Image src='/assets/calendar.png' className='quick-icon' />
          <Text className='quick-text'>施工进度</Text>
        </View>
        <View className='quick-item' onClick={() => handleQuickAction('photo')}>
          <Image src='/assets/camera.png' className='quick-icon' />
          <Text className='quick-text'>验收拍照</Text>
        </View>
        <View className='quick-item' onClick={() => handleQuickAction('report')}>
          <Image src='/assets/report.png' className='quick-icon' />
          <Text className='quick-text'>报告中心</Text>
        </View>
        <View className='quick-item' onClick={() => handleQuickAction('supervision')}>
          <Image src='/assets/phone.png' className='quick-icon' />
          <Text className='quick-text'>监理咨询</Text>
        </View>
      </View>
    </View>
  )
}

export default Index

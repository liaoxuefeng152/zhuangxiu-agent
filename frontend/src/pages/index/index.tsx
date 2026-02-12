import React, { useState, useEffect } from 'react'
import { View, Text, Swiper, SwiperItem, Image, ScrollView } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import { BANNER_IMAGES, USE_BANNER_IMAGES } from '../../config/assets'
import { safeSwitchTab, TAB_CONSTRUCTION } from '../../utils/navigation'
import UploadConfirmModal from '../../components/UploadConfirmModal'
import CityPickerModal from '../../components/CityPickerModal'
import './index.scss'

/** 根据已选城市名取简称（如 深圳市→深，未选显示「定位」） */
function getCityShortName(): string {
  const city = Taro.getStorageSync('selected_city') as string
  if (!city || !city.trim()) return '定位'
  const name = city.replace(/市$/, '').trim()
  return name.charAt(0) || '定位'
}

/**
 * P02 首页（优化版）- 核心功能聚合、6大阶段快捷、会员权益、城市定位入口
 */
const REMIND_PERMISSION_KEY = 'show_remind_permission_modal'
const CITY_SELECTION_KEY = 'show_city_selection_modal'

const Index: React.FC = () => {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [hasNewMessage, setHasNewMessage] = useState(false)
  const [noMorePrompt, setNoMorePrompt] = useState(false)
  const [uploadModal, setUploadModal] = useState<{ visible: boolean; type: 'quote' | 'contract'; url: string }>({ visible: false, type: 'quote', url: '' })
  const [remindPermissionModal, setRemindPermissionModal] = useState(false)
  const [cityPickerModal, setCityPickerModal] = useState(false)
  const [cityShort, setCityShort] = useState(() => getCityShortName())
  
  // 监听storage变化，更新城市显示（使用mounted标志避免页面卸载后setState报错）
  useEffect(() => {
    let mounted = true
    
    const updateCityDisplay = () => {
      try {
        if (!mounted) return
        const city = Taro.getStorageSync('selected_city') as string
        const shortName = city ? city.replace(/市$/, '').trim().charAt(0) || '定位' : '定位'
        setCityShort(shortName)
      } catch (_) {
        // 页面已销毁时setState可能报__subPageFrameEndTime__，吞掉异常
      }
    }
    
    // 页面显示时更新城市显示
    const timer = setInterval(() => {
      updateCityDisplay()
    }, 500)
    
    return () => {
      mounted = false
      clearInterval(timer)
    }
  }, [])

  const swiperList = [
    { id: 1, title: '花30万装修，不该靠运气', subtitle: 'AI帮你避坑', action: 'guide', image: BANNER_IMAGES[0] },
    { id: 2, title: '装修公司靠谱吗？', subtitle: '10秒AI核验', action: 'company', image: BANNER_IMAGES[1] },
    { id: 3, title: '报价单/合同藏陷阱？', subtitle: 'AI逐条分析', action: 'upload', image: BANNER_IMAGES[2] }
  ]

  const handleScanCompany = () => {
    Taro.navigateTo({ url: '/pages/company-scan/index' })
  }

  const showUploadModal = (type: 'quote' | 'contract', url: string) => {
    const hasCompanyScan = Taro.getStorageSync('has_company_scan')
    if (!hasCompanyScan && !noMorePrompt) {
      setUploadModal({ visible: true, type, url })
    } else {
      Taro.navigateTo({ url })
    }
  }

  const handleUploadConfirm = (noMore: boolean, url: string) => {
    setUploadModal((m) => ({ ...m, visible: false }))
    if (noMore) {
      setNoMorePrompt(true)
      Taro.setStorageSync('no_upload_prompt', '1')
    }
    Taro.navigateTo({ url })
  }

  const handleUploadGoScan = () => {
    setUploadModal((m) => ({ ...m, visible: false }))
    Taro.navigateTo({ url: '/pages/company-scan/index' })
  }

  const handleUploadQuote = () => showUploadModal('quote', '/pages/quote-upload/index')
  const handleUploadContract = () => showUploadModal('contract', '/pages/contract-upload/index')

  useEffect(() => {
    const stored = Taro.getStorageSync('no_upload_prompt')
    if (stored) setNoMorePrompt(true)
  }, [])

  // 用户进入首页后，首先弹出城市选择，其次是进度提醒
  useEffect(() => {
    try {
      // 检查是否已选择城市
      const selectedCity = Taro.getStorageSync('selected_city') as string
      const hasCity = selectedCity && selectedCity.trim()
      
      // 检查是否需要显示城市选择弹窗（从引导页跳转过来）
      const shouldShowCitySelection = Taro.getStorageSync(CITY_SELECTION_KEY) || !hasCity
      
      if (shouldShowCitySelection) {
        Taro.removeStorageSync(CITY_SELECTION_KEY)
        // 如果没有选择城市，先弹出城市选择
        if (!hasCity) {
          setCityPickerModal(true)
        } else {
          // 如果已选择城市，检查是否需要显示进度提醒
          checkAndShowRemindModal()
        }
      } else {
        // 如果不需要显示城市选择，检查是否需要显示进度提醒
        checkAndShowRemindModal()
      }
    } catch (_) {}
  }, [])

  // 检查并显示进度提醒弹窗
  const checkAndShowRemindModal = () => {
    try {
      if (Taro.getStorageSync(REMIND_PERMISSION_KEY)) {
        Taro.removeStorageSync(REMIND_PERMISSION_KEY)
        setRemindPermissionModal(true)
      }
    } catch (_) {}
  }

  // 城市选择确认回调
  const handleCityConfirm = (city: string) => {
    console.log('[首页] 城市选择确认', city)
    // 先关闭弹窗
    setCityPickerModal(false)
    // 更新城市显示（从storage读取最新值）
    const cityName = Taro.getStorageSync('selected_city') as string
    const shortName = cityName ? cityName.replace(/市$/, '').trim().charAt(0) || '定位' : '定位'
    setCityShort(shortName)
    console.log('[首页] 更新城市显示', shortName)
    // 城市选择完成后，延迟显示进度提醒弹窗
    setTimeout(() => {
      checkAndShowRemindModal()
    }, 300)
  }

  // 城市选择关闭回调（用户取消）
  const handleCityClose = () => {
    setCityPickerModal(false)
    // 即使取消城市选择，也检查是否需要显示进度提醒
    setTimeout(() => {
      checkAndShowRemindModal()
    }, 300)
  }

  useEffect(() => {
    const loadUnread = async () => {
      try {
        const token = Taro.getStorageSync('access_token')
        if (!token) {
          setHasNewMessage(false)
          return
        }
        // 使用封装好的 API 方法，确保正确添加认证 header
        const { messageApi } = await import('../../services/api')
        const res = await messageApi.getUnreadCount()
        const d = (res.data as any)?.data ?? res.data
        const count = d?.count ?? 0
        setHasNewMessage(count > 0)
      } catch (err) {
        // 401 错误表示未登录，不显示错误提示
        console.log('[首页] 获取未读消息数失败:', err)
        setHasNewMessage(false)
      }
    }
    loadUnread()
  }, [])

  useDidShow(() => setCityShort(getCityShortName()))

  // 原型 P02：AI施工验收 → P09；未设置开工日期则弹日期选择（7/15/30天）
  const handleAIConstruction = () => {
    const startDate = Taro.getStorageSync('construction_start_date')
    if (!startDate) {
      Taro.showActionSheet({
        itemList: ['7天后开工', '15天后开工', '30天后开工', '选择其他日期'],
        success: (res) => {
          if (res.tapIndex === 3) {
            safeSwitchTab(TAB_CONSTRUCTION, { defer: 150 })
            return
          }
          const days = [7, 15, 30][res.tapIndex]
          const d = new Date()
          d.setDate(d.getDate() + days)
          const dateStr = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
          Taro.setStorageSync('construction_start_date', dateStr)
          const token = Taro.getStorageSync('access_token')
          if (token) {
            import('../../services/api').then(({ constructionApi }) => {
              constructionApi.setStartDate(dateStr).catch(() => {})
            })
          }
          Taro.showToast({ title: '进度计划已更新', icon: 'success' })
          safeSwitchTab(TAB_CONSTRUCTION, { defer: 150 })
        },
        fail: () => {} // 用户取消不视为错误
      })
    } else {
      safeSwitchTab(TAB_CONSTRUCTION)
    }
  }

  const goToConstructionStage = (stageIndex: number) => {
    Taro.setStorageSync('construction_scroll_stage', stageIndex)
    safeSwitchTab(TAB_CONSTRUCTION)
  }

  const handleRemindAllow = () => {
    setRemindPermissionModal(false)
    try {
      if (typeof Taro.requestSubscribeMessage === 'function') {
        Taro.requestSubscribeMessage({
          tmplIds: [],
          entityIds: [],
          success: () => Taro.setStorageSync('remind_permission_granted', true),
          fail: () => {}
        }).catch(() => {})
      }
    } catch (_) {}
  }

  const handleRemindReject = () => {
    setRemindPermissionModal(false)
  }

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
            if (res.tapIndex === 0) handleUploadQuote()
            else if (res.tapIndex === 1) handleUploadContract()
          },
          fail: () => {} // 用户取消不视为错误
        })
        break
    }
  }

  return (
    <View className='index-page'>
      <View className='header'>
        <View
          className='city-entry'
          onClick={() => Taro.navigateTo({ url: '/pages/city-picker/index' })}
        >
          <Text className='city-entry-text'>{cityShort}</Text>
        </View>
        <Text className='title'>装修避坑管家</Text>
        <View className='message-icon' onClick={() => Taro.navigateTo({ url: '/pages/message/index' })}>
          <Text className='icon-text'>🔔</Text>
          {hasNewMessage && <View className='dot' />}
        </View>
      </View>

      <View className='swiper-container'>
        <Swiper
          className='swiper'
          indicatorDots
          indicatorColor='rgba(255,255,255,0.4)'
          indicatorActiveColor='#fff'
          autoplay
          interval={3000}
          circular
          current={currentIndex}
          onChange={(e) => setCurrentIndex(e.detail.current)}
        >
          {swiperList.map((item) => (
            <SwiperItem key={item.id}>
              <View className='swiper-item' onClick={() => handleSwiperClick(item.action)}>
                {USE_BANNER_IMAGES && item.image ? (
                  <Image src={item.image} className='swiper-img' mode='aspectFill' />
                ) : (
                  <View className='swiper-bg' />
                )}
                <View className='swiper-content'>
                  <Text className='swiper-title' style={{ color: '#FFD700' }}>{item.title}</Text>
                  <Text className='swiper-subtitle' style={{ color: '#FFEB3B' }}>{item.subtitle}</Text>
                </View>
              </View>
            </SwiperItem>
          ))}
        </Swiper>
      </View>

      {/* 原型 P02：核心功能4宫格 */}
      <View className='main-actions grid-four'>
        <View className='action-card' onClick={handleScanCompany}>
          <Text className='action-card-icon'>🏢</Text>
          <Text className='action-card-text'>装修公司检测</Text>
        </View>
        <View className='action-card' onClick={handleUploadQuote}>
          <Text className='action-card-icon'>💰</Text>
          <Text className='action-card-text'>装修报价分析</Text>
        </View>
        <View className='action-card' onClick={handleUploadContract}>
          <Text className='action-card-icon'>📜</Text>
          <Text className='action-card-text'>装修合同审核</Text>
        </View>
        <View className='action-card highlight' onClick={handleAIConstruction}>
          <Text className='action-card-icon'>🔍</Text>
          <Text className='action-card-text'>AI施工验收</Text>
          <Text className='action-card-hint'>6大阶段</Text>
        </View>
      </View>

      {/* 6大阶段快捷入口：横向滑动，点击直达 P09 对应阶段 */}
      <View className='section-label'><Text>6大阶段</Text></View>
      <ScrollView scrollX className='stage-quick-scroll' showScrollbar={false}>
        <View className='stage-quick-list'>
          {['S00材料', 'S01隐蔽', 'S02泥瓦', 'S03木工', 'S04油漆', 'S05收尾'].map((label, i) => (
            <View key={i} className='stage-quick-item' onClick={() => goToConstructionStage(i)}>
              <Text className='stage-quick-icon'>{['📦', '🔌', '🧱', '🪵', '🖌', '✅'][i]}</Text>
              <Text className='stage-quick-text'>{label}</Text>
            </View>
          ))}
        </View>
      </ScrollView>

      {/* 会员权益金卡 */}
      <View className='member-card' onClick={() => Taro.navigateTo({ url: '/pages/report-unlock/index' })}>
        <Text className='member-card-text'>6大阶段全报告解锁+无限次AI提醒</Text>
        <Text className='member-card-btn'>立即开通</Text>
      </View>

      {/* 装修小贴士 */}
      <Text className='tips-text'>本地装修行业规范实时更新，AI检测更精准</Text>

      <UploadConfirmModal
        visible={uploadModal.visible}
        type={uploadModal.type}
        onConfirm={(noMore) => handleUploadConfirm(noMore, uploadModal.url)}
        onGoScan={handleUploadGoScan}
        onClose={() => setUploadModal((m) => ({ ...m, visible: false }))}
      />

      {/* 城市选择弹窗：用户进入首页后首先弹出 */}
      <CityPickerModal
        visible={cityPickerModal}
        onConfirm={handleCityConfirm}
        onClose={handleCityClose}
      />

      {/* 进度+消息提醒权限请求弹窗：城市选择完成后弹出 */}
      {remindPermissionModal && (
        <View className='remind-permission-mask' onClick={handleRemindReject}>
          <View className='remind-permission-modal' onClick={(e) => e.stopPropagation()}>
            <Text className='remind-permission-title'>进度+消息提醒</Text>
            <Text className='remind-permission-desc'>开启后，6大阶段开始/验收前将为您推送微信服务通知，装修不遗漏</Text>
            <View className='remind-permission-btns'>
              <View className='remind-permission-btn reject' onClick={handleRemindReject}>
                <Text>拒绝</Text>
              </View>
              <View className='remind-permission-btn allow' onClick={handleRemindAllow}>
                <Text>允许</Text>
              </View>
            </View>
            <Text className='remind-permission-hint'>拒绝后可在【我的-设置】二次开启</Text>
          </View>
        </View>
      )}
    </View>
  )
}

export default Index

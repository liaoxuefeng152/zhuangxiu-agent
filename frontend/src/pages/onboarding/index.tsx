import React, { useState } from 'react'
import { View, Text, Swiper, SwiperItem, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { userApi } from '../../services/api'
import './index.scss'

/**
 * 引导页
 */
const Onboarding: React.FC = () => {
  const [current, setCurrent] = useState(0)

  // 引导页数据
  const slides = [
    {
      image: 'https://via.placeholder.com/375x667/1677FF/FFFFFF?text=Slide+1',
      title: '装修决策助手',
      subtitle: '智能检测装修公司风险，让装修更安心'
    },
    {
      image: 'https://via.placeholder.com/375x667/0958D9/FFFFFF?text=Slide+2',
      title: '报价单审核',
      subtitle: 'AI智能分析报价单，识别不合理收费'
    },
    {
      image: 'https://via.placeholder.com/375x667/40A9FF/FFFFFF?text=Slide+3',
      title: '合同风险识别',
      subtitle: '专业审核合同条款，规避法律风险'
    },
    {
      image: 'https://via.placeholder.com/375x667/69C0FF/FFFFFF?text=Slide+4',
      title: '施工陪伴',
      subtitle: '全程跟踪装修进度，确保按期交付'
    }
  ]

  // 微信登录
  const handleLogin = async () => {
    try {
      const res = await Taro.login()
      const result = await userApi.login(res.code)

      // 保存用户信息
      Taro.setStorageSync('access_token', result.access_token)
      Taro.setStorageSync('user_id', result.user_id)

      // 保存首次访问标记
      Taro.setStorageSync('has_onboarded', true)

      Taro.switchTab({
        url: '/pages/index/index'
      })
    } catch (error) {
      Taro.showToast({
        title: '登录失败',
        icon: 'none'
      })
    }
  }

  // 跳过引导
  const handleSkip = () => {
    Taro.setStorageSync('has_onboarded', true)
    Taro.switchTab({
      url: '/pages/index/index'
    })
  }

  return (
    <View className='onboarding-page'>
      <Swiper
        className='swiper'
        indicatorDots
        indicatorColor='rgba(255, 255, 255, 0.3)'
        indicatorActiveColor='#fff'
        current={current}
        onChange={(e) => setCurrent(e.detail.current)}
      >
        {slides.map((slide, index) => (
          <SwiperItem key={index}>
            <View className='slide'>
              <Image
                className='slide-image'
                src={slide.image}
                mode='aspectFill'
              />
              <View className='slide-content'>
                <Text className='slide-title'>{slide.title}</Text>
                <Text className='slide-subtitle'>{slide.subtitle}</Text>
              </View>
            </View>
          </SwiperItem>
        ))}
      </Swiper>

      {/* 底部按钮 */}
      <View className='footer'>
        {current === slides.length - 1 ? (
          <View className='btn primary' onClick={handleLogin}>
            <Text className='btn-text'>立即体验</Text>
          </View>
        ) : (
          <>
            <Text className='skip-btn' onClick={handleSkip}>跳过</Text>
          </>
        )}
      </View>
    </View>
  )
}

export default Onboarding

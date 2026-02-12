import React from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

/**
 * P20 设置页
 */
const SettingsPage: React.FC = () => {
  const nav = (url: string) => () => Taro.navigateTo({ url })
  const navToOnboarding = () => {
    Taro.removeStorageSync('onboarding_completed')
    Taro.removeStorageSync('has_onboarded')
    Taro.reLaunch({ url: '/pages/onboarding/index' })
  }

  return (
    <View className='settings-page'>
      <View className='section'>
        <View className='item' onClick={nav('/pages/neutral-statement/index')}>
          <Text>中立声明</Text>
          <Text className='arrow'>›</Text>
        </View>
        <View className='item' onClick={nav('/pages/account-notify/index')}>
          <Text>账户与通知</Text>
          <Text className='arrow'>›</Text>
        </View>
        <View className='item' onClick={nav('/pages/about/index')}>
          <Text>关于 & 帮助</Text>
          <Text className='arrow'>›</Text>
        </View>
        {/* V2.6.2优化：数据管理入口 */}
        <View className='item' onClick={nav('/pages/data-manage/index')}>
          <Text>数据管理</Text>
          <Text className='arrow'>›</Text>
        </View>
        {/* V2.6.2优化：回收站移至设置内 */}
        <View className='item' onClick={nav('/pages/recycle-bin/index')}>
          <Text>回收站（会员专属）</Text>
          <Text className='arrow'>›</Text>
        </View>
        <View className='item' onClick={nav('/pages/feedback/index')}>
          <Text>意见反馈</Text>
          <Text className='arrow'>›</Text>
        </View>
        <View className='item' onClick={nav('/pages/contact/index')}>
          <Text>联系客服</Text>
          <Text className='arrow'>›</Text>
        </View>
        <View className='item' onClick={navToOnboarding}>
          <Text>重新查看引导页</Text>
          <Text className='arrow'>›</Text>
        </View>
      </View>
    </View>
  )
}

export default SettingsPage

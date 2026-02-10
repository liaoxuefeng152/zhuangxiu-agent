import React from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { safeSwitchTab, TAB_HOME } from '../../utils/navigation'
import './index.scss'

/**
 * P33 网络异常页 - 全页面通用兜底
 * 网络断开/请求失败时跳转，支持重新加载/返回首页
 */
const NetworkErrorPage: React.FC = () => {
  const fromUrl = Taro.getCurrentInstance().router?.params?.from || ''

  const handleRetry = () => {
    Taro.getNetworkType({
      success: (res) => {
        if (res.networkType && res.networkType !== 'none') {
          if (fromUrl) {
            Taro.redirectTo({ url: decodeURIComponent(fromUrl) }).catch(() => {
              safeSwitchTab(TAB_HOME, { defer: 100 })
            })
          } else {
            safeSwitchTab(TAB_HOME, { defer: 100 })
          }
        } else {
          Taro.showToast({ title: '网络仍异常', icon: 'none' })
        }
      },
      fail: () => Taro.showToast({ title: '网络仍异常', icon: 'none' })
    })
  }

  const handleGoHome = () => {
    safeSwitchTab(TAB_HOME)
  }

  return (
    <View className='network-error-page'>
      <View className='icon-wrap'>
        <Text className='icon'>📶</Text>
      </View>
      <Text className='title'>网络连接异常</Text>
      <Text className='desc'>请检查网络设置后重新尝试</Text>
      <View className='btn-group'>
        <View className='btn primary' onClick={handleRetry}>
          <Text className='btn-text'>重新加载</Text>
        </View>
        <View className='btn secondary' onClick={handleGoHome}>
          <Text className='btn-text'>返回首页</Text>
        </View>
      </View>
    </View>
  )
}

export default NetworkErrorPage

import React from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

/**
 * P34 空数据页 - 通用占位
 */
interface EmptyStateProps {
  type?: 'report' | 'photo' | 'order' | 'message'
  text?: string
  actionText?: string
  actionUrl?: string
}

const DEFAULT: Record<string, { text: string; action: string; url: string }> = {
  report: { text: '暂无报告数据', action: '去检测', url: '/pages/company-scan/index' },
  photo: { text: '暂无施工照片', action: '去拍摄', url: '/pages/photo/index' },
  order: { text: '暂无订单', action: '去下单', url: '/pages/index/index' },
  message: { text: '暂无消息', action: '', url: '' }
}

const EmptyState: React.FC<EmptyStateProps> = ({ type = 'report', text, actionText, actionUrl }) => {
  const d = DEFAULT[type] || DEFAULT.report
  const displayText = text ?? d.text
  const btnText = actionText ?? d.action
  const btnUrl = actionUrl ?? d.url

  const handleAction = () => {
    if (btnUrl) Taro.navigateTo({ url: btnUrl })
  }

  return (
    <View className='empty-state'>
      <Text className='empty-icon'>📋</Text>
      <Text className='empty-text'>{displayText}</Text>
      {btnText && (
        <View className='empty-btn' onClick={handleAction}>
          <Text>{btnText}</Text>
        </View>
      )}
    </View>
  )
}

export default EmptyState

import React from 'react'
import { View, Text } from '@tarojs/components'
import './index.scss'

/**
 * P32 网络异常提示 - 覆盖层，点击重试
 */
interface Props {
  visible: boolean
  onRetry: () => void
}

const NetworkError: React.FC<Props> = ({ visible, onRetry }) => {
  if (!visible) return null

  return (
    <View className='network-error-mask'>
      <View className='network-error-content'>
        <Text className='error-icon'>📡</Text>
        <Text className='error-text'>网络异常，请检查网络后重试</Text>
        <View className='retry-btn' onClick={onRetry}>
          <Text>重试 / 刷新</Text>
        </View>
      </View>
    </View>
  )
}

export default NetworkError

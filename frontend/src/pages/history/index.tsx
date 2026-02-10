import React from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'

/**
 * 历史记录（公司/报价/合同）- 跳转至报告列表
 */
const HistoryPage: React.FC = () => {
  React.useEffect(() => {
    Taro.redirectTo({ url: '/pages/report-list/index' })
  }, [])
  return (
    <View style={{ padding: 24, textAlign: 'center' }}>
      <Text>跳转中...</Text>
    </View>
  )
}

export default HistoryPage

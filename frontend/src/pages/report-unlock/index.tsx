import React from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

/**
 * P28 报告解锁页 - 无返回按钮，仅右上角×关闭
 */
const ReportUnlockPage: React.FC = () => {
  const { type, scanId, name } = Taro.getCurrentInstance().router?.params || {}

  const navTo = (pkg: string) => {
    Taro.navigateTo({
      url: `/pages/payment/index?pkg=${pkg}&type=${type || 'report'}&scanId=${scanId || 0}&name=${encodeURIComponent(name || '')}`
    })
  }

  return (
    <View className='report-unlock-page'>
      <View className='content'>
        <Text className='title'>解锁完整报告</Text>
        <Text className='subtitle'>查看全部分析内容</Text>
        <View className='risk-tip'>
          <Text>⚠️ 未解锁可能遗漏关键风险信息</Text>
        </View>
        <View className='btns'>
          <View className='unlock-btn' onClick={() => navTo('single')}>
            <Text className='price'>单份解锁（9.9元）</Text>
            <Text className='desc'>解锁1份完整报告+PDF导出</Text>
          </View>
          <View className='unlock-btn highlight' onClick={() => navTo('triple')}>
            <Text className='price'>3份套餐（25元）</Text>
            <Text className='desc'>解锁3份+律师解读+7天客服</Text>
          </View>
        </View>
      </View>
    </View>
  )
}

export default ReportUnlockPage

import React, { useState } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

/**
 * P26 监理服务支付页
 */
const SupervisionPage: React.FC = () => {
  const [pkg, setPkg] = useState<'single' | 'triple'>('single')
  const price = pkg === 'single' ? 99 : 268

  const handlePay = () => {
    Taro.showModal({
      title: '支付确认',
      content: `服务内容：${pkg === 'single' ? '单次验收' : '全流程3次验收'}；价格：¥${price}；\n支付后未预约可全额退款，已预约取消扣30%手续费`,
      success: (res) => {
        if (res.confirm) {
          Taro.showToast({ title: '唤起支付...', icon: 'none' })
          setTimeout(() => Taro.navigateBack(), 1500)
        }
      }
    })
  }

  return (
    <View className='supervision-page'>
      <View className='section'>
        <Text className='section-title'>上门验收服务</Text>
        <Text className='section-desc'>专业监理师上门验收施工质量，出具验收报告，提供整改建议</Text>
        <View className='flow'>
          <Text>下单 → 预约时间 → 上门验收 → 出具报告</Text>
        </View>
      </View>

      <View className='price-section'>
        <View className={`option ${pkg === 'single' ? 'active' : ''}`} onClick={() => setPkg('single')}>
          <Text>单次验收 ¥99</Text>
        </View>
        <View className={`option ${pkg === 'triple' ? 'active' : ''}`} onClick={() => setPkg('triple')}>
          <Text>全流程3次验收 ¥268</Text>
        </View>
      </View>

      <View className='btn primary' onClick={handlePay}>
        <Text>立即支付 ¥{price}</Text>
      </View>

      <Text className='tip'>支付后1个工作日内安排监理师上门，服务覆盖全国大部分城市</Text>
      <Text className='refund'>支付后未预约可全额退款，已预约取消扣30%手续费</Text>
    </View>
  )
}

export default SupervisionPage

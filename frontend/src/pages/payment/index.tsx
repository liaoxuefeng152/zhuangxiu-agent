import React, { useState } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

/**
 * P28 完整报告解锁页
 */
const PaymentPage: React.FC = () => {
  const [pkg, setPkg] = useState<'single' | 'triple'>('single')
  const price = pkg === 'single' ? 9.9 : 25

  const { type, scanId, name } = Taro.getCurrentInstance().router?.params || {}

  const handleUnlock = () => {
    Taro.showModal({
      title: '支付确认',
      content: `解锁权益：详细风险分析、PDF导出、律师解读、1对1客服答疑；\n价格：¥${price}；\n一经解锁不支持退款，PDF导出永久有效`,
      success: (res) => {
        if (res.confirm) {
          const t = type || 'company'
          const sid = scanId || '0'
          Taro.setStorageSync(`report_unlocked_${t}_${sid}`, true)
          Taro.showToast({ title: '解锁成功', icon: 'success', duration: 2000 })
          setTimeout(() => {
            Taro.redirectTo({
              url: `/pages/report-detail/index?type=${t}&scanId=${sid}&name=${encodeURIComponent(name || '')}`
            })
          }, 1500)
        }
      }
    })
  }

  return (
    <View className='payment-page'>
      <View className='benefits'>
        <Text>✅ 详细风险分析及整改建议</Text>
        <Text>✅ 报告PDF导出权限</Text>
        <Text>✅ 专业律师解读（文字版）</Text>
        <Text>✅ 1对1客服答疑（7天内）</Text>
      </View>

      <View className='price-section'>
        <View className={`option ${pkg === 'single' ? 'active' : ''}`} onClick={() => setPkg('single')}>
          <Text>单份报告 ¥9.9</Text>
        </View>
        <View className={`option ${pkg === 'triple' ? 'active' : ''}`} onClick={() => setPkg('triple')}>
          <Text>3份报告 ¥25</Text>
          <Text className='save'>立省¥4.7</Text>
        </View>
      </View>

      <View className='btn primary' onClick={handleUnlock}>
        <Text>立即解锁 ¥{price}</Text>
      </View>

      <Text className='tip'>基础风控免费，扩展内容付费。一经解锁不支持退款，PDF导出永久有效</Text>
    </View>
  )
}

export default PaymentPage

import React, { useState } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { paymentApi } from '../../services/api'
import './index.scss'

/**
 * P26 监理服务支付页 - 创建监理订单后跳转支付页完成支付（P2 商业闭环）
 */
const SupervisionPage: React.FC = () => {
  const [pkg, setPkg] = useState<'single' | 'triple'>('single')
  const [loading, setLoading] = useState(false)
  const price = pkg === 'single' ? 99 : 268
  const orderType = pkg === 'single' ? 'supervision_single' : 'supervision_package'

  const handlePay = () => {
    Taro.showModal({
      title: '支付确认',
      content: `服务内容：${pkg === 'single' ? '单次验收' : '全流程3次验收'}；价格：¥${price}；\n支付后未预约可全额退款，已预约取消扣30%手续费`,
      success: async (res) => {
        if (!res.confirm) return
        setLoading(true)
        try {
          const r: any = await paymentApi.createOrder({ order_type: orderType })
          const d = r?.data ?? r
          const orderId = d?.order_id
          if (orderId && orderId > 0) {
            Taro.navigateTo({ url: `/pages/payment/index?order_id=${orderId}` })
          } else {
            Taro.showToast({ title: '创建订单失败', icon: 'none' })
          }
        } catch (e: any) {
          Taro.showToast({ title: e?.data?.detail || e?.message || '创建订单失败', icon: 'none' })
        } finally {
          setLoading(false)
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
        <Text>{loading ? '创建订单中...' : `立即支付 ¥${price}`}</Text>
      </View>

      <Text className='tip'>支付后1个工作日内安排监理师上门，服务覆盖全国大部分城市</Text>
      <Text className='refund'>支付后未预约可全额退款，已预约取消扣30%手续费</Text>
    </View>
  )
}

export default SupervisionPage

import React, { useState } from 'react'
import { View, Text, ScrollView, Picker } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

const REFUND_REASONS = ['不需要了', '报告不准确', '功能不符合预期', '其他原因']

/**
 * P34 退款申请页 - P25「申请退款」跳转
 */
const RefundPage: React.FC = () => {
  const [reason, setReason] = useState('')
  const [note, setNote] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const { orderId, amount, orderNo, used } = Taro.getCurrentInstance().router?.params || {}
  const amountYuan = amount ? (Number(amount) / 100).toFixed(2) : '0.00'

  React.useEffect(() => {
    if (used === '1') {
      Taro.showToast({ title: '已使用权益不可全额退款，将按比例扣除', icon: 'none', duration: 2500 })
    }
  }, [used])

  const canSubmit = !!reason.trim()

  const handleReasonChange = (e: any) => {
    const idx = e.detail?.value ?? 0
    setReason(REFUND_REASONS[idx] || '')
  }

  const handleSubmit = () => {
    if (!canSubmit || submitting) return
    setSubmitting(true)
    Taro.showLoading({ title: '提交中...' })
    // 实际应调用 paymentApi.refund(orderId, { reason, note })
    setTimeout(() => {
      Taro.hideLoading()
      setSubmitting(false)
      Taro.showToast({ title: '申请提交成功，1-3个工作日处理', icon: 'success' })
      Taro.navigateBack()
    }, 800)
  }

  return (
    <ScrollView scrollY className='refund-page'>
      <View className='section order-info'>
        <Text className='section-title'>订单信息</Text>
        <View className='info-row'>
          <Text className='label'>订单编号</Text>
          <Text className='value'>{orderNo || orderId || '-'}</Text>
        </View>
        <View className='info-row'>
          <Text className='label'>订单金额</Text>
          <Text className='value amount'>¥{amountYuan}</Text>
        </View>
        <Text className='hint'>7天无理由退款（未使用权益）</Text>
      </View>

      <View className='section'>
        <Text className='section-title'>退款原因</Text>
        <Picker mode='selector' range={REFUND_REASONS} onChange={handleReasonChange}>
          <View className='picker-wrap'>
            <Text className={reason ? 'value' : 'placeholder'}>{reason || '请选择退款原因'}</Text>
            <Text className='arrow'>›</Text>
          </View>
        </Picker>
      </View>

      <View className='section'>
        <Text className='section-title'>退款说明（选填）</Text>
        <textarea
          className='textarea'
          placeholder='请补充退款说明'
          value={note}
          onInput={(e: any) => setNote(e.detail?.value || '')}
          maxlength={200}
        />
      </View>

      <View className='submit-wrap'>
        <View
          className={`submit-btn ${canSubmit ? 'active' : ''}`}
          onClick={handleSubmit}
        >
          <Text className='btn-text'>提交申请</Text>
        </View>
      </View>
    </ScrollView>
  )
}

export default RefundPage

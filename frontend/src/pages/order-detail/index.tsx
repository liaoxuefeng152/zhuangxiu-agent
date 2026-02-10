import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { paymentApi } from '../../services/api'
import './index.scss'

/**
 * P19 订单详情页
 */
const OrderDetail: React.FC = () => {
  const [order, setOrder] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const id = (Taro.getCurrentInstance().router?.params?.id ?? '') as string

  useEffect(() => {
    if (!id) {
      setLoading(false)
      return
    }
    const load = async () => {
      try {
        const res = await paymentApi.getOrder(Number(id)) as any
        setOrder(res?.data ?? res ?? null)
      } catch {
        setOrder(null)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  const navTo = (url: string) => Taro.navigateTo({ url })

  const getStatusInfo = (o: any) => {
    const s = (o?.status ?? o?.pay_status ?? '').toLowerCase()
    if (s === 'pending' || s === '待支付' || s === 'unpaid') return { text: '待支付', color: '#FF4D4F' }
    if (s === 'paid' || s === '已支付') return { text: '已支付', color: '#52C41A' }
    if (s === 'done' || s === '已完成' || s === 'completed') return { text: '已完成', color: '#8C8C8C' }
    if (s === 'cancelled' || s === '已取消') return { text: '已取消', color: '#8C8C8C' }
    return { text: '待支付', color: '#FF4D4F' }
  }

  const handlePay = () => {
    if (!order) return
    Taro.showModal({
      title: '确认支付',
      content: `支付金额 ¥${((order.amount ?? order.price ?? 0) / 100).toFixed(2)}`,
      success: (res) => {
        if (res.confirm) {
          Taro.showToast({ title: '跳转支付...', icon: 'loading' })
          const orderId = order.id ?? order.order_id
          paymentApi.pay(orderId).then(() => {
            Taro.showToast({ title: '支付成功', icon: 'success' })
            setOrder((prev: any) => ({ ...prev, status: 'paid', pay_status: 'paid' }))
          }).catch(() => {
            Taro.showToast({ title: '支付失败', icon: 'none' })
          })
        }
      }
    })
  }

  if (loading) {
    return <View className='order-detail-page'><Text className='loading'>加载中...</Text></View>
  }

  if (!order) {
    return (
      <View className='order-detail-page'>
        <View className='empty-wrap'><Text>订单不存在</Text></View>
      </View>
    )
  }

  const status = getStatusInfo(order)
  const amount = ((order.amount ?? order.price ?? 0) / 100).toFixed(2)

  return (
    <ScrollView scrollY className='order-detail-page'>
      <View className='status-bar' style={{ background: status.color === '#FF4D4F' ? '#FFF1F0' : status.color === '#52C41A' ? '#F6FFED' : '#f5f5f5' }}>
        <Text className='status-text' style={{ color: status.color }}>{status.text}</Text>
      </View>

      <View className='section'>
        <View className='section-title'>订单信息</View>
        <View className='info-row'>
          <Text className='label'>订单编号</Text>
          <Text className='value'>{order.order_no ?? order.id ?? '-'}</Text>
        </View>
        <View className='info-row'>
          <Text className='label'>订单类型</Text>
          <Text className='value'>{order.order_type ?? order.type ?? '其他'}</Text>
        </View>
        <View className='info-row'>
          <Text className='label'>套餐/服务</Text>
          <Text className='value'>{order.package_name ?? order.product_name ?? '-'}</Text>
        </View>
        <View className='info-row'>
          <Text className='label'>订单金额</Text>
          <Text className='value amount'>¥{amount}</Text>
        </View>
        <View className='info-row'>
          <Text className='label'>创建时间</Text>
          <Text className='value'>{order.created_at ?? order.create_time ?? '-'}</Text>
        </View>
        {status.text === '已支付' || status.text === '已完成' ? (
          <View className='info-row'>
            <Text className='label'>支付时间</Text>
            <Text className='value'>{order.paid_at ?? order.pay_time ?? '-'}</Text>
          </View>
        ) : null}
      </View>

      <View className='section service-desc'>
        <View className='section-title'>服务说明</View>
        <Text className='desc-text'>报告解锁：解锁后可查看完整分析内容并导出PDF。监理服务：按套餐约定提供上门验收及报告。付费服务7天内有异议可申请退款。</Text>
      </View>

      <View className='action-bar'>
        {status.text === '待支付' && (
          <View className='pay-btn' onClick={handlePay}>
            <Text>立即支付</Text>
          </View>
        )}
        {(status.text === '已支付' || status.text === '已完成') && (
          <View
            className='refund-btn'
            onClick={() => navTo(`/pages/refund/index?orderId=${order.id ?? order.order_id}&amount=${order.amount ?? order.price ?? 0}&orderNo=${encodeURIComponent(order.order_no || '')}&used=0`)}
          >
            <Text>申请退款</Text>
          </View>
        )}
        <View className='consult-btn' onClick={() => navTo('/pages/contact/index')}>
          <Text>售后咨询</Text>
        </View>
      </View>
    </ScrollView>
  )
}

export default OrderDetail

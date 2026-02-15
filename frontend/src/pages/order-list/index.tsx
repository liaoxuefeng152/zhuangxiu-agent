import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getWithAuth } from '../../services/api'
import EmptyState from '../../components/EmptyState'
import './index.scss'

/**
 * P24/P25 订单列表页（V2.6.2优化：合并订单详情，支持下拉查看详情）
 */
const OrderList: React.FC = () => {
  const [typeFilter, setTypeFilter] = useState<'all' | 'report' | 'supervision'>('all')
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'paid' | 'done'>('all')
  const [orders, setOrders] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedOrderId, setExpandedOrderId] = useState<number | null>(null)  // V2.6.2优化：展开的订单ID
  const [selectedOrder, setSelectedOrder] = useState<any>(null)  // V2.6.2优化：选中的订单详情

  const loadOrders = async () => {
    setLoading(true)
    try {
      const res = await getWithAuth('/payments/orders', { page: 1, page_size: 50 }) as any
      let list = res?.list ?? res?.data ?? (Array.isArray(res) ? res : [])
      if (!Array.isArray(list)) list = []

      let filtered = list
      if (typeFilter !== 'all') {
        filtered = filtered.filter((o: any) => {
          const t = (o.order_type ?? o.type ?? '').toLowerCase()
          if (typeFilter === 'report') return t.includes('report') || t.includes('解锁') || t.includes('报告')
          if (typeFilter === 'supervision') return t.includes('supervision') || t.includes('监理')
          return true
        })
      }
      if (statusFilter !== 'all') {
        filtered = filtered.filter((o: any) => {
          const s = (o.status ?? o.pay_status ?? '').toLowerCase()
          if (statusFilter === 'pending') return s === 'pending' || s === '待支付' || s === 'unpaid'
          if (statusFilter === 'paid') return s === 'paid' || s === '已支付'
          if (statusFilter === 'done') return s === 'done' || s === '已完成' || s === 'completed'
          return true
        })
      }
      setOrders(filtered)
    } catch {
      setOrders([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadOrders()
  }, [typeFilter, statusFilter])

  const navTo = (url: string) => Taro.navigateTo({ url })

  const getStatusText = (o: any) => {
    const s = (o.status ?? o.pay_status ?? '').toLowerCase()
    if (s === 'pending' || s === '待支付' || s === 'unpaid') return { text: '待支付', color: '#FF4D4F' }
    if (s === 'paid' || s === '已支付') return { text: '已支付', color: '#52C41A' }
    if (s === 'done' || s === '已完成' || s === 'completed') return { text: '已完成', color: '#8C8C8C' }
    return { text: '待支付', color: '#FF4D4F' }
  }

  const getTypeText = (o: any) => {
    const t = (o.order_type ?? o.type ?? '').toLowerCase()
    if (t.includes('report') || t.includes('解锁') || t.includes('报告')) return '报告解锁'
    if (t.includes('supervision') || t.includes('监理')) return '监理服务'
    return '其他'
  }

  return (
    <View className='order-list-page'>
      <View className='filter-row'>
        <View className='filter-group'>
          <Text className={`filter-tab ${typeFilter === 'all' ? 'active' : ''}`} onClick={() => setTypeFilter('all')}>全部</Text>
          <Text className={`filter-tab ${typeFilter === 'report' ? 'active' : ''}`} onClick={() => setTypeFilter('report')}>报告解锁</Text>
          <Text className={`filter-tab ${typeFilter === 'supervision' ? 'active' : ''}`} onClick={() => setTypeFilter('supervision')}>监理服务</Text>
        </View>
        <View className='filter-group'>
          <Text className={`filter-tab ${statusFilter === 'all' ? 'active' : ''}`} onClick={() => setStatusFilter('all')}>全部</Text>
          <Text className={`filter-tab ${statusFilter === 'pending' ? 'active' : ''}`} onClick={() => setStatusFilter('pending')}>待支付</Text>
          <Text className={`filter-tab ${statusFilter === 'paid' ? 'active' : ''}`} onClick={() => setStatusFilter('paid')}>已支付</Text>
          <Text className={`filter-tab ${statusFilter === 'done' ? 'active' : ''}`} onClick={() => setStatusFilter('done')}>已完成</Text>
        </View>
      </View>

      {loading ? (
        <View className='loading-wrap'><Text>加载中...</Text></View>
      ) : orders.length === 0 ? (
        <EmptyState type='order' />
      ) : (
        <ScrollView scrollY className='order-list-outer'>
          <View className='order-list'>
          {orders.map((o) => {
            const status = getStatusText(o)
            return (
              <View key={o.id ?? o.order_id ?? Math.random()} className='order-item'>
                <View className='order-header'>
                  <Text className='order-no'>订单编号：{o.order_no ?? o.id ?? '-'}</Text>
                  <Text className='order-status' style={{ color: status.color }}>{status.text}</Text>
                </View>
                <View className='order-body'>
                  <Text className='order-type'>{getTypeText(o)}</Text>
                  <Text className='order-amount'>¥{(o.amount ?? o.price ?? 0) / 100}</Text>
                </View>
                <View className='order-footer'>
                  <Text className='order-time'>创建时间：{o.created_at ?? o.create_time ?? '-'}</Text>
                  <View className='order-actions'>
                    {/* V2.6.2优化：支持下拉查看详情，无需跳转 */}
                    <Text className='action-btn' onClick={async () => {
                      const orderId = o.id ?? o.order_id
                      if (expandedOrderId === orderId) {
                        setExpandedOrderId(null)
                        setSelectedOrder(null)
                      } else {
                        setExpandedOrderId(orderId)
                        // V2.6.2优化：加载订单详情
                        try {
                          const res = await getWithAuth(`/payments/order/${orderId}`) as any
                          setSelectedOrder(res ?? null)
                        } catch {
                          setSelectedOrder(null)
                        }
                      }
                    }}>
                      {expandedOrderId === o.id ? '收起' : '查看详情'}
                    </Text>
                    {status.text === '待支付' && (
                      <Text className='action-btn primary' onClick={() => navTo(`/pages/payment/index?order_id=${o.id ?? o.order_id}`)}>去支付</Text>
                    )}
                    <Text className='action-btn' onClick={() => navTo('/pages/contact/index')}>售后咨询</Text>
                  </View>
                </View>
                {/* V2.6.2优化：订单详情展开区域 */}
                {expandedOrderId === o.id && selectedOrder && (
                  <View className='order-detail-expanded'>
                    <View className='detail-section'>
                      <Text className='detail-label'>订单编号：</Text>
                      <Text className='detail-value'>{selectedOrder.order_no ?? o.order_no ?? '-'}</Text>
                    </View>
                    <View className='detail-section'>
                      <Text className='detail-label'>订单类型：</Text>
                      <Text className='detail-value'>{getTypeText(selectedOrder)}</Text>
                    </View>
                    <View className='detail-section'>
                      <Text className='detail-label'>订单金额：</Text>
                      <Text className='detail-value'>¥{((selectedOrder.amount ?? o.amount ?? 0) / 100).toFixed(2)}</Text>
                    </View>
                    <View className='detail-section'>
                      <Text className='detail-label'>订单状态：</Text>
                      <Text className='detail-value' style={{ color: status.color }}>{status.text}</Text>
                    </View>
                    {selectedOrder.created_at && (
                      <View className='detail-section'>
                        <Text className='detail-label'>创建时间：</Text>
                        <Text className='detail-value'>{selectedOrder.created_at}</Text>
                      </View>
                    )}
                    {selectedOrder.paid_at && (
                      <View className='detail-section'>
                        <Text className='detail-label'>支付时间：</Text>
                        <Text className='detail-value'>{selectedOrder.paid_at}</Text>
                      </View>
                    )}
                    {status.text === '待支付' && (
                      <View className='detail-actions'>
                        <Text className='action-btn primary' onClick={() => navTo(`/pages/payment/index?order_id=${o.id ?? o.order_id}`)}>立即支付</Text>
                        <Text className='action-btn' onClick={() => navTo('/pages/refund/index')}>申请退款</Text>
                      </View>
                    )}
                  </View>
                )}
              </View>
            )
          })}
          </View>
        </ScrollView>
      )}
    </View>
  )
}

export default OrderList

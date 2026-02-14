import React, { useState, useEffect } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { paymentApi } from '../../services/api'
import { useAppDispatch } from '../../store/hooks'
import { setUserInfo } from '../../store/slices/userSlice'
import { userApi } from '../../services/api'
import './index.scss'

const MEMBER_PRICES: Record<string, number> = {
  member_month: 29.9,
  member_season: 69.9,
  member_year: 268
}

const MEMBER_NAMES: Record<string, string> = {
  member_month: '月卡',
  member_season: '季卡',
  member_year: '年卡'
}

/**
 * P28 支付确认页 - 报告解锁（走订单+确认支付）/ 会员开通 / 订单去支付
 */
const PaymentPage: React.FC = () => {
  const router = Taro.getCurrentInstance().router?.params || {}
  const { type, scanId, name, stage, pkg: pkgParam, order_id, amount } = router
  const isReportUnlock = !!(type && scanId !== undefined && scanId !== '')
  const isMembership = !!(pkgParam && String(pkgParam).startsWith('member_'))
  const isOrderPay = !!(order_id && Number(order_id) > 0)
  const dispatch = useAppDispatch()

  const [loading, setLoading] = useState(false)
  const [orderAmount, setOrderAmount] = useState<number>(0)
  const [orderLoaded, setOrderLoaded] = useState(false)

  const reportPrice = 9.9
  const memberPkg = isMembership ? String(pkgParam).toLowerCase() : ''
  const memberPrice = MEMBER_PRICES[memberPkg] ?? 0
  const displayPrice = isReportUnlock ? reportPrice : isMembership ? memberPrice : orderAmount

  useEffect(() => {
    if (isOrderPay && order_id) {
      paymentApi.getOrder(Number(order_id))
        .then((res: any) => {
          const d = res?.data ?? res
          setOrderAmount(Number(d?.amount ?? 0))
          setOrderLoaded(true)
        })
        .catch(() => setOrderLoaded(true))
    } else {
      setOrderLoaded(true)
    }
  }, [isOrderPay, order_id])

  const redirectReport = (t: string, sid: string, isAcceptance: boolean, stageVal?: string) => {
    if (isAcceptance && stageVal) {
      Taro.redirectTo({ url: `/pages/acceptance/index?stage=${stageVal}` })
    } else {
      Taro.redirectTo({
        url: `/pages/report-detail/index?type=${t}&scanId=${sid}&name=${encodeURIComponent(name || '')}`
      })
    }
  }

  const handleReportUnlock = () => {
    const t = type || 'company'
    const sid = String(scanId || '0')
    const resourceId = Number(sid)
    if (!resourceId && t !== 'company') return
    setLoading(true)
    paymentApi.createOrder({
      order_type: 'report_single',
      resource_type: t,
      resource_id: resourceId
    })
      .then((res: any) => {
        const d = res?.data ?? res
        const status = d?.status
        const orderId = d?.order_id ?? 0
        if (status === 'completed' && orderId === 0) {
          Taro.setStorageSync(`report_unlocked_${t}_${sid}`, true)
          if (t === 'acceptance' && stage) Taro.setStorageSync(`report_unlocked_acceptance_${stage}`, true)
          Taro.showToast({ title: '已免费解锁（会员）', icon: 'success' })
          setTimeout(() => redirectReport(t, sid, t === 'acceptance', stage), 1200)
          return
        }
        setLoading(false)
        Taro.showModal({
          title: '支付确认',
          content: `解锁权益：详细风险分析、PDF导出、律师解读、1对1客服答疑；\n价格：¥${d?.amount ?? reportPrice}；\n一经解锁不支持退款，PDF导出永久有效`,
          success: (modalRes) => {
            if (modalRes.confirm && orderId > 0) {
              setLoading(true)
              paymentApi.confirmPaid(orderId)
                .then(() => {
                  Taro.setStorageSync(`report_unlocked_${t}_${sid}`, true)
                  if (t === 'acceptance' && stage) Taro.setStorageSync(`report_unlocked_acceptance_${stage}`, true)
                  Taro.showToast({ title: '解锁成功', icon: 'success', duration: 2000 })
                  setTimeout(() => redirectReport(t, sid, t === 'acceptance', stage), 1500)
                })
                .catch((err: any) => {
                  setLoading(false)
                  Taro.showToast({ title: err?.data?.detail || err?.message || '支付确认失败', icon: 'none' })
                })
            }
          }
        })
      })
      .catch((err: any) => {
        setLoading(false)
        const msg = err?.data?.detail ?? err?.message ?? '创建订单失败'
        Taro.showToast({ title: String(msg), icon: 'none' })
      })
  }

  const handleMembership = () => {
    const pkg = memberPkg || 'member_year'
    if (!MEMBER_PRICES[pkg]) return
    setLoading(true)
    paymentApi.createOrder({ order_type: pkg })
      .then((res: any) => {
        const d = res?.data ?? res
        const status = d?.status
        const orderId = d?.order_id ?? 0
        if (status === 'completed' && orderId === 0) {
          Taro.setStorageSync('is_member', true)
          Taro.showToast({ title: '已是会员', icon: 'success' })
          setTimeout(() => Taro.redirectTo({ url: '/pages/profile/index' }), 1200)
          return
        }
        setLoading(false)
        Taro.showModal({
          title: '开通会员',
          content: `确认开通${MEMBER_NAMES[pkg] || pkg}？¥${d?.amount ?? MEMBER_PRICES[pkg]}。支付后立即生效。`,
          success: (modalRes) => {
            if (modalRes.confirm && orderId > 0) {
              setLoading(true)
              paymentApi.confirmPaid(orderId)
                .then(() => {
                  Taro.setStorageSync('is_member', true)
                  userApi.getProfile().then((pr: any) => {
                    const u = pr?.data ?? pr
                    if (u?.user_id ?? u?.userId) {
                      dispatch(setUserInfo({
                        userId: u.user_id ?? u.userId,
                        openid: u.openid ?? '',
                        nickname: u.nickname ?? '装修用户',
                        avatarUrl: u.avatar_url ?? u.avatarUrl ?? '',
                        phone: u.phone ?? '',
                        phoneVerified: u.phone_verified ?? false,
                        isMember: true
                      }))
                    }
                  })
                  Taro.showToast({ title: '开通成功', icon: 'success', duration: 2000 })
                  setTimeout(() => Taro.redirectTo({ url: '/pages/profile/index' }), 1500)
                })
                .catch((err: any) => {
                  setLoading(false)
                  Taro.showToast({ title: err?.data?.detail || '支付确认失败', icon: 'none' })
                })
            }
          }
        })
      })
      .catch((err: any) => {
        setLoading(false)
        Taro.showToast({ title: err?.data?.detail ?? '创建订单失败', icon: 'none' })
      })
  }

  const handleOrderPay = () => {
    const oid = Number(order_id)
    if (!oid) return
    Taro.showModal({
      title: '支付确认',
      content: `确认支付 ¥${orderAmount}？`,
      success: (res) => {
        if (res.confirm) {
          setLoading(true)
          paymentApi.confirmPaid(oid)
            .then(() => {
              Taro.showToast({ title: '支付成功', icon: 'success' })
              setTimeout(() => Taro.redirectTo({ url: '/pages/order-list/index' }), 1500)
            })
            .catch((err: any) => {
              setLoading(false)
              Taro.showToast({ title: err?.data?.detail || '支付失败', icon: 'none' })
            })
        }
      }
    })
  }

  const handlePay = () => {
    if (loading) return
    if (isReportUnlock) return handleReportUnlock()
    if (isMembership) return handleMembership()
    if (isOrderPay) return handleOrderPay()
    Taro.showToast({ title: '参数错误', icon: 'none' })
  }

  const title = isReportUnlock ? '解锁本份报告' : isMembership ? `开通${MEMBER_NAMES[memberPkg] || '会员'}` : '订单支付'
  const btnText = isReportUnlock ? `立即解锁 ¥${displayPrice}` : isMembership ? `立即开通 ¥${displayPrice}` : `立即支付 ¥${displayPrice}`

  return (
    <View className='payment-page'>
      {isReportUnlock && (
        <View className='benefits'>
          <Text>✅ 详细风险分析及整改建议</Text>
          <Text>✅ 报告PDF导出权限</Text>
          <Text>✅ 专业律师解读（文字版）</Text>
          <Text>✅ 1对1客服答疑（7天内）</Text>
        </View>
      )}
      {isMembership && (
        <View className='benefits'>
          <Text>✅ 所有报告免费解锁</Text>
          <Text>✅ 6大阶段AI验收无限次</Text>
          <Text>✅ 会员专属客服</Text>
          <Text>✅ 数据回收站、PDF导出无限制</Text>
        </View>
      )}
      {isOrderPay && orderLoaded && (
        <View className='benefits'>
          <Text>订单号：{order_id}</Text>
          <Text>支付金额：¥{orderAmount}</Text>
        </View>
      )}

      {orderLoaded && !(isOrderPay && orderAmount <= 0) && (
        <>
          <View className='btn primary' onClick={handlePay}>
            <Text>{loading ? '处理中...' : btnText}</Text>
          </View>
          <Text className='tip'>
            {isReportUnlock && '基础风控免费，扩展内容付费。一经解锁不支持退款，PDF导出永久有效'}
            {isMembership && '会员开通后立即生效，支持7天无理由退款（未使用权益）'}
            {isOrderPay && '支付成功后订单状态将更新'}
          </Text>
        </>
      )}
    </View>
  )
}

export default PaymentPage

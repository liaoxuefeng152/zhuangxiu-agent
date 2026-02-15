import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useAppSelector } from '../../store/hooks'
import './index.scss'

const PACKAGES = [
  { id: 'month', name: '月卡', price: 29.9, months: 1, desc: '1个月有效期' },
  { id: 'season', name: '季卡', price: 69.9, months: 3, desc: '3个月有效期' },
  { id: 'year', name: '年卡', price: 199, months: 12, desc: '12个月有效期', tag: '性价比首选' }
]

const BENEFITS = [
  { icon: '📄', title: '所有报告免费解锁', desc: '公司/报价/合同/验收报告' },
  { icon: '✅', title: '6大阶段AI验收无限次', desc: '材料核对+5大工序验收' },
  { icon: '💬', title: '会员专属客服', desc: '优先接入人工' },
  { icon: '🗑️', title: '数据回收站', desc: '删除数据7天内可恢复' },
  { icon: '📤', title: 'PDF导出无限制', desc: '报告一键导出' }
]

/**
 * P26 会员权益页 - 会员状态、核心权益列表、套餐选择、开通/续费
 */
const MembershipPage: React.FC = () => {
  const userInfo = useAppSelector((s) => s.user.userInfo)
  const isLoggedIn = useAppSelector((s) => s.user.isLoggedIn)
  const [selectedPkg, setSelectedPkg] = useState('year')
  const [memberExpire, setMemberExpire] = useState('') // 后端可返回会员到期日

  const isMember = userInfo?.isMember ?? !!Taro.getStorageSync('is_member')

  useEffect(() => {
    const expire = userInfo?.memberExpire || Taro.getStorageSync('member_expire') || ''
    setMemberExpire(expire)
  }, [userInfo?.memberExpire])

  const handleOpenMember = (pkgId?: string) => {
    const pkg = PACKAGES.find((p) => p.id === (pkgId || selectedPkg)) || PACKAGES[2]
    Taro.showModal({
      title: '开通会员',
      content: `确认开通${pkg.name}？¥${pkg.price}，${pkg.desc}。支付后立即生效。`,
      confirmText: '去支付',
      success: (res) => {
        if (res.confirm) {
          Taro.showToast({ title: '唤起支付...', icon: 'none' })
          Taro.navigateTo({
            url: `/pages/payment/index?pkg=member_${pkg.id}&amount=${pkg.price}`
          })
        }
      }
    })
  }

  const handleBenefitClick = (title: string) => {
    if (title.includes('客服')) Taro.navigateTo({ url: '/pages/contact/index' })
    else Taro.showToast({ title: title, icon: 'none' })
  }

  return (
    <ScrollView scrollY className='membership-page-outer'>
      <View className='membership-page'>
      <View className='nav-bar'>
        <Text className='nav-back' onClick={() => Taro.navigateBack()}>返回</Text>
        <Text className='nav-title'>会员权益</Text>
        {!isMember && (
          <Text className='nav-btn' onClick={handleOpenMember}>开通会员</Text>
        )}
      </View>

      <View className='status-card'>
        {isMember ? (
          <>
            <View className='icon-wrap member'>👑</View>
            <Text className='status-title'>会员有效期至</Text>
            <Text className='status-desc'>{memberExpire || 'XXXX-XX-XX'}</Text>
            <Text className='status-remain'>剩余 {memberExpire ? Math.max(0, Math.ceil((new Date(memberExpire).getTime() - Date.now()) / 86400000)) : 0} 天</Text>
          </>
        ) : (
          <>
            <View className='icon-wrap normal'>👤</View>
            <Text className='status-title'>普通用户</Text>
            <Text className='status-desc'>立即开通会员，解锁全部权益</Text>
          </>
        )}
      </View>

      <View className='section'>
        <Text className='section-title'>核心权益</Text>
        {BENEFITS.map((b, i) => (
          <View key={i} className='benefit-row' onClick={() => handleBenefitClick(b.title)}>
            <Text className='benefit-icon'>{b.icon}</Text>
            <View className='benefit-content'>
              <Text className='benefit-title'>{b.title}</Text>
              <Text className='benefit-desc'>{b.desc}</Text>
            </View>
            <Text className='benefit-arrow'>›</Text>
          </View>
        ))}
      </View>

      <View className='section'>
        <Text className='section-title'>会员套餐</Text>
        <View className='package-list'>
          {PACKAGES.map((p) => (
            <View
              key={p.id}
              className={`package-card ${selectedPkg === p.id ? 'active' : ''} ${p.tag ? 'highlight' : ''}`}
              onClick={() => setSelectedPkg(p.id)}
            >
              {p.tag && <Text className='package-tag'>{p.tag}</Text>}
              <Text className='package-name'>{p.name}</Text>
              <Text className='package-price'>¥{p.price}</Text>
              <Text className='package-desc'>{p.desc}</Text>
              <View className='package-btn' onClick={(e) => { e.stopPropagation(); setSelectedPkg(p.id); handleOpenMember(p.id); }}>
                <Text>立即开通</Text>
              </View>
            </View>
          ))}
        </View>
      </View>

      <View className='open-wrap'>
        <View className='btn primary' onClick={handleOpenMember}>
          <Text>{isMember ? '续费会员' : '立即开通会员'}</Text>
        </View>
      </View>

      <Text className='footer-tip'>会员开通后立即生效，支持7天无理由退款（未使用权益）</Text>
      </View>
    </ScrollView>
  )
}

export default MembershipPage

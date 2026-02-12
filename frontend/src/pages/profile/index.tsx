import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useAppSelector, useAppDispatch } from '../../store/hooks'
import { setUserInfo, logout } from '../../store/slices/userSlice'
import { env } from '../../config/env'
import './index.scss'

/**
 * P10 我的页面 - 个人数据聚合
 */
const Profile: React.FC = () => {
  const dispatch = useAppDispatch()
  const userInfo = useAppSelector((state) => state.user.userInfo)
  const isLoggedIn = useAppSelector((state) => state.user.isLoggedIn)

  const [companyScans, setCompanyScans] = useState(0)
  const [quoteCount, setQuoteCount] = useState(0)
  const [contractCount, setContractCount] = useState(0)
  const [reports, setReports] = useState<{ type: string; list: any[] }[]>([])

  const loadUserInfo = async () => {
    try {
      const token = Taro.getStorageSync('access_token')
      if (!token) return
      const res = await Taro.request({
        url: `${env.apiBaseUrl}/users/profile`,
        method: 'GET',
        header: { Authorization: `Bearer ${token}` }
      })
      const u = (res.data as any)?.data ?? res.data
      if (u && (u.user_id ?? u.userId)) {
        dispatch(setUserInfo({
          userId: u.user_id ?? u.userId,
          openid: u.openid ?? '',
          nickname: u.nickname ?? '装修用户',
          avatarUrl: u.avatar_url ?? u.avatarUrl ?? '',
          phone: u.phone ?? '',
          phoneVerified: u.phone_verified ?? false,
          isMember: u.is_member ?? u.isMember ?? false
        }))
      }
    } catch {
      // 未登录忽略
    }
  }

  const loadStats = async () => {
    try {
      const token = Taro.getStorageSync('access_token')
      if (!token) return
      const base = env.apiBaseUrl
      const header = { Authorization: `Bearer ${token}` }
      const [s, q, c] = await Promise.all([
        Taro.request({ url: `${base}/companies/scans`, method: 'GET', header }).then((r) => r.data?.data ?? {}),
        Taro.request({ url: `${base}/quotes/list`, method: 'GET', header }).then((r) => r.data?.data ?? {}),
        Taro.request({ url: `${base}/contracts/list`, method: 'GET', header }).then((r) => r.data?.data ?? {})
      ])
      setCompanyScans(s?.total ?? 0)
      setQuoteCount(q?.total ?? 0)
      setContractCount(c?.total ?? 0)
    } catch {
      setCompanyScans(0)
      setQuoteCount(0)
      setContractCount(0)
    }
  }

  useEffect(() => {
    if (isLoggedIn) {
      loadUserInfo()
      loadStats()
    }
  }, [isLoggedIn])

  const handleLogin = async () => {
    Taro.showLoading({ title: '登录中...' })
    try {
      // H5：Taro.login 不可用，用模拟登录。小程序：使用微信 code 真实登录
      const taroEnv = typeof Taro !== 'undefined' ? Taro.getEnv() : ''
      let code: string
      if (taroEnv === 'h5') {
        code = 'dev_h5_mock'
      } else {
        const loginRes = await Taro.login()
        code = loginRes?.code || ''
      }
      if (!code) {
        Taro.hideLoading()
        Taro.showToast({ title: '获取登录凭证失败', icon: 'none' })
        return
      }
      const res = await Taro.request({
        url: `${env.apiBaseUrl}/users/login`,
        method: 'POST',
        header: { 'Content-Type': 'application/json' },
        data: { code }
      })
      Taro.hideLoading()
      const raw = res.data as any
      const d = raw?.data ?? raw
      const token = d?.access_token
      const userId = d?.user_id
      const statusOk = (res as any).statusCode >= 200 && (res as any).statusCode < 300
      if (token && userId && statusOk) {
        Taro.setStorageSync('access_token', token)
        Taro.setStorageSync('user_id', userId)
        Taro.setStorageSync('login_fresh_at', Date.now())
        dispatch(setUserInfo({
          userId,
          openid: d?.openid ?? '',
          nickname: d?.nickname ?? '装修用户',
          avatarUrl: d?.avatar_url ?? '',
          phone: '',
          phoneVerified: false,
          isMember: d?.is_member ?? false
        }))
        Taro.showToast({ title: '登录成功', icon: 'success' })
        loadUserInfo()
        loadStats()
      } else {
        const errRaw = raw ?? (res as any)?.data
        const errMsg = errRaw?.detail ?? errRaw?.msg ?? (typeof errRaw === 'string' ? errRaw : '登录失败')
        Taro.showToast({ title: typeof errMsg === 'string' ? errMsg : '登录失败', icon: 'none', duration: 3000 })
      }
    } catch (e: any) {
      Taro.hideLoading()
      const msg = e?.data?.detail ?? e?.data?.msg ?? e?.errMsg ?? e?.message ?? '登录失败，请检查网络或后端'
      Taro.showToast({ title: typeof msg === 'string' ? msg : '登录失败', icon: 'none', duration: 3000 })
    }
  }

  const handleLogout = () => {
    Taro.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          Taro.removeStorageSync('access_token')
          Taro.removeStorageSync('user_id')
          dispatch(logout())
          setCompanyScans(0)
          setQuoteCount(0)
          setContractCount(0)
          Taro.showToast({ title: '已退出登录', icon: 'success' })
        }
      }
    })
  }

  const navTo = (url: string) => Taro.navigateTo({ url })

  return (
    <ScrollView scrollY className='profile-page'>
      <View className='header-banner'>
        <Text className='my-equity' onClick={() => navTo('/pages/membership/index')}>我的权益</Text>
        {isLoggedIn ? (
          <>
            <View className='avatar-wrap' onClick={() => Taro.getUserProfile?.({ desc: '用于展示' }).then(() => {}).catch(() => {})}>
              <Text className='avatar-placeholder'>👤</Text>
            </View>
            <Text className='nickname'>{userInfo?.nickname || '装修用户'}</Text>
            <View className='member-badge'>
              {userInfo?.isMember ? '6大阶段全解锁会员（有效期至XXXX-XX-XX）' : '普通用户'}
            </View>
          </>
        ) : (
          <View className='login-cta'>
            <Text className='avatar-placeholder'>👤</Text>
            <Text className='login-text'>登录后查看更多信息</Text>
            <View className='login-btn' onClick={handleLogin}>
              <Text>立即登录</Text>
            </View>
          </View>
        )}
      </View>

      <View className='section'>
        {/* V2.6.2优化：合并报告列表和照片管理为"我的数据" */}
        <View className='folder-item' onClick={() => navTo('/pages/data-manage/index?tab=report')}>
          <Text className='folder-icon'>📁</Text>
          <Text className='folder-name'>我的数据</Text>
          <Text className='folder-desc'>报告/照片管理</Text>
          <Text className='arrow'>›</Text>
        </View>
        <View className='folder-item' onClick={() => navTo('/pages/order-list/index')}>
          <Text className='folder-icon'>📦</Text>
          <Text className='folder-name'>我的订单</Text>
          <Text className='arrow'>›</Text>
        </View>
        <View className='folder-item' onClick={() => navTo('/pages/calendar/index')}>
          <Text className='folder-icon'>📅</Text>
          <Text className='folder-name'>装修日历</Text>
          <Text className='arrow'>›</Text>
        </View>
        <View className='folder-item' onClick={() => navTo('/pages/contact/index')}>
          <Text className='folder-icon'>📞</Text>
          <Text className='folder-name'>专属客服</Text>
          <Text className='arrow'>›</Text>
        </View>
      </View>

      <View className='section'>
        <View className='folder-item' onClick={() => navTo('/pages/account-notify/index')}>
          <Text className='folder-icon'>⚙️</Text>
          <Text className='folder-name'>账户与通知设置</Text>
          <Text className='arrow'>›</Text>
        </View>
        <View className='folder-item' onClick={() => navTo('/pages/privacy/index')}>
          <Text className='folder-icon'>🔒</Text>
          <Text className='folder-name'>隐私保障</Text>
          <Text className='arrow'>›</Text>
        </View>
        <View className='folder-item' onClick={() => navTo('/pages/guide/index')}>
          <Text className='folder-icon'>📖</Text>
          <Text className='folder-name'>使用指南</Text>
          <Text className='arrow'>›</Text>
        </View>
        <View className='folder-item' onClick={() => navTo('/pages/about/index')}>
          <Text className='folder-icon'>ℹ️</Text>
          <Text className='folder-name'>关于&帮助</Text>
          <Text className='arrow'>›</Text>
        </View>
        <View className='folder-item' onClick={() => navTo('/pages/feedback/index')}>
          <Text className='folder-icon'>💬</Text>
          <Text className='folder-name'>意见反馈</Text>
          <Text className='arrow'>›</Text>
        </View>
      </View>

      {isLoggedIn && (
        <View className='logout-section'>
          <View className='logout-btn' onClick={handleLogout}>
            <Text>退出登录</Text>
          </View>
        </View>
      )}

      <View className='version-info'>
        <Text>版本 2.1.0</Text>
      </View>
    </ScrollView>
  )
}

export default Profile

import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { userApi } from '../../services/api'
import { useAppSelector, useAppDispatch } from "../../store/hooks"
import { logout } from "../../store/slices/userSlice"
import './index.scss'

/**
 * 我的页面
 */
const Profile: React.FC = () => {
  const dispatch = useAppDispatch()
  const userInfo = useAppSelector(state => state.user.userInfo)
  const isLoggedIn = useAppSelector(state => state.user.isLoggedIn)
  const [loading, setLoading] = useState(false)
  const [companyScans, setCompanyScans] = useState(0)
  const [quoteCount, setQuoteCount] = useState(0)
  const [contractCount, setContractCount] = useState(0)

  // 加载用户信息
  const loadUserInfo = async () => {
    try {
      const info = await userApi.getProfile()
      setUserInfo(info)
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  // 加载统计数据
  const loadStats = async () => {
    try {
      // 调用各模块的列表接口获取统计
      const [scans, quotes, contracts] = await Promise.all([
        userApi.getCompanyScans(),
        userApi.getQuotes(),
        userApi.getContracts()
      ])

      setCompanyScans(scans?.total || 0)
      setQuoteCount(quotes?.total || 0)
      setContractCount(contracts?.total || 0)
    } catch (error) {
      console.error('加载统计数据失败:', error)
    }
  }

  // 页面加载
  useEffect(() => {
    if (isLoggedIn) {
      loadUserInfo()
      loadStats()
    }
  }, [isLoggedIn])

  // 登录
  const handleLogin = async () => {
    try {
      const res = await Taro.login()
      const result = await userApi.login(res.code)

      // 保存用户信息
      Taro.setStorageSync('access_token', result.access_token)
      Taro.setStorageSync('user_id', result.user_id)
      setUserInfo(result)

      Taro.showToast({
        title: '登录成功',
        icon: 'success'
      })

      loadUserInfo()
      loadStats()
    } catch (error) {
      Taro.showToast({
        title: '登录失败',
        icon: 'none'
      })
    }
  }

  // 退出登录
  const handleLogout = () => {
    Taro.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          Taro.removeStorageSync('access_token')
          Taro.removeStorageSync('user_id')
          logout()
          setCompanyScans(0)
          setQuoteCount(0)
          setContractCount(0)

          Taro.showToast({
            title: '已退出登录',
            icon: 'success'
          })
        }
      }
    })
  }

  // 跳转到历史记录
  const navigateToHistory = (type: string) => {
    Taro.navigateTo({
      url: `/pages/history/index?type=${type}`
    })
  }

  // 跳转到设置
  const navigateToSettings = () => {
    Taro.navigateTo({
      url: '/pages/settings/index'
    })
  }

  // 跳转到会员中心
  const navigateToMembership = () => {
    Taro.navigateTo({
      url: '/pages/membership/index'
    })
  }

  // 联系客服
  const contactSupport = () => {
    Taro.makePhoneCall({
      phoneNumber: '400-xxx-xxxx'
    })
  }

  return (
    <ScrollView scrollY className='profile-page'>
      {/* 用户信息卡片 */}
      <View className='user-card'>
        {isLoggedIn ? (
          <>
            <Image
              className='avatar'
              src={userInfo?.avatar_url || 'https://via.placeholder.com/80'}
            />
            <View className='user-info'>
              <Text className='nickname'>{userInfo?.nickname || '装修用户'}</Text>
              <Text className='user-id'>
                ID: {userInfo?.user_id || '未登录'}
              </Text>
            </View>

            {userInfo?.is_member && (
              <View className='member-badge'>
                <Text className='member-text'>VIP会员</Text>
              </View>
            )}
          </>
        ) : (
          <View className='login-cta'>
            <Text className='login-text'>登录后查看更多信息</Text>
            <View className='login-btn' onClick={handleLogin}>
              <Text className='login-btn-text'>立即登录</Text>
            </View>
          </View>
        )}
      </View>

      {/* 统计数据 */}
      {isLoggedIn && (
        <View className='stats-section'>
          <View className='stat-item' onClick={() => navigateToHistory('company')}>
            <Text className='stat-value'>{companyScans}</Text>
            <Text className='stat-label'>公司检测</Text>
          </View>
          <View className='stat-divider'></View>
          <View className='stat-item' onClick={() => navigateToHistory('quote')}>
            <Text className='stat-value'>{quoteCount}</Text>
            <Text className='stat-label'>报价单</Text>
          </View>
          <View className='stat-divider'></View>
          <View className='stat-item' onClick={() => navigateToHistory('contract')}>
            <Text className='stat-value'>{contractCount}</Text>
            <Text className='stat-label'>合同审核</Text>
          </View>
        </View>
      )}

      {/* 功能菜单 */}
      <View className='menu-section'>
        {isLoggedIn && (
          <View className='menu-item' onClick={navigateToMembership}>
            <View className='menu-left'>
              <Text className='menu-icon'>👑</Text>
              <Text className='menu-title'>会员中心</Text>
            </View>
            <Text className='menu-arrow'>›</Text>
          </View>
        )}

        <View className='menu-item' onClick={() => navigateToHistory('company')}>
          <View className='menu-left'>
            <Text className='menu-icon'>🏢</Text>
            <Text className='menu-title'>检测历史</Text>
          </View>
          <Text className='menu-arrow'>›</Text>
        </View>

        <View className='menu-item' onClick={navigateToSettings}>
          <View className='menu-left'>
            <Text className='menu-icon'>⚙️</Text>
            <Text className='menu-title'>设置</Text>
          </View>
          <Text className='menu-arrow'>›</Text>
        </View>

        <View className='menu-item' onClick={contactSupport}>
          <View className='menu-left'>
            <Text className='menu-icon'>📞</Text>
            <Text className='menu-title'>联系客服</Text>
          </View>
          <Text className='menu-arrow'>›</Text>
        </View>

        <View className='menu-item'>
          <View className='menu-left'>
            <Text className='menu-icon'>📖</Text>
            <Text className='menu-title'>使用帮助</Text>
          </View>
          <Text className='menu-arrow'>›</Text>
        </View>

        <View className='menu-item'>
          <View className='menu-left'>
            <Text className='menu-icon'>ℹ️</Text>
            <Text className='menu-title'>关于我们</Text>
          </View>
          <Text className='menu-arrow'>›</Text>
        </View>
      </View>

      {/* 退出登录 */}
      {isLoggedIn && (
        <View className='logout-section'>
          <View className='logout-btn' onClick={handleLogout}>
            <Text className='logout-text'>退出登录</Text>
          </View>
        </View>
      )}

      {/* 版本信息 */}
      <View className='version-info'>
        <Text className='version-text'>版本 1.0.0</Text>
      </View>
    </ScrollView>
  )
}

export default Profile

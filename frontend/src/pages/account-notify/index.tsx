import React, { useState, useEffect } from 'react'
import { View, Text, Switch, Picker } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useAppDispatch, useAppSelector } from '../../store/hooks'
import { logout } from '../../store/slices/userSlice'
import './index.scss'

const REMIND_DAYS = [1, 2, 3, 5, 7]

/**
 * P19 账户与通知设置 - 账户块、提醒提前天数 1/2/3/5/7、红点开关、深色模式、清除缓存
 */
const AccountNotifyPage: React.FC = () => {
  const dispatch = useAppDispatch()
  const userInfo = useAppSelector((s) => s.user.userInfo)
  const [smartRemind, setSmartRemind] = useState(true)
  const [remindDays, setRemindDays] = useState(3)
  const [wechatNotify, setWechatNotify] = useState(true)
  const [redDotNotify, setRedDotNotify] = useState(true)
  const [darkMode, setDarkMode] = useState(false)
  const [autoCache, setAutoCache] = useState(true)

  useEffect(() => {
    const d = Taro.getStorageSync('remind_days')
    if (typeof d === 'number' && REMIND_DAYS.includes(d)) setRemindDays(d)
    const r = Taro.getStorageSync('smart_remind')
    if (typeof r === 'boolean') setSmartRemind(r)
  }, [])

  const handleRemindDays = (e: any) => {
    const v = REMIND_DAYS[Number(e.detail.value)] ?? 3
    setRemindDays(v)
    Taro.setStorageSync('remind_days', v)
    Taro.showToast({ title: '设置已更新', icon: 'success' })
  }

  const handleSwitch = (key: string, v: boolean) => {
    if (key === 'smart') {
      setSmartRemind(v)
      Taro.setStorageSync('smart_remind', v)
    } else if (key === 'wechat') setWechatNotify(v)
    else if (key === 'reddot') setRedDotNotify(v)
    else if (key === 'dark') setDarkMode(v)
    else if (key === 'cache') setAutoCache(v)
    Taro.showToast({ title: '设置已更新', icon: 'success' })
  }

  const handleClearCache = () => {
    try {
      const keys = ['no_upload_prompt', 'construction_scroll_stage']
      keys.forEach((k) => Taro.removeStorageSync(k))
      Taro.showToast({ title: '缓存已清除', icon: 'success' })
    } catch {
      Taro.showToast({ title: '清除失败', icon: 'none' })
    }
  }

  const handleLogout = () => {
    Taro.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (r) => {
        if (r.confirm) {
          Taro.removeStorageSync('access_token')
          Taro.removeStorageSync('user_id')
          dispatch(logout())
          Taro.showToast({ title: '已退出登录', icon: 'success' })
          Taro.reLaunch({ url: '/pages/onboarding/index' })
        }
      }
    })
  }

  const phone = userInfo?.phone || ''
  const phoneDisplay = phone ? `${phone.slice(0, 3)}****${phone.slice(-4)}` : ''

  return (
    <View className='account-notify-page'>
      <View className='section'>
        <Text className='section-title'>账户信息</Text>
        <View className='row'>
          <Text className='label'>头像/昵称</Text>
          <Text className='value' onClick={() => Taro.getUserProfile?.({ desc: '用于展示' }).catch(() => {})}>点击修改</Text>
        </View>
        <View className='row'>
          <Text className='label'>手机号</Text>
          <Text className='value'>{phone ? `已绑定：${phoneDisplay}` : '绑定手机号'}</Text>
        </View>
        <View className='row'>
          <Text className='label'>当前设备</Text>
          <Text className='value'>微信小程序</Text>
        </View>
        <View className='row'>
          <Text className='logout-btn' onClick={handleLogout}>退出登录</Text>
        </View>
      </View>

      <View className='section'>
        <Text className='section-title'>通知设置</Text>
        <View className='row switch'>
          <Text className='label'>智能提醒总开关</Text>
          <Switch checked={smartRemind} color='#007AFF' onChange={(e) => handleSwitch('smart', e.detail.value)} />
        </View>
        <View className='row'>
          <Text className='label'>提醒提前天数</Text>
          <Picker mode='selector' range={REMIND_DAYS} value={REMIND_DAYS.indexOf(remindDays)} onChange={handleRemindDays}>
            <Text className='value'>{remindDays} 天</Text>
          </Picker>
        </View>
        <View className='row switch'>
          <Text className='label'>微信服务通知</Text>
          <Switch checked={wechatNotify} color='#007AFF' onChange={(e) => handleSwitch('wechat', e.detail.value)} />
        </View>
        <View className='row switch'>
          <Text className='label'>小程序内红点提醒</Text>
          <Switch checked={redDotNotify} color='#007AFF' onChange={(e) => handleSwitch('reddot', e.detail.value)} />
        </View>
      </View>

      <View className='section'>
        <Text className='section-title'>其他设置</Text>
        <View className='row switch'>
          <Text className='label'>深色模式</Text>
          <Switch checked={darkMode} color='#007AFF' onChange={(e) => handleSwitch('dark', e.detail.value)} />
        </View>
        <View className='row switch'>
          <Text className='label'>自动缓存</Text>
          <Switch checked={autoCache} color='#007AFF' onChange={(e) => handleSwitch('cache', e.detail.value)} />
        </View>
        <View className='row'>
          <Text className='label'>清除缓存</Text>
          <Text className='link' onClick={handleClearCache}>清除</Text>
        </View>
      </View>
    </View>
  )
}

export default AccountNotifyPage

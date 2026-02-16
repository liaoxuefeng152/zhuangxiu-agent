import React, { useState, useEffect } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import dayjs from 'dayjs'
import { invitationsApi } from '../../services/api'
import './index.scss'

/**
 * P31 进度分享页 - 分享卡片预览 + 分享给好友/朋友圈 + 邀请好友功能（V2.6.8优化）
 */
const STAGES = ['材料进场', '隐蔽工程', '泥瓦工', '木工', '油漆', '安装收尾']

const ProgressSharePage: React.FC = () => {
  const [startDate, setStartDate] = useState('')
  const [progress, setProgress] = useState(0)
  const [customText, setCustomText] = useState('')
  const [endDate, setEndDate] = useState('')
  const [invitationData, setInvitationData] = useState<{
    invitationCode?: string
    invitationUrl?: string
    invitationText?: string
    availableEntitlements?: number
  }>({})

  useEffect(() => {
    const saved = Taro.getStorageSync('construction_start_date')
    const status = Taro.getStorageSync('construction_stage_status')
    if (saved) {
      setStartDate(saved)
      const statusObj = status ? JSON.parse(status) : {}
      const completed = Object.values(statusObj).filter((s) => s === 'completed').length
      setProgress(Math.round((completed / STAGES.length) * 100))
      const end = dayjs(saved).add(51, 'day')
      setEndDate(end.format('YYYY-MM-DD'))
    }

    // 加载邀请数据
    loadInvitationData()
  }, [])

  const loadInvitationData = async () => {
    try {
      // 获取邀请状态
      const statusRes = await invitationsApi.checkInvitationStatus()
      setInvitationData(prev => ({
        ...prev,
        availableEntitlements: statusRes.available_entitlements || 0
      }))
    } catch (error) {
      console.error('加载邀请数据失败:', error)
    }
  }

  const handleShareFriend = () => {
    Taro.showShareMenu({ withShareTicket: true })
    Taro.showToast({ title: '点击右上角分享给好友', icon: 'none' })
  }

  const handleShareTimeline = () => {
    Taro.showShareMenu({ withShareTicket: true })
    Taro.showToast({ title: '点击右上角分享到朋友圈', icon: 'none' })
  }

  const handleSaveImage = () => {
    Taro.showToast({ title: '长按卡片可保存图片', icon: 'none' })
  }

  const handleCreateInvitation = async () => {
    try {
      Taro.showLoading({ title: '生成邀请中...' })
      const res = await invitationsApi.createInvitation()
      setInvitationData({
        ...invitationData,
        invitationCode: res.invitation_code,
        invitationUrl: res.invitation_url,
        invitationText: res.invitation_text
      })
      
      Taro.hideLoading()
      Taro.showModal({
        title: '邀请已生成',
        content: '邀请链接和文案已生成，您可以分享给好友',
        showCancel: false,
        confirmText: '好的',
        success: () => {
          // 复制邀请文案到剪贴板
          if (res.invitation_text) {
            Taro.setClipboardData({
              data: res.invitation_text,
              success: () => {
                Taro.showToast({ title: '邀请文案已复制', icon: 'success' })
              }
            })
          }
        }
      })
    } catch (error: any) {
      Taro.hideLoading()
      Taro.showToast({
        title: error.message || '生成邀请失败',
        icon: 'none',
        duration: 2000
      })
    }
  }

  const handleCheckInvitationStatus = async () => {
    try {
      Taro.showLoading({ title: '加载中...' })
      const res = await invitationsApi.checkInvitationStatus()
      setInvitationData(prev => ({
        ...prev,
        availableEntitlements: res.available_entitlements || 0
      }))
      Taro.hideLoading()
      
      Taro.showModal({
        title: '邀请状态',
        content: `已成功邀请: ${res.successful_invites || 0}人\n待接受邀请: ${res.pending_invites || 0}人\n可用免费解锁: ${res.available_entitlements || 0}次`,
        showCancel: false,
        confirmText: '好的'
      })
    } catch (error: any) {
      Taro.hideLoading()
      Taro.showToast({
        title: error.message || '获取邀请状态失败',
        icon: 'none',
        duration: 2000
      })
    }
  }

  return (
    <View className='progress-share-page'>
      <Text className='page-title'>分享装修进度</Text>

      <View className='card-preview'>
        <View className='share-card'>
          <Text className='card-brand'>装修避坑管家</Text>
          <Text className='card-title'>施工进度</Text>
          <View className='progress-wrap'>
            <View className='progress-bar'>
              <View className='progress-fill' style={{ width: `${progress}%` }} />
            </View>
            <Text className='progress-text'>{progress}%</Text>
          </View>
          <Text className='card-stage'>{STAGES.slice(0, Math.ceil((progress / 100) * 6) || 1).join(' → ')}</Text>
          <Text className='card-date'>预计完工：{endDate || '-'}</Text>
          {customText ? <Text className='card-custom'>{customText}</Text> : null}
        </View>
      </View>

      <View className='share-btns'>
        <View className='share-btn' onClick={handleShareFriend}>
          <Text className='btn-icon'>👤</Text>
          <Text className='btn-text'>分享给好友</Text>
        </View>
        <View className='share-btn' onClick={handleShareTimeline}>
          <Text className='btn-icon'>⭕</Text>
          <Text className='btn-text'>分享到朋友圈</Text>
        </View>
      </View>

      <View className='invite-block'>
        <Text className='invite-title'>邀请好友得1次免费报告解锁</Text>
        <Text className='invite-desc'>邀请1人注册并登录，您将获得1次免费解锁任意报告权益（有效期30天）</Text>
        
        {invitationData.availableEntitlements !== undefined && invitationData.availableEntitlements > 0 && (
          <View className='entitlement-badge'>
            <Text className='entitlement-text'>🎁 您有 {invitationData.availableEntitlements} 次免费解锁可用</Text>
          </View>
        )}

        <View className='invite-actions'>
          <View className='invite-btn primary' onClick={handleCreateInvitation}>
            <Text>生成邀请链接</Text>
          </View>
          <View className='invite-btn secondary' onClick={handleCheckInvitationStatus}>
            <Text>查看邀请状态</Text>
          </View>
        </View>

        {invitationData.invitationText && (
          <View className='invite-info'>
            <Text className='invite-info-title'>您的邀请码: {invitationData.invitationCode}</Text>
            <Text className='invite-info-text'>{invitationData.invitationText}</Text>
          </View>
        )}
      </View>

      <Text className='save-hint' onClick={handleSaveImage}>长按上方卡片可保存至相册</Text>
    </View>
  )
}

export default ProgressSharePage

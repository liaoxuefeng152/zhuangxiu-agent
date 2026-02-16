import React, { useState, useEffect } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { invitationsApi } from '../../services/api'
import './index.scss'

/**
 * P33 邀请好友页面 - 专门的邀请功能页面（V2.6.8新增）
 * 解决从报告分享页跳转到进度分享页的困惑问题
 */
const InvitationPage: React.FC = () => {
  const [invitationData, setInvitationData] = useState<{
    invitationCode?: string
    invitationUrl?: string
    invitationText?: string
    availableEntitlements?: number
    successfulInvites?: number
    pendingInvites?: number
  }>({})

  useEffect(() => {
    // 加载邀请数据
    loadInvitationData()
  }, [])

  const loadInvitationData = async () => {
    try {
      // 获取邀请状态
      const statusRes = await invitationsApi.checkInvitationStatus()
      setInvitationData({
        availableEntitlements: statusRes.available_entitlements || 0,
        successfulInvites: statusRes.successful_invites || 0,
        pendingInvites: statusRes.pending_invites || 0
      })
    } catch (error) {
      console.error('加载邀请数据失败:', error)
    }
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
      setInvitationData({
        availableEntitlements: res.available_entitlements || 0,
        successfulInvites: res.successful_invites || 0,
        pendingInvites: res.pending_invites || 0
      })
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

  const handleShareFriend = () => {
    if (!invitationData.invitationText) {
      Taro.showToast({ 
        title: '请先生成邀请链接', 
        icon: 'none',
        duration: 2000
      })
      return
    }
    
    Taro.showShareMenu({ withShareTicket: true })
    Taro.showToast({ 
      title: '点击右上角分享给好友', 
      icon: 'none',
      duration: 2000
    })
  }

  const handleCopyInvitationText = () => {
    if (!invitationData.invitationText) {
      Taro.showToast({ 
        title: '请先生成邀请链接', 
        icon: 'none',
        duration: 2000
      })
      return
    }
    
    Taro.setClipboardData({
      data: invitationData.invitationText,
      success: () => {
        Taro.showToast({ title: '邀请文案已复制', icon: 'success' })
      }
    })
  }

  const handleCopyInvitationCode = () => {
    if (!invitationData.invitationCode) {
      Taro.showToast({ 
        title: '请先生成邀请链接', 
        icon: 'none',
        duration: 2000
      })
      return
    }
    
    Taro.setClipboardData({
      data: invitationData.invitationCode,
      success: () => {
        Taro.showToast({ title: '邀请码已复制', icon: 'success' })
      }
    })
  }

  return (
    <View className='invitation-page'>
      <Text className='page-title'>邀请好友得免费报告</Text>
      
      <View className='reward-card'>
        <Text className='reward-title'>🎁 邀请奖励</Text>
        <Text className='reward-desc'>邀请1位好友注册并登录，您将获得：</Text>
        <View className='reward-item'>
          <Text className='reward-icon'>✅</Text>
          <Text className='reward-text'>1次免费解锁任意报告权益</Text>
        </View>
        <View className='reward-item'>
          <Text className='reward-icon'>✅</Text>
          <Text className='reward-text'>权益有效期30天</Text>
        </View>
        <View className='reward-item'>
          <Text className='reward-icon'>✅</Text>
          <Text className='reward-text'>好友也可获得新人福利</Text>
        </View>
      </View>

      <View className='stats-card'>
        <Text className='stats-title'>我的邀请统计</Text>
        <View className='stats-grid'>
          <View className='stat-item'>
            <Text className='stat-value'>{invitationData.successfulInvites || 0}</Text>
            <Text className='stat-label'>成功邀请</Text>
          </View>
          <View className='stat-item'>
            <Text className='stat-value'>{invitationData.pendingInvites || 0}</Text>
            <Text className='stat-label'>待接受</Text>
          </View>
          <View className='stat-item'>
            <Text className='stat-value'>{invitationData.availableEntitlements || 0}</Text>
            <Text className='stat-label'>可用解锁</Text>
          </View>
        </View>
      </View>

      <View className='invitation-actions'>
        <View className='action-btn primary' onClick={handleCreateInvitation}>
          <Text className='action-btn-text'>生成邀请链接</Text>
          <Text className='action-btn-desc'>创建专属邀请链接和邀请码</Text>
        </View>
        
        <View className='action-btn secondary' onClick={handleCheckInvitationStatus}>
          <Text className='action-btn-text'>刷新邀请状态</Text>
          <Text className='action-btn-desc'>查看最新邀请统计</Text>
        </View>
      </View>

      {invitationData.invitationCode && (
        <View className='invitation-info'>
          <Text className='info-title'>您的邀请信息</Text>
          
          <View className='info-item'>
            <Text className='info-label'>邀请码：</Text>
            <Text className='info-value'>{invitationData.invitationCode}</Text>
            <Text className='info-copy' onClick={handleCopyInvitationCode}>复制</Text>
          </View>
          
          <View className='info-item'>
            <Text className='info-label'>邀请链接：</Text>
            <Text className='info-value link' onClick={() => {
              if (invitationData.invitationUrl) {
                Taro.setClipboardData({
                  data: invitationData.invitationUrl,
                  success: () => {
                    Taro.showToast({ title: '链接已复制', icon: 'success' })
                  }
                })
              }
            }}>
              {invitationData.invitationUrl ? '点击复制邀请链接' : '未生成'}
            </Text>
          </View>
          
          <View className='share-actions'>
            <View className='share-btn' onClick={handleShareFriend}>
              <Text className='share-icon'>👤</Text>
              <Text className='share-text'>分享给好友</Text>
            </View>
            <View className='share-btn' onClick={handleCopyInvitationText}>
              <Text className='share-icon'>📋</Text>
              <Text className='share-text'>复制邀请文案</Text>
            </View>
          </View>
        </View>
      )}

      <View className='invitation-guide'>
        <Text className='guide-title'>📝 邀请指南</Text>
        <View className='guide-step'>
          <Text className='step-number'>1</Text>
          <Text className='step-text'>点击"生成邀请链接"创建您的专属邀请</Text>
        </View>
        <View className='guide-step'>
          <Text className='step-number'>2</Text>
          <Text className='step-text'>将邀请链接或邀请码分享给好友</Text>
        </View>
        <View className='guide-step'>
          <Text className='step-number'>3</Text>
          <Text className='step-text'>好友通过您的链接注册并登录</Text>
        </View>
        <View className='guide-step'>
          <Text className='step-number'>4</Text>
          <Text className='step-text'>您将获得1次免费解锁任意报告的权益</Text>
        </View>
      </View>
    </View>
  )
}

export default InvitationPage

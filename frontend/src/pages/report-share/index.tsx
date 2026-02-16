import React, { useState, useEffect, useRef } from 'react'
import { View, Text, Image } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import { useAppDispatch } from '../../store/hooks'
import { updateUserInfo } from '../../store/slices/userSlice'
import { pointsApi, userApi } from '../../services/api'
import './index.scss'

/**
 * P32 报告分享页 - 分享报告卡片预览 + 分享给好友/朋友圈
 * V2.6.7新增：分享成功后获得积分奖励
 */
const STAGE_TITLES: Record<string, string> = {
  material: 'S00材料进场核对台账',
  plumbing: '水电阶段验收报告',
  carpentry: '泥瓦工阶段验收报告',
  woodwork: '木工阶段验收报告',
  painting: '油漆阶段验收报告',
  flooring: '地板阶段验收报告',
  soft_furnishing: '软装阶段验收报告',
  installation: '安装收尾阶段验收报告'
}

const ReportSharePage: React.FC = () => {
  const dispatch = useAppDispatch()
  const router = Taro.getCurrentInstance().router
  const stage = router?.params?.stage || 'plumbing'
  const analysisId = router?.params?.id ? Number(router.params.id) : undefined
  const reportTitle = STAGE_TITLES[stage] || '验收报告'
  
  const [shareRewarded, setShareRewarded] = useState(false)
  const isFirstLoad = useRef(true)
  const hasCheckedReward = useRef(false)

  // 配置页面分享
  useEffect(() => {
    // 设置页面分享配置
    Taro.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
  }, [])

  // 检测用户从分享返回，发放积分
  useDidShow(() => {
    // 首次加载不检查（避免页面刚打开就触发）
    if (isFirstLoad.current) {
      isFirstLoad.current = false
      return
    }

    // 如果已经检查过奖励，不再重复检查
    if (hasCheckedReward.current || shareRewarded) {
      return
    }

    // 用户从分享返回，尝试发放积分
    handleShareReward()
  })

  // 发放分享积分
  const handleShareReward = async () => {
    if (shareRewarded || hasCheckedReward.current) {
      return
    }
    
    hasCheckedReward.current = true
    
    try {
      const res = await pointsApi.shareReward('report', 'acceptance', analysisId)
      const data = res?.data ?? res
      
      if (data.already_rewarded) {
        setShareRewarded(true)
        Taro.showToast({ 
          title: '今日已获得分享奖励', 
          icon: 'none',
          duration: 2000
        })
      } else if (data.reward_points > 0) {
        setShareRewarded(true)
        Taro.showToast({ 
          title: `分享成功，获得${data.reward_points}积分！`, 
          icon: 'success',
          duration: 2000
        })
        // 刷新用户信息（更新积分）
        try {
          const userRes = await userApi.getProfile()
          const userData = userRes?.data ?? userRes
          if (userData?.points !== undefined) {
            dispatch(updateUserInfo({ points: userData.points }))
          }
        } catch (error) {
          console.error('刷新用户信息失败:', error)
        }
      }
    } catch (error: any) {
      console.error('分享奖励失败:', error)
      // 静默失败，不影响分享体验
      hasCheckedReward.current = false // 失败后允许重试
    }
  }

  // 分享给好友
  const handleShareFriend = () => {
    Taro.showShareMenu({ withShareTicket: true })
    Taro.showToast({ 
      title: '点击右上角分享给好友', 
      icon: 'none',
      duration: 2000
    })
  }

  // 分享到朋友圈
  const handleShareTimeline = () => {
    Taro.showShareMenu({ withShareTicket: true })
    Taro.showToast({ 
      title: '点击右上角分享到朋友圈', 
      icon: 'none',
      duration: 2000
    })
  }

  return (
    <View className='report-share-page'>
      <Text className='page-title'>分享{reportTitle}</Text>

      <View className='card-preview'>
        <View className='share-card'>
          <Text className='card-brand'>装修避坑管家</Text>
          <Text className='card-title'>{reportTitle}</Text>
          <View className='card-content'>
            <Text className='card-desc'>专业的装修验收报告</Text>
            <Text className='card-hint'>分享给好友，一起避坑</Text>
          </View>
          {shareRewarded && (
            <View className='reward-badge'>
              <Text className='reward-text'>✓ 已获得10积分</Text>
            </View>
          )}
        </View>
      </View>

      <View className='share-btns'>
        <View className='share-btn' onClick={handleShareFriend}>
          <Text className='btn-icon'>👤</Text>
          <Text className='btn-text'>分享给好友</Text>
          <Text className='btn-hint'>+10积分</Text>
        </View>
        <View className='share-btn' onClick={handleShareTimeline}>
          <Text className='btn-icon'>⭕</Text>
          <Text className='btn-text'>分享到朋友圈</Text>
          <Text className='btn-hint'>+10积分</Text>
        </View>
      </View>

      <View className='invite-block'>
        <Text className='invite-title'>分享报告得积分</Text>
        <Text className='invite-desc'>分享报告给好友或朋友圈，每次可获得10积分奖励（每日限1次）</Text>
      </View>
    </View>
  )
}


// 分享给好友
export const onShareAppMessage = (res: any) => {
  const router = Taro.getCurrentInstance().router
  const stage = router?.params?.stage || 'plumbing'
  const analysisId = router?.params?.id
  
  return {
    title: `我的${STAGE_TITLES[stage] || '验收报告'} - 装修避坑管家`,
    path: `/pages/acceptance/index?stage=${stage}${analysisId ? `&id=${analysisId}` : ''}`,
    imageUrl: '' // 可以设置分享图片
  }
}

// 分享到朋友圈
export const onShareTimeline = () => {
  const router = Taro.getCurrentInstance().router
  const stage = router?.params?.stage || 'plumbing'
  
  return {
    title: `我的${STAGE_TITLES[stage] || '验收报告'} - 装修避坑管家`,
    imageUrl: '' // 可以设置分享图片
  }
}

export default ReportSharePage

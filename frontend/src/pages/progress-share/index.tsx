import React, { useState, useEffect } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import dayjs from 'dayjs'
import './index.scss'

/**
 * P31 进度分享页 - 专注于分享施工进度（V2.6.8重构：移除邀请功能，专注进度分享）
 */
const STAGES = ['材料进场', '隐蔽工程', '泥瓦工', '木工', '油漆', '安装收尾']
const STAGE_DESCRIPTIONS: Record<string, string> = {
  '材料进场': '核对材料规格品牌，确保符合合同要求',
  '隐蔽工程': '水电管线预埋，验收合格后封闭',
  '泥瓦工': '墙面地面找平，瓷砖铺贴',
  '木工': '吊顶、柜体、门窗套制作安装',
  '油漆': '墙面涂料、木器漆施工',
  '安装收尾': '灯具、洁具、五金安装，保洁收尾'
}

const ProgressSharePage: React.FC = () => {
  const [startDate, setStartDate] = useState('')
  const [progress, setProgress] = useState(0)
  const [currentStage, setCurrentStage] = useState('')
  const [endDate, setEndDate] = useState('')
  const [stageDetails, setStageDetails] = useState<Array<{name: string, status: string, description: string}>>([])

  useEffect(() => {
    // 从本地存储加载施工进度数据
    const saved = Taro.getStorageSync('construction_start_date')
    const status = Taro.getStorageSync('construction_stage_status')
    
    if (saved) {
      setStartDate(saved)
      
      // 解析阶段状态
      const statusObj = status ? JSON.parse(status) : {}
      const completed = Object.values(statusObj).filter((s) => s === 'completed').length
      const progressValue = Math.round((completed / STAGES.length) * 100)
      setProgress(progressValue)
      
      // 计算预计完工日期（假设总工期51天）
      const end = dayjs(saved).add(51, 'day')
      setEndDate(end.format('YYYY-MM-DD'))
      
      // 确定当前阶段
      const currentIndex = Math.min(Math.ceil((progressValue / 100) * STAGES.length), STAGES.length - 1)
      setCurrentStage(STAGES[currentIndex])
      
      // 构建阶段详情
      const details = STAGES.map((stage, index) => ({
        name: stage,
        status: index < completed ? 'completed' : (index === completed ? 'in-progress' : 'pending'),
        description: STAGE_DESCRIPTIONS[stage] || ''
      }))
      setStageDetails(details)
    }
  }, [])

  const handleShareFriend = () => {
    Taro.showShareMenu({ withShareTicket: true })
    Taro.showToast({ 
      title: '点击右上角分享给好友', 
      icon: 'none',
      duration: 2000
    })
  }

  const handleShareTimeline = () => {
    Taro.showShareMenu({ withShareTicket: true })
    Taro.showToast({ 
      title: '点击右上角分享到朋友圈', 
      icon: 'none',
      duration: 2000
    })
  }

  const handleSaveImage = () => {
    Taro.showToast({ 
      title: '长按卡片可保存图片', 
      icon: 'none',
      duration: 2000
    })
  }

  const handleViewDetails = () => {
    Taro.navigateTo({ url: '/pages/construction/index' })
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
          
          <Text className='card-stage'>当前阶段：{currentStage || '未开始'}</Text>
          <Text className='card-date'>开工日期：{startDate || '未设置'}</Text>
          <Text className='card-date'>预计完工：{endDate || '-'}</Text>
          
          {progress > 0 && (
            <View className='stage-summary'>
              <Text className='stage-summary-title'>已完成阶段：</Text>
              {stageDetails
                .filter(stage => stage.status === 'completed')
                .map((stage, index) => (
                  <Text key={index} className='stage-item'>✓ {stage.name}</Text>
                ))}
            </View>
          )}
        </View>
      </View>

      <View className='share-btns'>
        <View className='share-btn' onClick={handleShareFriend}>
          <Text className='btn-icon'>👤</Text>
          <Text className='btn-text'>分享给好友</Text>
          <Text className='btn-hint'>分享进度</Text>
        </View>
        <View className='share-btn' onClick={handleShareTimeline}>
          <Text className='btn-icon'>⭕</Text>
          <Text className='btn-text'>分享到朋友圈</Text>
          <Text className='btn-hint'>记录装修</Text>
        </View>
      </View>

      <View className='progress-details'>
        <Text className='details-title'>施工进度详情</Text>
        
        {stageDetails.length > 0 ? (
          <View className='stages-list'>
            {stageDetails.map((stage, index) => (
              <View key={index} className={`stage-item ${stage.status}`}>
                <View className='stage-header'>
                  <Text className='stage-index'>{index + 1}</Text>
                  <Text className='stage-name'>{stage.name}</Text>
                  <Text className={`stage-status ${stage.status}`}>
                    {stage.status === 'completed' ? '✓ 已完成' : 
                     stage.status === 'in-progress' ? '▶ 进行中' : '○ 待开始'}
                  </Text>
                </View>
                <Text className='stage-desc'>{stage.description}</Text>
              </View>
            ))}
          </View>
        ) : (
          <View className='empty-state'>
            <Text className='empty-text'>暂无施工进度数据</Text>
            <Text className='empty-hint'>请在施工陪伴页设置开工日期</Text>
            <View className='empty-btn' onClick={handleViewDetails}>
              <Text>去设置开工日期 →</Text>
            </View>
          </View>
        )}
      </View>

      <View className='share-tips'>
        <Text className='tips-title'>分享小贴士</Text>
        <Text className='tips-item'>• 分享给家人朋友，一起监督装修进度</Text>
        <Text className='tips-item'>• 记录每个阶段的完成情况</Text>
        <Text className='tips-item'>• 保存进度卡片，留作装修纪念</Text>
      </View>

      <Text className='save-hint' onClick={handleSaveImage}>💡 长按上方卡片可保存至相册</Text>
    </View>
  )
}

export default ProgressSharePage

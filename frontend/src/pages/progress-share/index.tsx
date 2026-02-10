import React, { useState, useEffect } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import dayjs from 'dayjs'
import './index.scss'

/**
 * P31 进度分享页 - 分享卡片预览 + 分享给好友/朋友圈
 */
const STAGES = ['材料进场', '隐蔽工程', '泥瓦工', '木工', '油漆', '安装收尾']

const ProgressSharePage: React.FC = () => {
  const [startDate, setStartDate] = useState('')
  const [progress, setProgress] = useState(0)
  const [customText, setCustomText] = useState('')
  const [endDate, setEndDate] = useState('')

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
  }, [])

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

      <Text className='save-hint' onClick={handleSaveImage}>长按上方卡片可保存至相册</Text>
    </View>
  )
}

export default ProgressSharePage

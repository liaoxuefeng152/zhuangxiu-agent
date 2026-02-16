import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import Taro, { usePullDownRefresh } from '@tarojs/taro'
import { pointsApi, userApi } from '../../services/api'
import { useAppSelector, useAppDispatch } from '../../store/hooks'
import { updateUserInfo } from '../../store/slices/userSlice'
import './index.scss'

/**
 * P33 积分记录页 - 展示用户积分明细和汇总
 * V2.6.7新增
 */
const PointsPage: React.FC = () => {
  const dispatch = useAppDispatch()
  const userInfo = useAppSelector((state) => state.user.userInfo)
  const [summary, setSummary] = useState<{ total_points: number; month_points: number } | null>(null)
  const [records, setRecords] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)

  const loadSummary = async () => {
    try {
      const res = await pointsApi.getSummary()
      const data = res?.data ?? res
      setSummary(data)
      // 同步更新用户信息中的积分
      if (data?.total_points !== undefined) {
        dispatch(updateUserInfo({ points: data.total_points }))
      }
    } catch (error) {
      console.error('加载积分汇总失败:', error)
    }
  }

  const loadRecords = async (pageNum: number = 1, append: boolean = false) => {
    if (loading) return
    setLoading(true)
    try {
      const res = await pointsApi.getRecords(pageNum, 20)
      const data = res?.data ?? res
      const newRecords = data.records || []
      
      if (append) {
        setRecords([...records, ...newRecords])
      } else {
        setRecords(newRecords)
      }
      
      setHasMore(newRecords.length >= 20)
      setPage(pageNum)
    } catch (error) {
      console.error('加载积分记录失败:', error)
      Taro.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSummary()
    loadRecords(1, false)
  }, [])

  usePullDownRefresh(() => {
    loadSummary()
    loadRecords(1, false).finally(() => {
      Taro.stopPullDownRefresh()
    })
  })

  const loadMore = () => {
    if (!hasMore || loading) return
    loadRecords(page + 1, true)
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hour = String(date.getHours()).padStart(2, '0')
    const minute = String(date.getMinutes()).padStart(2, '0')
    return `${month}-${day} ${hour}:${minute}`
  }

  const getSourceTypeText = (sourceType: string) => {
    const map: Record<string, string> = {
      'share_report_acceptance': '分享验收报告',
      'share_report_quote': '分享报价单',
      'share_report_contract': '分享合同',
      'share_progress': '分享施工进度',
      'daily_checkin': '每日签到',
      'purchase': '购买会员'
    }
    return map[sourceType] || sourceType
  }

  return (
    <ScrollView 
      scrollY 
      className='points-page'
      onScrollToLower={loadMore}
      lowerThreshold={100}
    >
      <View className='points-header'>
        <View className='points-card'>
          <Text className='points-label'>我的积分</Text>
          <Text className='points-value'>{summary?.total_points ?? userInfo?.points ?? 0}</Text>
          <Text className='points-hint'>本月获得 {summary?.month_points ?? 0} 积分</Text>
        </View>
      </View>

      <View className='points-section'>
        <Text className='section-title'>积分明细</Text>
        {records.length === 0 ? (
          <View className='empty-state'>
            <Text className='empty-text'>暂无积分记录</Text>
          </View>
        ) : (
          <View className='records-list'>
            {records.map((record, index) => (
              <View key={record.id || index} className='record-item'>
                <View className='record-left'>
                  <Text className='record-type'>{getSourceTypeText(record.source_type)}</Text>
                  <Text className='record-desc'>{record.description || ''}</Text>
                  <Text className='record-time'>{formatDate(record.created_at)}</Text>
                </View>
                <View className='record-right'>
                  <Text className={`record-points ${record.points > 0 ? 'positive' : 'negative'}`}>
                    {record.points > 0 ? '+' : ''}{record.points}
                  </Text>
                </View>
              </View>
            ))}
            {hasMore && (
              <View className='load-more' onClick={loadMore}>
                <Text>{loading ? '加载中...' : '加载更多'}</Text>
              </View>
            )}
          </View>
        )}
      </View>

      <View className='points-rules'>
        <Text className='rules-title'>积分规则</Text>
        <View className='rules-list'>
          <View className='rule-item'>
            <Text className='rule-desc'>分享报告：每次+10积分（每日限1次）</Text>
          </View>
          <View className='rule-item'>
            <Text className='rule-desc'>分享进度：每次+5积分（每日限1次）</Text>
          </View>
          <View className='rule-item'>
            <Text className='rule-desc'>每日签到：每次+1积分</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  )
}

PointsPage.config = {
  navigationBarTitleText: '我的积分',
  enablePullDownRefresh: true
}

export default PointsPage

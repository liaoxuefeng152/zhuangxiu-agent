import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getWithAuth, deleteWithAuth, postWithAuth } from '../../services/api'
import EmptyState from '../../components/EmptyState'
import './index.scss'

/**
 * P21 回收站页 - 仅会员可见，30天内可恢复（V2.6.2优化）
 */
const RecycleBinPage: React.FC = () => {
  const [list, setList] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [isMember, setIsMember] = useState(false)

  // 加载回收站数据
  const loadRecycleData = async () => {
    setLoading(true)
    try {
      const res = await getWithAuth('/users/data/recycle') as any
      const data = res?.data || {}
      
      if (data.member_only && data.list.length === 0) {
        // 非会员或会员但无数据
        setIsMember(false)
      } else {
        setIsMember(true)
        // 处理数据，计算剩余天数
        const processedList = (data.list || []).map((item: any) => {
          let deletedAt = item.deleted_at
          let daysLeft = 30
          
          if (deletedAt) {
            const deletedDate = new Date(deletedAt)
            const now = new Date()
            const diffTime = Math.abs(now.getTime() - deletedDate.getTime())
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
            daysLeft = Math.max(0, 30 - diffDays)
          }
          
          // 根据类型设置显示信息
          let name = ''
          let icon = '📄'
          
          if (item.type === 'photo') {
            name = `施工照片 - ${item.stage || '未知阶段'}`
            icon = '📷'
          } else if (item.type === 'acceptance') {
            name = `验收报告 - ${item.stage || '未知阶段'}`
            icon = '✅'
          }
          
          return {
            ...item,
            name,
            icon,
            daysLeft,
            url: item.file_url || null
          }
        })
        
        setList(processedList)
      }
    } catch (error: any) {
      console.error('加载回收站数据失败:', error)
      if (error?.response?.status === 403) {
        setIsMember(false)
      }
      setList([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRecycleData()
  }, [])

  // 恢复数据
  const handleRestore = async (item: any) => {
    try {
      Taro.showLoading({ title: '恢复中...' })
      
      await postWithAuth('/users/data/restore', {
        type: item.type,
        id: item.id
      })
      
      Taro.hideLoading()
      Taro.showToast({ title: '已恢复至原分类', icon: 'success' })
      
      // 重新加载数据
      loadRecycleData()
    } catch (error: any) {
      Taro.hideLoading()
      console.error('恢复数据失败:', error)
      
      if (error?.response?.status === 403) {
        Taro.showToast({ title: '仅会员支持数据恢复', icon: 'none' })
      } else if (error?.response?.status === 404) {
        Taro.showToast({ title: '记录已过期无法恢复', icon: 'none' })
      } else {
        Taro.showToast({ title: '恢复失败', icon: 'none' })
      }
    }
  }

  // 永久删除
  const handleDelete = async (item: any) => {
    Taro.showModal({
      title: '确认永久删除',
      content: '永久删除后不可恢复，确定继续吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            Taro.showLoading({ title: '删除中...' })
            
            // 调用永久删除API
            await deleteWithAuth(`/users/data/permanent/${item.type}/${item.id}`)
            
            // 从前端列表中移除
            setList(prev => prev.filter(x => x.id !== item.id))
            
            Taro.hideLoading()
            Taro.showToast({ title: '已永久删除', icon: 'success' })
          } catch (error: any) {
            Taro.hideLoading()
            console.error('永久删除失败:', error)
            
            if (error?.response?.status === 403) {
              Taro.showToast({ title: '仅会员支持永久删除', icon: 'none' })
            } else if (error?.response?.status === 404) {
              Taro.showToast({ title: '记录不存在或不在回收站', icon: 'none' })
            } else {
              Taro.showToast({ title: '删除失败', icon: 'none' })
            }
          }
        }
      }
    })
  }

  // 清空回收站
  const handleClearAll = () => {
    if (list.length === 0) return
    
    Taro.showModal({
      title: '确认清空回收站？',
      content: `将永久删除 ${list.length} 项数据，此操作不可恢复`,
      success: async (res) => {
        if (res.confirm) {
          try {
            Taro.showLoading({ title: '清空中...' })
            
            // 调用清空回收站API
            await deleteWithAuth('/users/data/recycle/clear')
            
            // 清空前端列表
            setList([])
            
            Taro.hideLoading()
            Taro.showToast({ title: '回收站已清空', icon: 'success' })
          } catch (error: any) {
            Taro.hideLoading()
            console.error('清空回收站失败:', error)
            
            if (error?.response?.status === 403) {
              Taro.showToast({ title: '仅会员支持清空回收站', icon: 'none' })
            } else {
              Taro.showToast({ title: '清空失败', icon: 'none' })
            }
          }
        }
      }
    })
  }

  // 如果不是会员，显示提示
  if (!isMember && !loading) {
    return (
      <View className='recycle-bin-page'>
        <View className='member-only'>
          <Text className='member-icon'>🔒</Text>
          <Text className='member-title'>会员专享功能</Text>
          <Text className='member-desc'>回收站功能需要会员权限</Text>
          <Text className='member-desc'>会员可恢复30天内删除的数据</Text>
          <View className='member-actions'>
            <Text className='member-btn' onClick={() => Taro.navigateTo({ url: '/pages/membership/index' })}>
              查看会员权益
            </Text>
            <Text className='member-btn secondary' onClick={() => Taro.navigateBack()}>
              返回数据管理
            </Text>
          </View>
        </View>
      </View>
    )
  }

  return (
    <ScrollView scrollY className='recycle-bin-page-outer'>
      <View className='recycle-bin-page'>
        <View className='nav-row'>
          <Text className='nav-title'>回收站</Text>
          {list.length > 0 && (
            <Text className='clear-btn' onClick={handleClearAll}>清空回收站</Text>
          )}
        </View>

        <View className='member-hint'>
          <Text>会员专享：删除数据30天内可恢复，普通用户无回收站功能</Text>
        </View>

        {loading ? (
          <View className='loading'>
            <Text>加载中...</Text>
          </View>
        ) : list.length === 0 ? (
          <View className='empty'>
            <Text className='empty-icon'>🗑</Text>
            <Text className='empty-text'>回收站为空</Text>
            <Text className='empty-desc'>删除的数据将在这里保留30天</Text>
            <Text className='back-link' onClick={() => Taro.navigateBack()}>返回数据管理</Text>
          </View>
        ) : (
          <View className='list'>
            {list.map((item) => (
              <View key={`${item.type}-${item.id}`} className='list-item'>
                <View className='item-thumb'>
                  {item.url ? (
                    <Image src={item.url} mode='aspectFill' className='thumb-img' />
                  ) : (
                    <Text className='file-icon'>{item.icon}</Text>
                  )}
                </View>
                <View className='item-info'>
                  <Text className='item-name'>{item.name || '未命名数据'}</Text>
                  <Text className='item-time'>
                    {item.deleted_at ? `删除时间: ${new Date(item.deleted_at).toLocaleDateString()}` : '-'} 
                    {item.daysLeft !== undefined && ` · 剩余${item.daysLeft}天过期`}
                  </Text>
                  <Text className='item-type'>{item.type === 'photo' ? '施工照片' : '验收报告'}</Text>
                </View>
                <View className='item-actions'>
                  <Text className='action-link' onClick={() => handleRestore(item)}>恢复</Text>
                  <Text className='action-link danger' onClick={() => handleDelete(item)}>永久删除</Text>
                </View>
              </View>
            ))}
          </View>
        )}
        
        {list.length > 0 && (
          <View className='recycle-tips'>
            <Text className='tip'>💡 提示：</Text>
            <Text className='tip'>1. 数据在回收站保留30天，过期自动清理</Text>
            <Text className='tip'>2. 恢复后数据将回到原分类</Text>
            <Text className='tip'>3. 永久删除后无法恢复</Text>
          </View>
        )}
      </View>
    </ScrollView>
  )
}

export default RecycleBinPage

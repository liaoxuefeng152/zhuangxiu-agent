import React, { useState } from 'react'
import { View, Text, ScrollView, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

/**
 * P21 回收站页 - 仅会员可见，7天内可恢复
 */
const RecycleBinPage: React.FC = () => {
  const [list, setList] = useState<any[]>([])
  const isMember = !!Taro.getStorageSync('access_token') // 简化：有登录即视为可进，实际应查 is_member

  React.useEffect(() => {
    if (!isMember) {
      Taro.showToast({ title: '仅会员支持数据恢复功能', icon: 'none' })
      Taro.redirectTo({ url: '/pages/data-manage/index' })
    }
  }, [isMember])

  const handleRestore = (item: any) => {
    setList((prev) => prev.filter((x) => x.id !== item.id))
    Taro.showToast({ title: '已恢复至原分类', icon: 'success' })
  }

  const handleDelete = (item: any) => {
    Taro.showModal({
      title: '确认永久删除',
      content: '删除后不可恢复',
      success: (res) => {
        if (res.confirm) {
          setList((prev) => prev.filter((x) => x.id !== item.id))
          Taro.showToast({ title: '已删除', icon: 'success' })
        }
      }
    })
  }

  const handleClearAll = () => {
    Taro.showModal({
      title: '确认清空？',
      content: '清空后所有数据不可恢复',
      success: (res) => {
        if (res.confirm) {
          setList([])
          Taro.showToast({ title: '回收站已清空', icon: 'success' })
        }
      }
    })
  }

  if (!isMember) {
    return <View className='recycle-bin-page'><Text>正在跳转...</Text></View>
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
        <Text>会员专享：删除数据7天内可恢复，普通用户无回收站功能</Text>
      </View>

      {list.length === 0 ? (
        <View className='empty'>
          <Text className='empty-icon'>🗑</Text>
          <Text className='empty-text'>回收站为空</Text>
          <Text className='back-link' onClick={() => Taro.navigateBack()}>返回数据管理</Text>
        </View>
      ) : (
        <View className='list'>
          {list.map((item) => (
            <View key={item.id} className='list-item'>
              <View className='item-thumb'>
                {item.url ? (
                  <Image src={item.url} mode='aspectFill' className='thumb-img' />
                ) : (
                  <Text className='file-icon'>📄</Text>
                )}
              </View>
              <View className='item-info'>
                <Text className='item-name'>{item.name || item.file_name || '未命名'}</Text>
                <Text className='item-time'>
                  {item.deleted_at || item.created_at || '-'} · 剩余{item.daysLeft ?? 7}天过期
                </Text>
              </View>
              <View className='item-actions'>
                <Text className='action-link' onClick={() => handleRestore(item)}>恢复</Text>
                <Text className='action-link danger' onClick={() => handleDelete(item)}>永久删除</Text>
              </View>
            </View>
          ))}
        </View>
      )}
      </View>
    </ScrollView>
  )
}

export default RecycleBinPage

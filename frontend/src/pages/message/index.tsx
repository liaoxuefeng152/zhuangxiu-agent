import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import EmptyState from '../../components/EmptyState'
import { getWithAuth, putWithAuth } from '../../services/api'
import './index.scss'

const TABS = [
  { key: 'construction', label: '施工提醒', icon: '🔔' },
  { key: 'report', label: '报告通知', icon: '📄' },
  { key: 'system', label: '系统消息', icon: '⚙️' },
  { key: 'service', label: '客服回复', icon: '💬' }
]

/**
 * P14 消息中心 - 四分类标签 + 批量操作（全选/删除已选/标为已读）
 */
const MessagePage: React.FC = () => {
  const [allList, setAllList] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState('construction')
  const [batchMode, setBatchMode] = useState(false)
  const [selected, setSelected] = useState<Set<number>>(new Set())

  const loadMessages = async () => {
    try {
      setLoading(true)
      const res = await messageApi.getList({ page: 1, page_size: 50 }) as any
      setAllList(res?.list ?? [])
    } catch {
      setAllList([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMessages()
  }, [])

  const filteredList = allList.filter((m) => (m.category || 'construction') === tab)

  const handleReadAll = async () => {
    try {
      await putWithAuth('/messages/read-all')
      Taro.showToast({ title: '已全部标为已读', icon: 'success' })
      loadMessages()
    } catch {
      Taro.showToast({ title: '操作失败', icon: 'none' })
    }
  }

  const handleItemClick = async (item: any) => {
    if (batchMode) {
      setSelected((prev) => {
        const next = new Set(prev)
        if (next.has(item.id)) next.delete(item.id)
        else next.add(item.id)
        return next
      })
      return
    }
    if (!item.is_read) {
      try { await messageApi.markRead(item.id) } catch { /* ignore */ }
      loadMessages()
    }
    if (item.link_url) Taro.navigateTo({ url: item.link_url })
  }

  const toggleSelectAll = () => {
    if (selected.size >= filteredList.length) setSelected(new Set())
    else setSelected(new Set(filteredList.map((m) => m.id)))
  }

  const deleteSelected = () => {
    const ids = Array.from(selected)
    const canDelete = filteredList.filter((m) => ids.includes(m.id) && (m.category === 'system' || m.category === 'service'))
    if (canDelete.length === 0) {
      Taro.showToast({ title: '施工提醒/报告通知不可删除', icon: 'none' })
      return
    }
    Taro.showModal({
      title: '确认删除',
      content: `删除 ${selected.size} 条消息？`,
      success: (r) => {
        if (r.confirm) {
          setSelected(new Set())
          setBatchMode(false)
          loadMessages()
          Taro.showToast({ title: '已删除', icon: 'success' })
        }
      }
    })
  }

  const markSelectedRead = () => {
    selected.forEach((id) => {
      putWithAuth(`/messages/${id}/read`).catch(() => {})
    })
    setSelected(new Set())
    setBatchMode(false)
    loadMessages()
    Taro.showToast({ title: '已标为已读', icon: 'success' })
  }

  const unreadCount = allList.filter((m) => !m.is_read).length

  return (
    <ScrollView scrollY className='message-page'>
      <View className='header'>
        <Text className='title'>消息中心</Text>
        <Text className='batch-btn' onClick={() => setBatchMode(!batchMode)}>
          {batchMode ? '取消' : '批量操作'}
        </Text>
      </View>

      <View className='tabs'>
        {TABS.map((t) => (
          <View
            key={t.key}
            className={`tab ${tab === t.key ? 'active' : ''}`}
            onClick={() => { setTab(t.key); setSelected(new Set()); }}
          >
            <Text>{t.label}</Text>
            {t.key === 'construction' && unreadCount > 0 && <View className='tab-dot' />}
          </View>
        ))}
      </View>

      {batchMode && (
        <View className='batch-bar'>
          <Text className='batch-link' onClick={toggleSelectAll}>
            {selected.size >= list.length ? '取消全选' : '全选'}
          </Text>
          <Text className='batch-link' onClick={deleteSelected}>删除已选</Text>
          <Text className='batch-link' onClick={markSelectedRead}>标为已读</Text>
        </View>
      )}

      {loading ? (
        <View className='loading-wrap'><Text>加载中...</Text></View>
      ) : filteredList.length === 0 ? (
        <EmptyState type='message' text='暂无相关消息' actionText='' />
      ) : (
        <View className='list'>
          {filteredList.map((item) => (
            <View
              key={item.id}
              className={`item ${item.is_read ? '' : 'unread'} ${selected.has(item.id) ? 'selected' : ''}`}
              onClick={() => handleItemClick(item)}
            >
              <Text className='item-icon'>{TABS.find((t) => t.key === (item.category || 'construction'))?.icon || '🔔'}</Text>
              <View className='item-content'>
                <Text className='item-title'>{item.title}</Text>
                <Text className='item-summary'>{item.summary || item.content || ''}</Text>
              </View>
              <View className='item-right'>
                <Text className='item-time'>{item.created_at ? new Date(item.created_at).toLocaleString() : ''}</Text>
                {!item.is_read && <View className='unread-dot' />}
              </View>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  )
}

export default MessagePage

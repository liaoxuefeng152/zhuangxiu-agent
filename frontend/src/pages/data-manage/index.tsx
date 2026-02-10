import React, { useState } from 'react'
import { View, Text, ScrollView, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

const DATA_TABS = [
  { key: 'photo', label: '施工照片' },
  { key: 'report', label: '分析报告' },
  { key: 'ledger', label: '台账报告' },
  { key: 'acceptance', label: '验收报告' }
]

// 阶段标签（PRD 6大阶段 S00-S05）
const STAGE_TABS = ['全部', 'S00材料', 'S01隐蔽', 'S02泥瓦', 'S03木工', 'S04油漆', 'S05收尾']

/**
 * P20 数据管理页 - 照片/报告批量管理、回收站入口
 */
const DataManagePage: React.FC = () => {
  const [tab, setTab] = useState('photo')
  const [stage, setStage] = useState('全部')
  const [batchMode, setBatchMode] = useState(false)
  const [list, setList] = useState<any[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())

  const toggleSelect = (id: string) => {
    const next = new Set(selected)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelected(next)
  }

  const handleBatchDelete = () => {
    if (selected.size === 0) {
      Taro.showToast({ title: '请先选择数据', icon: 'none' })
      return
    }
    Taro.showModal({
      title: '确认删除',
      content: `将删除 ${selected.size} 项，会员7天内可恢复`,
      success: (res) => {
        if (res.confirm) {
          setList((prev) => prev.filter((x) => !selected.has(String(x.id))))
          setSelected(new Set())
          setBatchMode(false)
          Taro.showToast({ title: '已移入回收站', icon: 'success' })
        }
      }
    })
  }

  const handleRecycleBin = () => {
    const isMember = !!Taro.getStorageSync('is_member')
    if (!isMember) {
      Taro.showToast({ title: '仅会员支持数据恢复功能', icon: 'none' })
      return
    }
    Taro.navigateTo({ url: '/pages/recycle-bin/index' })
  }

  return (
    <ScrollView scrollY className='data-manage-page'>
      <View className='nav-row'>
        <Text className='nav-title'>数据管理</Text>
        <Text
          className='batch-btn'
          onClick={() => setBatchMode(!batchMode)}
        >
          {batchMode ? '取消' : '批量操作'}
        </Text>
      </View>

      <ScrollView scrollX className='tabs data-tabs' scrollWithAnimation>
        {DATA_TABS.map((t) => (
          <Text
            key={t.key}
            className={`tab ${tab === t.key ? 'active' : ''}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </Text>
        ))}
      </ScrollView>

      {tab === 'photo' && (
        <ScrollView scrollX className='tabs stage-tabs' scrollWithAnimation>
          {STAGE_TABS.map((s) => (
            <Text
              key={s}
              className={`tab ${stage === s ? 'active' : ''}`}
              onClick={() => setStage(s)}
            >
              {s}
            </Text>
          ))}
        </ScrollView>
      )}

      <View className='list-wrap'>
        {list.length === 0 && (
          <View className='empty'>
            <Text className='empty-icon'>📁</Text>
            <Text className='empty-text'>暂无{tab === 'photo' ? '照片' : '报告'}数据</Text>
          </View>
        )}
        {list.map((item) => (
          <View key={item.id} className='list-item'>
            {batchMode && (
              <View
                className='checkbox'
                onClick={() => toggleSelect(String(item.id))}
              >
                {selected.has(String(item.id)) ? '✓' : ''}
              </View>
            )}
            <View className='item-thumb'>
              {item.url ? (
                <Image src={item.url} mode='aspectFill' className='thumb-img' />
              ) : (
                <Text className='file-icon'>📄</Text>
              )}
            </View>
            <View className='item-info'>
              <Text className='item-name'>{item.name || item.file_name || '未命名'}</Text>
              <Text className='item-time'>{item.created_at || item.time || '-'}</Text>
            </View>
            <View className='item-actions'>
              {tab !== 'photo' && <Text className='action-link' onClick={() => {}}>导出</Text>}
              <Text className='action-link danger' onClick={() => {}}>删除</Text>
            </View>
          </View>
        ))}
      </View>

      {batchMode && (
        <View className='batch-bar'>
          <Text className='batch-info'>已选 {selected.size} 项</Text>
          <View className='batch-btn-wrap'>
            <Text className='batch-action' onClick={handleBatchDelete}>删除已选</Text>
          </View>
        </View>
      )}

      <View className='recycle-section'>
        <Text className='recycle-title'>回收站</Text>
        <Text className='recycle-desc'>会员专享：删除数据7天内可恢复</Text>
        <View className='recycle-btn' onClick={handleRecycleBin}>
          <Text>进入回收站</Text>
        </View>
      </View>

      <View className='storage-tip'>
        <Text>已使用 0 MB / 总存储 100 MB</Text>
      </View>
    </ScrollView>
  )
}

export default DataManagePage

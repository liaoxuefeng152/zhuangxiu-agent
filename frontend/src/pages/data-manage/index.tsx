import React, { useState, useEffect, useMemo } from 'react'
import { View, Text, ScrollView, Image, Input } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { companyApi, quoteApi, contractApi, constructionPhotoApi } from '../../services/api'
import EmptyState from '../../components/EmptyState'
import './index.scss'

const DATA_TABS = [
  { key: 'photo', label: '施工照片' },
  { key: 'report', label: '分析报告' },  // V2.6.2优化：合并报告列表功能
  { key: 'ledger', label: '台账报告' },
  { key: 'acceptance', label: '验收报告' }
]

// 阶段标签（PRD 6大阶段 S00-S05）
const STAGE_TABS = ['全部', 'S00材料', 'S01隐蔽', 'S02泥瓦', 'S03木工', 'S04油漆', 'S05收尾']

/**
 * P18/P20/P29 数据管理页（V2.6.2优化：合并报告列表和照片管理）
 * - 支持报告列表（公司/报价单/合同）
 * - 支持照片管理（按阶段分类）
 * - 批量操作、回收站入口
 */
const DataManagePage: React.FC = () => {
  const router = Taro.getCurrentInstance().router
  const initialTab = (router?.params?.tab as string) || 'photo'
  const [tab, setTab] = useState(initialTab)
  const [stage, setStage] = useState('全部')
  const [batchMode, setBatchMode] = useState(false)
  const [list, setList] = useState<any[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(false)
  const [reportType, setReportType] = useState<'company' | 'quote' | 'contract'>('company')  // V2.6.2优化：报告类型
  const [searchKw, setSearchKw] = useState('')  // V2.6.2优化：搜索关键词

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

  // V2.6.2优化：加载报告列表
  const loadReports = async () => {
    setLoading(true)
    try {
      let res: any
      if (reportType === 'company') {
        res = await companyApi.getList()
      } else if (reportType === 'quote') {
        res = await quoteApi.getList()
      } else {
        res = await contractApi.getList()
      }
      const data = res?.data ?? res
      setList(Array.isArray(data?.list) ? data.list : (Array.isArray(data) ? data : []))
    } catch {
      setList([])
    } finally {
      setLoading(false)
    }
  }

  // V2.6.2优化：加载照片列表
  const loadPhotos = async () => {
    setLoading(true)
    try {
      const apiStage = stage === '全部' ? undefined : STAGE_TABS.indexOf(stage) > 0 ? 
        ['material', 'plumbing', 'carpentry', 'woodwork', 'painting', 'installation'][STAGE_TABS.indexOf(stage) - 1] : undefined
      const res = await constructionPhotoApi.getList(apiStage) as any
      const data = res?.data ?? res
      setList(Array.isArray(data?.list) ? data.list : (Array.isArray(data) ? data : []))
    } catch {
      setList([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (tab === 'report') {
      loadReports()
    } else if (tab === 'photo') {
      loadPhotos()
    }
  }, [tab, reportType, stage])

  // V2.6.2优化：过滤报告列表（搜索）
  const filteredReports = useMemo(() => {
    if (tab !== 'report') return list
    let items = list
    const kw = searchKw.trim().toLowerCase()
    if (kw) {
      items = items.filter((item) => {
        const name = (item.company_name || item.file_name || '').toLowerCase()
        return name.includes(kw)
      })
    }
    return items
  }, [list, searchKw, tab])

  const getReportUrl = (item: any) => {
    if (reportType === 'company') {
      return `/pages/report-detail/index?type=company&scanId=${item.id}&name=${encodeURIComponent(item.company_name || '')}`
    }
    if (reportType === 'quote') {
      return `/pages/report-detail/index?type=quote&scanId=${item.id}&name=${encodeURIComponent(item.file_name || '')}`
    }
    return `/pages/report-detail/index?type=contract&scanId=${item.id}&name=${encodeURIComponent(item.file_name || '')}`
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

      {/* V2.6.2优化：报告类型切换 */}
      {tab === 'report' && (
        <ScrollView scrollX className='tabs report-type-tabs' scrollWithAnimation>
          {[
            { key: 'company', label: '公司风险' },
            { key: 'quote', label: '报价单' },
            { key: 'contract', label: '合同' }
          ].map((t) => (
            <Text
              key={t.key}
              className={`tab ${reportType === t.key ? 'active' : ''}`}
              onClick={() => setReportType(t.key as any)}
            >
              {t.label}
            </Text>
          ))}
        </ScrollView>
      )}

      {/* V2.6.2优化：报告搜索 */}
      {tab === 'report' && (
        <View className='search-bar'>
          <Input
            className='search-input'
            placeholder='搜索公司名/文件名'
            value={searchKw}
            onInput={(e) => setSearchKw(e.detail.value)}
          />
        </View>
      )}

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
        {loading ? (
          <View className='empty'>
            <Text className='empty-text'>加载中...</Text>
          </View>
        ) : (tab === 'report' ? filteredReports : list).length === 0 ? (
          <EmptyState 
            type={tab === 'photo' ? 'photo' : 'report'} 
            text={`暂无${tab === 'photo' ? '照片' : '报告'}数据`}
            actionText={tab === 'report' ? '去检测' : '去拍摄'}
            actionUrl={tab === 'report' ? '/pages/company-scan/index' : '/pages/photo/index'}
          />
        ) : (
          (tab === 'report' ? filteredReports : list).map((item) => (
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
              {tab === 'report' && (
                <Text className='action-link' onClick={() => Taro.navigateTo({ url: getReportUrl(item) })}>查看</Text>
              )}
              {tab !== 'photo' && <Text className='action-link' onClick={() => {}}>导出</Text>}
              <Text className='action-link danger' onClick={() => {}}>删除</Text>
            </View>
          </View>
          ))
        )}
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

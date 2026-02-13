import React, { useState, useEffect, useMemo } from 'react'
import { View, Text, ScrollView, Image, Input } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getWithAuth } from '../../services/api'
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

const STAGE_NAMES: Record<string, string> = {
  S00: 'S00 材料进场',
  S01: 'S01 隐蔽工程',
  S02: 'S02 泥瓦工',
  S03: 'S03 木工',
  S04: 'S04 油漆',
  S05: 'S05 安装收尾',
  material: 'S00 材料进场',
  plumbing: 'S01 隐蔽工程',
  carpentry: 'S02 泥瓦工',
  woodwork: 'S03 木工',
  painting: 'S04 油漆',
  installation: 'S05 安装收尾'
}

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
  const [loadPhotoError, setLoadPhotoError] = useState<string | null>(null)  // 施工照片加载失败原因，便于区分「无数据」与「请求失败」

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

  // V2.6.2优化：加载报告列表（用 getWithAuth 避免小程序 axios 不传 header 导致 401）
  const loadReports = async () => {
    setLoading(true)
    try {
      let res: any
      if (reportType === 'company') {
        res = await getWithAuth('/companies/scans')
      } else if (reportType === 'quote') {
        res = await getWithAuth('/quotes/list')
      } else {
        res = await getWithAuth('/contracts/list')
      }
      setList(Array.isArray(res?.list) ? res.list : [])
    } catch (e: any) {
      if (e?.response?.status === 401) console.warn('需要登录才能查看报告列表')
      setList([])
    } finally {
      setLoading(false)
    }
  }

  // V2.6.2优化：加载照片列表（用 getWithAuth 避免小程序 axios 不传 header 导致 401）
  const loadPhotos = async () => {
    setLoading(true)
    setLoadPhotoError(null)
    try {
      const apiStage = stage === '全部' ? undefined : STAGE_TABS.indexOf(stage) > 0 ?
        ['material', 'plumbing', 'carpentry', 'woodwork', 'painting', 'installation'][STAGE_TABS.indexOf(stage) - 1] : undefined
      const res = await getWithAuth('/construction-photos', apiStage ? { stage: apiStage } : undefined) as any
      const data = res?.list ?? res
      setList(Array.isArray(data) ? data : [])
    } catch (e: any) {
      if (e?.response?.status === 401) {
        setLoadPhotoError('请先登录')
      } else {
        setLoadPhotoError('加载失败，请重试')
      }
      setList([])
    } finally {
      setLoading(false)
    }
  }

  // 验收报告：各阶段 AI 验收分析记录列表（GET /acceptance）
  const loadAcceptance = async () => {
    setLoading(true)
    try {
      const res = await getWithAuth('/acceptance') as any
      setList(Array.isArray(res?.list) ? res.list : [])
    } catch (e: any) {
      if (e?.response?.status === 401) console.warn('需要登录才能查看验收报告')
      setList([])
    } finally {
      setLoading(false)
    }
  }

  // 台账报告：施工进度各阶段台账（GET /constructions/schedule，将 stages 转为列表）
  const loadLedger = async () => {
    setLoading(true)
    try {
      const res = await getWithAuth('/constructions/schedule') as any
      const stages = res?.stages || {}
      const order = ['S00', 'S01', 'S02', 'S03', 'S04', 'S05']
      const arr = order.map((key) => {
        const s = stages[key] || {}
        return {
          id: key,
          name: STAGE_NAMES[key] || key,
          start_date: s.start_date || s.expected_start,
          acceptance_date: s.acceptance_date || s.expected_acceptance,
          status: s.status || 'pending',
          ...s
        }
      })
      setList(arr)
    } catch (e: any) {
      if (e?.response?.status === 404) setList([])
      else if (e?.response?.status === 401) console.warn('需要登录才能查看台账')
      else setList([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (tab === 'report') {
      loadReports()
    } else if (tab === 'photo') {
      loadPhotos()
    } else if (tab === 'acceptance') {
      loadAcceptance()
    } else if (tab === 'ledger') {
      loadLedger()
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

  const displayList = tab === 'report' ? filteredReports : list
  const isEmpty = !loading && displayList.length === 0
  const emptyText = tab === 'photo'
    ? (loadPhotoError || '暂无照片数据（请先在施工陪伴各阶段中拍摄/上传）')
    : tab === 'acceptance'
      ? '暂无验收报告'
      : tab === 'ledger'
        ? '暂无台账（请先在施工陪伴页设置开工日期）'
        : '暂无报告数据'
  const emptyActionUrl = tab === 'ledger' ? '/pages/construction/index' : tab === 'report' ? '/pages/company-scan/index' : '/pages/photo/index'
  const emptyActionText = tab === 'ledger' ? '去设置' : tab === 'report' ? '去检测' : '去拍摄'

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
        ) : isEmpty ? (
          <EmptyState 
            type={tab === 'photo' ? 'photo' : 'report'} 
            text={emptyText}
            actionText={emptyActionText}
            actionUrl={emptyActionUrl}
          />
        ) : (
          displayList.map((item) => (
          <View key={item.id ?? item.stage ?? item.key} className='list-item'>
            {tab !== 'ledger' && batchMode && (
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
                <Text className='file-icon'>{tab === 'ledger' ? '📋' : tab === 'acceptance' ? '✅' : '📄'}</Text>
              )}
            </View>
            <View className='item-info'>
              <Text className='item-name'>
                {tab === 'ledger'
                  ? (item.name || STAGE_NAMES[item.id] || item.id)
                  : tab === 'acceptance'
                    ? (STAGE_NAMES[item.stage] || item.stage || '验收')
                    : (item.name || item.file_name || item.company_name || '未命名')}
              </Text>
              <Text className='item-time'>
                {tab === 'ledger'
                  ? (item.start_date ? `开始: ${item.start_date}` : '—') + (item.acceptance_date ? ` | 验收: ${item.acceptance_date}` : '')
                  : item.created_at || item.time || '-'}
              </Text>
              {tab === 'acceptance' && (
                <View className='item-status'>
                  <Text className={`status-badge ${(item.severity || item.result_status) === 'passed' ? 'safe' : 'warning'}`}>
                    {(item.severity || item.result_status) === 'passed' ? '通过' : (item.severity || item.result_status) === 'rectify' ? '待整改' : (item.result_status || item.severity) || '—'}
                  </Text>
                </View>
              )}
              {/* V2.6.2优化：显示分析结果状态 */}
              {tab === 'report' && (
                <View className='item-status'>
                  {reportType === 'quote' && item.risk_score !== undefined && (
                    <Text className={`status-badge ${item.risk_score >= 61 ? 'high' : item.risk_score >= 31 ? 'warning' : 'safe'}`}>
                      {item.risk_score >= 61 ? '高风险' : item.risk_score >= 31 ? '警告' : '合规'}
                    </Text>
                  )}
                  {reportType === 'contract' && item.risk_level && (
                    <Text className={`status-badge ${item.risk_level === 'high' ? 'high' : item.risk_level === 'warning' ? 'warning' : 'safe'}`}>
                      {item.risk_level === 'high' ? '高风险' : item.risk_level === 'warning' ? '警告' : '合规'}
                    </Text>
                  )}
                  {item.status && (
                    <Text className={`status-text ${item.status === 'completed' ? 'completed' : item.status === 'analyzing' ? 'analyzing' : 'failed'}`}>
                      {item.status === 'completed' ? '已完成' : item.status === 'analyzing' ? '分析中' : '失败'}
                    </Text>
                  )}
                </View>
              )}
            </View>
            <View className='item-actions'>
              {tab === 'report' && (
                <Text className='action-link' onClick={() => Taro.navigateTo({ url: getReportUrl(item) })}>查看</Text>
              )}
              {tab === 'acceptance' && (
                <Text className='action-link' onClick={() => Taro.navigateTo({ url: `/pages/acceptance/index?id=${item.id}` })}>查看</Text>
              )}
              {tab === 'ledger' && (
                <Text className='action-link' onClick={() => Taro.navigateTo({ url: '/pages/construction/index' })}>查看</Text>
              )}
              {tab !== 'photo' && tab !== 'ledger' && <Text className='action-link' onClick={() => {}}>导出</Text>}
              {tab !== 'ledger' && <Text className='action-link danger' onClick={() => {}}>删除</Text>}
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

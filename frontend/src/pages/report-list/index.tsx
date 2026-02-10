import React, { useState, useEffect, useMemo } from 'react'
import { View, Text, ScrollView, Input } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { companyApi, quoteApi, contractApi } from '../../services/api'
import EmptyState from '../../components/EmptyState'
import './index.scss'

type TimeFilter = 'all' | '7d' | '30d'

/**
 * 报告中心 - 报告列表（PRD D08：搜索+时间筛选）
 */
const ReportListPage: React.FC = () => {
  const [type, setType] = useState('company')
  const [list, setList] = useState<any[]>([])
  const [loadError, setLoadError] = useState(false)
  const [searchKw, setSearchKw] = useState('')
  const [timeFilter, setTimeFilter] = useState<TimeFilter>('all')

  const loadList = async () => {
    setLoadError(false)
    try {
      if (type === 'company') {
        const res = await companyApi.getList()
        setList((res as any)?.data?.list ?? (res as any)?.list ?? [])
      } else if (type === 'quote') {
        const res = await quoteApi.getList()
        setList((res as any)?.data?.list ?? (res as any)?.list ?? [])
      } else {
        const res = await contractApi.getList()
        setList((res as any)?.data?.list ?? (res as any)?.list ?? [])
      }
    } catch {
      setList([])
      setLoadError(true)
    }
  }

  useEffect(() => {
    loadList()
  }, [type])

  const filteredList = useMemo(() => {
    let items = list
    const kw = searchKw.trim().toLowerCase()
    if (kw) {
      items = items.filter((item) => {
        const name = (item.company_name || item.file_name || '').toLowerCase()
        return name.includes(kw)
      })
    }
    if (timeFilter !== 'all') {
      const now = Date.now()
      const ms = timeFilter === '7d' ? 7 * 24 * 60 * 60 * 1000 : 30 * 24 * 60 * 60 * 1000
      const cutoff = now - ms
      items = items.filter((item) => {
        const t = item.created_at ? new Date(item.created_at).getTime() : 0
        return t >= cutoff
      })
    }
    return items
  }, [list, searchKw, timeFilter])

  const getReportUrl = (item: any) => {
    if (type === 'company') {
      return `/pages/report-detail/index?type=company&scanId=${item.id}&name=${encodeURIComponent(item.company_name || '')}`
    }
    if (type === 'quote') {
      return `/pages/report-detail/index?type=quote&scanId=${item.id}&name=${encodeURIComponent(item.file_name || '')}`
    }
    return `/pages/report-detail/index?type=contract&scanId=${item.id}&name=${encodeURIComponent(item.file_name || '')}`
  }

  return (
    <View className='report-list-page'>
      <View className='tabs'>
        {['company', 'quote', 'contract'].map((t) => (
          <Text
            key={t}
            className={`tab ${type === t ? 'active' : ''}`}
            onClick={() => setType(t)}
          >
            {t === 'company' && '公司风险'}
            {t === 'quote' && '报价单'}
            {t === 'contract' && '合同'}
          </Text>
        ))}
      </View>
      <View className='filter-bar'>
        <Input
          className='search-input'
          placeholder='搜索公司名/文件名'
          value={searchKw}
          onInput={(e) => setSearchKw(e.detail.value)}
        />
        <View className='time-filters'>
          {(['all', '7d', '30d'] as const).map((f) => (
            <Text
              key={f}
              className={`time-tab ${timeFilter === f ? 'active' : ''}`}
              onClick={() => setTimeFilter(f)}
            >
              {f === 'all' && '全部'}
              {f === '7d' && '近7天'}
              {f === '30d' && '近30天'}
            </Text>
          ))}
        </View>
      </View>
      <ScrollView scrollY className='list'>
        {filteredList.length === 0 ? (
          loadError ? (
            <View className='load-error-wrap'>
              <Text className='load-error-text'>加载失败，请检查网络或后端地址</Text>
              <Text className='load-error-hint'>若在手机预览：请把 frontend/.env.development 里的 TARO_APP_API_BASE_URL 改成电脑的局域网 IP（如 http://192.168.x.x:8000/api/v1），保存后重新编译再预览</Text>
              <View className='retry-btn' onClick={loadList}>
                <Text>重试</Text>
              </View>
            </View>
          ) : (
            <EmptyState type='report' text={list.length === 0 ? '暂无报告数据' : '无匹配结果'} actionText='去检测' actionUrl='/pages/company-scan/index' />
          )
        ) : (
          filteredList.map((item) => (
            <View
              key={item.id}
              className='item'
              onClick={() => Taro.navigateTo({ url: getReportUrl(item) })}
            >
              <Text className='name'>{item.company_name || item.file_name || `报告${item.id}`}</Text>
              <Text className='time'>{item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}</Text>
            </View>
          ))
        )}
      </ScrollView>
    </View>
  )
}

export default ReportListPage

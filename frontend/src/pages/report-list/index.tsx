import React, { useState, useEffect, useMemo } from 'react'
import { View, Text, ScrollView, Input } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getWithAuth } from '../../services/api'
import EmptyState from '../../components/EmptyState'
import './index.scss'

type TimeFilter = 'all' | '7d' | '30d'

// 格式化日期函数，处理时区问题
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  
  // 处理时区：如果字符串没有时区后缀（Z或+/-），则添加'Z'表示UTC时间
  // 与后端约定一致：无时区后缀的时间字符串视为UTC时间
  let normalizedDateStr = dateStr
  if (typeof dateStr === 'string') {
    const hasTimezone = /[Zz]$|[+-]\d{2}:?\d{2}$/.test(dateStr)
    if (!hasTimezone) {
      normalizedDateStr = dateStr + 'Z'
    }
  }
  
  const date = new Date(normalizedDateStr)
  
  // 检查日期是否有效
  if (isNaN(date.getTime())) {
    // 如果解析失败，尝试直接解析原始字符串
    const fallbackDate = new Date(dateStr)
    if (!isNaN(fallbackDate.getTime())) {
      return fallbackDate.toLocaleDateString()
    }
    return dateStr
  }
  
  return date.toLocaleDateString()
}

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
      let res: any
      if (type === 'company') {
        res = await getWithAuth('/companies/scans')
      } else if (type === 'quote') {
        res = await getWithAuth('/quotes/list')
      } else {
        res = await getWithAuth('/contracts/list')
      }
      setList(res?.list ?? [])
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
        if (!item.created_at) return false
        // 使用formatDate函数中的时区处理逻辑来解析时间
        let normalizedDateStr = item.created_at
        if (typeof item.created_at === 'string') {
          const hasTimezone = /[Zz]$|[+-]\d{2}:?\d{2}$/.test(item.created_at)
          if (!hasTimezone) {
            normalizedDateStr = item.created_at + 'Z'
          }
        }
        const date = new Date(normalizedDateStr)
        const t = isNaN(date.getTime()) ? 0 : date.getTime()
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
      <ScrollView scrollY className='list-outer'>
        <View className='list'>
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
              <View className='item-content'>
                <Text className='name'>{item.company_name || item.file_name || `报告${item.id}`}</Text>
                <Text className='time'>{item.created_at ? formatDate(item.created_at) : ''}</Text>
                {/* V2.6.2优化：显示分析结果状态 */}
                <View className='item-status'>
                  {type === 'quote' && item.risk_score !== undefined && (
                    <Text className={`status-badge ${item.risk_score >= 61 ? 'high' : item.risk_score >= 31 ? 'warning' : 'safe'}`}>
                      {item.risk_score >= 61 ? '需关注' : item.risk_score >= 31 ? '一般关注' : '合规'}
                    </Text>
                  )}
                  {type === 'contract' && item.risk_level && (
                    <Text className={`status-badge ${item.risk_level === 'high' ? 'high' : item.risk_level === 'warning' ? 'warning' : 'safe'}`}>
                      {item.risk_level === 'high' ? '需关注' : item.risk_level === 'warning' ? '一般关注' : '合规'}
                    </Text>
                  )}
                  {item.status && (
                    <Text className={`status-text ${item.status === 'completed' ? 'completed' : item.status === 'analyzing' ? 'analyzing' : 'failed'}`}>
                      {item.status === 'completed' ? '已完成' : item.status === 'analyzing' ? '分析中' : '失败'}
                    </Text>
                  )}
                </View>
              </View>
            </View>
          ))
        )}
        </View>
      </ScrollView>
    </View>
  )
}

export default ReportListPage

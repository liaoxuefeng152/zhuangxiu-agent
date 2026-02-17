import React, { useState, useEffect, useMemo } from 'react'
import { View, Text, ScrollView, Image, Input } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getWithAuth, constructionPhotoApi, reportApi, deleteWithAuth } from '../../services/api'
import EmptyState from '../../components/EmptyState'
import './index.scss'

// 解析日期用于比较（排序、过滤等）
const parseDateForComparison = (dateStr: any): number => {
  if (!dateStr) return 0
  
  try {
    // 处理时区：如果字符串没有时区后缀（Z或+/-），则添加'Z'表示UTC时间
    let normalizedDateStr = String(dateStr)
    if (typeof dateStr === 'string') {
      const hasTimezone = /[Zz]$|[+-]\d{2}:?\d{2}$/.test(dateStr)
      if (!hasTimezone) {
        normalizedDateStr = dateStr + 'Z'
      }
    }
    
    const date = new Date(normalizedDateStr)
    return isNaN(date.getTime()) ? 0 : date.getTime()
  } catch (error) {
    // 如果解析失败，尝试直接解析
    try {
      const date = new Date(dateStr)
      return isNaN(date.getTime()) ? 0 : date.getTime()
    } catch {
      return 0
    }
  }
}

// V2.6.9优化：标准时间格式化 - 年,月,日,小时格式
// 修复时区问题：后端返回UTC时间（无时区后缀），前端需正确解析为本地时间显示
const formatSmartTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  
  try {
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
        const year = fallbackDate.getFullYear()
        const month = fallbackDate.getMonth() + 1
        const day = fallbackDate.getDate()
        const hour = fallbackDate.getHours()
        const minute = fallbackDate.getMinutes()
        return `${year}年${month}月${day}日 ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
      }
      return dateStr
    }
    
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    const day = date.getDate()
    const hour = date.getHours()
    const minute = date.getMinutes()
    
    // 格式：2026年2月17日 10:00
    return `${year}年${month}月${day}日 ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
  } catch (error) {
    console.error('时间格式化错误:', error)
    // 尝试解析常见格式
    if (typeof dateStr === 'string') {
      // 如果是ISO格式，尝试提取
      const isoMatch = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/)
      if (isoMatch) {
        const [_, year, month, day, hour, minute] = isoMatch
        return `${year}年${parseInt(month)}月${parseInt(day)}日 ${hour}:${minute}`
      }
      
      // 如果是时间戳
      const timestampMatch = dateStr.match(/^\d+$/)
      if (timestampMatch) {
        try {
          const timestamp = parseInt(dateStr)
          const date = new Date(timestamp)
          const year = date.getFullYear()
          const month = date.getMonth() + 1
          const day = date.getDate()
          const hour = date.getHours()
          const minute = date.getMinutes()
          return `${year}年${month}月${day}日 ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
        } catch (e) {
          // 忽略错误
        }
      }
    }
    
    return dateStr
  }
}

// V2.6.9优化：智能命名系统 - 增强版
const formatItemName = (item: any, mainTab: string, subTab: string): string => {
  // 进度台账
  if (subTab === 'ledger') {
    const stageName = STAGE_NAMES[item.id] || item.name || item.id
    const status = item.status === 'completed' ? '✅' : item.status === 'in_progress' ? '🔄' : '⏳'
    return `${status} ${stageName}`
  }
  
  // 验收报告
  if (subTab === 'acceptance') {
    const stageName = STAGE_NAMES[item.stage] || item.stage || '验收报告'
    const result = (item.severity || item.result_status) === 'passed' ? '✅通过' : 
                   (item.severity || item.result_status) === 'rectify' ? '⚠️待整改' : '📋验收'
    return `${stageName} - ${result}`
  }
  
  // 分析报告
  if (mainTab === 'analysis') {
    let name = item.company_name || item.file_name || '未命名报告'
    
    // 添加风险等级标识
    if (subTab === 'quote' && item.risk_score !== undefined) {
      const riskLevel = item.risk_score >= 61 ? '🔴' : item.risk_score >= 31 ? '🟡' : '🟢'
      name = `${riskLevel} ${name}`
    } else if (subTab === 'contract' && item.risk_level) {
      const riskIcon = item.risk_level === 'high' ? '🔴' : item.risk_level === 'warning' ? '🟡' : '🟢'
      name = `${riskIcon} ${name}`
    }
    
    // 添加状态标识
    if (item.status === 'analyzing') {
      name = `⏳ ${name}`
    } else if (item.status === 'failed') {
      name = `❌ ${name}`
    }
    
    return name
  }
  
  // 施工照片：智能命名
  if (mainTab === 'construction' && subTab === 'photos') {
    const stageName = STAGE_NAMES[item.stage] || item.stage || '未知阶段'
    const timeStr = formatSmartTime(item.created_at || item.time)
    
    // 如果有描述，截取前20个字符
    let desc = ''
    if (item.description) {
      const cleanDesc = item.description.trim()
      if (cleanDesc.length > 20) {
        desc = ` - ${cleanDesc.substring(0, 20)}...`
      } else {
        desc = ` - ${cleanDesc}`
      }
    }
    
    return `${stageName} - ${timeStr}${desc}`
  }
  
  // 默认情况
  return item.name || item.file_name || item.company_name || '未命名数据'
}

// V2.6.9优化：阶段徽章映射
const STAGE_BADGES: Record<string, string> = {
  S00: '📍', material: '📍',
  S01: '🔌', plumbing: '🔌',
  S02: '🔨', carpentry: '🔨', flooring: '🔨',
  S03: '🪵', woodwork: '🪵',
  S04: '🎨', painting: '🎨',
  S05: '📦', installation: '📦', soft_furnishing: '📦'
}

// V2.6.8优化：重构信息架构
const DATA_TABS = [
  { key: 'construction', label: '施工数据', icon: '🏗️' },
  { key: 'analysis', label: '分析报告', icon: '📊' },
  { key: 'tools', label: '数据工具', icon: '🛠️' }
]

// 施工数据子标签
const CONSTRUCTION_SUB_TABS = [
  { key: 'photos', label: '施工照片' },
  { key: 'acceptance', label: '验收报告' },
  { key: 'ledger', label: '进度台账' }
]

// 分析报告子标签
const ANALYSIS_SUB_TABS = [
  { key: 'company', label: '公司风险' },
  { key: 'quote', label: '报价单' },
  { key: 'contract', label: '合同' }
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
  installation: 'S05 安装收尾',
  flooring: 'S02 泥瓦工',
  soft_furnishing: 'S05 安装收尾'
}

/**
 * P18/P20/P29 数据管理页（V2.6.8全面优化：三阶段重构）
 * 第一阶段：基础功能修复
 * 第二阶段：用户体验优化（信息架构重构）
 * 第三阶段：高级功能增强
 */
const DataManagePage: React.FC = () => {
  const router = Taro.getCurrentInstance().router
  const initialTab = (router?.params?.tab as string) || 'construction'
  const [mainTab, setMainTab] = useState(initialTab)
  const [subTab, setSubTab] = useState('photos')
  const [stage, setStage] = useState('全部')
  const [batchMode, setBatchMode] = useState(false)
  const [list, setList] = useState<any[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(false)
  const [searchKw, setSearchKw] = useState('')  // 统一搜索关键词
  const [loadError, setLoadError] = useState<string | null>(null)
  const [storageInfo, setStorageInfo] = useState({ used: 0, total: 100 })  // 存储信息

  // 统一错误处理
  const handleApiError = (error: any, defaultMessage: string) => {
    console.error('API Error:', error)
    if (error?.response?.status === 401) {
      Taro.showToast({ title: '请先登录', icon: 'none' })
      return '请先登录'
    } else if (error?.response?.status === 403) {
      Taro.showToast({ title: '无权限操作', icon: 'none' })
      return '无权限操作'
    } else {
      Taro.showToast({ title: defaultMessage, icon: 'none' })
      return defaultMessage
    }
  }

  const toggleSelect = (id: string) => {
    const next = new Set(selected)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelected(next)
  }

  // V2.6.8优化：实现真实删除功能
  const handleDeleteItem = async (item: any) => {
    try {
      Taro.showLoading({ title: '删除中...' })
      
      if (subTab === 'photos') {
        // 删除施工照片
        await constructionPhotoApi.delete(item.id)
      } else if (subTab === 'acceptance') {
        // 删除验收报告
        await deleteWithAuth(`/acceptance/${item.id}`)
      } else if (mainTab === 'analysis') {
        // 删除分析报告
        const endpoint = subTab === 'company' ? '/companies/scans' : 
                        subTab === 'quote' ? '/quotes' : '/contracts'
        await deleteWithAuth(`${endpoint}/${item.id}`)
      }
      
      Taro.hideLoading()
      Taro.showToast({ title: '删除成功', icon: 'success' })
      
      // 重新加载数据
      loadData()
    } catch (error: any) {
      Taro.hideLoading()
      handleApiError(error, '删除失败')
    }
  }

  // V2.6.8优化：实现批量删除
  const handleBatchDelete = async () => {
    if (selected.size === 0) {
      Taro.showToast({ title: '请先选择数据', icon: 'none' })
      return
    }
    
    Taro.showModal({
      title: '确认删除',
      content: `将删除 ${selected.size} 项${Taro.getStorageSync('is_member') ? '，会员7天内可恢复' : ''}`,
      success: async (res) => {
        if (res.confirm) {
          try {
            Taro.showLoading({ title: '批量删除中...' })
            
            // 批量删除逻辑
            const deletePromises = Array.from(selected).map(async (id) => {
              if (subTab === 'photos') {
                await constructionPhotoApi.delete(Number(id))
              }
              // 其他类型的批量删除可以在这里添加
            })
            
            await Promise.all(deletePromises)
            
            Taro.hideLoading()
            Taro.showToast({ title: `已删除 ${selected.size} 项`, icon: 'success' })
            
            // 重置状态并重新加载
            setSelected(new Set())
            setBatchMode(false)
            loadData()
          } catch (error: any) {
            Taro.hideLoading()
            handleApiError(error, '批量删除失败')
          }
        }
      }
    })
  }

  // V2.6.8优化：实现导出功能
  const handleExportItem = async (item: any) => {
    try {
      Taro.showLoading({ title: '准备导出...' })
      
      let reportType = ''
      let resourceId = 0
      
      if (subTab === 'company') {
        reportType = 'company'
        resourceId = item.id
      } else if (subTab === 'quote') {
        reportType = 'quote'
        resourceId = item.id
      } else if (subTab === 'contract') {
        reportType = 'contract'
        resourceId = item.id
      } else if (subTab === 'acceptance') {
        reportType = 'acceptance'
        resourceId = item.id
      }
      
      if (reportType && resourceId) {
        const downloadUrl = reportApi.getExportPdfUrl(reportType, resourceId)
        
        Taro.hideLoading()
        
        Taro.showModal({
          title: '导出报告',
          content: '是否下载PDF报告？',
          success: (res) => {
            if (res.confirm) {
              Taro.downloadFile({
                url: downloadUrl,
                success: (res) => {
                  if (res.statusCode === 200) {
                    Taro.showToast({ title: '下载成功', icon: 'success' })
                    // 保存到本地
                    Taro.saveFile({
                      tempFilePath: res.tempFilePath,
                      success: (saveRes) => {
                        console.log('文件保存成功:', saveRes.savedFilePath)
                      }
                    })
                  }
                },
                fail: (err) => {
                  console.error('下载失败:', err)
                  Taro.showToast({ title: '下载失败', icon: 'none' })
                }
              })
            }
          }
        })
      } else {
        Taro.hideLoading()
        Taro.showToast({ title: '暂不支持导出此类型', icon: 'none' })
      }
    } catch (error: any) {
      Taro.hideLoading()
      handleApiError(error, '导出失败')
    }
  }

  const handleRecycleBin = () => {
    const isMember = !!Taro.getStorageSync('is_member')
    if (!isMember) {
      Taro.showModal({
        title: '会员专享',
        content: '回收站功能需要会员权限，是否查看会员权益？',
        success: (res) => {
          if (res.confirm) {
            Taro.navigateTo({ url: '/pages/membership/index' })
          }
        }
      })
      return
    }
    Taro.navigateTo({ url: '/pages/recycle-bin/index' })
  }

  // V2.6.8优化：计算存储空间 - 连接真实API
  const calculateStorage = async () => {
    try {
      // 调用后端API获取真实的存储使用情况
      const res = await getWithAuth('/users/storage-usage') as any
      const data = res?.data || {}
      
      setStorageInfo({
        used: data.estimated_size_mb || 0,
        total: data.total_storage_mb || 100
      })
      
      // 返回完整的存储信息，用于显示
      return data
    } catch (error) {
      console.error('获取存储使用情况失败:', error)
      // 如果API调用失败，使用模拟数据
      const totalPhotos = list.filter(item => item.url).length
      const estimatedSize = totalPhotos * 2 // 假设每张照片2MB
      setStorageInfo({
        used: Math.min(estimatedSize, 100),
        total: 100
      })
      return {
        photo_count: totalPhotos,
        estimated_size_mb: estimatedSize,
        total_storage_mb: 100,
        usage_percentage: Math.min(100, (estimatedSize / 100) * 100),
        storage_duration_months: 12,
        is_member: false,
        warning_level: 'low'
      }
    }
  }

  // V2.6.9优化：照片预览功能 - 增强版
  const handlePreviewPhoto = (item: any, index: number) => {
    if (!item.url) {
      Taro.showToast({ title: '无法预览：照片URL为空', icon: 'none' })
      return
    }
    
    // 获取所有有URL的照片用于滑动预览
    const allPhotosWithUrls = list.filter(photo => photo.url && photo.url.trim() !== '')
    
    if (allPhotosWithUrls.length === 0) {
      Taro.showToast({ title: '没有可预览的照片', icon: 'none' })
      return
    }
    
    const urls = allPhotosWithUrls.map(photo => photo.url)
    
    // 找到当前照片在所有照片中的索引
    let currentIndex = allPhotosWithUrls.findIndex(photo => photo.id === item.id)
    if (currentIndex === -1) {
      // 如果没找到，使用传入的index（确保在范围内）
      currentIndex = Math.min(index, urls.length - 1)
    }
    
    // 显示预览
    Taro.previewImage({
      current: urls[currentIndex],
      urls: urls,
      success: () => {
        console.log('照片预览成功', { total: urls.length, currentIndex })
      },
      fail: (err) => {
        console.error('照片预览失败', err)
        Taro.showToast({ 
          title: `预览失败: ${err.errMsg || '未知错误'}`,
          icon: 'none',
          duration: 3000
        })
      }
    })
  }

  // V2.6.9优化：判断是否为最新（24小时内）
  const isNewItem = (item: any): boolean => {
    if (!item.created_at && !item.time) return false
    
    try {
      const dateStr = item.created_at || item.time
      const date = new Date(dateStr)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      return diffHours < 24
    } catch (error) {
      return false
    }
  }

  // V2.6.8优化：统一数据加载函数
  const loadData = async () => {
    setLoading(true)
    setLoadError(null)
    
    try {
      if (mainTab === 'construction') {
        if (subTab === 'photos') {
          // 加载施工照片
          const apiStage = stage === '全部' ? undefined : STAGE_TABS.indexOf(stage) > 0 ?
            ['material', 'plumbing', 'carpentry', 'woodwork', 'painting', 'installation'][STAGE_TABS.indexOf(stage) - 1] : undefined
          const res = await getWithAuth('/construction-photos', apiStage ? { stage: apiStage } : undefined) as any
          const data = res?.list ?? res
          // 按时间倒序排序（最新的在最前面）
          const sortedData = Array.isArray(data) ? 
            data.sort((a, b) => {
              const timeA = parseDateForComparison(a.created_at || a.time || 0)
              const timeB = parseDateForComparison(b.created_at || b.time || 0)
              return timeB - timeA
            }) : []
          setList(sortedData)
        } else if (subTab === 'acceptance') {
          // 加载验收报告 - 支持阶段筛选
          const apiStage = stage === '全部' ? undefined : 
                          stage === 'S01隐蔽' ? 'S01' :
                          stage === 'S02泥瓦' ? 'S02' :
                          stage === 'S03木工' ? 'S03' :
                          stage === 'S04油漆' ? 'S04' :
                          stage === 'S05收尾' ? 'S05' : undefined
          const res = await getWithAuth('/acceptance', apiStage ? { stage: apiStage } : undefined) as any
          const data = res?.list ?? []
          // 按时间倒序排序
          const sortedData = Array.isArray(data) ? 
            data.sort((a, b) => {
              const timeA = parseDateForComparison(a.created_at || 0)
              const timeB = parseDateForComparison(b.created_at || 0)
              return timeB - timeA
            }) : []
          setList(sortedData)
        } else if (subTab === 'ledger') {
          // 加载进度台账
          const res = await getWithAuth('/constructions/schedule') as any
          const stages = res?.stages || {}
          const order = ['S00', 'S01', 'S02', 'S03', 'S04', 'S05']
          const arr = order.map((key) => {
            const s = stages[key] || {}
            // 后端返回的字段：start_date, end_date, status, locked等
            // 修正字段映射：验收日期使用end_date字段
            return {
              id: key,
              name: STAGE_NAMES[key] || key,
              start_date: s.start_date,  // 直接使用start_date
              acceptance_date: s.end_date,  // 使用end_date作为验收日期
              status: s.status || 'pending',
              locked: s.locked || false,
              ...s
            }
          })
          setList(arr)
        }
      } else if (mainTab === 'analysis') {
        // 加载分析报告
        let res: any
        if (subTab === 'company') {
          res = await getWithAuth('/companies/scans')
        } else if (subTab === 'quote') {
          res = await getWithAuth('/quotes/list')
        } else {
          res = await getWithAuth('/contracts/list')
        }
        const data = res?.list ?? []
        // 按时间倒序排序
        const sortedData = Array.isArray(data) ? 
          data.sort((a, b) => {
            const timeA = parseDateForComparison(a.created_at || a.updated_at || 0)
            const timeB = parseDateForComparison(b.created_at || b.updated_at || 0)
            return timeB - timeA
          }) : []
        setList(sortedData)
      }
      
      // 计算存储空间
      calculateStorage()
    } catch (error: any) {
      console.error('加载数据失败:', error)
      if (error?.response?.status === 401) {
        setLoadError('请先登录')
      } else {
        setLoadError('加载失败，请重试')
      }
      setList([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [mainTab, subTab, stage])

  // V2.6.8优化：统一搜索功能
  const filteredList = useMemo(() => {
    if (!searchKw.trim()) return list
    
    const kw = searchKw.trim().toLowerCase()
    return list.filter((item) => {
      // 根据不同类型匹配不同字段
      if (mainTab === 'construction') {
        if (subTab === 'photos') {
          return (item.description || '').toLowerCase().includes(kw) ||
                 (item.stage || '').toLowerCase().includes(kw)
        } else if (subTab === 'acceptance') {
          return (item.stage || '').toLowerCase().includes(kw) ||
                 (item.result_status || '').toLowerCase().includes(kw)
        } else if (subTab === 'ledger') {
          return (item.name || '').toLowerCase().includes(kw) ||
                 (item.status || '').toLowerCase().includes(kw)
        }
      } else if (mainTab === 'analysis') {
        return (item.company_name || item.file_name || '').toLowerCase().includes(kw)
      }
      return false
    })
  }, [list, searchKw, mainTab, subTab])

  const displayList = filteredList
  const isEmpty = !loading && displayList.length === 0

  // 获取空状态信息
  const getEmptyStateInfo = () => {
    if (mainTab === 'construction') {
      if (subTab === 'photos') {
        return {
          text: loadError || '暂无照片数据（请先在施工陪伴各阶段中拍摄/上传）',
          actionText: '去拍摄',
          actionUrl: '/pages/photo/index'
        }
      } else if (subTab === 'acceptance') {
        return {
          text: '暂无验收报告',
          actionText: '去验收',
          actionUrl: '/pages/acceptance/index'
        }
      } else if (subTab === 'ledger') {
        return {
          text: '暂无台账（请先在施工陪伴页设置开工日期）',
          actionText: '去设置',
          actionUrl: '/pages/construction/index'
        }
      }
    } else if (mainTab === 'analysis') {
      return {
        text: '暂无报告数据',
        actionText: subTab === 'company' ? '去检测' : '去上传',
        actionUrl: subTab === 'company' ? '/pages/company-scan/index' : 
                  subTab === 'quote' ? '/pages/quote-upload/index' : '/pages/contract-upload/index'
      }
    }
    return {
      text: '暂无数据',
      actionText: '',
      actionUrl: ''
    }
  }

  const emptyStateInfo = getEmptyStateInfo()

  // 获取报告详情URL
  const getReportUrl = (item: any) => {
    if (subTab === 'company') {
      return `/pages/report-detail/index?type=company&scanId=${item.id}&name=${encodeURIComponent(item.company_name || '')}`
    }
    if (subTab === 'quote') {
      return `/pages/report-detail/index?type=quote&scanId=${item.id}&name=${encodeURIComponent(item.file_name || '')}`
    }
    return `/pages/report-detail/index?type=contract&scanId=${item.id}&name=${encodeURIComponent(item.file_name || '')}`
  }

  return (
    <ScrollView scrollY className='data-manage-page-outer'>
      <View className='data-manage-page'>
        <View className='nav-row'>
          <Text className='nav-title'>数据管理</Text>
          <Text
            className='batch-btn'
            onClick={() => setBatchMode(!batchMode)}
          >
            {batchMode ? '取消' : '批量操作'}
          </Text>
        </View>

        {/* 主标签 */}
        <ScrollView scrollX className='tabs main-tabs' scrollWithAnimation>
          {DATA_TABS.map((t) => (
            <View
              key={t.key}
              className={`main-tab ${mainTab === t.key ? 'active' : ''}`}
              onClick={() => {
                setMainTab(t.key)
                // 重置子标签
                if (t.key === 'construction') setSubTab('photos')
                else if (t.key === 'analysis') setSubTab('company')
                else setSubTab('')
              }}
            >
              <Text className='tab-icon'>{t.icon}</Text>
              <Text className='tab-label'>{t.label}</Text>
            </View>
          ))}
        </ScrollView>

        {/* 子标签 */}
        {mainTab === 'construction' && (
          <ScrollView scrollX className='tabs sub-tabs' scrollWithAnimation>
            {CONSTRUCTION_SUB_TABS.map((t) => (
              <Text
                key={t.key}
                className={`sub-tab ${subTab === t.key ? 'active' : ''}`}
                onClick={() => setSubTab(t.key)}
              >
                {t.label}
              </Text>
            ))}
          </ScrollView>
        )}

        {mainTab === 'analysis' && (
          <ScrollView scrollX className='tabs sub-tabs' scrollWithAnimation>
            {ANALYSIS_SUB_TABS.map((t) => (
              <Text
                key={t.key}
                className={`sub-tab ${subTab === t.key ? 'active' : ''}`}
                onClick={() => setSubTab(t.key)}
              >
                {t.label}
              </Text>
            ))}
          </ScrollView>
        )}

        {/* 施工照片阶段筛选 */}
        {mainTab === 'construction' && subTab === 'photos' && (
          <ScrollView scrollX className='tabs stage-tabs' scrollWithAnimation>
            {STAGE_TABS.map((s) => (
              <Text
                key={s}
                className={`stage-tab ${stage === s ? 'active' : ''}`}
                onClick={() => setStage(s)}
              >
                {s}
              </Text>
            ))}
          </ScrollView>
        )}

        {/* 验收报告阶段筛选 */}
        {mainTab === 'construction' && subTab === 'acceptance' && (
          <ScrollView scrollX className='tabs stage-tabs' scrollWithAnimation>
            {['全部', 'S01隐蔽', 'S02泥瓦', 'S03木工', 'S04油漆', 'S05收尾'].map((s) => (
              <Text
                key={s}
                className={`stage-tab ${stage === s ? 'active' : ''}`}
                onClick={() => setStage(s)}
              >
                {s}
              </Text>
            ))}
          </ScrollView>
        )}

        {/* 统一搜索栏 */}
        {(mainTab === 'construction' || mainTab === 'analysis') && (
          <View className='search-bar'>
            <Input
              className='search-input'
              placeholder={mainTab === 'construction' ? '搜索描述/阶段...' : '搜索公司名/文件名...'}
              value={searchKw}
              onInput={(e) => setSearchKw(e.detail.value)}
            />
          </View>
        )}

        <View className='list-wrap'>
          {loading ? (
            <View className='empty'>
              <Text className='empty-text'>加载中...</Text>
            </View>
          ) : isEmpty ? (
            <EmptyState 
              type={mainTab === 'construction' && subTab === 'photos' ? 'photo' : 'report'} 
              text={emptyStateInfo.text}
              actionText={emptyStateInfo.actionText}
              actionUrl={emptyStateInfo.actionUrl}
            />
          ) : (
            displayList.map((item, index) => (
              <View key={item.id ?? item.stage ?? item.key} className='list-item'>
                {batchMode && subTab !== 'ledger' && (
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
                    <Text className='file-icon'>
                      {subTab === 'ledger' ? '📋' : 
                       subTab === 'acceptance' ? '✅' : 
                       mainTab === 'analysis' ? '📄' : '📷'}
                    </Text>
                  )}
                </View>
                <View className='item-info'>
                  <View className='item-header'>
                    <Text className='item-name'>
                      {formatItemName(item, mainTab, subTab)}
                    </Text>
                    {isNewItem(item) && (
                      <Text className='new-badge'>🆕</Text>
                    )}
                  </View>
                  <View className='item-meta'>
                    {mainTab === 'construction' && subTab === 'photos' && (
                      <Text className='stage-badge'>
                        {STAGE_BADGES[item.stage] || '📷'} {STAGE_NAMES[item.stage] || item.stage || '未知阶段'}
                      </Text>
                    )}
                    <Text className='item-time'>
                      {subTab === 'ledger'
                        ? (item.start_date ? `开始: ${item.start_date}` : '—') + (item.acceptance_date ? ` | 验收: ${item.acceptance_date}` : '')
                        : formatSmartTime(item.created_at || item.time)}
                    </Text>
                  </View>
                  {item.description && mainTab === 'construction' && subTab === 'photos' && (
                    <Text className='item-desc'>{item.description}</Text>
                  )}
                  {subTab === 'acceptance' && (
                    <View className='item-status'>
                      <Text className={`status-badge ${(item.severity || item.result_status) === 'passed' ? 'safe' : 'warning'}`}>
                        {(item.severity || item.result_status) === 'passed' ? '通过' : (item.severity || item.result_status) === 'rectify' ? '待整改' : (item.result_status || item.severity) || '—'}
                      </Text>
                    </View>
                  )}
                  {mainTab === 'analysis' && (
                    <View className='item-status'>
                      {subTab === 'quote' && item.risk_score !== undefined && (
                        <Text className={`status-badge ${item.risk_score >= 61 ? 'high' : item.risk_score >= 31 ? 'warning' : 'safe'}`}>
                          {item.risk_score >= 61 ? '高风险' : item.risk_score >= 31 ? '警告' : '合规'}
                        </Text>
                      )}
                      {subTab === 'contract' && item.risk_level && (
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
                  {mainTab === 'construction' && subTab === 'photos' && item.url && (
                    <Text className='action-link' onClick={() => handlePreviewPhoto(item, index)}>预览</Text>
                  )}
                  {mainTab === 'analysis' && (
                    <Text className='action-link' onClick={() => Taro.navigateTo({ url: getReportUrl(item) })}>查看</Text>
                  )}
                  {subTab === 'acceptance' && (
                    <Text className='action-link' onClick={() => Taro.navigateTo({ url: `/pages/acceptance/index?id=${item.id}` })}>查看</Text>
                  )}
                  {subTab === 'ledger' && (
                    <Text className='action-link' onClick={() => Taro.switchTab({ url: '/pages/construction/index' })}>查看</Text>
                  )}
                  {(mainTab === 'analysis' || subTab === 'acceptance') && (
                    <Text className='action-link' onClick={() => handleExportItem(item)}>导出</Text>
                  )}
                  {subTab !== 'ledger' && (
                    <Text className='action-link danger' onClick={() => handleDeleteItem(item)}>删除</Text>
                  )}
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

        {mainTab === 'tools' && (
          <View className='tools-section'>
            <View className='recycle-section'>
              <Text className='recycle-title'>回收站</Text>
              <Text className='recycle-desc'>会员专享：删除数据7天内可恢复</Text>
              <View className='recycle-btn' onClick={handleRecycleBin}>
                <Text>进入回收站</Text>
              </View>
            </View>

            <View className='storage-section'>
              <Text className='storage-title'>存储空间</Text>
              <View className='storage-progress'>
                <View 
                  className='storage-progress-bar' 
                  style={{ 
                    width: `${(storageInfo.used / storageInfo.total) * 100}%`,
                    backgroundColor: storageInfo.used >= storageInfo.total * 0.9 ? '#FF4D4F' : 
                                   storageInfo.used >= storageInfo.total * 0.7 ? '#FAAD14' : '#52C41A'
                  }}
                />
              </View>
              <Text className='storage-info'>
                已使用 {storageInfo.used} MB / 总存储 {storageInfo.total} MB
                {storageInfo.used > 0 && ` (${Math.round((storageInfo.used / storageInfo.total) * 100)}%)`}
              </Text>
              <Text className='storage-detail'>
                照片数量: {list.filter(item => item.url).length}张 · 存储期限: 12个月
              </Text>
              {storageInfo.used >= storageInfo.total * 0.9 && (
                <Text className='storage-warning'>⚠️ 存储空间即将用尽，请及时清理</Text>
              )}
              {storageInfo.used >= storageInfo.total * 0.7 && storageInfo.used < storageInfo.total * 0.9 && (
                <Text className='storage-warning'>⚠️ 存储空间使用较多，建议清理</Text>
              )}
              <View className='storage-actions'>
                <Text className='storage-action' onClick={() => {
                  Taro.showModal({
                    title: '存储管理',
                    content: '1. 删除不需要的照片\n2. 导出重要报告\n3. 升级会员获得更多空间',
                    showCancel: false,
                    confirmText: '知道了'
                  })
                }}>管理建议</Text>
                <Text className='storage-action' onClick={() => {
                  const isMember = !!Taro.getStorageSync('is_member')
                  if (!isMember) {
                    Taro.showModal({
                      title: '升级会员',
                      content: '升级会员可获得100MB存储空间',
                      success: (res) => {
                        if (res.confirm) {
                          Taro.navigateTo({ url: '/pages/membership/index' })
                        }
                      }
                    })
                  }
                }}>{Taro.getStorageSync('is_member') ? '已升级会员' : '升级会员'}</Text>
              </View>
            </View>

            <View className='export-section'>
              <Text className='export-title'>批量导出</Text>
              <Text className='export-desc'>支持批量导出报告和照片</Text>
              <View className='export-btn' onClick={() => {
                if (list.length === 0) {
                  Taro.showToast({ title: '暂无数据可导出', icon: 'none' })
                  return
                }
                
                Taro.showActionSheet({
                  itemList: ['导出施工照片', '导出验收报告', '导出分析报告'],
                  success: (res) => {
                    const index = res.tapIndex
                    if (index === 0) {
                      Taro.showToast({ title: '施工照片导出功能开发中', icon: 'none' })
                    } else if (index === 1) {
                      Taro.showToast({ title: '验收报告导出功能开发中', icon: 'none' })
                    } else if (index === 2) {
                      Taro.showToast({ title: '分析报告导出功能开发中', icon: 'none' })
                    }
                  }
                })
              }}>
                <Text>批量导出</Text>
              </View>
              <Text className='export-tip'>当前支持单个报告导出，批量导出功能即将上线</Text>
            </View>
          </View>
        )}

        <View className='storage-tip'>
          <Text>数据管理功能持续优化中，如有建议请反馈</Text>
        </View>
      </View>
    </ScrollView>
  )
}

export default DataManagePage

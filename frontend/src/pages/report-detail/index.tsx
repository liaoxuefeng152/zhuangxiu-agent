import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import { reportApi, getWithAuth } from '../../services/api'
import './index.scss'

// 公司信息摘要（只展示数据统计，不做评价）
const COMPANY_SUMMARY_TEXT: Record<string, string> = {
  legal_cases: '📋 法律案件',
  enterprise_info: '🏢 企业信息',
  decoration_cases: '🔨 装修相关',
  case_types: '📊 案件类型',
  recent_cases: '📅 最近案件'
}

// 风险等级展示（使用中性表述）
const RISK_TEXT: Record<string, string> = {
  high: '⚠️ 需关注',
  warning: '⚠️ 一般关注',
  compliant: '✅ 合规',
  failed: '❌ AI分析失败'
}

// 生成公司数据摘要
function generateCompanyDataSummary(enterpriseInfo: any, legalAnalysis: any): string {
  if (!enterpriseInfo && !legalAnalysis) return '暂无公司信息'
  
  const summaries: string[] = []
  
  if (enterpriseInfo) {
    if (enterpriseInfo.enterprise_age !== undefined) {
      summaries.push(`企业年龄：${enterpriseInfo.enterprise_age}年`)
    }
    if (enterpriseInfo.start_date) {
      summaries.push(`成立时间：${enterpriseInfo.start_date}`)
    }
  }
  
  if (legalAnalysis) {
    if (legalAnalysis.legal_case_count !== undefined) {
      summaries.push(`法律案件：${legalAnalysis.legal_case_count}件`)
    }
    if (legalAnalysis.decoration_related_cases !== undefined) {
      summaries.push(`装修相关：${legalAnalysis.decoration_related_cases}件`)
    }
  }
  
  return summaries.length > 0 ? summaries.join(' | ') : '基础信息完整'
}

/** 解析后端 created_at：若字符串无时区后缀则视为 UTC，保证显示为正确的本地时间 */
function formatCreatedAt (raw: string | null | undefined): string {
  if (!raw) return '—'
  const s = String(raw).trim()
  if (!s) return '—'
  // 无 Z 或 +/- 时区则视为 UTC（与后端序列化约定一致）
  const hasTz = /[Zz]$|[+-]\d{2}:?\d{2}$/.test(s)
  const asUtc = hasTz ? s : s + 'Z'
  try {
    const d = new Date(asUtc)
    if (isNaN(d.getTime())) return '—'
    return d.toLocaleString('zh-CN')
  } catch {
    return '—'
  }
}

/** 将后端合同分析结果转为报告页用的 { tag, text } 列表 */
function mapContractToItems (data: {
  risk_items?: Array<{ term?: string; description?: string; risk_level?: string; category?: string }>
  high_risk_clauses?: Array<{ clause?: string; reason?: string }>
  unfair_terms?: Array<{ term?: string; description?: string; modification?: string }>
  unfair_clauses?: Array<{ clause?: string; reason?: string }>
  missing_terms?: Array<{ term?: string; reason?: string; importance?: string }>
  missing_clauses?: Array<{ clause?: string; suggestion?: string }>
  suggested_modifications?: Array<{ original?: string; modified?: string; reason?: string }>
  suggestions?: Array<string>
  result_json?: {
    risk_items?: Array<any>
    high_risk_clauses?: Array<any>
    unfair_terms?: Array<any>
    unfair_clauses?: Array<any>
    missing_terms?: Array<any>
    missing_clauses?: Array<any>
    suggested_modifications?: Array<any>
    suggestions?: Array<string>
    summary?: string
  }
}): Array<{ tag: string; text: string }> {
  const items: Array<{ tag: string; text: string }> = []
  
  // 优先使用result_json中的数据，如果没有则使用顶层字段
  const resultJson = data.result_json || {}
  
  // 风险条款：支持 risk_items (term+description) 和 high_risk_clauses (clause+reason)
  const riskItems = resultJson.risk_items || data.risk_items || resultJson.high_risk_clauses || data.high_risk_clauses || []
  riskItems.forEach((it: any) => {
    // 优先使用 term+description，其次使用 clause+reason
    const title = it.term || it.clause || ''
    const desc = it.description || it.reason || ''
    if (title || desc) {
      const text = title ? `${title}：${desc}` : desc
      items.push({ tag: '风险条款', text: text.slice(0, 120) })
    }
  })
  
  // 不公平条款：支持 unfair_terms (term+description) 和 unfair_clauses (clause+reason)
  const unfairTerms = resultJson.unfair_terms || data.unfair_terms || resultJson.unfair_clauses || data.unfair_clauses || []
  unfairTerms.forEach((it: any) => {
    // 优先使用 term+description，其次使用 clause+reason
    const title = it.term || it.clause || ''
    const desc = it.description || it.reason || ''
    if (title || desc) {
      const text = title ? `${title}：${desc}` : desc
      items.push({ tag: '不公平条款', text: text.slice(0, 120) })
    }
  })
  
  // 缺失条款：支持 missing_terms (term+reason) 和 missing_clauses (clause+suggestion)
  const missingTerms = resultJson.missing_terms || data.missing_terms || resultJson.missing_clauses || data.missing_clauses || []
  missingTerms.forEach((it: any) => {
    // 优先使用 term+reason，其次使用 clause+suggestion
    const title = it.term || it.clause || ''
    const desc = it.reason || it.suggestion || ''
    const importance = it.importance || '中'
    if (title || desc) {
      const text = title ? `${title}（${importance}）：${desc}` : `（${importance}）${desc}`
      items.push({ tag: '缺失条款', text: text.slice(0, 120) })
    }
  })
  
  // 修改建议：支持 suggested_modifications (original+modified+reason) 和 suggestions (字符串数组)
  const modifications = resultJson.suggested_modifications || data.suggested_modifications || []
  modifications.forEach((it: any) => {
    if (typeof it === 'object' && it !== null) {
      // 对象格式：{original, modified, reason}
      const modified = it.modified || it.action || ''
      const reason = it.reason || ''
      if (modified || reason) {
        const text = modified ? `${modified}：${reason}` : reason
        items.push({ tag: '修改建议', text: text.slice(0, 120) })
      }
    }
  })
  
  // 通用建议（字符串数组）
  const suggestions = resultJson.suggestions || data.suggestions || []
  suggestions.forEach((suggestion: any) => {
    if (typeof suggestion === 'string' && suggestion.trim()) {
      items.push({ tag: '建议', text: suggestion.slice(0, 120) })
    }
  })
  
  return items
}

/** 将后端报价单分析结果转为报告页用的 { tag, text } 列表 */
function mapQuoteToItems (data: {
  high_risk_items?: Array<{ category?: string; item?: string; description?: string; impact?: string; suggestion?: string }>
  warning_items?: Array<{ category?: string; item?: string; description?: string; suggestion?: string }>
  missing_items?: Array<{ item?: string; importance?: string; reason?: string }>
  overpriced_items?: Array<{ item?: string; quoted_price?: number; market_ref_price?: string; price_diff?: string }>
  suggestions?: string[]
  result_json?: {
    high_risk_items?: Array<any>
    warning_items?: Array<any>
    missing_items?: Array<any>
    overpriced_items?: Array<any>
    suggestions?: string[]
  }
}): Array<{ tag: string; text: string }> {
  const items: Array<{ tag: string; text: string }> = []
  
  // 优先使用result_json中的数据，如果没有则使用顶层字段
  const resultJson = data.result_json || {}
  const highRiskItems = resultJson.high_risk_items || data.high_risk_items || []
  const warningItems = resultJson.warning_items || data.warning_items || []
  const missingItems = resultJson.missing_items || data.missing_items || []
  const overpricedItems = resultJson.overpriced_items || data.overpriced_items || []
  const suggestions = resultJson.suggestions || data.suggestions || []
  
  // 高风险项 -> "漏项"或"高风险"
  highRiskItems.forEach((it: any) => {
    const tag = it.category === '漏项' ? '漏项' : '高风险'
    const text = `${it.item || ''}：${it.description || ''}${it.impact ? `（${it.impact}）` : ''}`
    items.push({ tag, text: text.slice(0, 120) })
  })
  
  // 警告项 -> "警告"或"虚高"
  warningItems.forEach((it: any) => {
    const tag = it.category === '虚高' ? '虚高' : '警告'
    const text = `${it.item || ''}：${it.description || ''}`
    items.push({ tag, text: text.slice(0, 120) })
  })
  
  // 漏项
  missingItems.forEach((it: any) => {
    const text = `${it.item || ''}（${it.importance || '中'}）：${it.reason || ''}`
    items.push({ tag: '漏项', text: text.slice(0, 120) })
  })
  
  // 虚高项
  overpricedItems.forEach((it: any) => {
    const text = `${it.item || ''}：报价${it.quoted_price || ''}元，${it.market_ref_price || ''}，${it.price_diff || ''}`
    items.push({ tag: '虚高', text: text.slice(0, 120) })
  })
  
  // 建议
  suggestions.forEach((suggestion: string) => {
    items.push({ tag: '建议', text: suggestion.slice(0, 120) })
  })
  
  return items
}

/**
 * P06/P08/P11-P13 报告详情/预览页 - 30%预览+灰色遮挡+解锁
 * 合同类型时拉取 GET /contracts/contract/:id，与后端字段 risk_level/risk_items/unfair_terms 等对齐
 */
const ReportDetailPage: React.FC = () => {
  const [report, setReport] = useState<any>(null)
  const [unlocked, setUnlocked] = useState(false)
  const [analysisFailed, setAnalysisFailed] = useState(false)
  const [pageParams, setPageParams] = useState<Record<string, string>>(() => {
    try {
      const inst = Taro.getCurrentInstance()
      const p = inst?.router?.params
      return (p && typeof p === 'object' && !Array.isArray(p) ? { ...p } : {}) as Record<string, string>
    } catch {
      return {}
    }
  })
  useDidShow(() => {
    try {
      const inst = Taro.getCurrentInstance()
      const p = inst?.router?.params
      const plain = (p && typeof p === 'object' && !Array.isArray(p) ? { ...p } : {}) as Record<string, string>
      setPageParams(prev => (JSON.stringify(prev) === JSON.stringify(plain) ? prev : plain))
    } catch (_) {}
  })
  const type = (pageParams?.type ?? pageParams?.Type ?? '') as string
  const scanId = String(pageParams?.scanId ?? pageParams?.scanid ?? pageParams?.ScanId ?? '')
  const name = pageParams?.name

  const titles: Record<string, string> = {
    company: '公司信息报告',
    quote: '报价单分析报告',
    contract: '合同审核报告'
  }

  // 不再使用硬编码的示例数据
  // 所有数据都从API获取，如果API失败则显示错误信息

  useEffect(() => {
    setAnalysisFailed(false)
    const key = `report_unlocked_${type}_${scanId || '0'}`
    setUnlocked(!!Taro.getStorageSync(key))

    // 合同类型：调用API获取分析结果
    if (type === 'contract' && scanId) {
      // 检查scanId是否有效（必须大于0）
      const contractId = Number(scanId)
      if (!contractId || contractId <= 0) {
        console.warn('获取合同分析结果失败: 无效的合同ID', scanId)
        // API失败时显示空数据
        setAnalysisFailed(true)
        setReport({
          time: '—',
          reportNo: 'R-C-' + (scanId || '0'),
          riskLevel: 'failed',
          riskText: RISK_TEXT.failed,
          items: [],
          previewCount: 0,
          summary: '无效的合同ID'
        })
        return
      }
      
      // 检查是否已登录
      const token = Taro.getStorageSync('access_token')
      if (!token) {
        console.warn('获取合同分析结果失败: 未登录')
        // 未登录时显示错误信息
        setAnalysisFailed(true)
        setReport({
          time: '—',
          reportNo: 'R-C-' + scanId,
          riskLevel: 'failed',
          riskText: RISK_TEXT.failed,
          items: [],
          previewCount: 0,
          summary: '请先登录后查看完整报告'
        })
        return
      }
      getWithAuth(`/contracts/contract/${contractId}`)
        .then((data: any) => {
          if (data && typeof data.is_unlocked === 'boolean') setUnlocked(data.is_unlocked)
          else setUnlocked(!!Taro.getStorageSync(`report_unlocked_contract_${scanId || '0'}`))
          const summaryText = data.result_json?.summary || data.summary || ''
          const isFallbackResult = summaryText === 'AI分析服务暂时不可用，请稍后重试'
          if (data?.status === 'failed' || isFallbackResult) {
            setAnalysisFailed(true)
            setReport({
              time: formatCreatedAt(data.created_at),
              reportNo: 'R-C-' + (data.id || scanId),
              riskLevel: 'failed',
              riskText: RISK_TEXT.failed,
              items: [],
              previewCount: 0,
              summary: 'AI分析失败，请重新上传或稍后重试'
            })
            return
          }
          const riskLevel = (data.risk_level || 'compliant') as string
          const items = mapContractToItems(data)
          const previewCount = Math.max(1, Math.ceil(items.length * 0.3))
          
          // 生成摘要：优先使用result_json中的summary，如果没有则使用顶层summary
          const summary = summaryText || (items.length > 0 ? `发现${items.length}项风险和建议` : '分析完成')
          
          setReport({
            time: formatCreatedAt(data.created_at),
            reportNo: 'R-C-' + (data.id || scanId),
            riskLevel,
            riskText: RISK_TEXT[riskLevel] || RISK_TEXT.compliant,
            items: items.length ? items : [],
            previewCount,
            summary
          })
        })
        .catch((err: any) => {
          console.error('获取合同分析结果失败:', err)
          // 401错误表示未登录或token失效，不强制跳转
          if (err?.response?.status === 401 || err?.message?.includes('401')) {
            console.warn('获取合同分析结果失败: 认证失败')
          }
          // 失败时显示错误信息
          setAnalysisFailed(true)
          setReport({
            time: '—',
            reportNo: 'R-C-' + scanId,
            riskLevel: 'failed',
            riskText: RISK_TEXT.failed,
            items: [],
            previewCount: 0,
            summary: '获取分析结果失败，请稍后重试'
          })
        })
      return
    }

    // 报价单类型：调用API获取分析结果
    if (type === 'quote' && scanId) {
      // 检查scanId是否有效（必须大于0）
      const quoteId = Number(scanId)
      if (!quoteId || quoteId <= 0 || isNaN(quoteId)) {
        console.warn('获取报价单分析结果失败: 无效的报价单ID', scanId)
        // API失败时显示空数据
        setAnalysisFailed(true)
        setReport({
          time: '—',
          reportNo: 'R-Q-' + (scanId || '0'),
          riskLevel: 'failed',
          riskText: RISK_TEXT.failed,
          items: [],
          previewCount: 0,
          summary: '无效的报价单ID'
        })
        return
      }
      
      // 检查是否已登录
      const token = Taro.getStorageSync('access_token')
      if (!token) {
        console.warn('获取报价单分析结果失败: 未登录')
        // 未登录时显示错误信息
        setAnalysisFailed(true)
        setReport({
          time: '—',
          reportNo: 'R-Q-' + scanId,
          riskLevel: 'failed',
          riskText: RISK_TEXT.failed,
          items: [],
          previewCount: 0,
          summary: '请先登录后查看完整报告'
        })
        return
      }
      
      getWithAuth(`/quotes/quote/${quoteId}`)
        .then((data: any) => {
          if (data && typeof data.is_unlocked === 'boolean') setUnlocked(data.is_unlocked)
          else setUnlocked(!!Taro.getStorageSync(`report_unlocked_quote_${scanId || '0'}`))
          const quoteSuggestions = data.result_json?.suggestions || data.suggestions
          const quoteFallbackMsg = Array.isArray(quoteSuggestions) && quoteSuggestions[0] === 'AI分析服务暂时不可用，请稍后重试'
          if (data?.status === 'failed' || quoteFallbackMsg) {
            setAnalysisFailed(true)
            setReport({
              time: formatCreatedAt(data.created_at),
              reportNo: 'R-Q-' + (data.id || scanId),
              riskLevel: 'failed',
              riskText: RISK_TEXT.failed,
              items: [],
              previewCount: 0,
              summary: 'AI分析失败，请重新上传或稍后重试'
            })
            return
          }
          const riskScore = data.risk_score || 0
          let riskLevel: string
          if (riskScore >= 61) {
            riskLevel = 'high'
          } else if (riskScore >= 31) {
            riskLevel = 'warning'
          } else {
            riskLevel = 'compliant'
          }
          
          const items = mapQuoteToItems(data)
          const previewCount = Math.max(1, Math.ceil(items.length * 0.3))
          
          // 生成摘要
          const summary = data.result_json?.suggestions?.[0] || 
                         (items.length > 0 ? `发现${items.length}项风险和建议` : '分析完成')
          
          setReport({
            time: formatCreatedAt(data.created_at),
            reportNo: 'R-Q-' + (data.id || scanId),
            riskLevel,
            riskText: RISK_TEXT[riskLevel] || RISK_TEXT.compliant,
            items: items.length ? items : [],
            previewCount,
            summary
          })
        })
        .catch((err: any) => {
          console.error('获取报价单分析结果失败:', err)
          // 401错误表示未登录或token失效
          if (err?.response?.status === 401 || err?.message?.includes('401')) {
            console.warn('获取报价单分析结果失败: 认证失败')
          }
          // 失败时显示错误信息
          setAnalysisFailed(true)
          setReport({
            time: '—',
            reportNo: 'R-Q-' + scanId,
            riskLevel: 'failed',
            riskText: RISK_TEXT.failed,
            items: [],
            previewCount: 0,
            summary: '获取分析结果失败，请稍后重试'
          })
        })
      return
    }

    // 公司检测：拉取扫描结果并同步后端 is_unlocked
    if (type === 'company' && scanId) {
      const cid = Number(scanId)
      if (cid > 0) {
        getWithAuth(`/companies/scan/${cid}`)
          .then((data: any) => {
            if (data && typeof data.is_unlocked === 'boolean') setUnlocked(data.is_unlocked)
            else setUnlocked(!!Taro.getStorageSync(`report_unlocked_company_${scanId}`))
            
            // 处理公司检测数据
            if (data?.status === 'failed') {
              setAnalysisFailed(true)
              setReport({
                time: formatCreatedAt(data.created_at),
                reportNo: 'R-C-' + (data.id || scanId),
                riskLevel: 'failed',
                riskText: RISK_TEXT.failed,
                items: [],
                previewCount: 0,
                summary: '公司信息分析失败，请稍后重试'
              })
              return
            }
            
            // 公司检测数据展示（只展示原始数据，不做评价）
            const enterpriseInfo = data?.company_info || {}
            const legalAnalysis = data?.legal_risks || {}
            
            // 生成公司数据摘要
            const summary = generateCompanyDataSummary(enterpriseInfo, legalAnalysis)
            
            // 将公司数据转换为items格式
            const items: Array<{ tag: string; text: string }> = []
            
            // 企业基本信息
            if (enterpriseInfo.name) {
              items.push({ tag: '企业信息', text: `公司名称：${enterpriseInfo.name}` })
            }
            if (enterpriseInfo.enterprise_age !== undefined) {
              items.push({ tag: '企业信息', text: `企业年龄：${enterpriseInfo.enterprise_age}年` })
            }
            if (enterpriseInfo.start_date) {
              items.push({ tag: '企业信息', text: `成立时间：${enterpriseInfo.start_date}` })
            }
            if (enterpriseInfo.oper_name) {
              items.push({ tag: '企业信息', text: `法定代表人：${enterpriseInfo.oper_name}` })
            }
            
            // 法律案件信息
            if (legalAnalysis.legal_case_count !== undefined) {
              items.push({ tag: '法律案件', text: `法律案件总数：${legalAnalysis.legal_case_count}件` })
            }
            if (legalAnalysis.decoration_related_cases !== undefined) {
              items.push({ tag: '法律案件', text: `装修相关案件：${legalAnalysis.decoration_related_cases}件` })
            }
            if (legalAnalysis.recent_case_date) {
              items.push({ tag: '法律案件', text: `最近案件日期：${legalAnalysis.recent_case_date}` })
            }
            if (legalAnalysis.case_types && legalAnalysis.case_types.length > 0) {
              items.push({ tag: '法律案件', text: `案件类型：${legalAnalysis.case_types.join('、')}` })
            }
            
            // 最近案件详情 - 展示所有案件，不再限制数量
            if (legalAnalysis.recent_cases && legalAnalysis.recent_cases.length > 0) {
              legalAnalysis.recent_cases.forEach((caseItem: any, index: number) => {
                // 构建案件详细信息
                let caseDetails = `${caseItem.data_type_zh || '案件'}：${caseItem.title || ''}（${caseItem.date || ''}）`
                
                // 添加案件类型信息
                if (caseItem.case_type) {
                  caseDetails += ` | 类型：${caseItem.case_type}`
                }
                
                // 添加案由信息
                if (caseItem.cause) {
                  caseDetails += ` | 案由：${caseItem.cause}`
                }
                
                // 添加判决结果信息
                if (caseItem.result) {
                  caseDetails += ` | 结果：${caseItem.result}`
                }
                
                // 添加相关法条信息
                if (caseItem.related_laws && caseItem.related_laws.length > 0) {
                  caseDetails += ` | 相关法条：${caseItem.related_laws.join('、')}`
                }
                
                // 添加案件编号信息
                if (caseItem.case_no) {
                  caseDetails += ` | 案号：${caseItem.case_no}`
                }
                
                items.push({ 
                  tag: '案件详情', 
                  text: caseDetails
                })
              })
            }
            
            const previewCount = Math.max(1, Math.ceil(items.length * 0.3))
            
            // 公司检测不使用风险等级，使用中性表述
            const riskLevel = 'compliant'  // 中性表述
            
            setReport({
              time: formatCreatedAt(data.created_at),
              reportNo: 'R-C-' + (data.id || scanId),
              riskLevel,
              riskText: RISK_TEXT[riskLevel] || RISK_TEXT.compliant,
              items,
              previewCount,
              summary
            })
          })
          .catch((err: any) => {
            console.error('获取公司检测结果失败:', err)
            setUnlocked(!!Taro.getStorageSync(`report_unlocked_company_${scanId}`))
            // 失败时显示错误信息
            setAnalysisFailed(true)
            setReport({
              time: '—',
              reportNo: 'R-C-' + scanId,
              riskLevel: 'failed',
              riskText: RISK_TEXT.failed,
              items: [],
              previewCount: 0,
              summary: '获取公司信息失败，请稍后重试'
            })
          })
        return
      }
    }

    // 其他类型（公司检测等）：显示空数据
    setAnalysisFailed(true)
    setReport({
      time: '—',
      reportNo: 'R' + Date.now().toString(36).toUpperCase(),
      riskLevel: 'failed',
      riskText: RISK_TEXT.failed,
      items: [],
      previewCount: 0,
      summary: '暂不支持此类型报告或数据获取失败'
    })
  }, [type, scanId])

  const handleUnlock = () => {
    const inst = Taro.getCurrentInstance()
    const p = (inst?.router?.params as Record<string, string>) || {}
    // 优先用 state（useDidShow 同步的），小程序栈内 router.params 可能不可靠
    const t = (type || p.type || p.Type || 'company') as string
    const sid = String(scanId ?? p.scanId ?? p.scanid ?? p.ScanId ?? '0')
    const needId = t === 'contract' || t === 'quote'
    if (needId && (!sid || sid === '0' || Number(sid) <= 0)) {
      Taro.showToast({ title: '参数错误，请从报告列表重新进入', icon: 'none' })
      return
    }
    const params = new URLSearchParams()
    params.set('type', t)
    params.set('scanId', sid)
    const nameVal = name ?? p.name
    if (nameVal) params.set('name', String(nameVal))
    const stageParam = p.stage ?? inst?.router?.params?.stage
    if (t === 'acceptance' && stageParam) params.set('stage', String(stageParam))
    Taro.navigateTo({ url: `/pages/report-unlock/index?${params.toString()}` })
  }

  const handleSupervision = () => {
    // P36 AI监理咨询页，携带当前报告上下文
    const q = new URLSearchParams()
    if (type) q.set('type', type)
    if (scanId) q.set('reportId', String(scanId))
    if (name) q.set('name', name)
    Taro.navigateTo({ url: `/pages/ai-supervision/index?${q.toString()}` })
  }

  const handleExportPdf = async () => {
    const rt = (type || 'company') as string
    const rid = parseInt(String(scanId || 0), 10)
    if (!rid && rt !== 'company') {
      Taro.showModal({
        title: '无法导出',
        content: '当前报告无有效编号（R-C-0），无法导出。请到「我的」→「报告列表」中打开已分析成功的合同报告后再导出。',
        confirmText: '去列表',
        cancelText: '知道了',
        success: (res) => {
          if (res.confirm) Taro.navigateTo({ url: '/pages/report-list/index' })
        }
      })
      return
    }
    try {
      Taro.showLoading({ title: '导出中...' })
      await reportApi.downloadPdf(rt, rid || 0)
      Taro.hideLoading()
      Taro.showToast({ title: '导出成功', icon: 'success' })
    } catch (e: any) {
      Taro.hideLoading()
      const msg = e?.message || '导出失败，请确保已解锁'
      Taro.showToast({ title: msg, icon: 'none' })
    }
  }

  const handleRiskClick = (item: any) => {
    Taro.showModal({
      title: '风险解读',
      content: `${item.text}\n\n关联：行业规范及《民法典》相关条款`,
      showCancel: false
    })
  }

  const itemsArr = Array.isArray(report?.items) ? report.items : []
  const previewCount = Math.max(0, Number(report?.previewCount) || 0)
  const previewItems = itemsArr.slice(0, previewCount)
  const lockedItems = itemsArr.slice(previewCount)
  const showOverlay = !unlocked && lockedItems.length > 0

  return (
    <ScrollView scrollY className='report-detail-page-outer'>
      <View className='report-detail-page'>
      <View className='header'>
        <Text className='report-name'>{(type && titles[type] ? titles[type] : titles.company)} - {name || '未命名'}</Text>
        <Text className='gen-time'>生成时间：{report?.time}</Text>
        <Text className='report-no'>报告编号：{report?.reportNo}</Text>
      </View>

      {analysisFailed && (
        <View className='summary-wrap' style={{ backgroundColor: '#fff3f3', borderColor: '#ffcdd2' }}>
          <Text className='summary-text'>❌ AI分析失败，请重新上传或稍后重试</Text>
        </View>
      )}

      <View className={`risk-badge ${report?.riskLevel}`}>
        <Text className='risk-text'>{report?.riskText}</Text>
      </View>

      {report?.summary && !analysisFailed && (
        <View className='summary-wrap'>
          <Text className='summary-text'>{report.summary}</Text>
        </View>
      )}

      <View className='items-wrap'>
        <View className='items'>
          {previewItems.map((item, i) => (
            <View key={i} className='item' onClick={() => handleRiskClick(item)}>
              <View className={`tag ${item.tag === '高风险' || item.tag === '霸王条款' || item.tag === '漏项' ? 'high' : item.tag === '警告' || item.tag === '虚高' || item.tag === '陷阱' ? 'warn' : 'ok'}`}>
                <Text>{item.tag}</Text>
              </View>
              <Text className='item-text'>{item.text}</Text>
            </View>
          ))}
          {unlocked && lockedItems.map((item, i) => (
            <View key={'lock-' + i} className='item' onClick={() => handleRiskClick(item)}>
              <View className={`tag ${item.tag === '高风险' ? 'high' : item.tag === '警告' ? 'warn' : 'ok'}`}><Text>{item.tag}</Text></View>
              <Text className='item-text'>{item.text}</Text>
            </View>
          ))}
        </View>
        {showOverlay && (
          <View className='content-overlay'>
            <Text className='overlay-text'>解锁完整报告，查看全部分析内容</Text>
            <Text className='overlay-hint'>未解锁可能遗漏关键风险信息</Text>
          </View>
        )}
      </View>

      <View className='actions'>
        {analysisFailed ? (
          <>
            <View className='btn primary' onClick={() => Taro.navigateTo({ url: type === 'quote' ? '/pages/quote-upload/index' : '/pages/contract-upload/index' })}>
              <Text>重新上传</Text>
            </View>
            <View className='btn secondary' onClick={handleSupervision}>
              <Text>咨询AI监理</Text>
            </View>
          </>
        ) : !unlocked ? (
          <>
            <View className='btn primary' onClick={handleUnlock}>
              <Text>解锁完整报告</Text>
            </View>
            <View className='btn secondary' onClick={handleSupervision}>
              <Text>咨询AI监理</Text>
            </View>
          </>
        ) : (
          <>
            <View className='btn primary' onClick={handleExportPdf}>
              <Text>导出PDF</Text>
            </View>
            <View className='btn secondary' onClick={handleSupervision}>
              <Text>咨询AI监理</Text>
            </View>
            <View className='member-upgrade' onClick={() => Taro.navigateTo({ url: '/pages/membership/index' })}>
              <Text className='member-upgrade-text'>开通会员，全部报告无限解锁 →</Text>
            </View>
          </>
        )}
      </View>
      </View>
    </ScrollView>
  )
}

export default ReportDetailPage

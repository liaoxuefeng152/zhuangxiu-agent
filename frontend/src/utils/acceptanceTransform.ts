/**
 * 后端验收分析 API 返回格式 → 前端展示格式转换
 * 支持两种后端格式：
 * 1. 旧格式: issues[{ category, description, severity, location }], suggestions[{ item, action }]
 * 2. 新格式: issues[{ item, description, severity }], passed_items[], suggestions[], acceptance_status, quality_score
 */
export type ResultItem = { level: 'high' | 'mid' | 'low'; title: string; desc: string; suggest: string }

interface BackendIssueOld {
  category?: string
  description?: string
  severity?: string
  location?: string
}

interface BackendIssueNew {
  item?: string
  description?: string
  severity?: string
}

interface BackendSuggestion {
  item?: string
  action?: string
}

export interface BackendAnalysisResult {
  // 旧格式字段
  issues?: (BackendIssueOld | BackendIssueNew | string)[]
  suggestions?: BackendSuggestion[]
  severity?: string
  summary?: string
  
  // 新格式字段
  acceptance_status?: string
  quality_score?: number
  passed_items?: string[]
}

/** 判断是否为后端 AI 不可用时的兜底返回（应视为失败，不展示） */
export function isAiUnavailableFallback(data: BackendAnalysisResult | null | undefined): boolean {
  if (!data) return true
  const summary = (data.summary ?? '').toString()
  const firstSug = data.suggestions?.[0]
  if (
    /暂不可用|请稍后重试|分析服务/.test(summary) ||
    (firstSug && /AI分析暂不可用|请稍后重试/.test((firstSug.item ?? '') + (firstSug.action ?? '')))
  ) {
    return true
  }
  return false
}

export function transformBackendToFrontend(data: BackendAnalysisResult): { items: ResultItem[] } {
  const issues = data?.issues ?? []
  const suggestions = data?.suggestions ?? []
  const summary = data?.summary ?? ''
  const acceptanceStatus = data?.acceptance_status
  const qualityScore = data?.quality_score
  const passedItems = data?.passed_items ?? []
  
  const defaultSuggest = suggestions[0]?.action ?? '请根据实际情况整改'

  const items: ResultItem[] = []
  
  // 处理issues数组
  issues.forEach((issue, i) => {
    if (typeof issue === 'string') {
      // 如果是字符串格式的问题
      const sev = 'mid' // 默认中风险
      const level: 'high' | 'mid' | 'low' = 'mid'
      const suggest = suggestions[i]?.action ?? suggestions[0]?.action ?? defaultSuggest
      items.push({
        level,
        title: issue,
        desc: issue,
        suggest
      })
    } else if (typeof issue === 'object') {
      // 处理对象格式的问题
      const sev = (issue.severity || 'low').toLowerCase()
      const level: 'high' | 'mid' | 'low' =
        sev === 'high' ? 'high' : sev === 'warning' || sev === 'mid' ? 'mid' : 'low'
      
      // 获取标题：优先使用item字段，然后是category，最后是description
      const title = (issue as any).item ?? (issue as any).category ?? issue.description ?? '验收项'
      const desc = issue.description ?? (issue as any).category ?? title
      const suggest = suggestions[i]?.action ?? suggestions[0]?.action ?? defaultSuggest
      
      items.push({
        level,
        title,
        desc,
        suggest
      })
    }
  })

  // 如果没有问题但有通过项目，添加通过项
  if (items.length === 0 && passedItems.length > 0) {
    passedItems.slice(0, 3).forEach(item => {
      items.push({
        level: 'low',
        title: item,
        desc: '验收通过',
        suggest: '保持'
      })
    })
  }

  // 根据验收状态和质量评分添加总结项
  if (acceptanceStatus || qualityScore !== undefined) {
    let statusText = ''
    if (acceptanceStatus === '通过') {
      statusText = '验收通过'
    } else if (acceptanceStatus === '不通过') {
      statusText = '验收不通过'
    } else if (acceptanceStatus === '部分通过') {
      statusText = '部分通过'
    }
    
    if (qualityScore !== undefined) {
      statusText += ` (质量评分: ${qualityScore}/100)`
    }
    
    if (statusText) {
      items.unshift({
        level: 'low',
        title: '验收状态',
        desc: statusText,
        suggest: acceptanceStatus === '通过' ? '保持' : '请按建议整改'
      })
    }
  }

  // 若无问题但为 pass，补一条合格项
  if (items.length === 0 && (data?.severity === 'pass' || !data?.severity)) {
    items.push({
      level: 'low',
      title: '验收通过',
      desc: summary || '该阶段验收基本合格',
      suggest: '保持'
    })
  }

  return { items }
}

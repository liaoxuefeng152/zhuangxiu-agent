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
  // suggestions 兼容两种格式：字符串数组（新格式）或对象数组（旧格式）
  suggestions?: Array<BackendSuggestion | string>
  severity?: string
  summary?: string
  
  // 新格式字段
  acceptance_status?: string
  quality_score?: number
  passed_items?: string[]
  
  // result_json 中的完整数据
  result_json?: any
}

/** 判断是否为后端 AI 不可用时的兜底返回（应视为失败，不展示） */
export function isAiUnavailableFallback(data: BackendAnalysisResult | null | undefined): boolean {
  if (!data) return true
  const summary = (data.summary ?? '').toString()
  // 明确包含服务不可用提示时视为兜底
  if (/AI分析服务暂时不可用/.test(summary)) {
    return true
  }
  // 检查 result_json 中的 summary（后端存的 AI 原始数据）
  const rjSummary = ((data as any).result_json?.summary ?? '').toString()
  if (/AI分析服务暂时不可用/.test(rjSummary)) {
    return true
  }
  // 检查 mock_data 标记（后端兜底时设置此标记）
  if ((data as any).result_json?.is_mock_data === true) {
    return true
  }
  return false
}

/** 从 suggestions 数组中提取指定索引的建议文本（兼容字符串和对象两种格式） */
function getSuggestText(suggestions: Array<BackendSuggestion | string>, index: number, fallback: string): string {
  const sug = suggestions[index] ?? suggestions[0]
  if (!sug) return fallback
  if (typeof sug === 'string') return sug
  return sug.action ?? fallback
}

export function transformBackendToFrontend(data: BackendAnalysisResult): { items: ResultItem[] } {
  // 优先从 result_json 中读取完整数据（后端将 AI 原始结果存在此字段）
  const resultJson = data?.result_json || {}
  const issues = data?.issues ?? resultJson.issues ?? []
  const suggestionsRaw: Array<BackendSuggestion | string> = data?.suggestions ?? resultJson.suggestions ?? []
  const summary = data?.summary ?? resultJson.summary ?? ''
  const acceptanceStatus = data?.acceptance_status ?? resultJson.acceptance_status
  const qualityScore = data?.quality_score ?? resultJson.quality_score
  const passedItems = data?.passed_items ?? resultJson.passed_items ?? []
  
  const defaultSuggest = getSuggestText(suggestionsRaw, 0, '请根据实际情况整改')

  const items: ResultItem[] = []
  
  // 处理issues数组
  issues.forEach((issue: any, i: number) => {
    if (typeof issue === 'string') {
      // 字符串格式，尝试解析 "item: desc (severity)" 格式
      const level: 'high' | 'mid' | 'low' = 'mid'
      const suggest = getSuggestText(suggestionsRaw, i, defaultSuggest)
      items.push({
        level,
        title: issue,
        desc: issue,
        suggest
      })
    } else if (typeof issue === 'object' && issue !== null) {
      // 对象格式
      const sev = ((issue as any).severity || 'low').toLowerCase()
      const level: 'high' | 'mid' | 'low' =
        sev === 'high' ? 'high' : sev === 'warning' || sev === 'mid' ? 'mid' : 'low'
      
      // 获取标题：优先使用item字段，然后是category，最后是description
      const title = (issue as any).item ?? (issue as any).category ?? (issue as any).description ?? '验收项'
      const desc = (issue as any).description ?? (issue as any).category ?? title
      const suggest = getSuggestText(suggestionsRaw, i, defaultSuggest)
      
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

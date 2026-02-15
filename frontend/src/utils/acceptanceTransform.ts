/**
 * 后端验收分析 API 返回格式 → 前端展示格式转换
 * 后端: issues[{ category, description, severity, location }], suggestions[{ item, action }]
 * 前端: items[{ level, title, desc, suggest }]
 */
export type ResultItem = { level: 'high' | 'mid' | 'low'; title: string; desc: string; suggest: string }

interface BackendIssue {
  category?: string
  description?: string
  severity?: string
  location?: string
}

interface BackendSuggestion {
  item?: string
  action?: string
}

export interface BackendAnalysisResult {
  issues?: BackendIssue[]
  suggestions?: BackendSuggestion[]
  severity?: string
  summary?: string
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
  const defaultSuggest = suggestions[0]?.action ?? '请根据实际情况整改'

  const items: ResultItem[] = issues.map((issue, i) => {
    const sev = (issue.severity || 'low').toLowerCase()
    const level: 'high' | 'mid' | 'low' =
      sev === 'high' ? 'high' : sev === 'warning' ? 'mid' : 'low'
    const suggest = suggestions[i]?.action ?? suggestions[0]?.action ?? defaultSuggest
    return {
      level,
      title: issue.category ?? issue.description ?? '验收项',
      desc: issue.description ?? issue.category ?? '',
      suggest
    }
  })

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

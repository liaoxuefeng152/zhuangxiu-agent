/**
 * 公司信息展示工具
 * 只展示聚合数据API返回的原文，不做任何风险评价
 * 避免使用"高风险"、"中风险"、"低风险"等可能引起法律争议的表述
 */

// 数据分类标签（中性表述，只描述数据类型）
export const DATA_CATEGORY_MAP: Record<string, string> = {
  // 数据分类 -> 展示文本
  'legal_cases': '法律案件',
  'enterprise_info': '企业信息',
  'decoration_cases': '装修相关案件',
  'case_types': '案件类型',
  'recent_cases': '最近案件'
}

// 生成公司信息摘要（只展示数据统计，不做评价）
export function generateCompanySummary(
  enterpriseInfo: any,
  legalAnalysis: any
): string {
  let summary = `# 公司信息报告\n\n`
  
  // 企业基本信息统计
  if (enterpriseInfo) {
    summary += `## 企业基本信息\n`
    if (enterpriseInfo.name) summary += `**公司名称**：${enterpriseInfo.name}\n`
    if (enterpriseInfo.enterprise_age !== undefined) summary += `**企业年龄**：${enterpriseInfo.enterprise_age}年\n`
    if (enterpriseInfo.start_date) summary += `**成立日期**：${enterpriseInfo.start_date}\n`
    if (enterpriseInfo.oper_name) summary += `**法定代表人**：${enterpriseInfo.oper_name}\n`
    summary += `\n`
  }
  
  // 法律案件统计
  if (legalAnalysis) {
    summary += `## 法律案件统计\n`
    if (legalAnalysis.legal_case_count !== undefined) {
      summary += `**法律案件总数**：${legalAnalysis.legal_case_count}件\n`
    }
    if (legalAnalysis.decoration_related_cases !== undefined) {
      summary += `**装修相关案件**：${legalAnalysis.decoration_related_cases}件\n`
    }
    if (legalAnalysis.recent_case_date) {
      summary += `**最近案件日期**：${legalAnalysis.recent_case_date}\n`
    }
    if (legalAnalysis.case_types && legalAnalysis.case_types.length > 0) {
      summary += `**案件类型**：${legalAnalysis.case_types.join('、')}\n`
    }
    summary += `\n`
  }
  
  summary += `## 数据来源说明\n`
  summary += `1. 企业基本信息来源于国家企业信用信息公示系统\n`
  summary += `2. 法律案件信息来源于中国裁判文书网等公开司法数据\n`
  summary += `3. 数据更新日期：${new Date().toLocaleDateString('zh-CN')}\n\n`
  
  summary += `## 免责声明\n`
  summary += `本报告基于公开信息生成，仅供参考，不构成任何投资、合作建议。用户应自行核实信息的准确性和时效性，本平台不对信息的完整性和准确性承担法律责任。\n\n`
  summary += `*报告生成时间：${new Date().toLocaleString('zh-CN')}*\n`
  
  return summary
}

// 获取数据分类对应的图标（中性图标）
export function getDataCategoryIcon(category: string): string {
  const map: Record<string, string> = {
    'legal_cases': '📋',
    'enterprise_info': '🏢',
    'decoration_cases': '🔨',
    'case_types': '📊',
    'recent_cases': '📅'
  }
  return map[category] || '📄'
}

// 获取数据分类对应的CSS类名
export function getDataCategoryClass(category: string): string {
  const map: Record<string, string> = {
    'legal_cases': 'legal-cases',
    'enterprise_info': 'enterprise-info',
    'decoration_cases': 'decoration-cases',
    'case_types': 'case-types',
    'recent_cases': 'recent-cases'
  }
  return map[category] || 'data-category'
}

// 检查是否需要显示数据更新提示
export function shouldShowDataUpdateNotice(lastUpdateDate: string): boolean {
  if (!lastUpdateDate) return false
  try {
    const lastUpdate = new Date(lastUpdateDate)
    const now = new Date()
    const diffDays = Math.floor((now.getTime() - lastUpdate.getTime()) / (1000 * 60 * 60 * 24))
    return diffDays > 30  // 超过30天显示更新提示
  } catch {
    return false
  }
}

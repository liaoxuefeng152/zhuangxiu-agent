/**
 * 公司数据格式化工具
 * 用于直接展示聚合数据API返回的原文，不做评价
 */

// 格式化企业基本信息
export function formatEnterpriseInfo(enterpriseInfo: any): string {
  if (!enterpriseInfo) return '暂无企业信息'
  
  const info = enterpriseInfo
  
  let formatted = `# 企业基本信息\n\n`
  
  // 基础信息
  if (info.name) formatted += `**公司名称**：${info.name}\n`
  if (info.credit_code) formatted += `**统一社会信用代码**：${info.credit_code}\n`
  if (info.registration_number) formatted += `**工商注册号**：${info.registration_number}\n`
  if (info.legal_person) formatted += `**法定代表人**：${info.legal_person}\n`
  if (info.registered_capital) formatted += `**注册资本**：${info.registered_capital}\n`
  if (info.start_date) formatted += `**成立日期**：${info.start_date}\n`
  if (info.enterprise_age) formatted += `**企业年龄**：${info.enterprise_age}\n`
  if (info.business_status) formatted += `**经营状态**：${info.business_status}\n`
  if (info.industry) formatted += `**所属行业**：${info.industry}\n`
  if (info.address) formatted += `**注册地址**：${info.address}\n`
  if (info.business_scope) formatted += `**经营范围**：${info.business_scope}\n`
  
  // 股东信息
  if (info.shareholders && info.shareholders.length > 0) {
    formatted += `\n## 股东信息\n`
    info.shareholders.forEach((shareholder: any, index: number) => {
      formatted += `${index + 1}. **${shareholder.name || '未知'}**`
      if (shareholder.shareholding_ratio) formatted += `（持股比例：${shareholder.shareholding_ratio}）`
      formatted += `\n`
    })
  }
  
  // 主要人员
  if (info.key_personnel && info.key_personnel.length > 0) {
    formatted += `\n## 主要人员\n`
    info.key_personnel.forEach((person: any, index: number) => {
      formatted += `${index + 1}. **${person.name || '未知'}**`
      if (person.position) formatted += `（${person.position}）`
      formatted += `\n`
    })
  }
  
  return formatted
}

// 格式化法律案件信息
export function formatLegalAnalysis(legalAnalysis: any): string {
  if (!legalAnalysis) return '暂无法律案件信息'
  
  const analysis = legalAnalysis
  
  let formatted = `# 法律案件分析\n\n`
  
  // 案件统计
  if (analysis.legal_case_count !== undefined) {
    formatted += `**法律案件总数**：${analysis.legal_case_count}件\n`
  }
  if (analysis.decoration_related_cases !== undefined) {
    formatted += `**装修相关案件**：${analysis.decoration_related_cases}件\n`
  }
  if (analysis.recent_case_date) {
    formatted += `**最近案件日期**：${analysis.recent_case_date}\n`
  }
  
  // 案件类型分布
  if (analysis.case_types && analysis.case_types.length > 0) {
    formatted += `\n## 案件类型分布\n`
    analysis.case_types.forEach((type: any, index: number) => {
      formatted += `${index + 1}. **${type.type || '未知类型'}**`
      if (type.count !== undefined) formatted += `（${type.count}件）`
      formatted += `\n`
    })
  }
  
  // 最近案件详情
  if (analysis.recent_cases && analysis.recent_cases.length > 0) {
    formatted += `\n## 最近案件详情\n`
    analysis.recent_cases.forEach((caseItem: any, index: number) => {
      formatted += `### 案件 ${index + 1}\n`
      if (caseItem.title) formatted += `**案件标题**：${caseItem.title}\n`
      if (caseItem.case_number) formatted += `**案号**：${caseItem.case_number}\n`
      if (caseItem.court) formatted += `**审理法院**：${caseItem.court}\n`
      if (caseItem.date) formatted += `**案件日期**：${caseItem.date}\n`
      if (caseItem.case_type) formatted += `**案件类型**：${caseItem.case_type}\n`
      if (caseItem.parties) formatted += `**当事人**：${caseItem.parties}\n`
      if (caseItem.summary) formatted += `**案件摘要**：${caseItem.summary}\n`
      formatted += `\n`
    })
  }
  
  return formatted
}

// 生成完整的公司报告原文
export function generateCompanyReport(
  companyName: string,
  enterpriseInfo: any,
  legalAnalysis: any,
  riskSummary: any
): string {
  let report = `# 公司信息报告\n\n`
  report += `**报告生成时间**：${new Date().toLocaleString('zh-CN')}\n`
  report += `**公司名称**：${companyName}\n\n`
  
  report += `---\n\n`
  
  // 企业基本信息
  report += formatEnterpriseInfo(enterpriseInfo)
  
  report += `\n---\n\n`
  
  // 法律案件信息
  report += formatLegalAnalysis(legalAnalysis)
  
  report += `\n---\n\n`
  
  // 数据来源说明
  report += `## 数据来源说明\n`
  report += `1. 企业基本信息来源于国家企业信用信息公示系统\n`
  report += `2. 法律案件信息来源于中国裁判文书网等公开司法数据\n`
  report += `3. 数据更新日期：${new Date().toLocaleDateString('zh-CN')}\n\n`
  
  // 免责声明
  report += `## 免责声明\n`
  report += `1. 本报告基于公开信息生成，仅供参考\n`
  report += `2. 报告内容不构成任何投资、合作建议\n`
  report += `3. 用户应自行核实信息的准确性和时效性\n`
  report += `4. 本平台不对信息的完整性和准确性承担法律责任\n\n`
  
  report += `*报告生成系统：装修决策Agent*\n`
  
  return report
}

// 获取预览摘要（用于解锁页面）
export function getPreviewSummary(
  enterpriseInfo: any,
  legalAnalysis: any
): string {
  const previews: string[] = []
  
  if (enterpriseInfo) {
    if (enterpriseInfo.enterprise_age) {
      previews.push(`企业年龄：${enterpriseInfo.enterprise_age}`)
    }
    if (enterpriseInfo.business_status) {
      previews.push(`经营状态：${enterpriseInfo.business_status}`)
    }
  }
  
  if (legalAnalysis) {
    if (legalAnalysis.legal_case_count) {
      previews.push(`法律案件：${legalAnalysis.legal_case_count}件`)
    }
    if (legalAnalysis.decoration_related_cases) {
      previews.push(`装修相关案件：${legalAnalysis.decoration_related_cases}件`)
    }
  }
  
  return previews.length > 0 ? previews.join(' | ') : '暂无预览信息'
}

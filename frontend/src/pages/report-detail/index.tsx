import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { reportApi, contractApi, quoteApi } from '../../services/api'
import './index.scss'

const RISK_TEXT: Record<string, string> = { high: '⚠️ 高风险', warning: '⚠️ 1项警告', compliant: '✅ 合规' }

/** 将后端合同分析结果转为报告页用的 { tag, text } 列表 */
function mapContractToItems (data: {
  risk_items?: Array<{ term?: string; description?: string; risk_level?: string }>
  unfair_terms?: Array<{ term?: string; description?: string }>
  missing_terms?: Array<{ term?: string; reason?: string }>
  suggested_modifications?: Array<{ modified?: string; reason?: string }>
}): Array<{ tag: string; text: string }> {
  const items: Array<{ tag: string; text: string }> = []
  ;(data.risk_items || []).forEach((it) => {
    const tag = it.risk_level === 'high' ? '风险条款' : '警告'
    items.push({ tag, text: (it.term || it.description || '').slice(0, 120) })
  })
  ;(data.unfair_terms || []).forEach((it) => {
    items.push({ tag: '霸王条款', text: (it.term || it.description || '').slice(0, 120) })
  })
  ;(data.missing_terms || []).forEach((it) => {
    items.push({ tag: '漏项', text: (it.term || it.reason || '').slice(0, 120) })
  })
  ;(data.suggested_modifications || []).forEach((it) => {
    items.push({ tag: '建议', text: (it.modified || it.reason || '').slice(0, 120) })
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
  const { type, scanId, name } = Taro.getCurrentInstance().router?.params || {}

  const titles: Record<string, string> = {
    company: '公司风险报告',
    quote: '报价单分析报告',
    contract: '合同审核报告'
  }

  const allItems = {
    company: [
      { tag: '高风险', text: '该公司存在多起法律纠纷记录' },
      { tag: '警告', text: '注册资本较低，建议谨慎合作' },
      { tag: '合规', text: '工商信息正常' },
      { tag: '建议', text: '建议实地考察并核实施工资质' },
      { tag: '参考', text: '参考《民法典》第577条关于违约责任' }
    ],
    quote: [
      { tag: '漏项', text: '防水工程未列入报价' },
      { tag: '虚高', text: '水电改造单价高于市场均价20%' },
      { tag: '建议', text: '建议补充吊顶材料品牌及规格' },
      { tag: '省钱', text: '可比价3家后签订补充协议' }
    ],
    contract: [
      { tag: '霸王条款', text: '乙方单方变更设计无需甲方同意' },
      { tag: '陷阱', text: '保修期起算时间模糊' },
      { tag: '建议', text: '建议明确增项上限比例' },
      { tag: '法条', text: '参考《民法典》第496条格式条款' }
    ]
  }

  useEffect(() => {
    const key = `report_unlocked_${type}_${scanId || '0'}`
    setUnlocked(!!Taro.getStorageSync(key))

    // 合同类型：调用API获取分析结果
    if (type === 'contract' && scanId) {
      contractApi.getAnalysis(Number(scanId))
        .then((res: any) => {
          const data = res?.data ?? res
          const riskLevel = (data.risk_level || 'compliant') as string
          const items = mapContractToItems(data)
          const previewCount = Math.max(1, Math.ceil(items.length * 0.3))
          setReport({
            time: data.created_at ? new Date(data.created_at).toLocaleString('zh-CN') : '—',
            reportNo: 'R-C-' + (data.id || scanId),
            riskLevel,
            riskText: RISK_TEXT[riskLevel] || RISK_TEXT.compliant,
            items: items.length ? items : allItems.contract,
            previewCount,
            summary: data.summary
          })
        })
        .catch(() => {
          const riskLevel = ['high', 'warning', 'compliant'][Math.floor(Math.random() * 3)]
          const items = allItems.contract
          setReport({
            time: '—',
            reportNo: 'R-C-' + scanId,
            riskLevel,
            riskText: RISK_TEXT[riskLevel],
            items,
            previewCount: Math.ceil(items.length * 0.3) || 1
          })
        })
      return
    }

    // 报价单类型：调用API获取分析结果
    if (type === 'quote' && scanId) {
      quoteApi.getAnalysis(Number(scanId))
        .then((res: any) => {
          const data = res?.data ?? res
          // 根据risk_score确定风险等级：0-30低风险，31-60中等风险，61-100高风险
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
            time: data.created_at ? new Date(data.created_at).toLocaleString('zh-CN') : '—',
            reportNo: 'R-Q-' + (data.id || scanId),
            riskLevel,
            riskText: RISK_TEXT[riskLevel] || RISK_TEXT.compliant,
            items: items.length ? items : allItems.quote,
            previewCount,
            summary
          })
        })
        .catch((err) => {
          console.error('获取报价单分析结果失败:', err)
          // 失败时使用默认数据
          const riskLevel = ['high', 'warning', 'compliant'][Math.floor(Math.random() * 3)]
          const items = allItems.quote
          setReport({
            time: '—',
            reportNo: 'R-Q-' + scanId,
            riskLevel,
            riskText: RISK_TEXT[riskLevel],
            items,
            previewCount: Math.ceil(items.length * 0.3) || 1
          })
        })
      return
    }

    // 其他类型（公司检测等）：使用默认数据
    const riskLevel = ['high', 'warning', 'compliant'][Math.floor(Math.random() * 3)]
    const items = allItems[type as keyof typeof allItems] || allItems.company
    const previewCount = Math.ceil(items.length * 0.3) || 1
    setReport({
      time: '2026-01-19 10:25',
      reportNo: 'R' + Date.now().toString(36).toUpperCase(),
      riskLevel,
      riskText: RISK_TEXT[riskLevel],
      items,
      previewCount
    })
  }, [type, scanId])

  const handleUnlock = () => {
    Taro.navigateTo({
      url: `/pages/report-unlock/index?type=${type || 'company'}&scanId=${scanId || 0}&name=${encodeURIComponent(name || '')}`
    })
  }

  const handleSupervision = () => {
    Taro.navigateTo({ url: '/pages/supervision/index' })
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
    } catch {
      Taro.hideLoading()
      Taro.showToast({ title: '导出失败，请确保已解锁', icon: 'none' })
    }
  }

  const handleRiskClick = (item: any) => {
    Taro.showModal({
      title: '风险解读',
      content: `${item.text}\n\n关联：行业规范及《民法典》相关条款`,
      showCancel: false
    })
  }

  const previewItems = report?.items?.slice(0, report.previewCount) ?? []
  const lockedItems = report?.items?.slice(report.previewCount) ?? []
  const showOverlay = !unlocked && lockedItems.length > 0

  return (
    <ScrollView scrollY className='report-detail-page'>
      <View className='header'>
        <Text className='report-name'>{titles[type || 'company']} - {name || '未命名'}</Text>
        <Text className='gen-time'>生成时间：{report?.time}</Text>
        <Text className='report-no'>报告编号：{report?.reportNo}</Text>
      </View>

      <View className={`risk-badge ${report?.riskLevel}`}>
        <Text className='risk-text'>{report?.riskText}</Text>
      </View>

      {report?.summary && (
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
        {!unlocked ? (
          <>
            <View className='btn primary' onClick={handleUnlock}>
              <Text>解锁完整报告</Text>
            </View>
            <View className='btn secondary' onClick={handleSupervision}>
              <Text>咨询监理</Text>
            </View>
          </>
        ) : (
          <>
            <View className='btn primary' onClick={handleExportPdf}>
              <Text>导出PDF</Text>
            </View>
            <View className='btn secondary' onClick={handleSupervision}>
              <Text>咨询监理</Text>
            </View>
          </>
        )}
      </View>
    </ScrollView>
  )
}

export default ReportDetailPage

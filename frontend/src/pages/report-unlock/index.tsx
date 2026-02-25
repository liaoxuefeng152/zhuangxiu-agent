import React, { useState, useEffect } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { invitationsApi, getWithAuth } from '../../services/api'
import './index.scss'

const REPORT_TYPE_NAMES: Record<string, string> = {
  company: '公司风险报告',
  quote: '报价单分析报告',
  contract: '合同审核报告',
  acceptance: '验收报告'
}

// 风险等级映射（合规化表述）
const RISK_LEVEL_MAP: Record<string, string> = {
  needs_attention: '需重点关注',
  moderate_concern: '一般关注',
  compliant: '合规'
}

/**
 * P27 报告解锁页 - 明确当前解锁哪份报告，支持免费解锁权益（V2.6.8优化）
 * 新增：预览亮点展示，吸引用户解锁完整报告
 */
const ReportUnlockPage: React.FC = () => {
  const { type, scanId, name, stage } = Taro.getCurrentInstance().router?.params || {}
  const reportType = type || 'report'
  const typeName = REPORT_TYPE_NAMES[reportType] || '完整报告'
  const reportName = name ? decodeURIComponent(name) : (stage ? `${stage}阶段` : '')
  const displayTitle = reportName ? `${typeName} - ${reportName}` : typeName

  const [hasFreeUnlock, setHasFreeUnlock] = useState(false)
  const [isChecking, setIsChecking] = useState(false)
  const [previewData, setPreviewData] = useState<any>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)

  useEffect(() => {
    // 检查是否有免费解锁权益
    checkFreeUnlockEntitlements()
    
    // 加载预览数据
    if (scanId) {
      loadPreviewData()
    }
  }, [])

  const checkFreeUnlockEntitlements = async () => {
    try {
      setIsChecking(true)
      const entitlements = await invitationsApi.getFreeUnlockEntitlements()
      // 检查是否有可用的通用权益
      const availableEntitlements = entitlements.filter(
        (ent: any) => 
          ent.status === 'available' && 
          !ent.report_type && 
          !ent.report_id &&
          (!ent.expires_at || new Date(ent.expires_at) > new Date())
      )
      setHasFreeUnlock(availableEntitlements.length > 0)
    } catch (error) {
      console.error('检查免费解锁权益失败:', error)
    } finally {
      setIsChecking(false)
    }
  }

  const loadPreviewData = async () => {
    if (!scanId) return
    
    try {
      setLoadingPreview(true)
      let response: any
      
      if (reportType === 'company') {
        response = await getWithAuth(`/companies/scan/${scanId}`)
      } else if (reportType === 'quote') {
        response = await getWithAuth(`/quotes/quote/${scanId}`)
      } else if (reportType === 'contract') {
        response = await getWithAuth(`/contracts/contract/${scanId}`)
      }
      
      if (response?.preview_data) {
        setPreviewData(response.preview_data)
      }
    } catch (error) {
      console.error('加载预览数据失败:', error)
    } finally {
      setLoadingPreview(false)
    }
  }

  const goPayment = () => {
    const q = new URLSearchParams()
    q.set('pkg', 'single')
    q.set('type', reportType)
    if (scanId) q.set('scanId', String(scanId))
    if (name) q.set('name', name)
    if (stage) q.set('stage', stage)
    Taro.navigateTo({ url: `/pages/payment/index?${q.toString()}` })
  }

  const handleFreeUnlock = async () => {
    if (!scanId) {
      Taro.showToast({
        title: '报告ID无效',
        icon: 'none',
        duration: 2000
      })
      return
    }

    try {
      Taro.showLoading({ title: '使用免费解锁中...' })
      const result = await invitationsApi.useFreeUnlock(reportType, Number(scanId))
      
      if (result.success) {
        Taro.hideLoading()
        Taro.showToast({
          title: '免费解锁成功！',
          icon: 'success',
          duration: 2000
        })
        
        // 解锁成功后返回上一页
        setTimeout(() => {
          Taro.navigateBack()
        }, 1500)
      } else {
        Taro.hideLoading()
        Taro.showToast({
          title: result.message || '免费解锁失败',
          icon: 'none',
          duration: 2000
        })
      }
    } catch (error: any) {
      Taro.hideLoading()
      Taro.showToast({
        title: error.message || '免费解锁失败',
        icon: 'none',
        duration: 2000
      })
    }
  }

  const handleBack = () => {
    if (reportType === 'acceptance' && stage) {
      Taro.navigateTo({ url: `/pages/acceptance/index?stage=${stage}` })
    } else {
      Taro.navigateBack()
    }
  }

  const riskTip =
    reportType === 'contract'
      ? '未解锁时霸王条款、保修期陷阱等关键条款未展示，建议解锁后逐条核对'
      : reportType === 'quote'
        ? '漏项与虚高明细、市场比价未展示，可能影响预算判断'
        : reportType === 'company'
          ? '法律纠纷、经营异常等详情未展示'
          : '未解锁可能遗漏关键风险与整改建议'

  // 渲染报告预览亮点
  const renderPreviewHighlights = () => {
    if (!previewData) return null

    const highlights: Array<{icon: string; title: string; value: string; desc: string}> = []

    if (reportType === 'company') {
      const enterprise = previewData.enterprise_info_preview
      const legal = previewData.legal_analysis_preview
      const risk = previewData.risk_summary_preview

      // 企业信息亮点
      if (enterprise?.enterprise_age) {
        highlights.push({
          icon: '🏢',
          title: '企业年限',
          value: `${enterprise.enterprise_age}年`,
          desc: '成立时间较长，经营相对稳定'
        })
      }

      // 法律案件亮点
      if (legal?.legal_case_count > 0) {
        highlights.push({
          icon: '⚖️',
          title: '法律案件',
          value: `${legal.legal_case_count}起`,
          desc: `其中${legal.decoration_related_cases || 0}起与装修相关`
        })
      }

      // 风险等级亮点
      if (risk?.risk_level) {
        highlights.push({
          icon: risk.risk_level === 'needs_attention' ? '⚠️' : risk.risk_level === 'moderate_concern' ? '📋' : '✅',
          title: '风险关注等级',
          value: RISK_LEVEL_MAP[risk.risk_level] || '合规',
          desc: `风险评分：${risk.risk_score || 0}/100`
        })
      }

      // 风险原因亮点
      if (risk?.top_risk_reasons?.length > 0) {
        risk.top_risk_reasons.slice(0, 2).forEach((reason: string, index: number) => {
          highlights.push({
            icon: '🔍',
            title: `关注点${index + 1}`,
            value: reason.split('，')[0] || reason.substring(0, 10),
            desc: reason.length > 20 ? `${reason.substring(0, 20)}...` : reason
          })
        })
      }
    } else if (reportType === 'quote') {
      // 报价单预览亮点
      if (previewData?.risk_score !== undefined) {
        highlights.push({
          icon: '💰',
          title: '风险评分',
          value: `${previewData.risk_score}/100`,
          desc: '分数越低风险越高，建议仔细核对'
        })
      }

      if (previewData?.high_risk_items_count > 0) {
        highlights.push({
          icon: '⚠️',
          title: '高风险项目',
          value: `${previewData.high_risk_items_count}项`,
          desc: '可能存在漏项、虚高或不合规'
        })
      }

      if (previewData?.warning_items_count > 0) {
        highlights.push({
          icon: '📋',
          title: '关注项目',
          value: `${previewData.warning_items_count}项`,
          desc: '建议与市场价对比核实'
        })
      }

      if (previewData?.total_price !== undefined) {
        highlights.push({
          icon: '💵',
          title: '报价总额',
          value: `¥${previewData.total_price.toLocaleString()}`,
          desc: '建议与市场参考价对比'
        })
      }
    } else if (reportType === 'contract') {
      // 合同预览亮点
      if (previewData?.risk_level) {
        highlights.push({
          icon: previewData.risk_level === 'needs_attention' ? '⚠️' : previewData.risk_level === 'moderate_concern' ? '📋' : '✅',
          title: '风险等级',
          value: RISK_LEVEL_MAP[previewData.risk_level] || '合规',
          desc: '基于条款公平性、完整性评估'
        })
      }

      if (previewData?.unfair_terms_count > 0) {
        highlights.push({
          icon: '⚖️',
          title: '不公平条款',
          value: `${previewData.unfair_terms_count}条`,
          desc: '可能存在霸王条款或对您不利的约定'
        })
      }

      if (previewData?.missing_terms_count > 0) {
        highlights.push({
          icon: '🔍',
          title: '缺失条款',
          value: `${previewData.missing_terms_count}项`,
          desc: '建议补充关键条款以保障权益'
        })
      }

      if (previewData?.suggested_modifications_count > 0) {
        highlights.push({
          icon: '📝',
          title: '修改建议',
          value: `${previewData.suggested_modifications_count}条`,
          desc: '专业律师建议的修改方案'
        })
      }
    }

    if (highlights.length === 0) return null

    return (
      <View className='preview-highlights'>
        <Text className='preview-title'>🔍 报告预览亮点</Text>
        <Text className='preview-subtitle'>解锁完整报告可查看详细分析、具体案件详情及专业建议</Text>
        
        <View className='highlights-grid'>
          {highlights.map((item, index) => (
            <View key={index} className='highlight-item'>
              <Text className='highlight-icon'>{item.icon}</Text>
              <Text className='highlight-title'>{item.title}</Text>
              <Text className='highlight-value'>{item.value}</Text>
              <Text className='highlight-desc'>{item.desc}</Text>
            </View>
          ))}
        </View>

        <View className='data-source-notice'>
          <Text className='notice-text'>数据来源：公开工商信息及司法案件数据，仅供参考</Text>
          <Text className='notice-text'>完整报告包含：详细案件列表、风险条款分析、合作建议等</Text>
        </View>
      </View>
    )
  }

  // 渲染通用预览提示
  const renderGenericPreview = () => {
    if (reportType === 'company') return null
    
    return (
      <View className='generic-preview'>
        <Text className='preview-title'>📋 报告内容预览</Text>
        <View className='preview-items'>
          {reportType === 'contract' && (
            <>
              <View className='preview-item'>
                <Text className='preview-icon'>⚖️</Text>
                <Text className='preview-text'>霸王条款识别与修改建议</Text>
              </View>
              <View className='preview-item'>
                <Text className='preview-icon'>🔍</Text>
                <Text className='preview-text'>缺失关键条款补充</Text>
              </View>
              <View className='preview-item'>
                <Text className='preview-icon'>📝</Text>
                <Text className='preview-text'>专业律师解读与风险提示</Text>
              </View>
            </>
          )}
          {reportType === 'quote' && (
            <>
              <View className='preview-item'>
                <Text className='preview-icon'>💰</Text>
                <Text className='preview-text'>市场比价与价格合理性分析</Text>
              </View>
              <View className='preview-item'>
                <Text className='preview-icon'>📋</Text>
                <Text className='preview-text'>漏项识别与预算风险提示</Text>
              </View>
              <View className='preview-item'>
                <Text className='preview-icon'>⚖️</Text>
                <Text className='preview-text'>虚高价格项目明细</Text>
              </View>
            </>
          )}
        </View>
      </View>
    )
  }

  return (
    <View className='report-unlock-page'>
      <View className='nav-row'>
        <Text className='nav-back' onClick={handleBack}>返回</Text>
        <Text className='nav-title'>解锁报告</Text>
      </View>
      <View className='content'>
        <Text className='title'>解锁完整报告</Text>
        <Text className='report-which'>您正在解锁：{displayTitle}</Text>
        
        {/* 预览亮点区域 */}
        {renderPreviewHighlights()}
        {renderGenericPreview()}
        
        <View className='risk-tip'>
          <Text>⚠️ {riskTip}</Text>
        </View>
        
        {hasFreeUnlock && (
          <View className='free-unlock-section'>
            <Text className='free-unlock-title'>🎁 使用免费解锁权益</Text>
            <Text className='free-unlock-desc'>您有可用的免费解锁权益，可以免费解锁此报告</Text>
            <View className='free-unlock-btn' onClick={handleFreeUnlock}>
              <Text className='free-unlock-btn-text'>免费解锁本份报告</Text>
              <Text className='free-unlock-btn-desc'>使用1次免费解锁权益</Text>
            </View>
          </View>
        )}

        <View className='btns'>
          <View className='unlock-btn highlight' onClick={goPayment}>
            <Text className='price'>解锁本份报告 ￥9.9</Text>
            <Text className='desc'>含完整风险分析、PDF导出、律师解读与7天客服答疑</Text>
          </View>
          <View className='member-guide' onClick={() => Taro.navigateTo({ url: '/pages/membership/index' })}>
            <Text className='member-guide-text'>开通会员，所有报告+验收报告无限解锁 →</Text>
          </View>
        </View>

        {!hasFreeUnlock && !isChecking && (
          <View className='get-free-unlock'>
            <Text className='get-free-unlock-text'>没有免费解锁权益？</Text>
            <Text className='get-free-unlock-desc'>邀请好友注册即可获得免费解锁权益</Text>
            <View className='get-free-unlock-btn' onClick={() => Taro.navigateTo({ url: '/pages/invitation/index' })}>
              <Text>去邀请好友 →</Text>
            </View>
          </View>
        )}
      </View>
    </View>
  )
}

export default ReportUnlockPage

import React from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

const REPORT_TYPE_NAMES: Record<string, string> = {
  company: '公司风险报告',
  quote: '报价单分析报告',
  contract: '合同审核报告',
  acceptance: '验收报告'
}

/**
 * P27 报告解锁页 - 明确当前解锁哪份报告，仅支持解锁本份（一次扫描一份报告）
 */
const ReportUnlockPage: React.FC = () => {
  const { type, scanId, name, stage } = Taro.getCurrentInstance().router?.params || {}
  const reportType = type || 'report'
  const typeName = REPORT_TYPE_NAMES[reportType] || '完整报告'
  const reportName = name ? decodeURIComponent(name) : (stage ? `${stage}阶段` : '')
  const displayTitle = reportName ? `${typeName} - ${reportName}` : typeName

  const goPayment = () => {
    const q = new URLSearchParams()
    q.set('pkg', 'single')
    q.set('type', reportType)
    if (scanId) q.set('scanId', String(scanId))
    if (name) q.set('name', name)
    if (stage) q.set('stage', stage)
    Taro.navigateTo({ url: `/pages/payment/index?${q.toString()}` })
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

  return (
    <View className='report-unlock-page'>
      <View className='nav-row'>
        <Text className='nav-back' onClick={handleBack}>返回</Text>
        <Text className='nav-title'>解锁报告</Text>
      </View>
      <View className='content'>
        <Text className='title'>解锁完整报告</Text>
        <Text className='report-which'>您正在解锁：{displayTitle}</Text>
        <View className='risk-tip'>
          <Text>⚠️ {riskTip}</Text>
        </View>
        <View className='btns'>
          <View className='unlock-btn highlight' onClick={goPayment}>
            <Text className='price'>解锁本份报告 ￥9.9</Text>
            <Text className='desc'>含完整风险分析、PDF导出、律师解读与7天客服答疑</Text>
          </View>
          <View className='member-guide' onClick={() => Taro.navigateTo({ url: '/pages/membership/index' })}>
            <Text className='member-guide-text'>开通会员，所有报告+验收报告无限解锁 →</Text>
          </View>
        </View>
      </View>
    </View>
  )
}

export default ReportUnlockPage

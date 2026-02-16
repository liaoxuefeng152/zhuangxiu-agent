import React, { useState, useEffect } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { invitationsApi } from '../../services/api'
import './index.scss'

const REPORT_TYPE_NAMES: Record<string, string> = {
  company: '公司风险报告',
  quote: '报价单分析报告',
  contract: '合同审核报告',
  acceptance: '验收报告'
}

/**
 * P27 报告解锁页 - 明确当前解锁哪份报告，支持免费解锁权益（V2.6.8优化）
 */
const ReportUnlockPage: React.FC = () => {
  const { type, scanId, name, stage } = Taro.getCurrentInstance().router?.params || {}
  const reportType = type || 'report'
  const typeName = REPORT_TYPE_NAMES[reportType] || '完整报告'
  const reportName = name ? decodeURIComponent(name) : (stage ? `${stage}阶段` : '')
  const displayTitle = reportName ? `${typeName} - ${reportName}` : typeName

  const [hasFreeUnlock, setHasFreeUnlock] = useState(false)
  const [isChecking, setIsChecking] = useState(false)

  useEffect(() => {
    // 检查是否有免费解锁权益
    checkFreeUnlockEntitlements()
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
            <View className='get-free-unlock-btn' onClick={() => Taro.navigateTo({ url: '/pages/progress-share/index' })}>
              <Text>去邀请好友 →</Text>
            </View>
          </View>
        )}
      </View>
    </View>
  )
}

export default ReportUnlockPage

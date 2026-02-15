import React, { useState, useEffect, useRef } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getWithAuth, acceptanceApi } from '../../services/api'
import { transformBackendToFrontend, isAiUnavailableFallback } from '../../utils/acceptanceTransform'
import './index.scss'

/** 合同/报价 AI 分析可能需 40s～90s（扣子流式），超时时间设长一些 */
const TIMEOUT_COMPANY_QUOTE_CONTRACT = 90
/** 验收 AI 分析（OCR + 大模型）约 20s～90s */
const TIMEOUT_ACCEPTANCE = 90
const TIMEOUT_STAGE = 10

const PROGRESS_TEXTS: Record<string, string> = {
  company: '正在核验工商信息，检测中',
  quote: '正在分析报价单',
  contract: '正在审核合同',
  material: '正在生成【材料进场核对】台账报告',
  plumbing: 'AI正在分析隐蔽工程验收照片',
  carpentry: 'AI正在分析泥瓦工验收照片',
  woodwork: 'AI正在分析木工验收照片',
  painting: 'AI正在分析油漆验收照片',
  installation: 'AI正在分析安装收尾验收照片'
}

/**
 * P04 检测中页 - 按类型展示进度文案，超时重试，禁止返回 Toast，100% 自动跳转结果页
 */
const ScanProgressPage: React.FC = () => {
  const [uploadProgress, setUploadProgress] = useState(0)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [phase, setPhase] = useState<'upload' | 'analysis'>('upload')
  const [done, setDone] = useState(false)
  const [timeoutHit, setTimeoutHit] = useState(false)
  const timerRef = useRef<any>(null)
  const countRef = useRef<any>(null)
  const startTimeRef = useRef(Date.now())
  const mountedRef = useRef(true)
  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [])

  const { scanId, companyName, type, stage } = Taro.getCurrentInstance().router?.params || {}
  const scanIdNum = parseInt(scanId || '0', 10)
  const progressType = type || 'company'
  const stageKey = (type === 'acceptance' && stage) ? stage : progressType
  const isCompany = progressType === 'company'
  const [acceptancePending, setAcceptancePending] = useState<{ file_urls: string[] } | null>(null)
  const acceptanceReportRef = useRef<{ items: any[] } | null>(null)
  const isTwoPhase = progressType === 'quote' || progressType === 'contract' || !!(progressType === 'acceptance' && acceptancePending)
  const isStage = progressType === 'acceptance' || (!isCompany && !isTwoPhase && ['material', 'plumbing', 'carpentry', 'woodwork', 'painting', 'installation'].includes(progressType))
  const timeoutSec = progressType === 'acceptance' ? TIMEOUT_ACCEPTANCE : isStage ? TIMEOUT_STAGE : TIMEOUT_COMPANY_QUOTE_CONTRACT
  const progressText = PROGRESS_TEXTS[stageKey] || PROGRESS_TEXTS[progressType] || PROGRESS_TEXTS.company

  const currentProgress = isTwoPhase ? (phase === 'upload' ? uploadProgress : analysisProgress) : uploadProgress

  // 验收类型：从 Storage 读取 P15 上传后的待分析数据
  useEffect(() => {
    if (progressType === 'acceptance' && stageKey) {
      try {
        const raw = Taro.getStorageSync('construction_acceptance_pending_' + stageKey)
        if (raw) {
          const data = JSON.parse(raw)
          if (data?.file_urls?.length) setAcceptancePending(data)
        }
      } catch (_) {}
    }
  }, [progressType, stageKey])

  // 禁止返回：点击返回 Toast 提示
  useEffect(() => {
    const handler = () => {
      if (!done && !timeoutHit) {
        Taro.showToast({ title: '正在处理中，请稍候', icon: 'none' })
        return true
      }
      return false
    }
    // @ts-ignore
    if (Taro.onBackPress) Taro.onBackPress(handler)
    return () => {}
  }, [done, timeoutHit])

  // 超时检测
  useEffect(() => {
    if (done || timeoutHit) return
    const t = setTimeout(() => {
      setTimeoutHit(true)
    }, timeoutSec * 1000)
    return () => clearTimeout(t)
  }, [done, timeoutHit, timeoutSec])

  // 验收且有待分析数据：上传已完成，直接进入分析阶段
  const isAcceptanceWithApi = !!(progressType === 'acceptance' && acceptancePending)
  useEffect(() => {
    if (isAcceptanceWithApi) {
      setUploadProgress(100)
      setPhase('analysis')
    }
  }, [isAcceptanceWithApi])

  // 验收：调用后端 AI 分析接口
  useEffect(() => {
    if (!isAcceptanceWithApi || done || timeoutHit || !acceptancePending?.file_urls?.length) return () => {}
    const run = async () => {
      try {
        const res: any = await acceptanceApi.analyze(stageKey, acceptancePending.file_urls)
        const data = res?.data ?? res
        if (!mountedRef.current) return
        if (isAiUnavailableFallback(data)) {
          Taro.showToast({ title: 'AI验收失败，请稍后再试', icon: 'none' })
          try {
            Taro.removeStorageSync('construction_acceptance_pending_' + stageKey)
          } catch (_) {}
          setTimeoutHit(true)
          return
        }
        const { items } = transformBackendToFrontend(data)
        acceptanceReportRef.current = { items }
        try {
          Taro.removeStorageSync('construction_acceptance_pending_' + stageKey)
        } catch (_) {}
        setAnalysisProgress(100)
        setDone(true)
      } catch (e) {
        if (!mountedRef.current) return
        Taro.showToast({ title: 'AI验收失败，请稍后再试', icon: 'none' })
        try {
          Taro.removeStorageSync('construction_acceptance_pending_' + stageKey)
        } catch (_) {}
        setTimeoutHit(true)
      }
    }
    run()
    return () => {}
  }, [isAcceptanceWithApi, acceptancePending, stageKey, done, timeoutHit])

  // 进度模拟（回调内检查 mounted，避免 redirect 后定时器仍执行导致 __subPageFrameEndTime__ 报错）
  // 验收走真实 API 时，只做分析进度动画，不在此处 setDone；验收无待分析数据时不跑进度
  useEffect(() => {
    if (timeoutHit || (progressType === 'acceptance' && !acceptancePending)) return () => {}
    if (isTwoPhase) {
      const step = () => {
        try {
          if (!mountedRef.current) return
          if (phase === 'upload') {
            setUploadProgress((p) => {
              if (p >= 100) {
                setPhase('analysis')
                return 100
              }
              return Math.min(p + 12, 100)
            })
          } else {
            setAnalysisProgress((p) => {
              if (p >= 100 && !isAcceptanceWithApi) {
                setDone(true)
                return 100
              }
              return Math.min(p + (isAcceptanceWithApi ? 1 : 6), 100)
            })
          }
        } catch (_) {
          // 小程序 redirect 后定时器仍可能触发，吞掉 __subPageFrameEndTime__ 等异常
        }
      }
      const t = setInterval(step, isAcceptanceWithApi ? 800 : 300)
      return () => clearInterval(t)
    } else {
      const step = () => {
        try {
          if (!mountedRef.current) return
          setUploadProgress((p) => {
            if (p >= 100) {
              setDone(true)
              return 100
            }
            return Math.min(p + 8, 100)
          })
        } catch (_) {
          // 小程序 redirect 后定时器仍可能触发，吞掉 __subPageFrameEndTime__ 等异常
        }
      }
      const t = setInterval(step, 400)
      return () => clearInterval(t)
    }
  }, [isTwoPhase, phase, timeoutHit, isAcceptanceWithApi])

  // 轮询公司检测结果
  useEffect(() => {
    if (!scanIdNum || !isCompany || timeoutHit) return () => {}
    const poll = async () => {
      if (!mountedRef.current) return
      try {
        const res = await getWithAuth(`/companies/scan/${scanIdNum}`)
        if (!mountedRef.current) return
        if (res?.status === 'completed') {
          try {
            if (!mountedRef.current) return
            setUploadProgress(100)
            setDone(true)
          } catch (_) {
            // 页面已销毁时 setState 可能报 __subPageFrameEndTime__
          }
        }
      } catch {
        // ignore
      }
    }
    const t = setInterval(poll, 1500)
    return () => { clearInterval(t) }
  }, [scanIdNum, isCompany, timeoutHit])

  // 轮询合同分析结果（后端分析约 40s～90s，轮询到 status=completed 再跳转）
  useEffect(() => {
    if (!scanIdNum || progressType !== 'contract' || timeoutHit) return () => {}
    const poll = async () => {
      if (!mountedRef.current) return
      try {
        const res = await getWithAuth(`/contracts/contract/${scanIdNum}`)
        if (!mountedRef.current) return
        if (res?.status === 'completed') {
          try {
            if (!mountedRef.current) return
            setAnalysisProgress(100)
            setDone(true)
          } catch (_) {
            // 页面已销毁时 setState 可能报 __subPageFrameEndTime__
          }
        }
      } catch {
        // ignore
      }
    }
    const t = setInterval(poll, 2000)
    return () => { clearInterval(t) }
  }, [scanIdNum, progressType, timeoutHit])

  // 轮询报价单分析结果
  useEffect(() => {
    if (!scanIdNum || progressType !== 'quote' || timeoutHit) return () => {}
    const poll = async () => {
      if (!mountedRef.current) return
      try {
        const res = await getWithAuth(`/quotes/quote/${scanIdNum}`)
        if (!mountedRef.current) return
        if (res?.status === 'completed') {
          try {
            if (!mountedRef.current) return
            setAnalysisProgress(100)
            setDone(true)
          } catch (_) {
            // 页面已销毁时 setState 可能报 __subPageFrameEndTime__
          }
        }
      } catch {
        // ignore
      }
    }
    const t = setInterval(poll, 2000)
    return () => { clearInterval(t) }
  }, [scanIdNum, progressType, timeoutHit])

  // 100% 自动跳转对应结果页；验收类型时仅写入后端 AI 真实数据，不展示假数据
  useEffect(() => {
    if (!done) return
    const reportType = isCompany ? 'company' : progressType === 'quote' ? 'quote' : progressType === 'contract' ? 'contract' : 'acceptance'
    if (isStage && stageKey) {
      const REPORT_KEY = 'construction_acceptance_report_'
      const STATUS_KEY = 'construction_stage_status'
      const realItems = acceptanceReportRef.current?.items
      if (!realItems?.length) {
        return
      }
      try {
        Taro.setStorageSync(REPORT_KEY + stageKey, JSON.stringify({ items: realItems }))
        const raw = Taro.getStorageSync(STATUS_KEY)
        const status: Record<string, string> = raw ? JSON.parse(raw) : {}
        status[stageKey] = 'completed'
        Taro.setStorageSync(STATUS_KEY, JSON.stringify(status))
      } catch (_) {}
    }
    const url = isStage
      ? `/pages/acceptance/index?stage=${stageKey}`
      : `/pages/report-detail/index?type=${reportType}&scanId=${scanId || 0}&name=${encodeURIComponent(companyName || '')}`
    const t = setTimeout(() => {
      Taro.redirectTo({ url })
    }, 800)
    return () => clearTimeout(t)
  }, [done, isCompany, isStage, stageKey, scanId, companyName])

  const handleRetry = () => {
    if (!timeoutHit) return
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
    setTimeoutHit(false)
    setUploadProgress(0)
    setAnalysisProgress(0)
    setPhase('upload')
    setDone(false)
    startTimeRef.current = Date.now()
    const step = () => {
      try {
        if (!mountedRef.current) return
        setUploadProgress((p) => {
          if (p >= 100) {
            setDone(true)
            return 100
          }
          return Math.min(p + 8, 100)
        })
      } catch (_) {
        // 小程序页面销毁后 setState 可能报 __subPageFrameEndTime__
      }
    }
    const t = setInterval(step, 400)
    timerRef.current = t
    setTimeout(() => {
      if (timerRef.current === t) {
        clearInterval(t)
        timerRef.current = null
      }
    }, 5000)
  }

  const handleViewReport = () => {
    const reportType = isCompany ? 'company' : progressType === 'quote' ? 'quote' : progressType === 'contract' ? 'contract' : 'acceptance'
    const url = isStage
      ? `/pages/acceptance/index?stage=${stageKey}`
      : `/pages/report-detail/index?type=${reportType}&scanId=${scanId || 0}&name=${encodeURIComponent(companyName || '')}`
    Taro.redirectTo({ url })
  }

  if (timeoutHit) {
    return (
      <View className='scan-progress-page'>
        <View className='loading-wrap'>
          <View className='loading-icon'>⏳</View>
          <Text className='progress-text'>{progressType === 'acceptance' ? 'AI验收失败，请稍后再试' : '分析超时，点击重试'}</Text>
          <View className='progress-bar' onClick={handleRetry}>
            <View className='progress-fill' style={{ width: '0%' }} />
          </View>
          <Text className='retry-hint'>点击进度条重新检测</Text>
        </View>
      </View>
    )
  }

  // 验收类型但无待分析数据：提示从拍照页上传
  if (progressType === 'acceptance' && !acceptancePending) {
    return (
      <View className='scan-progress-page'>
        <View className='loading-wrap'>
          <View className='loading-icon'>⚠️</View>
          <Text className='progress-text'>请从拍照页上传照片后再检测</Text>
          <View className='progress-bar' onClick={() => Taro.navigateBack()}>
            <View className='progress-fill' style={{ width: '0%' }} />
          </View>
          <Text className='retry-hint'>点击返回</Text>
        </View>
      </View>
    )
  }

  return (
    <View className='scan-progress-page'>
      {!done ? (
        <View className='loading-wrap'>
          <View className='loading-icon'>⏳</View>
          {isTwoPhase ? (
            <>
              <View className='two-phase-bar'>
                <View className='phase-seg'>
                  <Text className='phase-label'>上传</Text>
                  <View className='phase-fill-wrap'>
                    <View className='phase-fill' style={{ width: `${uploadProgress}%` }} />
                  </View>
                </View>
                <View className='phase-seg'>
                  <Text className='phase-label'>分析</Text>
                  <View className='phase-fill-wrap'>
                    <View className='phase-fill' style={{ width: `${analysisProgress}%` }} />
                  </View>
                </View>
              </View>
              <Text className='progress-text'>
                {phase === 'upload' ? '正在上传文件…' : `${progressText}…${currentProgress}%`}
              </Text>
            </>
          ) : (
            <>
              <View className='progress-bar'>
                <View className='progress-fill' style={{ width: `${uploadProgress}%` }} />
              </View>
              <Text className='progress-text'>{progressText}…{currentProgress}%</Text>
            </>
          )}
          <Text className='remain-text'>分析完成后自动跳转，请勿退出页面</Text>
        </View>
      ) : (
        <View className='done-wrap'>
          <Text className='done-icon'>✅</Text>
          <Text className='done-title'>检测完成</Text>
          <View className='view-report-btn' onClick={handleViewReport}>
            <Text className='btn-text'>查看报告</Text>
          </View>
          <Text className='auto-redirect'>正在跳转...</Text>
        </View>
      )}
    </View>
  )
}

export default ScanProgressPage

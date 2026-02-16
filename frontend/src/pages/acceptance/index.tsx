import React, { useState, useEffect, useCallback, useRef } from 'react'
import { View, Text, ScrollView, Image, Textarea } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import { safeSwitchTab, TAB_CONSTRUCTION } from '../../utils/navigation'
import { useAppSelector } from '../../store/hooks'
import { putWithAuth, getWithAuth, acceptanceApi, reportApi, pointsApi } from '../../services/api'
import { getBackendStageCode, getCompletionPayload, persistStageStatusToStorage } from '../../utils/constructionStage'
import { transformBackendToFrontend, isAiUnavailableFallback } from '../../utils/acceptanceTransform'
import './index.scss'

const STORAGE_KEY_REPORT = 'construction_acceptance_report_'

const STAGE_TITLES: Record<string, string> = {
  material: 'S00材料进场核对台账',
  plumbing: '水电阶段验收报告',
  carpentry: '泥瓦工阶段验收报告',
  woodwork: '木工阶段验收报告',
  painting: '油漆阶段验收报告',
  flooring: '地板阶段验收报告',
  soft_furnishing: '软装阶段验收报告',
  installation: '安装收尾阶段验收报告'
}

type ResultItem = { level: 'high' | 'mid' | 'low'; title: string; desc: string; suggest: string }

/**
 * P30 阶段验收/台账报告页（最终完整版）- 整改/复检/导出/申诉
 */
const AcceptancePage: React.FC = () => {
  const router = Taro.getCurrentInstance().router
  const stage = (router?.params?.stage as string) || 'plumbing'
  const forceLock = router?.params?.forceLock === '1' // 调试：?forceLock=1 强制未解锁态
  const userInfo = useAppSelector((s) => s.user.userInfo)

  // 微信小程序 scroll-view 需明确高度才能滚动，用 getSystemInfo 计算
  const [scrollHeight, setScrollHeight] = useState<string>('100vh')
  useEffect(() => {
    try {
      const sys = Taro.getSystemInfoSync()
      const statusBar = sys.statusBarHeight ?? 20
      const navPx = Math.ceil((88 * (sys.windowWidth ?? 375)) / 750)
      const h = (sys.windowHeight ?? 667) - statusBar - navPx
      setScrollHeight(`${h}px`)
    } catch (_) {}
  }, [])
  const isMember = userInfo?.isMember ?? !!Taro.getStorageSync('is_member')
  const [unlocked, setUnlocked] = useState(false)
  const [apiUnlocked, setApiUnlocked] = useState(false)
  const refreshUnlocked = useCallback(() => {
    if (forceLock) {
      setUnlocked(false)
      return
    }
    const stageUnlocked = !!Taro.getStorageSync(`report_unlocked_acceptance_${stage}`)
    const ok = isMember || stageUnlocked || apiUnlocked
    setUnlocked(ok)
  }, [stage, isMember, forceLock, apiUnlocked])

  const [uploaded, setUploaded] = useState<string[]>([])
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<{ items: ResultItem[] } | null>(null)
  const [rectifyStatus, setRectifyStatus] = useState<'none' | 'recheck' | 'done'>('none')
  const [recheckCount, setRecheckCount] = useState(0)
  const [detailModal, setDetailModal] = useState<ResultItem | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadFailed, setLoadFailed] = useState(false)
  const [btnDisabled, setBtnDisabled] = useState(false)

  // 申诉
  const [appealStatus, setAppealStatus] = useState<'none' | 'pending' | 'rejected' | 'approved'>('none')
  const [appealModal, setAppealModal] = useState(false)
  const [appealReason, setAppealReason] = useState('')
  const [appealImages, setAppealImages] = useState<string[]>([])
  const [appealSubmitting, setAppealSubmitting] = useState(false)
  const [appealSuccessModal, setAppealSuccessModal] = useState(false)
  const [rejectTipVisible, setRejectTipVisible] = useState(false)
  const [isAppealRevised, setIsAppealRevised] = useState(false) // 申诉复核版
  const [photoErrors, setPhotoErrors] = useState<Set<number>>(new Set()) // 照片加载失败索引

  // 申请复检弹窗
  const [recheckModal, setRecheckModal] = useState(false)
  const [recheckPhotos, setRecheckPhotos] = useState<string[]>([])
  const [recheckSubmitting, setRecheckSubmitting] = useState(false)

  // 标记为已通过弹窗
  const [markPassedModal, setMarkPassedModal] = useState(false)
  const [markPassedPhotos, setMarkPassedPhotos] = useState<string[]>([])
  const [markPassedNote, setMarkPassedNote] = useState('')
  const [markPassedSubmitting, setMarkPassedSubmitting] = useState(false)
  const [severity, setSeverity] = useState<string>('') // 风险等级：high/mid/low
  const [stageStatus, setStageStatus] = useState<string>('') // 阶段状态：用于判断是否为rectify_exhausted
  const [acceptanceTime, setAcceptanceTime] = useState<string>('') // 验收时间：后端 created_at

  const pageTitle = STAGE_TITLES[stage] || '验收报告'
  const items = (result?.items ?? []).slice().sort((a, b) => {
    const order: Record<string, number> = { high: 0, mid: 1, low: 2 }
    return (order[a.level] ?? 2) - (order[b.level] ?? 2)
  })
  const qualifiedCount = items.filter((i) => i.level === 'low').length
  const unqualifiedCount = items.filter((i) => i.level === 'high' || i.level === 'mid').length
  const unqualifiedItems = items.filter((i) => i.level === 'high' || i.level === 'mid')
  const hasUnqualified = unqualifiedCount > 0
  const statusLabel =
    rectifyStatus === 'done'
      ? '已通过'
      : rectifyStatus === 'recheck'
        ? '待复检'
        : hasUnqualified
          ? '未通过'
          : '已通过'
  const statusClass =
    statusLabel === '已通过' ? 'pass' : statusLabel === '待复检' ? 'pending' : 'fail'
  const showRectifyArea = hasUnqualified && (statusLabel === '未通过' || statusLabel === '待复检')
  const showAppealBtn = result && statusLabel === '未通过' && appealStatus !== 'pending'
  // 判断是否显示"标记为已通过"按钮：复检3次已用完，且低/中风险（后端会校验rectify_exhausted）
  const canMarkPassed = recheckCount >= 3 && statusLabel === '未通过' && 
    (severity === 'low' || severity === 'mid' || severity === 'warning' || severity === 'pass') && 
    severity !== 'high'

  useEffect(() => {
    refreshUnlocked()
  }, [refreshUnlocked])

  useDidShow(() => {
    refreshUnlocked()
    const analysisId = router?.params?.id
    if (analysisId && result) {
      acceptanceApi.getResult(Number(analysisId)).then((res: any) => {
        const data = res?.data ?? res
        const payload = { ...data, summary: data?.result_json?.summary ?? data?.summary }
        if (isAiUnavailableFallback(payload)) return
        const { items } = transformBackendToFrontend(payload)
        if (items?.length) setResult({ items })
        const rs = (data?.result_status ?? '') as string
        setRectifyStatus(mapResultStatusToRectify(rs))
      }).catch(() => {})
    }
  })

  // 从后端 result_status 映射到前端 rectifyStatus
  const mapResultStatusToRectify = (resultStatus: string): 'none' | 'recheck' | 'done' => {
    if (resultStatus === 'pending_recheck') return 'recheck'
    if (resultStatus === 'passed') return 'done'
    return 'none'
  }

  // 进入页时：若 P04 已写入报告，则直接展示；支持 ?id= 从后端拉取
  useEffect(() => {
    if (!stage) return
    const analysisId = router?.params?.id
    if (analysisId) {
      setLoading(true)
      acceptanceApi.getResult(Number(analysisId)).then((res: any) => {
        const data = res?.data ?? res
        const payload = { ...data, summary: data?.result_json?.summary ?? data?.summary }
        if (isAiUnavailableFallback(payload)) {
          setLoadFailed(true)
          return
        }
        const { items } = transformBackendToFrontend(payload)
        if (items?.length) setResult({ items })
        const rs = (data?.result_status ?? data?.resultStatus ?? '') as string
        setRectifyStatus(mapResultStatusToRectify(rs))
        const rc = Number(data?.recheck_count ?? 0) || 0
        setRecheckCount(rc)
        const sev = (data?.severity ?? '') as string
        setSeverity(sev)
        const createdAt = data?.created_at
        if (createdAt) {
          try {
            const d = new Date(createdAt.indexOf('Z') >= 0 || /[+-]\d{2}:?\d{2}$/.test(createdAt) ? createdAt : createdAt + 'Z')
            setAcceptanceTime(isNaN(d.getTime()) ? '' : d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }))
          } catch { setAcceptanceTime('') }
        }
        if (data?.is_unlocked === true) {
          Taro.setStorageSync(`report_unlocked_acceptance_${stage}`, true)
          refreshUnlocked()
        }
        // 获取Construction阶段状态
        getWithAuth('/constructions/schedule').then((scheduleRes: any) => {
          const scheduleData = scheduleRes?.data ?? scheduleRes
          const stages = scheduleData?.stages ?? {}
          const stageMap: Record<string, string> = {
            plumbing: 'S01', carpentry: 'S02', woodwork: 'S03',
            painting: 'S04', installation: 'S05', material: 'S00'
          }
          const backendStage = stageMap[stage] || stage
          const stageInfo = stages[backendStage] || {}
          const status = stageInfo?.status || ''
          setStageStatus(status)
        }).catch(() => {})
      }).catch(() => setLoadFailed(true)).finally(() => setLoading(false))
      return
    }
    try {
      const saved = Taro.getStorageSync(STORAGE_KEY_REPORT + stage)
      if (saved) {
        const data = JSON.parse(saved)
        if (data?.items?.length) setResult({ items: data.items })
      }
    } catch (_) {}
  }, [stage, router?.params?.id])

  const hasSyncedPassRef = useRef(false)

  useEffect(() => {
    if (!stage || !result) return
    if (statusLabel === '已通过' && rectifyStatus !== 'recheck') {
      if (hasSyncedPassRef.current) return
      hasSyncedPassRef.current = true
      syncStageStatus(getCompletionPayload(stage))
    } else if (statusLabel !== '已通过') {
      hasSyncedPassRef.current = false
    }
  }, [stage, statusLabel, rectifyStatus, result, syncStageStatus])

  const chooseImage = () => {
    const p = Taro.chooseImage({
      count: 9 - uploaded.length,
      sourceType: ['camera', 'album'],
      fail: (err) => {
        if (!err?.errMsg?.includes('cancel')) Taro.showToast({ title: '选择失败', icon: 'none' })
      },
      success: async (res) => {
        const next = [...uploaded, ...res.tempFilePaths].slice(0, 9)
        setUploaded(next)
        if (next.length > 0 && !result) {
          setAnalyzing(true)
          setLoadFailed(false)
          try {
            const fileUrls: string[] = []
            for (const path of next) {
              const up: any = await acceptanceApi.uploadPhoto(path)
              const out = up?.data ?? up
              const key = out?.object_key ?? out?.file_url
              if (key) fileUrls.push(typeof key === 'string' ? key : (key.file_url || key.object_key))
            }
            if (fileUrls.length === 0) throw new Error('上传失败')
            const analyzeRes: any = await acceptanceApi.analyze(stage || 'plumbing', fileUrls)
            const data = analyzeRes?.data ?? analyzeRes
            if (isAiUnavailableFallback(data)) {
              Taro.showToast({ title: 'AI验收失败，请稍后再试', icon: 'none' })
              setLoadFailed(true)
              return
            }
            const { items } = transformBackendToFrontend(data)
            setResult({ items })
          } catch (e: any) {
            Taro.showToast({ title: 'AI验收失败，请稍后再试', icon: 'none' })
            setLoadFailed(true)
          } finally {
            setAnalyzing(false)
          }
        }
      }
    })
    if (p && typeof (p as Promise<unknown>).catch === 'function') (p as Promise<unknown>).catch(() => {})
  }

  const handleUnlock = () => {
    const q = new URLSearchParams()
    q.set('type', 'acceptance')
    q.set('stage', stage || '')
    acceptanceApi.getList({ stage: stage || 'plumbing', page: 1, page_size: 1 }).then((listRes: any) => {
      const list = listRes?.data?.list ?? listRes?.list ?? []
      const analysisId = list?.[0]?.id
      if (analysisId) q.set('scanId', String(analysisId))
      Taro.navigateTo({ url: '/pages/report-unlock/index?' + q.toString() })
    }).catch(() => {
      Taro.navigateTo({ url: '/pages/report-unlock/index?type=acceptance&stage=' + (stage || '') })
    })
  }

  const handleShare = () => {
    // 跳转到分享页面
    const analysisId = router?.params?.id
    const shareUrl = `/pages/report-share/index?stage=${stage}${analysisId ? `&id=${analysisId}` : ''}`
    Taro.navigateTo({ url: shareUrl })
  }

  const syncStageStatus = useCallback(
    async (nextStatus: string, toastMessage?: string) => {
      if (!stage) return false
      try {
        await putWithAuth('/constructions/stage-status', { stage: getBackendStageCode(stage), status: nextStatus })
        persistStageStatusToStorage(stage, nextStatus)
        if (toastMessage) Taro.showToast({ title: toastMessage, icon: 'success' })
        return true
      } catch (error: any) {
        const message = error?.response?.data?.detail || '状态更新失败，请稍后重试'
        Taro.showToast({ title: message, icon: 'none' })
        return false
      }
    },
    [stage]
  )

  const openRecheckModal = () => {
    setRecheckModal(true)
    setRecheckPhotos([])
  }

  const openMarkPassedModal = () => {
    setMarkPassedModal(true)
    setMarkPassedPhotos([])
    setMarkPassedNote('')
  }

  const addMarkPassedPhoto = () => {
    Taro.chooseImage({
      count: 5 - markPassedPhotos.length,
      sourceType: ['camera', 'album'],
      success: (res) => {
        setMarkPassedPhotos((prev) => [...prev, ...(res.tempFilePaths || [])].slice(0, 5))
      }
    }).catch(() => {})
  }

  const handleSubmitMarkPassed = async () => {
    if (markPassedPhotos.length < 1) {
      Taro.showToast({ title: '请上传至少1张说明照片', icon: 'none' })
      return
    }
    if (!markPassedNote || markPassedNote.trim().length < 20) {
      Taro.showToast({ title: '说明文字至少20字', icon: 'none' })
      return
    }
    if (markPassedSubmitting) return
    setMarkPassedSubmitting(true)
    try {
      const analysisId = router?.params?.id
      if (!analysisId) throw new Error('缺少验收记录ID')
      
      const fileUrls: string[] = []
      for (const path of markPassedPhotos) {
        const up: any = await acceptanceApi.uploadPhoto(path)
        const out = up?.data ?? up
        const key = out?.object_key ?? out?.file_url
        if (key) fileUrls.push(typeof key === 'string' ? key : (key.file_url || key.object_key))
      }
      if (fileUrls.length === 0) throw new Error('上传失败')
      
      await acceptanceApi.markPassed(Number(analysisId), fileUrls, markPassedNote.trim())
      
      Taro.showToast({ title: '已标记为已通过，可进入下一阶段', icon: 'success' })
      setMarkPassedModal(false)
      
      // 刷新验收结果
      const res: any = await acceptanceApi.getResult(Number(analysisId))
      const data = res?.data ?? res
      const payload = { ...data, summary: data?.result_json?.summary ?? data?.summary }
      const { items } = transformBackendToFrontend(payload)
      if (items?.length) setResult({ items })
      const rs = (data?.result_status ?? '') as string
      setRectifyStatus(mapResultStatusToRectify(rs))
      
      // 同步阶段状态
      await syncStageStatus('passed')
    } catch (error: any) {
      const message = error?.response?.data?.detail || error?.message || '操作失败，请稍后重试'
      Taro.showToast({ title: message, icon: 'none' })
    } finally {
      setMarkPassedSubmitting(false)
    }
  }

  const addRecheckPhoto = () => {
    Taro.chooseImage({
      count: 5 - recheckPhotos.length,
      sourceType: ['camera', 'album'],
      success: (res) => {
        setRecheckPhotos((prev) => [...prev, ...(res.tempFilePaths || [])].slice(0, 5))
      }
    }).catch(() => {})
  }

  const handleSubmitRecheck = async () => {
    if (recheckPhotos.length === 0) {
      Taro.showToast({ title: '请上传整改后照片（最多5张）', icon: 'none' })
      return
    }
    if (recheckSubmitting) return
    setRecheckSubmitting(true)
    try {
      const fileUrls: string[] = []
      for (const path of recheckPhotos) {
        const up: any = await acceptanceApi.uploadPhoto(path)
        const out = up?.data ?? up
        const key = out?.object_key ?? out?.file_url
        if (key) fileUrls.push(typeof key === 'string' ? key : (key.file_url || key.object_key))
      }
      if (fileUrls.length === 0) throw new Error('上传失败')
      let listRes: any = await acceptanceApi.getList({ stage: stage || 'plumbing', page: 1, page_size: 1 })
      let list = listRes?.data?.list ?? listRes?.list ?? []
      if (!list?.length) {
        const backendStage = getBackendStageCode(stage || 'plumbing')
        listRes = await acceptanceApi.getList({ stage: backendStage, page: 1, page_size: 1 })
        list = listRes?.data?.list ?? listRes?.list ?? []
      }
      const analysisId = list?.[0]?.id
      if (!analysisId) throw new Error('暂无验收记录')
      await acceptanceApi.requestRecheck(analysisId, fileUrls)
      await syncStageStatus('pending_recheck', '已提交，AI复检分析中...')
      setRectifyStatus('recheck')
      setRecheckCount((c) => c + 1)
      setRecheckModal(false)
      setAnalyzing(true)
      const pollInterval = 2000
      const maxWait = 90000
      const start = Date.now()
      const poll = async () => {
        if (Date.now() - start > maxWait) {
          setAnalyzing(false)
          Taro.showToast({ title: '复检分析超时，请稍后刷新查看', icon: 'none' })
          return
        }
        try {
          const res: any = await acceptanceApi.getResult(analysisId)
          const data = res?.data ?? res
          const rs = (data?.result_status ?? '') as string
          if (rs !== 'pending_recheck') {
            const payload = { ...data, summary: data?.result_json?.summary ?? data?.summary }
            if (!isAiUnavailableFallback(payload)) {
              const { items } = transformBackendToFrontend(payload)
              if (items?.length) setResult({ items })
              setRectifyStatus(mapResultStatusToRectify(rs))
              const rc = Number(data?.recheck_count ?? 0) || 0
              setRecheckCount(rc)
              Taro.showToast({ title: rs === 'passed' ? '复检通过' : '请按整改建议继续整改', icon: 'success' })
            }
            setAnalyzing(false)
            return
          }
        } catch (_) {
          // 继续轮询
        }
        setTimeout(poll, pollInterval)
      }
      setTimeout(poll, pollInterval)
    } catch (e: any) {
      const msg = e?.response?.data?.detail ?? e?.message ?? '提交失败，请重试'
      Taro.showToast({ title: typeof msg === 'string' ? msg : '提交失败，请重试', icon: 'none' })
    } finally {
      setRecheckSubmitting(false)
    }
  }

  const handleExportPdf = async () => {
    if (!result) {
      Taro.showToast({ title: '请先完成验收', icon: 'none' })
      return
    }
    if (btnDisabled || !unlocked) return
    try {
      Taro.showLoading({ title: '正在生成PDF...' })
      const stageParam = stage || 'plumbing'
      let listRes: any = await acceptanceApi.getList({ stage: stageParam, page: 1, page_size: 1 })
      let list = listRes?.data?.list ?? listRes?.list ?? []
      if (!list?.length) {
        const backendStage = getBackendStageCode(stageParam)
        if (backendStage !== stageParam) {
          listRes = await acceptanceApi.getList({ stage: backendStage, page: 1, page_size: 1 })
          list = listRes?.data?.list ?? listRes?.list ?? []
        }
      }
      const analysisId = list?.[0]?.id
      if (!analysisId) {
        Taro.hideLoading()
        Taro.showToast({ title: '暂无验收记录，无法导出', icon: 'none' })
        return
      }
      await reportApi.downloadPdf('acceptance', analysisId)
      Taro.hideLoading()
      Taro.showToast({ title: '导出成功', icon: 'success' })
    } catch (e: any) {
      Taro.hideLoading()
      Taro.showToast({ title: e?.message || '导出失败', icon: 'none' })
    }
  }

  const goAiSupervision = () => {
    const firstIssue = items.find((i) => i.level === 'high' || i.level === 'mid')
    const summary = firstIssue ? firstIssue.title : '验收问题咨询'
    Taro.navigateTo({
      url: `/pages/ai-supervision/index?stage=${stage}&summary=${encodeURIComponent(summary)}&reportId=${encodeURIComponent(stage + '_' + Date.now())}`
    })
  }

  const openAppealModal = () => {
    setAppealModal(true)
    setAppealReason('')
    setAppealImages([])
  }

  const addAppealImage = () => {
    Taro.chooseImage({
      count: 3 - appealImages.length,
      sourceType: ['camera', 'album'],
      success: (res) => {
        const files = res.tempFiles || []
        for (const f of files) {
          if (f.size && f.size > 10 * 1024 * 1024) {
            Taro.showToast({ title: '仅支持JPG/PNG格式，单张图片不超过10M', icon: 'none' })
            return
          }
        }
        setAppealImages((prev) => [...prev, ...(res.tempFilePaths || [])].slice(0, 3))
      }
    }).catch(() => {})
  }

  const submitAppeal = () => {
    const reason = appealReason.trim()
    if (!reason) return
    setAppealSubmitting(true)
    Taro.showLoading({ title: '提交中...' })
    setTimeout(() => {
      Taro.hideLoading()
      setAppealSubmitting(false)
      setAppealModal(false)
      setAppealStatus('pending')
      setAppealSuccessModal(true)
    }, 800)
  }

  return (
    <View className='acceptance-page'>
      {/* P30 顶部导航栏：V2.6.4 先解锁后导出，未解锁显示「解锁报告」，已解锁显示「PDF导出」 */}
      {/* V2.6.7优化：申诉移至底部操作区，导航栏仅保留PDF导出/解锁报告 */}
      <View className='nav-bar'>
        <Text className='nav-back' onClick={() => Taro.navigateBack()}>返回</Text>
        <Text className='nav-title'>{pageTitle}</Text>
        <View className='nav-right-wrap'>
          {result ? (
            <>
              {unlocked ? (
                <View className='nav-pdf' onClick={handleExportPdf}>
                  <Text className='nav-pdf-icon'>📄</Text>
                  <Text className='nav-pdf-text'>PDF导出</Text>
                </View>
              ) : (
                <Text className='nav-unlock' onClick={handleUnlock}>解锁报告</Text>
              )}
            </>
          ) : (
            <View className='nav-placeholder' />
          )}
        </View>
      </View>

      {/* 申诉驳回提示条 */}
      {rejectTipVisible && (
        <View className='reject-tip'>
          <Text className='reject-tip-text'>您的申诉已驳回，请按原报告整改后重新申请复检。</Text>
          <Text className='reject-tip-close' onClick={() => setRejectTipVisible(false)}>×</Text>
        </View>
      )}

      <ScrollView scrollY className='scroll-body-outer' style={{ height: scrollHeight }}>
        <View className='scroll-body'>
        {loading && (
          <View className='skeleton'>
            <View className='skeleton-line' />
            <View className='skeleton-line short' />
            <View className='skeleton-line' />
          </View>
        )}

        {loadFailed && !result && (
          <View className='load-fail' onClick={() => setLoadFailed(false)}>
            <Text>加载失败，点击重试</Text>
          </View>
        )}

        {!result && !loading && !loadFailed && (
          <View className='section empty-report-section'>
            <Text className='empty-report-title'>暂无验收报告</Text>
            <Text className='empty-report-desc'>请从施工陪伴页完成「AI验收」后在此查看报告</Text>
            <View className='btn-back-inline' onClick={() => safeSwitchTab(TAB_CONSTRUCTION)}>
              <Text>返回施工陪伴</Text>
            </View>
          </View>
        )}

        {analyzing && (
          <View className='analyzing'>
            <Text className='loading-icon'>⏳</Text>
            <Text>AI分析中，请稍候...</Text>
          </View>
        )}

        {result && !analyzing && (
          <>
            {/* 验收概览：含申诉复核版标注、风险等级 */}
            <View className='overview-card'>
              <View className='overview-status-row'>
                <View className={`status-tag ${statusClass}`}>{statusLabel}</View>
                {isAppealRevised && <Text className='status-appeal-tag'>（申诉复核版）</Text>}
                {statusLabel === '未通过' && severity && (
                  <Text className='overview-risk'>
                    风险等级：{severity === 'high' ? '高风险' : severity === 'warning' || severity === 'mid' ? '中风险' : '低风险'}
                  </Text>
                )}
              </View>
              <Text className='overview-time'>验收时间：{acceptanceTime || '-'}</Text>
              <Text className='overview-data'>验收项 {items.length} 项 / 合格 {qualifiedCount} 项 / 不合格 {unqualifiedCount} 项</Text>
            </View>

            {/* 验收详情列表：V2.6.4 未解锁时展示1-2个真实不合格项预览 */}
            <View className='section list-section'>
              <Text className='section-title'>验收详情</Text>
              {(unlocked ? items : unqualifiedItems.slice(0, 2)).map((item, i) => (
                <View key={i} className='detail-row'>
                  <View className='detail-left'>
                    <Text className='detail-name'>{item.title}</Text>
                    <Text className='detail-standard'>{item.desc}</Text>
                  </View>
                  <View className='detail-right'>
                    <Text className={`result-tag ${item.level === 'low' ? 'pass' : 'fail'}`}>{item.level === 'low' ? '合格' : '不合格'}</Text>
                    {unlocked && <Text className='link-detail' onClick={() => setDetailModal(item)}>查看详情</Text>}
                  </View>
                </View>
              ))}
              {!unlocked && items.length > 0 && (
                <View className='preview-lock-tip'>
                  <Text className='preview-lock-text'>解锁后可查看全部 {items.length} 项问题详情、整改建议及 PDF 导出</Text>
                </View>
              )}
            </View>

            {/* 不合格项整改区：申请复检（最多3次），与咨询AI监理并列 */}
            {showRectifyArea && (
              <View className={`section rectify-section ${!unlocked ? 'section-locked' : ''}`}>
                <Text className='section-title'>不合格项整改</Text>
                <Text className='rectify-desc'>
                  {recheckCount < 3 
                    ? `请按上述验收详情中的整改建议完成整改后，点击「申请复检」上传整改照片，将自动触发AI复检。还可申请复检 ${3 - recheckCount}/3 次`
                    : '复检次数已用完（最多3次）。可进入下一阶段，或点击「申诉」提交审核，或点击「标记为已通过」自行确认（仅限低/中风险问题）'
                  }
                </Text>
                <View className='rectify-actions'>
                  {recheckCount < 3 ? (
                    <>
                      <View className='rectify-btn primary' onClick={openRecheckModal}><Text>申请复检</Text></View>
                      <View className='rectify-btn yellow' onClick={goAiSupervision}><Text>咨询AI监理</Text></View>
                    </>
                  ) : (
                    <>
                      {canMarkPassed && (
                        <View className='rectify-btn secondary' onClick={openMarkPassedModal}>
                          <Text>标记为已通过</Text>
                        </View>
                      )}
                      <View className='rectify-btn yellow' onClick={goAiSupervision}><Text>咨询AI监理</Text></View>
                    </>
                  )}
                </View>
                {!unlocked && (
                  <View className='section-lock-overlay' onClick={handleUnlock}>
                    <Text className='section-lock-text'>解锁后可查看整改建议</Text>
                  </View>
                )}
              </View>
            )}

            {/* 功能操作区：已通过时显示咨询AI监理，未通过/待复检时已放在整改区 */}
            {!showRectifyArea && (
              <View className='action-row'>
                <View className='action-left'>
                  <Text className='action-link' onClick={handleShare}>分享</Text>
                </View>
                <View className='action-right'>
                  <View className='btn-ai btn-ai-yellow' onClick={goAiSupervision}><Text>咨询AI监理</Text></View>
                </View>
              </View>
            )}
          </>
        )}

        {(result || loading || loadFailed) && (
          <View className='bottom-actions'>
            <View className='btn-share-primary' onClick={handleShare}>
              <Text className='btn-share-icon'>📤</Text>
              <View className='btn-share-text-wrap'>
                <Text className='btn-share-text'>分享报告</Text>
                <Text className='btn-share-hint'>+10积分</Text>
              </View>
            </View>
            <View className='btn-back-secondary' onClick={() => safeSwitchTab(TAB_CONSTRUCTION)}>
              <Text>返回</Text>
            </View>
            {/* V2.6.7优化：申诉移至底部操作区，仅在未通过且未申诉时显示 */}
            {showAppealBtn && (
              <View className='btn-appeal-bottom' onClick={openAppealModal}>
                <Text className='btn-appeal-icon'>📝</Text>
                <Text>申诉</Text>
              </View>
            )}
            {appealStatus === 'pending' && (
              <View className='btn-appeal-bottom disabled'>
                <Text>申诉中</Text>
              </View>
            )}
          </View>
        )}
        </View>
      </ScrollView>

      {/* 查看详情弹窗 */}
      {detailModal && (
        <View className='detail-modal-mask' onClick={() => setDetailModal(null)}>
          <View className='detail-modal pop' onClick={(e) => e.stopPropagation()}>
            <Text className='detail-modal-close' onClick={() => setDetailModal(null)}>×</Text>
            <Text className='detail-modal-title'>{detailModal.title}</Text>
            {uploaded[0] && (
              <View className='detail-modal-photo-wrap'>
                <Text className='detail-modal-label'>问题照片</Text>
                <Image src={uploaded[0]} className='detail-modal-photo' mode='aspectFill' />
              </View>
            )}
            <Text className='detail-modal-label'>验收标准</Text>
            <Text className='detail-modal-text'>{detailModal.desc}</Text>
            <Text className='detail-modal-label'>整改建议</Text>
            <Text className='detail-modal-text'>{detailModal.suggest}</Text>
            <View className='detail-modal-btn' onClick={() => setDetailModal(null)}><Text>我已知晓</Text></View>
          </View>
        </View>
      )}

      {/* 申诉弹窗 */}
      {appealModal && (
        <View className='appeal-modal-mask' onClick={() => setAppealModal(false)}>
          <View className='appeal-modal pop' onClick={(e) => e.stopPropagation()}>
            <Text className='appeal-modal-title'>验收结果申诉</Text>
            <Textarea
              className='appeal-input'
              placeholder='请输入异议原因（最多500字）'
              placeholderClass='appeal-placeholder'
              value={appealReason}
              onInput={(e) => setAppealReason(e.detail.value)}
              maxlength={500}
            />
            <Text className='appeal-count'>{appealReason.length}/500</Text>
            <View className='appeal-images-wrap'>
              <Text className='appeal-images-label'>凭证上传（选填，最多3张）</Text>
              <View className='appeal-images-row'>
                {appealImages.map((url, i) => (
                  <View key={i} className='appeal-img-wrap'>
                    <Image src={url} className='appeal-img' mode='aspectFill' />
                    <Text className='appeal-img-del' onClick={() => setAppealImages((p) => p.filter((_, idx) => idx !== i))}>×</Text>
                  </View>
                ))}
                {appealImages.length < 3 && (
                  <View className='appeal-img-add' onClick={addAppealImage}>+</View>
                )}
              </View>
            </View>
            <View className='appeal-modal-actions'>
              <View className='appeal-btn cancel' onClick={() => setAppealModal(false)}><Text>取消</Text></View>
              <View
                className={`appeal-btn submit ${appealReason.trim() ? '' : 'disabled'}`}
                onClick={appealReason.trim() && !appealSubmitting ? submitAppeal : undefined}
              >
                <Text>提交申诉</Text>
              </View>
            </View>
          </View>
        </View>
      )}

      {/* 申请复检弹窗 */}
      {recheckModal && (
        <View className='appeal-modal-mask' onClick={() => !recheckSubmitting && setRecheckModal(false)}>
          <View className='appeal-modal pop' onClick={(e) => e.stopPropagation()}>
            <Text className='appeal-modal-title'>上传整改照片</Text>
            <Text className='recheck-modal-desc'>请上传整改后照片（最多5张），提交后将自动触发AI复检</Text>
            <View className='appeal-images-wrap'>
              <View className='appeal-images-row'>
                {recheckPhotos.map((url, i) => (
                  <View key={i} className='appeal-img-wrap'>
                    <Image src={url} className='appeal-img' mode='aspectFill' />
                    <Text className='appeal-img-del' onClick={() => setRecheckPhotos((p) => p.filter((_, idx) => idx !== i))}>×</Text>
                  </View>
                ))}
                {recheckPhotos.length < 5 && (
                  <View className='appeal-img-add' onClick={addRecheckPhoto}>+</View>
                )}
              </View>
            </View>
            <View className='appeal-modal-actions'>
              <View className='appeal-btn cancel' onClick={() => !recheckSubmitting && setRecheckModal(false)}><Text>取消</Text></View>
              <View
                className={`appeal-btn submit ${recheckPhotos.length > 0 && !recheckSubmitting ? '' : 'disabled'}`}
                onClick={recheckPhotos.length > 0 && !recheckSubmitting ? handleSubmitRecheck : undefined}
              >
                <Text>{recheckSubmitting ? '提交中...' : '提交复检'}</Text>
              </View>
            </View>
          </View>
        </View>
      )}

      {/* 申诉提交成功弹窗 */}
      {appealSuccessModal && (
        <View className='appeal-success-mask' onClick={() => setAppealSuccessModal(false)}>
          <View className='appeal-success pop' onClick={(e) => e.stopPropagation()}>
            <Text className='appeal-success-title'>申诉已提交！</Text>
            <Text className='appeal-success-desc'>人工客服将在1-2个工作日内审核，结果将通过小程序消息通知。</Text>
            <View className='appeal-success-btn' onClick={() => setAppealSuccessModal(false)}><Text>我知道了</Text>            </View>
          </View>
        </View>
      )}

      {/* 标记为已通过弹窗 */}
      {markPassedModal && (
        <View className='appeal-modal-mask' onClick={() => !markPassedSubmitting && setMarkPassedModal(false)}>
          <View className='appeal-modal pop' onClick={(e) => e.stopPropagation()}>
            <Text className='appeal-modal-title'>标记为已通过</Text>
            <Text className='recheck-modal-desc' style='color: #FF9900; margin-bottom: 24rpx;'>
              请确认：我已确认当前阶段施工质量符合要求，愿意承担后续风险。高风险问题必须通过申诉流程。
            </Text>
            <Textarea
              className='appeal-input'
              placeholder='请输入说明文字（至少20字，最多500字）'
              placeholderClass='appeal-placeholder'
              value={markPassedNote}
              onInput={(e) => setMarkPassedNote(e.detail.value)}
              maxlength={500}
            />
            <Text className='appeal-count'>{markPassedNote.length}/500 {markPassedNote.length < 20 && '(至少20字)'}</Text>
            <View className='appeal-images-wrap'>
              <Text className='appeal-images-label'>上传说明照片（至少1张，最多5张）</Text>
              <View className='appeal-images-row'>
                {markPassedPhotos.map((url, i) => (
                  <View key={i} className='appeal-img-wrap'>
                    <Image src={url} className='appeal-img' mode='aspectFill' />
                    <Text className='appeal-img-del' onClick={() => setMarkPassedPhotos((p) => p.filter((_, idx) => idx !== i))}>×</Text>
                  </View>
                ))}
                {markPassedPhotos.length < 5 && (
                  <View className='appeal-img-add' onClick={addMarkPassedPhoto}>+</View>
                )}
              </View>
            </View>
            <View className='appeal-modal-actions'>
              <View className='appeal-btn cancel' onClick={() => !markPassedSubmitting && setMarkPassedModal(false)}><Text>取消</Text></View>
              <View
                className={`appeal-btn submit ${markPassedPhotos.length >= 1 && markPassedNote.trim().length >= 20 && !markPassedSubmitting ? '' : 'disabled'}`}
                onClick={markPassedPhotos.length >= 1 && markPassedNote.trim().length >= 20 && !markPassedSubmitting ? handleSubmitMarkPassed : undefined}
              >
                <Text>{markPassedSubmitting ? '提交中...' : '确认标记'}</Text>
              </View>
            </View>
          </View>
        </View>
      )}
    </View>
  )
}

export default AcceptancePage

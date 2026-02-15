import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { View, Text, ScrollView, Picker } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import dayjs from 'dayjs'
import { safeSwitchTab, TAB_HOME } from '../../utils/navigation'
import AcceptanceGuideModal from '../../components/AcceptanceGuideModal'
import { getWithAuth, postWithAuth, putWithAuth } from '../../services/api'
import { materialChecksApi } from '../../services/api'
import {
  StageStatus,
  STAGE_STATUS_STORAGE_KEY,
  mapBackendStageStatus,
  getBackendStageCode,
  getCompletionPayload,
  persistStageStatusToStorage
} from '../../utils/constructionStage'
import './index.scss'

const STAGES = [
  { key: 'material', name: '材料进场核对', days: 3, label: 'S00', icon: '📦' },
  { key: 'plumbing', name: '隐蔽工程', days: 7, label: 'S01', icon: '🔌' },
  { key: 'carpentry', name: '泥瓦工', days: 10, label: 'S02', icon: '🧱' },
  { key: 'woodwork', name: '木工', days: 7, label: 'S03', icon: '🪚' },
  { key: 'painting', name: '油漆', days: 7, label: 'S04', icon: '🖌️' },
  { key: 'installation', name: '安装收尾', days: 5, label: 'S05', icon: '🔧' }
]

const TOTAL_DAYS = STAGES.reduce((s, x) => s + x.days, 0)
const STORAGE_KEY_DATE = 'construction_start_date'
const STORAGE_KEY_CALIBRATE = 'construction_stage_calibrate'
const REMIND_DAYS_OPTIONS = [1, 2, 3, 5, 7]
const DEVIATION_REASONS = ['材料未到', '施工拖延', '个人原因', '其他']

/** scene 传 P15：施工验收 / 复检（S00 人工核对走 P37） */
const SCENE_ACCEPT = 'accept'
const SCENE_RECHECK = 'recheck'

const buildDefaultStageStatus = (): Record<string, StageStatus> => {
  const defaults: Record<string, StageStatus> = {}
  STAGES.forEach((stage) => {
    defaults[stage.key] = 'pending'
  })
  return defaults
}

const getBackendStatusPayloadFromLocal = (stageKey: string, status: StageStatus): string | null => {
  if (status === 'rectify') return 'need_rectify'
  if (status === 'completed') return getCompletionPayload(stageKey)
  return null
}

/**
 * P09 施工陪伴页 - 6大阶段 + 智能提醒，流程互锁，按原型布局
 */
const Construction: React.FC = () => {
  const [startDate, setStartDate] = useState('')
  const [stageStatus, setStageStatus] = useState<Record<string, StageStatus>>(buildDefaultStageStatus())
  const [guideStage, setGuideStage] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [useApi, setUseApi] = useState(false)
  const [scrollToStageId, setScrollToStageId] = useState<string | null>(null)
  const [highlightStageIndex, setHighlightStageIndex] = useState<number | null>(null)
  const [expandedCard, setExpandedCard] = useState<number | null>(null)
  const [remindModalVisible, setRemindModalVisible] = useState(false)
  const [remindDays, setRemindDays] = useState(3)
  const [remindOpen, setRemindOpen] = useState(true)
  const [deviationReason, setDeviationReason] = useState('')
  const [manualEndDates, setManualEndDates] = useState<Record<string, string>>({})
  const [pendingSyncStages, setPendingSyncStages] = useState<Set<string>>(new Set())
  const [hasMaterialList, setHasMaterialList] = useState<boolean | null>(null)

  const hasToken = !!Taro.getStorageSync('access_token')

  const loadFromApi = useCallback(async () => {
    if (!hasToken) return
    try {
      const res = await getWithAuth('/constructions/schedule') as any
      const data = res?.data ?? res
      const stages = data?.stages ?? {}
      // 后端返回的 key 为 S00/S01/...，需用 getBackendStageCode(s.key) 取对应阶段状态
      const status: Record<string, StageStatus> = buildDefaultStageStatus()
      const calibrate: Record<string, string> = {}
      STAGES.forEach((s) => {
        const backendKey = getBackendStageCode(s.key)
        const backendStatus = stages[backendKey]?.status as string | undefined
        // 调试：记录后端返回的状态值
        if (process.env.NODE_ENV === 'development') {
          console.log(`[施工进度] ${s.key} (${backendKey}): 后端status=${backendStatus}, 映射后=${mapBackendStageStatus(backendStatus, s.key)}`)
        }
        status[s.key] = mapBackendStageStatus(backendStatus, s.key)
        if (stages[backendKey]?.end_date) calibrate[s.key] = dayjs(stages[backendKey].end_date).format('YYYY-MM-DD')
      })
      if (data?.start_date) {
        const formatted = dayjs(data.start_date).format('YYYY-MM-DD')
        setStartDate(formatted)
        saveLocal(formatted, status)
      } else {
        // 未设置开工日期（或后端返回空 schedule）：清空本地缓存，展示「设置开工日期」
        setStartDate('')
        Taro.removeStorageSync(STORAGE_KEY_DATE)
        Taro.setStorageSync(STAGE_STATUS_STORAGE_KEY, JSON.stringify(status))
      }
      setStageStatus(status)
      setPendingSyncStages(new Set())
      if (Object.keys(calibrate).length > 0) setManualEndDates((prev) => ({ ...prev, ...calibrate }))
      setUseApi(true)
      // 预拉材料清单，用于 S00 人工核对入口管控（需先上传报价单）
      materialChecksApi.getMaterialList().then((r: any) => {
        const list = r?.data?.list ?? r?.list ?? []
        setHasMaterialList(Array.isArray(list) && list.length > 0)
      }).catch(() => setHasMaterialList(false))
    } catch (e: any) {
      // V2.6.2优化：静默处理401/404错误（未登录或未设置进度计划）
      const is404 = e?.statusCode === 404 || e?.response?.status === 404 || e?.message?.includes('404')
      const is401 = e?.statusCode === 401 || e?.response?.status === 401 || e?.message?.includes('请稍后重试') || (e as any)?.isSilent
      if (is404 || is401) {
        // 静默处理，不显示错误提示
        const saved = Taro.getStorageSync(STORAGE_KEY_DATE)
        const statusSaved = Taro.getStorageSync(STAGE_STATUS_STORAGE_KEY)
        const calibrateSaved = Taro.getStorageSync(STORAGE_KEY_CALIBRATE)
        if (saved) setStartDate(saved)
        if (statusSaved) {
          try {
            const parsed = typeof statusSaved === 'string' ? JSON.parse(statusSaved) : statusSaved
            setStageStatus({ ...buildDefaultStageStatus(), ...parsed })
          } catch (_) {
            setStageStatus(buildDefaultStageStatus())
          }
        } else {
          setStageStatus(buildDefaultStageStatus())
        }
        if (calibrateSaved) {
          try {
            setManualEndDates(typeof calibrateSaved === 'string' ? JSON.parse(calibrateSaved) : calibrateSaved)
          } catch (_) {}
        }
      }
      setUseApi(false)
    } finally {
      setLoading(false)
    }
  }, [hasToken])

  const loadFromLocal = useCallback(() => {
    const saved = Taro.getStorageSync(STORAGE_KEY_DATE)
    const statusSaved = Taro.getStorageSync(STAGE_STATUS_STORAGE_KEY)
    const calibrateSaved = Taro.getStorageSync(STORAGE_KEY_CALIBRATE)
    if (saved) setStartDate(saved)
    if (statusSaved) {
      try {
        const parsed = typeof statusSaved === 'string' ? JSON.parse(statusSaved) : statusSaved
        setStageStatus({ ...buildDefaultStageStatus(), ...parsed })
      } catch (_) {
        setStageStatus(buildDefaultStageStatus())
      }
    } else {
      setStageStatus(buildDefaultStageStatus())
    }
    if (calibrateSaved) {
      try {
        setManualEndDates(typeof calibrateSaved === 'string' ? JSON.parse(calibrateSaved) : calibrateSaved)
      } catch (_) {}
    }
    const rd = Taro.getStorageSync('remind_days')
    if (typeof rd === 'number' && REMIND_DAYS_OPTIONS.includes(rd)) setRemindDays(rd)
    const ro = Taro.getStorageSync('smart_remind')
    if (typeof ro === 'boolean') setRemindOpen(ro)
    setUseApi(false)
    setLoading(false)
  }, [])

  useEffect(() => {
    if (hasToken) loadFromApi()
    else loadFromLocal()
  }, [hasToken, loadFromApi, loadFromLocal])

  // 从材料核对/验收等子页返回时重新拉取；首页6大阶段点击跳转时处理滚动与高亮
  useDidShow(() => {
    if (hasToken) loadFromApi()
    else loadFromLocal()
    if (startDate) {
      const raw = Taro.getStorageSync('construction_scroll_stage')
      const idx = typeof raw === 'number' ? raw : parseInt(String(raw ?? ''), 10)
      if (idx >= 0 && idx < STAGES.length) {
        Taro.removeStorageSync('construction_scroll_stage')
        setScrollToStageId(`stage-${idx}`)
        setHighlightStageIndex(idx)
        setTimeout(() => {
          setHighlightStageIndex(null)
          setScrollToStageId(null)
        }, 3500)
      }
    }
  })

  const mountedRef = useRef(true)
  useEffect(() => {
    mountedRef.current = true
    return () => { mountedRef.current = false }
  }, [])
  // 首页6大阶段点击跳转：读取 construction_scroll_stage，滚动到对应阶段并高亮
  useEffect(() => {
    if (!startDate) return
    const raw = Taro.getStorageSync('construction_scroll_stage')
    const idx = typeof raw === 'number' ? raw : parseInt(String(raw ?? ''), 10)
    if (idx >= 0 && idx < STAGES.length) {
      Taro.removeStorageSync('construction_scroll_stage')
      setScrollToStageId(`stage-${idx}`)
      setHighlightStageIndex(idx)
      const t = setTimeout(() => {
        if (mountedRef.current) {
          setHighlightStageIndex(null)
          setScrollToStageId(null)
        }
      }, 3500)
      return () => clearTimeout(t)
    }
  }, [startDate])

  useEffect(() => {
    if (!useApi || !hasToken || pendingSyncStages.size === 0) return
    pendingSyncStages.forEach((stageKey) => {
      const payload = getBackendStatusPayloadFromLocal(stageKey, stageStatus[stageKey])
      if (!payload) {
        clearStagePending(stageKey)
        return
      }
      putWithAuth('/constructions/stage-status', { stage: getBackendStageCode(stageKey), status: payload })
        .then(() => {
          persistStageStatusToStorage(stageKey, payload)
          clearStagePending(stageKey)
        })
        .catch(() => {
          // 保持待同步状态，稍后继续重试
        })
    })
  }, [useApi, hasToken, pendingSyncStages, stageStatus, clearStagePending])

  const saveLocal = (date: string, status: Record<string, string>) => {
    Taro.setStorageSync(STORAGE_KEY_DATE, date)
    Taro.setStorageSync(STAGE_STATUS_STORAGE_KEY, JSON.stringify(status))
  }

  const markStagePending = useCallback((stageKey: string) => {
    setPendingSyncStages((prev) => {
      const next = new Set(prev)
      next.add(stageKey)
      return next
    })
  }, [])

  const clearStagePending = useCallback((stageKey: string) => {
    setPendingSyncStages((prev) => {
      if (!prev.has(stageKey)) return prev
      const next = new Set(prev)
      next.delete(stageKey)
      return next
    })
  }, [])

  const { schedule, endDate, progress, completedCount, daysBehind, behindStageKey } = useMemo(() => {
    if (!startDate) return { schedule: [], endDate: '', progress: 0, completedCount: 0, daysBehind: 0, behindStageKey: '' }
    const start = dayjs(startDate)
    let cursor = start
    const schedule: Array<{ key: string; name: string; days: number; start: string; end: string; status: StageStatus; remaining?: number }> = []
    let daysBehind = 0
    let behindStageKey = ''
    for (const s of STAGES) {
      const st = stageStatus[s.key] || 'pending'
      const startStr = cursor.format('YYYY-MM-DD')
      const manualEnd = manualEndDates[s.key]
      const endDate = manualEnd ? dayjs(manualEnd) : cursor.add(s.days, 'day')
      const endStr = endDate.format('YYYY-MM-DD')
      let remaining: number | undefined
      if (st === 'in_progress' || st === 'pending') {
        const today = dayjs()
        if (today.isAfter(endDate)) {
          const behind = today.diff(endDate, 'day')
          if (behind > daysBehind) { daysBehind = behind; behindStageKey = s.key }
        }
        remaining = Math.max(0, endDate.diff(dayjs(), 'day'))
      }
      schedule.push({ key: s.key, name: s.name, days: s.days, start: startStr, end: endStr, status: st, remaining })
      cursor = endDate.add(1, 'day')
    }
    const completedCount = schedule.filter((x) => x.status === 'completed').length
    const progress = Math.round((completedCount / STAGES.length) * 100)
    const lastEnd = schedule.length > 0 ? schedule[schedule.length - 1].end : ''
    return { schedule, endDate: lastEnd, progress, completedCount, daysBehind, behindStageKey }
  }, [startDate, stageStatus, manualEndDates])

  const handleSetDate = async (e: any) => {
    const v = e.detail?.value
    if (!v) return
    const d = dayjs(v)
    if (d.isBefore(dayjs(), 'day')) {
      Taro.showToast({ title: '请选择今日及以后的日期', icon: 'none' })
      return
    }
    const dateStr = d.format('YYYY-MM-DD')
    if (useApi && hasToken) {
      try {
        await postWithAuth('/constructions/start-date', { start_date: dateStr })
        setStartDate(dateStr)
        await loadFromApi()
        Taro.showToast({ title: '进度计划更新成功', icon: 'success' })
      } catch {
        Taro.showToast({ title: '更新失败', icon: 'none' })
      }
    } else {
      setStartDate(dateStr)
      const nextStatus = buildDefaultStageStatus()
      setStageStatus(nextStatus)
      saveLocal(dateStr, nextStatus)
      Taro.showToast({ title: '进度计划更新成功', icon: 'success' })
    }
  }

  const handleMarkRectify = async (key: string) => {
    if (useApi && hasToken) {
      try {
        await constructionApi.updateStageStatus(getBackendStageCode(key), 'need_rectify')
        persistStageStatusToStorage(key, 'need_rectify')
        clearStagePending(key)
      } catch (error: any) {
        const message = error?.response?.data?.detail || '标记失败，请稍后重试'
        Taro.showToast({ title: message, icon: 'none' })
        return
      }
    } else {
      markStagePending(key)
    }
    const next = { ...stageStatus, [key]: 'rectify' as StageStatus }
    setStageStatus(next)
    saveLocal(startDate, next)
    Taro.showToast({ title: '已标记整改', icon: 'success' })
  }

  const handleQuickDate = (days: number) => {
    const d2 = dayjs().add(days, 'day').format('YYYY-MM-DD')
    if (useApi && hasToken) {
      postWithAuth('/constructions/start-date', { start_date: d2 }).then(async () => {
        setStartDate(d2)
        await loadFromApi()
        Taro.showToast({ title: '进度计划更新成功', icon: 'success' })
      }).catch(() => Taro.showToast({ title: '更新失败', icon: 'none' }))
    } else {
      setStartDate(d2)
      const nextStatus = buildDefaultStageStatus()
      setStageStatus(nextStatus)
      saveLocal(d2, nextStatus)
      Taro.showToast({ title: '进度计划更新成功', icon: 'success' })
    }
  }

  const isAIActionLocked = (index: number) => {
    if (index === 0) return false
    const prev = stageStatus[STAGES[index - 1].key]
    return prev !== 'completed' && prev !== 'rectify_done'
  }

  const statusLabel = (s: typeof schedule[0], index: number) => {
    const isS00 = index === 0
    if (s.status === 'completed') return isS00 ? '已核对' : '已通过'
    if (s.status === 'rectify' || s.status === 'rectify_done') return '待整改'
    if (s.status === 'in_progress') return isS00 ? '待人工核对' : '待验收'
    return isS00 ? '待人工核对' : '待验收'
  }

  /** S00 人工核对：跳 P37 材料进场人工核对页；S01-S05 AI验收：跳 P15 拍照页 */
  const goStageCheck = (index: number) => {
    const s = STAGES[index]
    const locked = isAIActionLocked(index)
    if (locked) {
      const msg = index === 1
        ? '请先完成材料进场人工核对'
        : `请先完成${STAGES[index - 1].name}验收`
      Taro.showToast({ title: msg, icon: 'none' })
      return
    }
    const isS00 = index === 0
    if (isS00) {
      if (hasMaterialList === false) {
        Taro.showToast({ title: '请先上传报价单以获取材料清单', icon: 'none', duration: 2500 })
        return
      }
      Taro.navigateTo({ url: `/pages/material-check/index?stage=material&scene=check` })
      Taro.showToast({ title: '请按清单逐项勾选并拍照留证', icon: 'none', duration: 2500 })
    } else {
      Taro.navigateTo({ url: `/pages/photo/index?stage=${s.key}&scene=${SCENE_ACCEPT}` })
      Taro.showToast({ title: '请拍摄/上传施工照片完成验收', icon: 'none', duration: 2500 })
    }
  }

  /** 申请复检：跳 P15 带 scene=recheck，上传整改后照片后走复检流程 */
  const goRecheck = (stageKey: string) => {
    Taro.navigateTo({ url: `/pages/photo/index?stage=${stageKey}&scene=${SCENE_RECHECK}` })
    Taro.showToast({ title: '请上传整改后照片，将自动触发AI复检', icon: 'none', duration: 2500 })
  }

  // V2.6.2优化：特殊申请功能移至设置页，此处删除

  const saveRemindSettings = () => {
    Taro.setStorageSync('remind_days', remindDays)
    Taro.setStorageSync('smart_remind', remindOpen)
    setRemindModalVisible(false)
    Taro.showToast({ title: '提醒设置成功', icon: 'success' })
  }

  const handleCalibrateTime = (stageKey: string, stageStart: string, e: any) => {
    const v = e?.detail?.value
    if (!v) return
    const d = dayjs(v)
    const today = dayjs().startOf('day')
    const startDay = dayjs(stageStart).startOf('day')
    if (d.isBefore(today)) {
      Taro.showToast({ title: '请选择当前日期及以后的时间', icon: 'none', duration: 2500 })
      return
    }
    if (!d.isAfter(startDay)) {
      Taro.showToast({ title: '校准时间须大于预计开始时间', icon: 'none', duration: 2500 })
      return
    }
    const newEnd = d.format('YYYY-MM-DD')
    const next = { ...manualEndDates, [stageKey]: newEnd }
    setManualEndDates(next)
    Taro.setStorageSync(STORAGE_KEY_CALIBRATE, JSON.stringify(next))
    setPendingSyncStages((s) => { const n = new Set(s); n.delete(stageKey); return n })
    const showSuccess = () => Taro.showToast({ title: '时间校准成功，后续进度计划已同步更新', icon: 'none', duration: 3000 })
    const showCached = () => {
      setPendingSyncStages((s) => new Set(s).add(stageKey))
      Taro.showToast({ title: '时间已缓存，联网后自动更新', icon: 'none', duration: 3000 })
    }
    if (useApi && hasToken) {
      constructionApi
        .calibrateStageEnd(stageKey, newEnd)
        .then(showSuccess)
        .catch(showCached)
    } else {
      showSuccess()
    }
  }

  if (loading) {
    return (
      <View className='construction-page'>
        <View className='nav-bar'><Text className='nav-title'>施工陪伴</Text></View>
        <View className='loading-wrap'><Text>加载中…</Text></View>
      </View>
    )
  }

  if (!startDate) {
    return (
      <View className='construction-page'>
        <View className='nav-bar'>
          <Text className='nav-back' onClick={() => safeSwitchTab(TAB_HOME)}>返回</Text>
          <Text className='nav-title'>施工陪伴</Text>
          <View className='nav-placeholder' />
        </View>
        <View className='empty-state'>
          <Text className='empty-icon'>📅</Text>
          <Text className='empty-text'>请先设置开工日期</Text>
          <View className='date-card empty'>
            <Text className='date-label'>设置开工日期</Text>
            <View className='date-actions'>
              <View className='remind-set' onClick={() => setRemindModalVisible(true)}>
                <Text className='remind-icon'>🔔</Text>
                <Text className='remind-text'>提醒设置</Text>
              </View>
              <View className='quick-date-row'>
                {[7, 15, 30].map((d) => (
                  <View key={d} className='quick-btn' onClick={() => handleQuickDate(d)}><Text>{d}天后开工</Text></View>
                ))}
              </View>
              <Picker mode='date' value={dayjs().format('YYYY-MM-DD')} start={dayjs().format('YYYY-MM-DD')} onChange={handleSetDate}>
                <View className='set-date-btn'><Text>选择其他日期</Text></View>
              </Picker>
            </View>
          </View>
        </View>
        {remindModalVisible && (
          <View className='remind-modal-mask' onClick={() => setRemindModalVisible(false)}>
            <View className='remind-modal' onClick={(e) => e.stopPropagation()}>
              <Text className='remind-modal-title'>提醒设置</Text>
              <View className='remind-row'><Text>智能提醒总开关</Text><View className={`switch-wrap ${remindOpen ? 'on' : ''}`} onClick={() => setRemindOpen(!remindOpen)}><Text className='switch-dot' style={{ marginLeft: remindOpen ? '40rpx' : '0' }} /></View></View>
              <View className='remind-row'><Text>提醒提前天数</Text>
                <Picker mode='selector' range={REMIND_DAYS_OPTIONS} value={REMIND_DAYS_OPTIONS.indexOf(remindDays)} onChange={(e) => setRemindDays(REMIND_DAYS_OPTIONS[Number(e.detail.value)] ?? 3)}>
                  <Text className='picker-text'>{remindDays}天</Text>
                </Picker>
              </View>
              <View className='remind-save-btn' onClick={saveRemindSettings}><Text>保存设置</Text></View>
            </View>
          </View>
        )}
      </View>
    )
  }

  return (
    <View className='construction-page'>
      {/* 顶部导航栏（V2.6.2优化：删除特殊申请入口，移至设置页） */}
      <View className='nav-bar'>
        <Text className='nav-back' onClick={() => safeSwitchTab(TAB_HOME)}>返回</Text>
        <Text className='nav-title'>施工陪伴</Text>
        <View className='nav-placeholder' />
      </View>

      <ScrollView scrollY className='scroll-body-outer' scrollIntoView={scrollToStageId || undefined}>
        <View className='scroll-body'>
        {/* 开工日期设置区 */}
        <View className='date-card'>
          <Text className='date-text'>开工日期：{startDate}</Text>
          <View className='date-actions'>
            <Picker mode='date' value={startDate} start={dayjs().format('YYYY-MM-DD')} onChange={handleSetDate}>
              <Text className='date-edit'>编辑</Text>
            </Picker>
            <View className='remind-set' onClick={() => setRemindModalVisible(true)}>
              <Text className='remind-icon'>🔔</Text>
              <Text className='remind-text'>提醒设置</Text>
            </View>
          </View>
        </View>

        {/* 全局进度概览 */}
        <View className='overview-card'>
          <Text className='overview-main'>整体进度：{progress}%</Text>
          {daysBehind > 0 && <Text className='overview-warn'>{STAGES.find((s) => s.key === behindStageKey)?.name || '当前'}阶段落后计划{daysBehind}天</Text>}
          <Text className='overview-remind'>待提醒事项将显示于此</Text>
        </View>

        {/* 6大阶段卡片 */}
        <View className='stages'>
          {schedule.map((s, i) => {
            const locked = isAIActionLocked(i)
            const isS00 = i === 0
            const materialListLocked = isS00 && hasMaterialList === false
            const progressPct = s.status === 'completed' ? 100 : (s.status === 'in_progress' || s.status === 'rectify' || s.status === 'rectify_done') ? 50 : 0
            const today = dayjs()
            const startD = dayjs(s.start).diff(today, 'day')
            const endD = dayjs(s.end).diff(today, 'day')
            const needRemind = s.status !== 'completed' && (startD >= 0 && startD <= remindDays) || (endD >= 0 && endD <= remindDays)
            return (
              <View key={s.key} id={`stage-${i}`} className={`stage-card ${highlightStageIndex === i ? 'stage-card-highlight' : ''}`}>
                {needRemind && <View className='stage-reddot' />}
                <View className='stage-header'>
                  <View className='stage-name-row'>
                    <Text className='stage-icon'>{STAGES[i].icon}</Text>
                    <Text className='stage-name'>{STAGES[i].label} {s.name}</Text>
                    <View className={`status-badge ${s.status}`}><Text>{statusLabel(s, i)}</Text></View>
                  </View>
                  <Text className='stage-plan-time'>{s.start} ~ {s.end}{pendingSyncStages.has(s.key) && <Text className='stage-pending-sync'>（待同步）</Text>}</Text>
                </View>
                <View className='progress-bar-wrap'>
                  <View className={`progress-fill ${s.status}`} style={{ width: `${progressPct}%` }} />
                </View>
                <View className='stage-actions'>
                  <View className='actions-left'>
                    <Text
                      className={`action-item ${(locked || materialListLocked) ? 'disabled' : ''}`}
                      onClick={() => {
                        if (locked) {
                          Taro.showToast({ title: i === 1 ? '请先完成材料进场人工核对' : `请先完成${STAGES[i - 1].name}验收`, icon: 'none' })
                          return
                        }
                        if (materialListLocked) {
                          Taro.showToast({ title: '请先上传报价单以获取材料清单', icon: 'none', duration: 2500 })
                          return
                        }
                        goStageCheck(i)
                      }}
                    >{isS00 ? '📋 人工核对' : '🔍 AI验收'}</Text>
                    <Text
                      className={`action-item ${locked ? 'disabled' : ''}`}
                      onClick={() => {
                        if (locked) {
                          Taro.showToast({ title: i === 1 ? '请先完成材料进场人工核对' : `请先完成${STAGES[i - 1].name}验收`, icon: 'none' })
                          return
                        }
                        setGuideStage(s.key)
                      }}
                    >
                      {isS00 ? '📋 核对指引' : '📋 验收指引'}
                    </Text>
                  </View>
                  <View className='actions-right'>
                    {/* V2.6.2优化：删除状态标签文字，仅保留状态角标 */}
                    {!locked && (s.status === 'in_progress' || s.status === 'pending') ? (
                      <Picker
                        mode='date'
                        value={s.end}
                        start={dayjs().format('YYYY-MM-DD')}
                        onChange={(e) => handleCalibrateTime(s.key, s.start, e)}
                      >
                        <Text className='link-txt'>调整时间</Text>
                      </Picker>
                    ) : null}
                    <View className={`btn-done ${s.status === 'completed' ? 'active' : ''}`}>
                      <Text>{statusLabel(s, i)}</Text>
                    </View>
                  </View>
                </View>
                {/* V2.6.2优化：简化记录板块，删除展开/折叠，仅保留查看台账/报告（已完成阶段） */}
                {s.status === 'completed' && (
                  <View className='record-panel'>
                    <Text className='record-text'>{s.name}记录：已通过</Text>
                    <Text
                      className='link-txt'
                      onClick={() => {
                        if (locked) {
                          Taro.showToast({ title: i === 1 ? '请先完成材料进场人工核对' : `请先完成${STAGES[i - 1].name}验收`, icon: 'none' })
                          return
                        }
                        Taro.navigateTo({ url: isS00 ? '/pages/material-check/index?stage=material' : `/pages/acceptance/index?stage=${s.key}` })
                      }}
                    >
                      查看台账/报告
                    </Text>
                  </View>
                )}
                {s.status !== 'completed' && (
                  <View className='record-panel'>
                    <Text className='record-text'>
                      {s.name}记录：{(s.status === 'rectify' || s.status === 'rectify_done') ? '待整改' : isS00 ? '待人工核对' : '待验收'}
                    </Text>
                  </View>
                )}
              </View>
            )
          })}
        </View>

        {/* V2.6.2优化：删除进度偏差提醒栏（信息已在全局进度概览中显示） */}

        {/* 一键分享进度 */}
        <View className='share-wrap'>
          <View className='btn-share' onClick={() => Taro.navigateTo({ url: '/pages/progress-share/index' })}>
            <Text>一键分享进度</Text>
          </View>
        </View>
        </View>
      </ScrollView>

      {/* 提醒设置弹窗 */}
      {remindModalVisible && (
        <View className='remind-modal-mask' onClick={() => setRemindModalVisible(false)}>
          <View className='remind-modal' onClick={(e) => e.stopPropagation()}>
            <Text className='remind-modal-title'>提醒设置</Text>
            <View className='remind-row'><Text>智能提醒总开关</Text><View className={`switch-wrap ${remindOpen ? 'on' : ''}`} onClick={() => setRemindOpen(!remindOpen)}><Text className='switch-dot' style={{ marginLeft: remindOpen ? '40rpx' : '0' }} /></View></View>
            <View className='remind-row'><Text>提醒提前天数</Text>
              <Picker mode='selector' range={REMIND_DAYS_OPTIONS} value={REMIND_DAYS_OPTIONS.indexOf(remindDays)} onChange={(e) => setRemindDays(REMIND_DAYS_OPTIONS[Number(e.detail.value)] ?? 3)}>
                <Text className='picker-text'>{remindDays}天</Text>
              </Picker>
            </View>
            <View className='remind-save-btn' onClick={saveRemindSettings}><Text>保存设置</Text></View>
          </View>
        </View>
      )}

      <AcceptanceGuideModal stageKey={guideStage || 'material'} visible={!!guideStage} onClose={() => setGuideStage(null)} />
    </View>
  )
}

export default Construction

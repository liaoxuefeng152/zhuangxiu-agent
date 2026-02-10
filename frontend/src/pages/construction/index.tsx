import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { View, Text, ScrollView, Picker } from '@tarojs/components'
import Taro from '@tarojs/taro'
import dayjs from 'dayjs'
import { safeSwitchTab, TAB_HOME } from '../../utils/navigation'
import AcceptanceGuideModal from '../../components/AcceptanceGuideModal'
import { constructionApi } from '../../services/api'
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
const STORAGE_KEY_STATUS = 'construction_stage_status'
const STORAGE_KEY_CALIBRATE = 'construction_stage_calibrate'
const REMIND_DAYS_OPTIONS = [1, 2, 3, 5, 7]
const DEVIATION_REASONS = ['材料未到', '施工拖延', '个人原因', '其他']

/** scene 传 P15：施工验收 / 复检（S00 人工核对走 P37） */
const SCENE_ACCEPT = 'accept'
const SCENE_RECHECK = 'recheck'

/**
 * P09 施工陪伴页 - 6大阶段 + 智能提醒，流程互锁，按原型布局
 */
const Construction: React.FC = () => {
  const [startDate, setStartDate] = useState('')
  type StageStatus = 'pending' | 'in_progress' | 'completed' | 'rectify'
const [stageStatus, setStageStatus] = useState<Record<string, StageStatus>>({})
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

  const hasToken = !!Taro.getStorageSync('access_token')

  const loadFromApi = useCallback(async () => {
    if (!hasToken) return
    try {
      const res = await constructionApi.getSchedule() as any
      const data = res?.data ?? res
      if (data?.start_date) setStartDate(dayjs(data.start_date).format('YYYY-MM-DD'))
      const stages = data?.stages ?? {}
      const status: Record<string, StageStatus> = {}
      const calibrate: Record<string, string> = {}
      STAGES.forEach((s) => {
        status[s.key] = (stages[s.key]?.status as StageStatus) || 'pending'
        if (stages[s.key]?.end_date) calibrate[s.key] = dayjs(stages[s.key].end_date).format('YYYY-MM-DD')
      })
      setStageStatus(status)
      if (Object.keys(calibrate).length > 0) setManualEndDates((prev) => ({ ...prev, ...calibrate }))
      setUseApi(true)
    } catch (e: any) {
      if (e?.response?.status === 404 || e?.message?.includes('404')) {
        const saved = Taro.getStorageSync(STORAGE_KEY_DATE)
        const statusSaved = Taro.getStorageSync(STORAGE_KEY_STATUS)
        const calibrateSaved = Taro.getStorageSync(STORAGE_KEY_CALIBRATE)
        if (saved) setStartDate(saved)
        if (statusSaved) setStageStatus(JSON.parse(statusSaved))
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
    const statusSaved = Taro.getStorageSync(STORAGE_KEY_STATUS)
    const calibrateSaved = Taro.getStorageSync(STORAGE_KEY_CALIBRATE)
    if (saved) setStartDate(saved)
    if (statusSaved) setStageStatus(JSON.parse(statusSaved))
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

  useEffect(() => {
    const idx = Taro.getStorageSync('construction_scroll_stage')
    if (typeof idx === 'number' && idx >= 0 && idx < STAGES.length) {
      setScrollToStageId(`stage-${idx}`)
      setHighlightStageIndex(idx)
      Taro.removeStorageSync('construction_scroll_stage')
      const t = setTimeout(() => setHighlightStageIndex(null), 3500)
      return () => clearTimeout(t)
    }
  }, [startDate])

  const saveLocal = (date: string, status: Record<string, string>) => {
    Taro.setStorageSync(STORAGE_KEY_DATE, date)
    Taro.setStorageSync(STORAGE_KEY_STATUS, JSON.stringify(status))
  }

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
    const nextStatus = { ...stageStatus }
    if ((nextStatus.material || 'pending') === 'pending') {
      nextStatus.material = 'in_progress'
    }
    if (useApi && hasToken) {
      try {
        await constructionApi.setStartDate(dateStr)
        setStartDate(dateStr)
        setStageStatus(nextStatus)
        saveLocal(dateStr, nextStatus)
        Taro.showToast({ title: '进度计划更新成功', icon: 'success' })
      } catch {
        Taro.showToast({ title: '更新失败', icon: 'none' })
      }
    } else {
      setStartDate(dateStr)
      setStageStatus(nextStatus)
      saveLocal(dateStr, nextStatus)
      Taro.showToast({ title: '进度计划更新成功', icon: 'success' })
    }
  }

  const handleMarkRectify = (key: string) => {
    const next = { ...stageStatus, [key]: 'rectify' as StageStatus }
    setStageStatus(next)
    saveLocal(startDate, next)
    if (useApi && hasToken) {
      constructionApi.updateStageStatus(key, 'rectify').catch(() => {})
    }
    Taro.showToast({ title: '已标记整改', icon: 'success' })
  }

  const handleQuickDate = (days: number) => {
    const d2 = dayjs().add(days, 'day').format('YYYY-MM-DD')
    const nextStatus = { ...stageStatus }
    if ((nextStatus.material || 'pending') === 'pending') nextStatus.material = 'in_progress'
    if (useApi && hasToken) {
      constructionApi.setStartDate(d2).then(() => {
        setStartDate(d2)
        setStageStatus(nextStatus)
        saveLocal(d2, nextStatus)
        Taro.showToast({ title: '进度计划更新成功', icon: 'success' })
      }).catch(() => Taro.showToast({ title: '更新失败', icon: 'none' }))
    } else {
      setStartDate(d2)
      setStageStatus(nextStatus)
      saveLocal(d2, nextStatus)
      Taro.showToast({ title: '进度计划更新成功', icon: 'success' })
    }
  }

  const isAIActionLocked = (index: number) => {
    if (index === 0) return false
    return stageStatus[STAGES[index - 1].key] !== 'completed'
  }

  const statusLabel = (s: typeof schedule[0], index: number) => {
    const isS00 = index === 0
    if (s.status === 'completed') return isS00 ? '已核对' : '已通过'
    if (s.status === 'rectify') return '待整改'
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
      Taro.navigateTo({ url: `/pages/material-check/index?stage=material&scene=check` })
      Taro.showToast({ title: '请按清单拍摄/上传材料照片完成人工核对', icon: 'none', duration: 2500 })
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

  const handleSpecialApply = () => {
    Taro.showActionSheet({
      itemList: ['自主装修豁免', '核对/验收争议申诉'],
      success: (res) => {
        if (res.tapIndex === 0) Taro.showToast({ title: '请到「我的-设置」提交申请', icon: 'none' })
        else Taro.navigateTo({ url: '/pages/feedback/index' })
      },
      fail: () => {}
    })
  }

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
      {/* 顶部导航栏 */}
      <View className='nav-bar'>
        <Text className='nav-back' onClick={() => safeSwitchTab(TAB_HOME)}>返回</Text>
        <Text className='nav-title'>施工陪伴</Text>
        <Text className='nav-special' onClick={handleSpecialApply}>特殊申请</Text>
      </View>

      <ScrollView scrollY className='scroll-body' scrollIntoView={scrollToStageId || undefined}>
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
            const expanded = expandedCard === i
            const progressPct = s.status === 'completed' ? 100 : (s.status === 'in_progress' || s.status === 'rectify') ? 50 : 0
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
                  <Text className='stage-plan-time'>{s.start} ~ {s.end}</Text>
                </View>
                <Text className='stage-expected'>
                  预计开始：{s.start} | 预计验收：{s.end}
                  {pendingSyncStages.has(s.key) && <Text className='stage-pending-sync'>（待同步）</Text>}
                </Text>
                <View className='progress-bar-wrap'>
                  <View className={`progress-fill ${s.status}`} style={{ width: `${progressPct}%` }} />
                </View>
                <View className='stage-actions'>
                  <View className='actions-left'>
                    <Text className={`action-item ${locked ? 'disabled' : ''}`} onClick={() => locked ? undefined : goStageCheck(i)}>{isS00 ? '📋 人工核对' : '🔍 AI验收'}</Text>
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
                    <Text className='status-label-txt'>{statusLabel(s, i)}</Text>
                    {!locked && (s.status === 'in_progress' || s.status === 'pending') ? (
                      <Picker
                        mode='date'
                        value={s.end}
                        start={dayjs().format('YYYY-MM-DD')}
                        onChange={(e) => handleCalibrateTime(s.key, s.start, e)}
                      >
                        <Text className='link-txt'>校准时间</Text>
                      </Picker>
                    ) : (
                      <Text className='link-txt link-txt-disabled'>校准时间</Text>
                    )}
                    <View className={`btn-done ${s.status === 'completed' ? 'active' : ''}`}><Text>已完成</Text></View>
                  </View>
                </View>
                <View className='record-panel'>
                  <Text className='record-text' onClick={() => setExpandedCard(expanded ? null : i)}>{s.name}记录：{s.status === 'completed' ? '已通过' : s.status === 'rectify' ? '待整改' : isS00 ? '待人工核对/问题待整改' : '待核对/问题待整改'}</Text>
                  <Text
                    className={`link-txt ${locked || s.status !== 'completed' ? 'disabled' : ''}`}
                    onClick={(e) => {
                      e.stopPropagation()
                      if (locked) {
                        Taro.showToast({ title: i === 1 ? '请先完成材料进场人工核对' : `请先完成${STAGES[i - 1].name}验收`, icon: 'none' })
                        return
                      }
                      if (s.status !== 'completed') {
                        Taro.showToast({ title: isS00 ? '请先完成材料进场人工核对' : '请先完成本阶段AI验收', icon: 'none' })
                        return
                      }
                      Taro.navigateTo({ url: isS00 ? '/pages/material-check/index?stage=material' : `/pages/acceptance/index?stage=${s.key}` })
                    }}
                  >
                    查看台账/报告
                  </Text>
                  <Text className='record-arrow' onClick={() => setExpandedCard(expanded ? null : i)}>{expanded ? '▼' : '▶'}</Text>
                </View>
                {expanded && (
                  <View className='record-expanded'>
                    <View
                      className={`record-btn ${locked || s.status !== 'completed' ? 'record-btn-muted' : ''}`}
                      onClick={() => {
                        if (locked) {
                          Taro.showToast({ title: i === 1 ? '请先完成材料进场人工核对' : `请先完成${STAGES[i - 1].name}验收`, icon: 'none' })
                          return
                        }
                        if (s.status !== 'completed') {
                          Taro.showToast({ title: isS00 ? '请先完成材料进场人工核对' : '请先完成本阶段AI验收', icon: 'none' })
                          return
                        }
                        Taro.navigateTo({ url: isS00 ? '/pages/material-check/index?stage=material' : `/pages/acceptance/index?stage=${s.key}` })
                      }}
                    >
                      <Text>查看详情</Text>
                    </View>
                    <View
                      className={`record-btn ${locked ? 'record-btn-muted' : ''}`}
                      onClick={() => {
                        if (locked) {
                          Taro.showToast({ title: i === 1 ? '请先完成材料进场人工核对' : `请先完成${STAGES[i - 1].name}验收`, icon: 'none' })
                          return
                        }
                        handleMarkRectify(s.key)
                      }}
                    >
                      <Text>标记整改</Text>
                    </View>
                    {isS00 ? (
                      <View className='record-btn record-btn-muted' onClick={() => Taro.showToast({ title: '材料进场需重新进行人工核对', icon: 'none' })}><Text>申请复检</Text></View>
                    ) : (
                      <View
                        className={`record-btn ${locked ? 'record-btn-muted' : ''}`}
                        onClick={() => {
                          if (locked) {
                            Taro.showToast({ title: `请先完成${STAGES[i - 1].name}验收`, icon: 'none' })
                            return
                          }
                          goRecheck(s.key)
                        }}
                      >
                        <Text>申请复检</Text>
                      </View>
                    )}
                  </View>
                )}
              </View>
            )
          })}
        </View>

        {/* 进度偏差提醒栏 */}
        {daysBehind > 0 && (
          <View className='deviation-bar'>
            <Text className='deviation-text'>{STAGES.find((s) => s.key === behindStageKey)?.name}阶段落后计划{daysBehind}天</Text>
            <Picker mode='selector' range={DEVIATION_REASONS} onChange={(e) => setDeviationReason(DEVIATION_REASONS[Number(e.detail.value)])}>
              <Text className='deviation-picker'>{deviationReason || '记录原因'}</Text>
            </Picker>
          </View>
        )}

        {/* 一键分享进度 */}
        <View className='share-wrap'>
          <View className='btn-share' onClick={() => Taro.navigateTo({ url: '/pages/progress-share/index' })}>
            <Text>一键分享进度</Text>
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

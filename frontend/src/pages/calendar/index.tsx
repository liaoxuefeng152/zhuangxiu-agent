import React, { useState, useMemo, useEffect, useCallback } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import dayjs from 'dayjs'
import { safeSwitchTab, TAB_CONSTRUCTION } from '../../utils/navigation'
import { getWithAuth } from '../../services/api'
import { getBackendStageCode } from '../../utils/constructionStage'
import { mapBackendStageStatus } from '../../utils/constructionStage'
import type { StageStatus } from '../../utils/constructionStage'
import './index.scss'

const WEEK_DAYS = ['日', '一', '二', '三', '四', '五', '六']

const STAGES = [
  { key: 'material', name: '材料进场核对', days: 3, label: 'S00', icon: '📦' },
  { key: 'plumbing', name: '隐蔽工程', days: 7, label: 'S01', icon: '🔌' },
  { key: 'carpentry', name: '泥瓦工', days: 10, label: 'S02', icon: '🧱' },
  { key: 'woodwork', name: '木工', days: 7, label: 'S03', icon: '🪚' },
  { key: 'painting', name: '油漆', days: 7, label: 'S04', icon: '🖌️' },
  { key: 'installation', name: '安装收尾', days: 5, label: 'S05', icon: '🔧' }
]

const STORAGE_KEY_DATE = 'construction_start_date'
const STORAGE_KEY_STATUS = 'construction_stage_status'
const STORAGE_KEY_CALIBRATE = 'construction_stage_calibrate'
const CALENDAR_GO_TO_STAGE = 'calendar_go_to_stage_index'

type CalendarEvent = {
  type: 'start' | 'plan_start' | 'plan_end' | 'actual' | 'overdue'
  label: string
  stageKey?: string
  stageIndex?: number
}

/**
 * P29 装修日历页 - 6大阶段计划/实际/提醒节点完整实现
 */
const CalendarPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<'month' | 'week'>('month')
  const [year, setYear] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [weekStart, setWeekStart] = useState(() => {
    const d = new Date()
    const day = d.getDay()
    const diff = d.getDate() - day
    return new Date(d.setDate(diff))
  })
  const [selectedDate, setSelectedDate] = useState<{ d: number; m: number; y: number } | null>(null)
  const [popover, setPopover] = useState<{ day: number; month: number; year: number; events: CalendarEvent[] } | null>(null)
  const [startDate, setStartDate] = useState('')
  const [schedule, setSchedule] = useState<Array<{ key: string; name: string; start: string; end: string; status: StageStatus }>>([])

  const loadSchedule = useCallback(async () => {
    const saved = Taro.getStorageSync(STORAGE_KEY_DATE)
    if (saved) {
      setStartDate(saved)
      try {
        const res = await getWithAuth('/constructions/schedule') as any
        const data = res?.data ?? res
        const stages = data?.stages ?? {}
        const calibrate: Record<string, string> = {}
        STAGES.forEach((s) => {
          const b = stages[getBackendStageCode(s.key)]
          if (b?.end_date) calibrate[s.key] = dayjs(b.end_date).format('YYYY-MM-DD')
        })
        const manualEnd = Taro.getStorageSync(STORAGE_KEY_CALIBRATE)
        const manual = manualEnd ? (typeof manualEnd === 'string' ? JSON.parse(manualEnd) : manualEnd) : {}
        const cal = { ...manual, ...calibrate }
        let cursor = dayjs(saved)
        const list: Array<{ key: string; name: string; start: string; end: string; status: StageStatus }> = []
        const statusRaw = Taro.getStorageSync(STORAGE_KEY_STATUS)
        const statusMap: Record<string, StageStatus> = statusRaw ? (typeof statusRaw === 'string' ? JSON.parse(statusRaw) : statusRaw) : {}
        STAGES.forEach((s) => {
          const st = statusMap[s.key] ?? mapBackendStageStatus(stages[getBackendStageCode(s.key)]?.status, s.key)
          const startStr = cursor.format('YYYY-MM-DD')
          const endDate = cal[s.key] ? dayjs(cal[s.key]) : cursor.add(s.days - 1, 'day')
          const endStr = endDate.format('YYYY-MM-DD')
          list.push({ key: s.key, name: s.name, start: startStr, end: endStr, status: st })
          cursor = endDate.add(1, 'day')
        })
        setSchedule(list)
      } catch (_) {
        buildScheduleFromLocal(saved)
      }
    } else {
      setStartDate('')
      setSchedule([])
    }
  }, [])

  const buildScheduleFromLocal = (saved: string) => {
    const statusRaw = Taro.getStorageSync(STORAGE_KEY_STATUS)
    const statusMap: Record<string, StageStatus> = statusRaw ? (typeof statusRaw === 'string' ? JSON.parse(statusRaw) : statusRaw) : {}
    const calRaw = Taro.getStorageSync(STORAGE_KEY_CALIBRATE)
    const cal = calRaw ? (typeof calRaw === 'string' ? JSON.parse(calRaw) : calRaw) : {}
    let cursor = dayjs(saved)
    const list: Array<{ key: string; name: string; start: string; end: string; status: StageStatus }> = []
    STAGES.forEach((s) => {
      const st = statusMap[s.key] ?? (s.key === 'material' ? 'in_progress' : 'pending')
      const startStr = cursor.format('YYYY-MM-DD')
      const endDate = cal[s.key] ? dayjs(cal[s.key]) : cursor.add(s.days - 1, 'day')
      const endStr = endDate.format('YYYY-MM-DD')
      list.push({ key: s.key, name: s.name, start: startStr, end: endStr, status: st })
      cursor = endDate.add(1, 'day')
    })
    setSchedule(list)
  }

  useEffect(() => {
    loadSchedule()
  }, [loadSchedule])

  useDidShow(() => {
    const saved = Taro.getStorageSync(STORAGE_KEY_DATE)
    if (saved) {
      if (!schedule.length) loadSchedule()
      else buildScheduleFromLocal(saved)
    }
  })

  const eventsMap = useMemo(() => {
    const map: Record<string, CalendarEvent[]> = {}
    if (!startDate || !schedule.length) return map
    const [sy, sm, sd] = startDate.split('-').map(Number)
    const key0 = `${sy}-${sm}-${sd}`
    if (!map[key0]) map[key0] = []
    map[key0].push({ type: 'start', label: '开工日期' })
    const today = dayjs()
    schedule.forEach((s, idx) => {
      const [ey, em, ed] = s.start.split('-').map(Number)
      const [endy, endm, endd] = s.end.split('-').map(Number)
      const startKey = `${ey}-${em}-${ed}`
      const endKey = `${endy}-${endm}-${endd}`
      if (!map[startKey]) map[startKey] = []
      if (startKey !== key0) map[startKey].push({ type: 'plan_start', label: `${s.name}计划开始`, stageKey: s.key, stageIndex: idx })
      if (!map[endKey]) map[endKey] = []
      map[endKey].push(
        s.status === 'completed'
          ? { type: 'actual', label: `${s.name}已验收`, stageKey: s.key, stageIndex: idx }
          : today.isAfter(dayjs(s.end)) && s.status !== 'completed'
            ? { type: 'overdue', label: `${s.name}延期`, stageKey: s.key, stageIndex: idx }
            : { type: 'plan_end', label: `${s.name}计划验收`, stageKey: s.key, stageIndex: idx }
      )
    })
    return map
  }, [startDate, schedule])

  const getMarkerClass = (events: CalendarEvent[]) => {
    if (!events?.length) return ''
    if (events.some((e) => e.type === 'overdue')) return 'marker-overdue'
    if (events.some((e) => e.type === 'actual')) return 'marker-actual'
    if (events.some((e) => e.type === 'start')) return 'marker-start'
    return 'marker-plan'
  }

  const daysInMonth = useMemo(() => {
    const first = new Date(year, month - 1, 1)
    const last = new Date(year, month, 0)
    const firstDay = first.getDay()
    const total = last.getDate()
    const prevMonth = month === 1 ? 12 : month - 1
    const prevYear = month === 1 ? year - 1 : year
    const prevTotal = new Date(prevYear, prevMonth, 0).getDate()
    const cells: { day: number; month: number; year: number; isCurrent: boolean }[] = []
    for (let i = 0; i < firstDay; i++) {
      cells.push({ day: prevTotal - firstDay + i + 1, month: prevMonth, year: prevYear, isCurrent: false })
    }
    for (let d = 1; d <= total; d++) {
      cells.push({ day: d, month, year, isCurrent: true })
    }
    const rest = 42 - cells.length
    for (let i = 0; i < rest; i++) {
      const nextMonth = month === 12 ? 1 : month + 1
      const nextYear = month === 12 ? year + 1 : year
      cells.push({ day: i + 1, month: nextMonth, year: nextYear, isCurrent: false })
    }
    return cells
  }, [year, month])

  const daysInWeek = useMemo(() => {
    const start = dayjs(weekStart)
    return Array.from({ length: 7 }, (_, i) => {
      const d = start.add(i, 'day')
      return { day: d.date(), month: d.month() + 1, year: d.year(), isCurrent: true }
    })
  }, [weekStart])

  const displayCells = viewMode === 'month' ? daysInMonth : daysInWeek

  const handlePrev = () => {
    if (viewMode === 'month') {
      if (month === 1) {
        setYear((y) => y - 1)
        setMonth(12)
      } else setMonth((m) => m - 1)
    } else {
      setWeekStart((d) => new Date(dayjs(d).subtract(7, 'day').valueOf()))
    }
  }

  const handleNext = () => {
    if (viewMode === 'month') {
      if (month === 12) {
        setYear((y) => y + 1)
        setMonth(1)
      } else setMonth((m) => m + 1)
    } else {
      setWeekStart((d) => new Date(dayjs(d).add(7, 'day').valueOf()))
    }
  }

  const getEventKey = (y: number, m: number, d: number) => `${y}-${m}-${d}`

  const handleDayTap = (cell: { day: number; month: number; year: number }) => {
    setSelectedDate({ d: cell.day, m: cell.month, y: cell.year })
    const key = getEventKey(cell.year, cell.month, cell.day)
    const events = eventsMap[key] || []
    setPopover(events.length ? { day: cell.day, month: cell.month, year: cell.year, events } : null)
  }

  const goToConstruction = (stageIndex?: number) => {
    setPopover(null)
    if (typeof stageIndex === 'number') {
      Taro.setStorageSync(CALENDAR_GO_TO_STAGE, stageIndex)
    }
    safeSwitchTab(TAB_CONSTRUCTION)
  }

  const monthTitle = viewMode === 'month' ? `${year}年${month}月` : `${dayjs(weekStart).format('YYYY年M月')} 第${Math.ceil(dayjs(weekStart).date() / 7)}周`

  return (
    <ScrollView scrollY className='calendar-page-outer'>
      <View className='calendar-page'>
        <View className='nav-row'>
          <Text className='nav-title'>装修日历</Text>
          <View className='view-toggle'>
            <Text className={viewMode === 'month' ? 'active' : ''} onClick={() => setViewMode('month')}>月视图</Text>
            <Text className='divider'>/</Text>
            <Text className={viewMode === 'week' ? 'active' : ''} onClick={() => setViewMode('week')}>周视图</Text>
          </View>
        </View>

        <View className='month-bar'>
          <Text className='arrow' onClick={handlePrev}>‹</Text>
          <Text className='month-title'>{monthTitle}</Text>
          <Text className='arrow' onClick={handleNext}>›</Text>
        </View>

        <View className='week-row'>
          {WEEK_DAYS.map((w) => (
            <Text key={w} className='week-cell'>{w}</Text>
          ))}
        </View>

        <View className={`days-grid ${viewMode === 'week' ? 'week-mode' : ''}`}>
          {displayCells.map((cell, idx) => {
            const key = getEventKey(cell.year, cell.month, cell.day)
            const events = eventsMap[key] || []
            const hasEvent = events.length > 0
            const markerClass = getMarkerClass(events)
            const isSelected =
              selectedDate && selectedDate.d === cell.day && selectedDate.m === cell.month && selectedDate.y === cell.year
            return (
              <View
                key={idx}
                className={`day-cell ${!cell.isCurrent ? 'other' : ''} ${hasEvent ? 'has-dot ' + markerClass : ''} ${isSelected ? 'selected' : ''}`}
                onClick={() => handleDayTap(cell)}
              >
                <Text className='day-num'>{cell.day}</Text>
                {hasEvent && <View className='dot' />}
              </View>
            )
          })}
        </View>

        {startDate && (
          <View className='legend'>
            <View className='legend-item'><View className='dot marker-start' /><Text>开工</Text></View>
            <View className='legend-item'><View className='dot marker-plan' /><Text>计划</Text></View>
            <View className='legend-item'><View className='dot marker-actual' /><Text>已验收</Text></View>
            <View className='legend-item'><View className='dot marker-overdue' /><Text>延期</Text></View>
          </View>
        )}

        {popover && (
          <View className='popover-mask' onClick={() => setPopover(null)}>
            <View className='popover' onClick={(e) => e.stopPropagation()}>
              <Text className='popover-title'>{popover.year}-{popover.month}-{popover.day}</Text>
              <View className='popover-events'>
                {popover.events.map((ev, i) => (
                  <Text key={i} className='event-item'>{ev.label}</Text>
                ))}
              </View>
              <View
                className='popover-btn'
                onClick={() => goToConstruction(popover.events[0]?.stageIndex)}
              >
                <Text>前往阶段</Text>
              </View>
            </View>
          </View>
        )}

        {!startDate && (
          <View className='empty-tip'>
            <Text>设置开工日期后，将在此展示6大阶段计划与验收节点</Text>
            <Text className='link' onClick={() => safeSwitchTab(TAB_CONSTRUCTION)}>去设置</Text>
          </View>
        )}
      </View>
    </ScrollView>
  )
}

export default CalendarPage

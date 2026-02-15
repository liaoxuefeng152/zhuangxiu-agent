import React, { useState, useMemo } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { safeSwitchTab, TAB_CONSTRUCTION } from '../../utils/navigation'
import './index.scss'

const WEEK_DAYS = ['日', '一', '二', '三', '四', '五', '六']

/**
 * P29 装修日历页 - 6大阶段计划/实际/提醒节点
 */
const CalendarPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<'month' | 'week'>('month')
  const [year, setYear] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [selectedDate, setSelectedDate] = useState<{ d: number; m: number; y: number } | null>(null)
  const [popover, setPopover] = useState<{ day: number; month: number; year: number; events: string[] } | null>(null)

  // 模拟节点：开工日、阶段计划开始/验收（按 PRD 周期可后端计算）
  const startDate = Taro.getStorageSync('construction_start_date') || ''
  const eventsMap = useMemo(() => {
    const map: Record<string, string[]> = {}
    if (startDate) {
      const [y, m, d] = startDate.split('-').map(Number)
      const key = `${y}-${m}-${d}`
      map[key] = ['开工日期']
    }
    // 可在此根据开工日期 + 6大阶段周期计算各阶段计划开始/验收日
    return map
  }, [startDate])

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

  const handlePrev = () => {
    if (month === 1) {
      setYear((y) => y - 1)
      setMonth(12)
    } else setMonth((m) => m - 1)
  }

  const handleNext = () => {
    if (month === 12) {
      setYear((y) => y + 1)
      setMonth(1)
    } else setMonth((m) => m + 1)
  }

  const getEventKey = (y: number, m: number, d: number) => `${y}-${m}-${d}`

  const handleDayTap = (cell: { day: number; month: number; year: number; isCurrent: boolean }) => {
    setSelectedDate({ d: cell.day, m: cell.month, y: cell.year })
    const key = getEventKey(cell.year, cell.month, cell.day)
    const events = eventsMap[key] || []
    setPopover(events.length ? { day: cell.day, month: cell.month, year: cell.year, events } : null)
  }

  const goToConstruction = () => {
    setPopover(null)
    safeSwitchTab(TAB_CONSTRUCTION)
  }

  return (
    <ScrollView scrollY className='calendar-page-outer'>
      <View className='calendar-page'>
      <View className='nav-row'>
        <Text className='nav-title'>装修日历</Text>
        <View className='view-toggle'>
          <Text
            className={viewMode === 'month' ? 'active' : ''}
            onClick={() => setViewMode('month')}
          >
            月视图
          </Text>
          <Text className='divider'>/</Text>
          <Text
            className={viewMode === 'week' ? 'active' : ''}
            onClick={() => setViewMode('week')}
          >
            周视图
          </Text>
        </View>
      </View>

      <View className='month-bar'>
        <Text className='arrow' onClick={handlePrev}>‹</Text>
        <Text className='month-title'>{year}年{month}月</Text>
        <Text className='arrow' onClick={handleNext}>›</Text>
      </View>

      <View className='week-row'>
        {WEEK_DAYS.map((w) => (
          <Text key={w} className='week-cell'>{w}</Text>
        ))}
      </View>

      <View className='days-grid'>
        {daysInMonth.map((cell, idx) => {
          const key = getEventKey(cell.year, cell.month, cell.day)
          const hasEvent = !!eventsMap[key]?.length
          const isSelected =
            selectedDate &&
            selectedDate.d === cell.day &&
            selectedDate.m === cell.month &&
            selectedDate.y === cell.year
          return (
            <View
              key={idx}
              className={`day-cell ${!cell.isCurrent ? 'other' : ''} ${hasEvent ? 'has-dot' : ''} ${isSelected ? 'selected' : ''}`}
              onClick={() => handleDayTap(cell)}
            >
              <Text className='day-num'>{cell.day}</Text>
              {hasEvent && <View className='dot' />}
            </View>
          )
        })}
      </View>

      {popover && (
        <View className='popover-mask' onClick={() => setPopover(null)}>
          <View className='popover' onClick={(e) => e.stopPropagation()}>
            <Text className='popover-title'>{popover.year}-{popover.month}-{popover.day}</Text>
            <View className='popover-events'>
              {popover.events.map((ev, i) => (
                <Text key={i} className='event-item'>{ev}</Text>
              ))}
            </View>
            <View className='popover-btn' onClick={goToConstruction}>
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

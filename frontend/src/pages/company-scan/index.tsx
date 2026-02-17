import React, { useState, useEffect } from 'react'
import { View, Text, Input, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getWithAuth, postWithAuth, companyApi } from '../../services/api'
import './index.scss'

const HISTORY_KEY = 'company_scan_history'
const MAX_HISTORY = 10

/**
 * P03 公司名称输入页 - 装修公司风险检测（原型：历史记录、≥3字、已输入X/50字、手动提交二次确认）
 */
const CompanyScanPage: React.FC = () => {
  const [value, setValue] = useState('')
  const [focus, setFocus] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [historyOpen, setHistoryOpen] = useState(false)
  const [historyList, setHistoryList] = useState<Array<{ name: string; time?: string }>>([])

  useEffect(() => {
    const v = value.replace(/\s+/g, '').replace(/[^\u4e00-\u9fa5a-zA-Z]/g, '')
    if (v.length < 3) {
      setSuggestions([])
      return
    }
    companyApi.search(v, 5).then((res: any) => {
      const list = res?.list ?? []
      setSuggestions(list.map((x: any) => x.name || x).filter(Boolean))
    }).catch(() => setSuggestions([]))
  }, [value])

  useEffect(() => {
    try {
      const raw = Taro.getStorageSync(HISTORY_KEY)
      const arr = raw ? (Array.isArray(raw) ? raw : JSON.parse(raw)) : []
      setHistoryList(arr.slice(0, MAX_HISTORY))
    } catch {
      setHistoryList([])
    }
  }, [historyOpen])

  const normalizedValue = value.replace(/\s+/g, '').slice(0, 50)
  const canSubmit = normalizedValue.length >= 3
  const charCount = normalizedValue.length

  const handleInput = (e: any) => setValue((e.detail?.value || '').replace(/\s+/g, ' ').trim())
  const handleClear = () => setValue('')
  const handleSelectSuggestion = (name: string) => {
    setValue(name)
    setFocus(false)
  }

  const pushHistory = (name: string) => {
    try {
      const raw = Taro.getStorageSync(HISTORY_KEY)
      const arr = raw ? (Array.isArray(raw) ? raw : JSON.parse(raw)) : []
      const next = [{ name, time: new Date().toISOString() }, ...arr.filter((x: any) => x.name !== name)].slice(0, MAX_HISTORY)
      Taro.setStorageSync(HISTORY_KEY, JSON.stringify(next))
    } catch (_) {}
  }

  const removeHistory = (name: string) => {
    const next = historyList.filter((x) => x.name !== name)
    Taro.setStorageSync(HISTORY_KEY, JSON.stringify(next))
    setHistoryList(next)
  }

  const handleScan = async () => {
    if (!canSubmit) {
      Taro.showToast({ title: '请输入有效公司名称', icon: 'none' })
      return
    }
    const name = normalizedValue || value.trim()
    try {
      const res = await postWithAuth('/companies/scan', { company_name: name }) as any
      pushHistory(name)
      Taro.setStorageSync('has_company_scan', true)
      Taro.navigateTo({
        url: `/pages/scan-progress/index?scanId=${res?.id ?? res?.data?.id ?? 0}&companyName=${encodeURIComponent(name)}&type=company`
      })
    } catch {
      Taro.setStorageSync('has_company_scan', true)
      Taro.navigateTo({
        url: `/pages/scan-progress/index?scanId=0&companyName=${encodeURIComponent(name)}&type=company`
      })
    }
  }

  const handleManualSubmit = () => {
    Taro.showModal({
      title: '确认提交？',
      content: '人工检测将在1-2个工作日完成，结果将推送至消息中心',
      success: (r) => {
        if (r.confirm) {
          pushHistory(normalizedValue || value.trim())
          Taro.navigateTo({
            url: `/pages/scan-progress/index?scanId=0&companyName=${encodeURIComponent(normalizedValue || value.trim())}&type=company`
          })
        }
      }
    })
  }

  const handleRescan = async (name: string) => {
    setHistoryOpen(false)
    try {
      const res = await postWithAuth('/companies/scan', { company_name: name }) as any
      pushHistory(name)
      Taro.navigateTo({ url: `/pages/scan-progress/index?scanId=${res?.id ?? res?.data?.id ?? 0}&companyName=${encodeURIComponent(name)}&type=company` })
    } catch {
      Taro.navigateTo({ url: `/pages/scan-progress/index?scanId=0&companyName=${encodeURIComponent(name)}&type=company` })
    }
  }

  return (
    <View className='company-scan-page'>
      <View className='content'>
        <View className='top-row'>
          <Text className='page-title'>装修公司检测</Text>
          <Text className='history-link-top' onClick={() => setHistoryOpen(true)}>历史记录</Text>
        </View>
        <View className='input-container'>
          <View className='input-wrapper'>
            <Text className='search-icon'>🔍</Text>
            <Input
              className='input'
              placeholder='请输入装修公司名称/拼音首字母'
              placeholderClass='placeholder'
              value={value}
              onInput={handleInput}
              onFocus={() => setFocus(true)}
              onBlur={() => setTimeout(() => setFocus(false), 200)}
              maxlength={50}
            />
            <Text className='char-count'>已输入{charCount}/50字</Text>
            {value.length > 0 && (
              <Text className='clear-btn' onClick={handleClear}>×</Text>
            )}
          </View>
          {suggestions.length > 0 && focus && (
            <View className='suggestions'>
              {suggestions.map((item) => (
                <View key={item} className='suggestion-item' onClick={() => handleSelectSuggestion(item)}>
                  <Text className='main-text'>{item}</Text>
                </View>
              ))}
            </View>
          )}
          {focus && suggestions.length === 0 && canSubmit && (
            <View className='empty-suggest'>
              <Text className='empty-icon'>📭</Text>
              <Text className='empty-text'>未找到相关公司，请核对名称/地区</Text>
              <View className='manual-btn' onClick={handleManualSubmit}>
                <Text>手动提交检测</Text>
              </View>
            </View>
          )}
        </View>

        <View
          className={`scan-btn ${canSubmit ? 'active' : 'disabled'}`}
          onClick={canSubmit ? handleScan : () => Taro.showToast({ title: '请输入有效公司名称', icon: 'none' })}
        >
          <Text className='btn-text'>开始检测</Text>
        </View>

        <View className='notice'>
          <Text className='notice-text'>检测数据来源于公开工商信息/投诉平台，仅供参考</Text>
        </View>
      </View>

      {historyOpen && (
        <View className='history-mask' onClick={() => setHistoryOpen(false)}>
          <View className='history-modal' onClick={(e) => e.stopPropagation()}>
            <Text className='history-title'>历史记录</Text>
            {historyList.length === 0 ? (
              <Text className='history-empty'>暂无检测记录</Text>
            ) : (
              <ScrollView scrollY className='history-list'>
                {historyList.map((item) => (
                  <View key={item.name} className='history-item'>
                    <Text className='history-name'>{item.name}</Text>
                    <View className='history-actions'>
                      <Text className='history-link' onClick={() => handleRescan(item.name)}>重新检测</Text>
                      <Text className='history-link danger' onClick={() => removeHistory(item.name)}>删除</Text>
                    </View>
                  </View>
                ))}
              </ScrollView>
            )}
            <Text className='history-close' onClick={() => setHistoryOpen(false)}>关闭</Text>
          </View>
        </View>
      )}
    </View>
  )
}

export default CompanyScanPage

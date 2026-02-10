import React, { useState } from 'react'
import { View, Text, Textarea, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

/**
 * P24 意见反馈页
 */
const FEEDBACK_TYPES = [
  { value: 'bug', label: '功能BUG' },
  { value: 'suggest', label: '操作建议' },
  { value: 'privacy', label: '隐私异议' },
  { value: 'report', label: '报告准确性' },
  { value: 'other', label: '其他问题' }
]

const FeedbackPage: React.FC = () => {
  const typeFromUrl = Taro.getCurrentInstance().router?.params?.type || ''
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [feedbackType, setFeedbackType] = useState(typeFromUrl === 'privacy' ? 'privacy' : '')

  const handleSubmit = () => {
    if (!content.trim()) {
      Taro.showToast({ title: '请输入问题或建议', icon: 'none' })
      return
    }
    if (content.trim().length < 10) {
      Taro.showToast({ title: '请至少输入10字', icon: 'none' })
      return
    }
    setSubmitting(true)
    Taro.showToast({ title: '反馈已收到，我们会尽快处理', icon: 'success' })
    setTimeout(() => {
      setSubmitting(false)
      Taro.navigateBack()
    }, 1500)
  }

  return (
    <View className='feedback-page'>
      <View className='section'>
        <Text className='label'>反馈类型</Text>
        <View className='type-list'>
          {FEEDBACK_TYPES.map((t) => (
            <View
              key={t.value}
              className={`type-item ${feedbackType === t.value ? 'active' : ''}`}
              onClick={() => setFeedbackType(t.value)}
            >
              <Text>{t.label}</Text>
            </View>
          ))}
        </View>
        <Text className='label'>反馈内容（不少于10字）</Text>
        <Textarea
          className='textarea'
          placeholder='请详细描述您的问题/建议'
          value={content}
          onInput={(e) => setContent(e.detail.value)}
          maxlength={500}
        />
        <Text className='count'>{content.length}/500</Text>
      </View>
      <View className='btn-wrap'>
        <Button className='btn primary' onClick={handleSubmit} disabled={submitting}>
          {submitting ? '提交中...' : '提交'}
        </Button>
      </View>
    </View>
  )
}

export default FeedbackPage

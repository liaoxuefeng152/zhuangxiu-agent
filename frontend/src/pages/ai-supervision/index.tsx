import React, { useState, useRef, useEffect } from 'react'
import { View, Text, ScrollView, Input } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

const STAGE_NAMES: Record<string, string> = {
  material: 'S00材料进场核对',
  plumbing: 'S01隐蔽工程',
  carpentry: 'S02泥瓦工',
  woodwork: 'S03木工',
  painting: 'S04油漆',
  installation: 'S05安装收尾'
}

type Msg = { role: 'user' | 'ai'; content: string; ref?: string }

/**
 * P36 AI监理咨询页 - 基于验收报告上下文的AI聊天 + 转人工入口
 */
const AiSupervisionPage: React.FC = () => {
  const router = Taro.getCurrentInstance().router
  const stage = (router?.params?.stage as string) || 'plumbing'
  const summary = router?.params?.summary ? decodeURIComponent(router.params.summary) : '水电布线间距不足30cm'

  const [messages, setMessages] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef<any>(null)

  const stageName = STAGE_NAMES[stage] || '当前阶段'

  useEffect(() => {
    setMessages([
      {
        role: 'ai',
        content: `您好，我是AI监理。您当前咨询的是「${stageName}」验收问题。\n\n请描述您遇到的具体问题（如：${summary}），我会基于《装修验收规范》为您分析并给出建议。`,
        ref: '基于本地验收规范'
      }
    ])
  }, [stage, stageName, summary])

  useEffect(() => {
    if (messages.length && scrollRef.current) {
      try {
        scrollRef.current.scrollTo({ scrollTop: 99999, animated: true })
      } catch (_) {}
    }
  }, [messages.length])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text) return
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setLoading(true)
    await new Promise((r) => setTimeout(r, 800 + Math.random() * 800))
    setMessages((prev) => [
      ...prev,
      {
        role: 'ai',
        content: '根据常见验收规范，建议您：\n1. 强弱电管线间距应≥30cm，避免信号干扰；\n2. 线管固定牢固、走向清晰；\n3. 预留检修口。若已整改可申请复检。如需人工监理上门可点击下方「转人工监理」。',
        ref: '《装修验收规范》相关条款'
      }
    ])
    setLoading(false)
  }

  const handleTransferHuman = () => {
    const isMember = !!Taro.getStorageSync('is_member')
    const price = isMember ? 0 : 49
    Taro.showModal({
      title: '转人工监理',
      content: isMember
        ? '会员每月2次免费人工咨询，是否立即转接？'
        : `人工监理咨询 ¥49/次，支付后立即转接，是否继续？`,
      confirmText: '确定',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          if (isMember) {
            Taro.showToast({ title: '正在转接人工...', icon: 'none' })
            Taro.navigateTo({ url: '/pages/contact/index' })
          } else {
            Taro.showToast({ title: '唤起支付...', icon: 'none' })
          }
        }
      }
    })
  }

  const goHistory = () => {
    Taro.showToast({ title: '咨询记录功能开发中', icon: 'none' })
  }

  return (
    <View className='ai-supervision-page'>
      <View className='nav-bar'>
        <Text className='nav-back' onClick={() => Taro.navigateBack()}>返回</Text>
        <Text className='nav-title'>AI监理咨询</Text>
        <Text className='nav-right' onClick={goHistory}>咨询记录</Text>
      </View>

      <View className='context-card'>
        <Text className='context-label'>当前咨询：{stageName}验收问题</Text>
        <Text className='context-summary'>{summary}</Text>
      </View>

      <ScrollView
        scrollY
        className='chat-area'
        scrollIntoView={'msg-' + (messages.length - 1)}
        scrollWithAnimation
        ref={scrollRef}
      >
        {messages.map((m, i) => (
          <View key={i} id={'msg-' + i} className={`bubble-wrap ${m.role}`}>
            {m.role === 'ai' && <View className='avatar ai'>AI</View>}
            <View className={`bubble ${m.role}`}>
              <Text className='bubble-text'>{m.content}</Text>
              {m.ref && <Text className='bubble-ref'>基于{m.ref}</Text>}
            </View>
            {m.role === 'user' && <View className='avatar user'>我</View>}
          </View>
        ))}
        {loading && (
          <View className='bubble-wrap ai'>
            <View className='avatar ai'>AI</View>
            <View className='bubble ai loading'><Text className='bubble-text'>正在分析...</Text></View>
          </View>
        )}
      </ScrollView>

      <View className='transfer-bar' onClick={handleTransferHuman}>
        <Text className='transfer-text'>AI无法解决？转人工监理</Text>
      </View>

      <View className='input-bar'>
        <Input
          className='input'
          placeholder='请描述您的问题'
          placeholderClass='input-placeholder'
          value={input}
          onInput={(e) => setInput(e.detail.value)}
          confirmType='send'
          onConfirm={sendMessage}
        />
        <View className='send-wrap'>
          <View className='btn-icon' onClick={() => Taro.chooseImage({ count: 1, success: () => Taro.showToast({ title: '图片上传开发中', icon: 'none' }) }).catch(() => {})}>📷</View>
          <View className={`btn-send ${input.trim() ? 'active' : ''}`} onClick={sendMessage}>
            <Text>发送</Text>
          </View>
        </View>
      </View>
    </View>
  )
}

export default AiSupervisionPage

import React, { useState, useEffect, useRef } from 'react'
import { View, Text, ScrollView, Input } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useAppSelector } from '../../store/hooks'
import './index.scss'

type Msg = { role: 'user' | 'service' | 'system'; content: string; time?: string }

const QUICK_REPLIES = [
  '报告解锁问题',
  '验收不通过',
  '提醒未收到',
  '会员权益',
  '退款申请',
  '其他问题'
]

/**
 * P23 在线客服页 - 聊天窗口、快捷回复、输入区、会员优先接入
 */
const ContactPage: React.FC = () => {
  const userInfo = useAppSelector((s) => s.user.userInfo)
  const isMember = userInfo?.isMember ?? !!Taro.getStorageSync('is_member')

  const [messages, setMessages] = useState<Msg[]>([
    { role: 'system', content: '欢迎使用装修避坑管家客服，工作时间内我们会尽快回复您。' },
    { role: 'service', content: '您好，请问有什么可以帮您？', time: '09:00' }
  ])
  const [input, setInput] = useState('')
  const scrollRef = useRef<any>(null)

  useEffect(() => {
    if (messages.length && scrollRef.current) {
      try {
        scrollRef.current.scrollTo({ scrollTop: 99999, animated: true })
      } catch (_) {}
    }
  }, [messages.length])

  const sendMessage = (text?: string) => {
    const content = (text || input.trim()).trim()
    if (!content) return
    if (!text) setInput('')
    const time = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })
    setMessages((prev) => [...prev, { role: 'user', content, time }])
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: 'service', content: '您的消息已收到，客服将尽快回复。如有紧急问题可致电 400-xxx-xxxx。', time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false }) }
      ])
    }, 600)
  }

  const handleQuickReply = (item: string) => {
    sendMessage(item)
  }

  const handleCall = () => {
    Taro.makePhoneCall({ phoneNumber: '400-xxx-xxxx' })
  }

  return (
    <View className='contact-page'>
      <View className='nav-bar'>
        <Text className='nav-back' onClick={() => Taro.navigateBack()}>返回</Text>
        <Text className='nav-title'>在线客服</Text>
        <Text className='nav-hours'>9:00-18:00</Text>
      </View>

      {isMember && (
        <View className='member-tip'>
          <Text>会员专属客服，优先接入</Text>
        </View>
      )}

      <ScrollView
        scrollY
        className='chat-area'
        scrollWithAnimation
        ref={scrollRef}
      >
        {messages.map((m, i) => (
          <View key={i} className={`bubble-wrap ${m.role}`}>
            {m.role === 'service' && <View className='avatar service'>客服</View>}
            <View className={`bubble ${m.role}`}>
              <Text className='bubble-text'>{m.content}</Text>
              {m.time && <Text className='bubble-time'>{m.time}</Text>}
            </View>
            {m.role === 'user' && <View className='avatar user'>我</View>}
          </View>
        ))}
      </ScrollView>

      <View className='quick-reply'>
        <ScrollView scrollX className='quick-scroll' showScrollbar={false}>
          {QUICK_REPLIES.map((item, i) => (
            <View key={i} className='quick-btn' onClick={() => handleQuickReply(item)}>
              <Text>{item}</Text>
            </View>
          ))}
        </ScrollView>
      </View>

      <View className='input-bar'>
        <Input
          className='input'
          placeholder='请输入您的问题'
          placeholderClass='input-placeholder'
          value={input}
          onInput={(e) => setInput(e.detail.value)}
          confirmType='send'
          onConfirm={() => sendMessage()}
        />
        <View className='btn-icon' onClick={() => Taro.chooseImage({ count: 1 }).then(() => Taro.showToast({ title: '图片上传开发中', icon: 'none' })).catch(() => {})}>
          <Text>📷</Text>
        </View>
        <View className={`btn-send ${input.trim() ? 'active' : ''}`} onClick={() => sendMessage()}>
          <Text>发送</Text>
        </View>
      </View>

      <View className='phone-row' onClick={handleCall}>
        <Text className='phone-label'>电话咨询</Text>
        <Text className='phone-num'>400-xxx-xxxx</Text>
      </View>
    </View>
  )
}

export default ContactPage

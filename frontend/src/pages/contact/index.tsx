import React, { useState, useEffect, useRef } from 'react'
import { View, Text, ScrollView, Input, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useAppSelector } from '../../store/hooks'
import { consultationApi, acceptanceApi } from '../../services/api'
import './index.scss'

type MsgAi = { role: 'user' | 'ai'; content: string; ref?: string; images?: string[] }
type MsgHuman = { role: 'user' | 'service' | 'system'; content: string; time?: string }

const QUICK_REPLIES = [
  '报告解锁问题',
  '验收不通过',
  '提醒未收到',
  '会员权益',
  '退款申请',
  '其他问题'
]

/**
 * P23 在线客服页 - AI智能解答优先，解决不了转人工
 * 双入口：AI 智能解答 | 人工客服
 */
const ContactPage: React.FC = () => {
  const userInfo = useAppSelector((s) => s.user.userInfo)
  const isMember = userInfo?.isMember ?? !!Taro.getStorageSync('is_member')

  const router = Taro.getCurrentInstance().router
  const initMode = (router?.params?.mode === 'human' ? 'human' : 'ai') as 'ai' | 'human'
  const [mode, setMode] = useState<'ai' | 'human'>(initMode)

  // AI 模式状态
  const [aiMessages, setAiMessages] = useState<MsgAi[]>([])
  const [aiInput, setAiInput] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [sessionCreating, setSessionCreating] = useState(true)
  const [pendingImages, setPendingImages] = useState<Array<{ local: string; objectKey: string; displayUrl: string }>>([])
  const [uploading, setUploading] = useState(false)

  // 人工模式状态
  const [humanMessages, setHumanMessages] = useState<MsgHuman[]>([
    { role: 'system', content: '欢迎使用装修避坑管家客服，工作时间内我们会尽快回复您。' },
    { role: 'service', content: '您好，请问有什么可以帮您？', time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false }) }
  ])
  const [humanInput, setHumanInput] = useState('')

  const scrollRef = useRef<any>(null)

  const aiWelcome = '您好，我是智能客服。可解答报告解锁、验收规范、会员权益、退款政策等问题，支持上传照片。\n\n解决不了可随时点击下方「转人工客服」。'

  useEffect(() => {
    setAiMessages([{ role: 'ai', content: aiWelcome, ref: '24/7 智能响应' }])
  }, [])

  useEffect(() => {
    const token = Taro.getStorageSync('access_token') || Taro.getStorageSync('token')
    if (!token) {
      setSessionCreating(false)
      return
    }
    let cancelled = false
    const run = async () => {
      try {
        const res: any = await consultationApi.createSession({})
        const sid = res?.data?.session_id ?? res?.session_id
        if (!cancelled && sid) setSessionId(Number(sid))
      } catch (_) {
        if (!cancelled) setSessionId(null)
      } finally {
        if (!cancelled) setSessionCreating(false)
      }
    }
    run()
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    if ((mode === 'ai' ? aiMessages.length : humanMessages.length) && scrollRef.current) {
      try {
        scrollRef.current.scrollTo({ scrollTop: 99999, animated: true })
      } catch (_) {}
    }
  }, [mode, aiMessages.length, humanMessages.length])

  const addPhoto = () => {
    const remain = 5 - pendingImages.length
    if (remain <= 0) {
      Taro.showToast({ title: '最多上传5张照片', icon: 'none' })
      return
    }
    Taro.chooseImage({
      count: remain,
      sourceType: ['camera', 'album'],
      success: async (res) => {
        const paths = res.tempFilePaths || []
        if (!paths.length) return
        setUploading(true)
        try {
          const added: Array<{ local: string; objectKey: string; displayUrl: string }> = []
          for (const p of paths) {
            const up: any = await acceptanceApi.uploadPhoto(p)
            const out = up?.data ?? up
            const objectKey = out?.object_key ?? out?.file_url
            const displayUrl = out?.file_url || (typeof objectKey === 'string' && objectKey.startsWith('http') ? objectKey : '')
            if (objectKey && displayUrl) added.push({ local: p, objectKey: String(objectKey), displayUrl })
          }
          if (added.length) setPendingImages((prev) => [...prev, ...added].slice(0, 5))
        } catch (e: any) {
          Taro.showToast({ title: e?.message || '上传失败', icon: 'none' })
        } finally {
          setUploading(false)
        }
      }
    }).catch(() => {})
  }

  const removePendingImage = (idx: number) => setPendingImages((prev) => prev.filter((_, i) => i !== idx))

  const sendAiMessage = async () => {
    const text = aiInput.trim()
    const hasImages = pendingImages.length > 0
    if (!text && !hasImages) return
    if (!sessionId) {
      Taro.showToast({ title: '会话未就绪，请稍后', icon: 'none' })
      return
    }
    const content = text || '请根据我上传的照片分析'
    const imageUrls = pendingImages.map((p) => p.objectKey)
    const displayUrls = pendingImages.map((p) => (p.displayUrl?.startsWith?.('http') ? p.displayUrl : p.objectKey))
    setAiInput('')
    setPendingImages([])
    setAiMessages((prev) => [...prev, { role: 'user', content, images: displayUrls.length ? displayUrls : undefined }])
    setAiLoading(true)
    try {
      const res: any = await consultationApi.sendMessage(sessionId, content, imageUrls.length ? imageUrls : undefined)
      if (res && (res.code === 403 || (res.code !== undefined && res.code !== 0))) {
        const errMsg = res.msg ?? res.detail ?? '请求失败，请稍后重试'
        Taro.showToast({ title: errMsg, icon: 'none', duration: 2500 })
        setAiMessages((prev) => [...prev, { role: 'ai', content: `抱歉，${errMsg}。可点击下方「转人工客服」继续咨询。`, ref: '' }])
        return
      }
      const reply = res?.data?.reply ?? res?.reply ?? ''
      if (reply) {
        setAiMessages((prev) => [...prev, { role: 'ai', content: reply, ref: '智能客服' }])
      } else {
        throw new Error('AI 返回为空')
      }
    } catch (e: any) {
      const msg = e?.response?.data?.msg ?? e?.response?.data?.detail ?? e?.message ?? 'AI分析失败，请稍后重试'
      const tip = typeof msg === 'string' ? msg : 'AI分析失败，请稍后重试'
      Taro.showToast({ title: tip, icon: 'none', duration: 2500 })
      setAiMessages((prev) => [...prev, { role: 'ai', content: `抱歉，${tip}。可点击下方「转人工客服」继续咨询。`, ref: '' }])
    } finally {
      setAiLoading(false)
    }
  }

  const switchToHuman = () => {
    setMode('human')
    setHumanMessages((prev) => [
      ...prev,
      { role: 'system', content: '已为您转接人工客服，工作时间内将尽快回复。' }
    ])
    Taro.showToast({ title: '已转人工客服', icon: 'none' })
  }

  const sendHumanMessage = (text?: string) => {
    const content = (text || humanInput.trim()).trim()
    if (!content) return
    if (!text) setHumanInput('')
    const time = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })
    setHumanMessages((prev) => [...prev, { role: 'user', content, time }])
    setTimeout(() => {
      setHumanMessages((prev) => [
        ...prev,
        { role: 'service', content: '您的消息已收到，客服将尽快回复。如有紧急问题可致电 400-xxx-xxxx。', time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false }) }
      ])
    }, 600)
  }

  const handleQuickReply = (item: string) => sendHumanMessage(item)

  const handleCall = () => {
    Taro.makePhoneCall({ phoneNumber: '400-xxx-xxxx' })
  }

  return (
    <View className='contact-page'>
      <View className='nav-bar'>
        <Text className='nav-back' onClick={() => Taro.navigateBack()}>返回</Text>
        <Text className='nav-title'>客服中心</Text>
        <Text className='nav-hours'>人工 9:00-18:00</Text>
      </View>

      <View className='mode-tabs'>
        <View className={`tab ${mode === 'ai' ? 'active' : ''}`} onClick={() => setMode('ai')}>
          <Text>AI 智能解答</Text>
          <Text className='tab-desc'>24/7 快速响应</Text>
        </View>
        <View className={`tab ${mode === 'human' ? 'active' : ''}`} onClick={() => setMode('human')}>
          <Text>人工客服</Text>
          <Text className='tab-desc'>工作日 9:00-18:00</Text>
        </View>
      </View>

      {isMember && mode === 'human' && (
        <View className='member-tip'>
          <Text>会员专属客服，优先接入</Text>
        </View>
      )}

      {mode === 'ai' ? (
        <>
          <ScrollView scrollY className='chat-area' scrollWithAnimation ref={scrollRef}>
            {aiMessages.map((m, i) => (
              <View key={i} className={`bubble-wrap ${m.role}`}>
                {m.role === 'ai' && <View className='avatar ai'>AI</View>}
                <View className={`bubble ${m.role}`}>
                  {m.images?.length ? (
                    <View className='bubble-images'>
                      {m.images.map((url, j) => (
                        <Image key={j} className='bubble-img' src={url} mode='aspectFill' />
                      ))}
                    </View>
                  ) : null}
                  <Text className='bubble-text'>{m.content}</Text>
                  {m.ref && <Text className='bubble-ref'>{m.ref}</Text>}
                </View>
                {m.role === 'user' && <View className='avatar user'>我</View>}
              </View>
            ))}
            {aiLoading && (
              <View className='bubble-wrap ai'>
                <View className='avatar ai'>AI</View>
                <View className='bubble ai loading'><Text className='bubble-text'>正在分析...</Text></View>
              </View>
            )}
          </ScrollView>

          <View className='transfer-bar' onClick={switchToHuman}>
            <Text className='transfer-text'>AI无法解决？转人工客服</Text>
          </View>

          {pendingImages.length > 0 && (
            <View className='pending-images'>
              {pendingImages.map((p, i) => (
                <View key={i} className='pending-img-wrap'>
                  <Image className='pending-img' src={p.local} mode='aspectFill' />
                  <Text className='pending-remove' onClick={() => removePendingImage(i)}>×</Text>
                </View>
              ))}
            </View>
          )}
          <View className='input-bar'>
            <Input
              className='input'
              placeholder='请输入您的问题'
              placeholderClass='input-placeholder'
              value={aiInput}
              onInput={(e) => setAiInput(e.detail.value)}
              confirmType='send'
              onConfirm={sendAiMessage}
            />
            <View className='send-wrap'>
              <View className='btn-icon' onClick={addPhoto}>{uploading ? '...' : '📷'}</View>
              <View className={`btn-send ${(aiInput.trim() || pendingImages.length) && sessionId ? 'active' : ''}`} onClick={sendAiMessage}>
                <Text>发送</Text>
              </View>
            </View>
          </View>
        </>
      ) : (
        <>
          <View className='quick-reply'>
            <ScrollView scrollX className='quick-scroll' showScrollbar={false}>
              {QUICK_REPLIES.map((item, i) => (
                <View key={i} className='quick-btn' onClick={() => handleQuickReply(item)}>
                  <Text>{item}</Text>
                </View>
              ))}
            </ScrollView>
          </View>
          <ScrollView scrollY className='chat-area' scrollWithAnimation ref={scrollRef}>
            {humanMessages.map((m, i) => (
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
          <View className='input-bar'>
            <Input
              className='input'
              placeholder='请输入您的问题'
              placeholderClass='input-placeholder'
              value={humanInput}
              onInput={(e) => setHumanInput(e.detail.value)}
              confirmType='send'
              onConfirm={() => sendHumanMessage()}
            />
            <View className={`btn-send ${humanInput.trim() ? 'active' : ''}`} onClick={() => sendHumanMessage()}>
              <Text>发送</Text>
            </View>
          </View>
          <View className='phone-row' onClick={handleCall}>
            <Text className='phone-label'>电话咨询</Text>
            <Text className='phone-num'>400-xxx-xxxx</Text>
          </View>
        </>
      )}
    </View>
  )
}

export default ContactPage

import React, { useState, useRef, useEffect } from 'react'
import { View, Text, ScrollView, Input, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { consultationApi, acceptanceApi } from '../../services/api'
import './index.scss'

const STAGE_NAMES: Record<string, string> = {
  material: 'S00材料进场核对',
  plumbing: 'S01隐蔽工程',
  carpentry: 'S02泥瓦工',
  woodwork: 'S03木工',
  painting: 'S04油漆',
  installation: 'S05安装收尾'
}

type Msg = { role: 'user' | 'ai'; content: string; ref?: string; images?: string[] }

/**
 * P36 AI监理咨询页 - 基于验收报告上下文的AI聊天 + 转人工入口
 */
const REPORT_TYPE_NAMES: Record<string, string> = {
  company: '公司风险报告',
  quote: '报价单分析报告',
  contract: '合同审核报告'
}

const AiSupervisionPage: React.FC = () => {
  const router = Taro.getCurrentInstance().router
  const stage = router?.params?.stage as string | undefined
  const summary = router?.params?.summary ? decodeURIComponent(router.params.summary) : '水电布线间距不足30cm'
  const reportType = router?.params?.type as string | undefined
  const reportId = router?.params?.reportId as string | undefined
  const reportName = router?.params?.name ? decodeURIComponent(router.params.name) : ''

  const [messages, setMessages] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [sessionCreating, setSessionCreating] = useState(true)
  const [pendingImages, setPendingImages] = useState<Array<{ local: string; objectKey: string; displayUrl: string }>>([])
  const [uploading, setUploading] = useState(false)
  const scrollRef = useRef<any>(null)

  const fromReportDetail = reportType && ['company', 'quote', 'contract'].includes(reportType)
  const stageName = stage ? (STAGE_NAMES[stage] || '当前阶段') : ''
  const contextLabel = fromReportDetail
    ? `${REPORT_TYPE_NAMES[reportType] || reportType}${reportName ? ` - ${reportName}` : ''}`
    : `${stageName}验收问题`
  const welcomeContent = fromReportDetail
    ? `您好，我是AI监理。您当前咨询的是「${contextLabel}」相关问题。\n\n请描述您的疑问（如风险解读、条款说明、报价疑问等），我会基于行业规范为您分析并给出建议。`
    : `您好，我是AI监理。您当前咨询的是「${stageName}」验收问题。\n\n请描述您遇到的具体问题（如：${summary}），我会基于《装修验收规范》为您分析并给出建议。`

  useEffect(() => {
    setMessages([
      {
        role: 'ai',
        content: welcomeContent,
        ref: fromReportDetail ? '基于行业规范与本地市场' : '基于本地验收规范'
      }
    ])
  }, [welcomeContent, fromReportDetail])

  useEffect(() => {
    const token = Taro.getStorageSync('access_token') || Taro.getStorageSync('token')
    if (!token) {
      setSessionCreating(false)
      return
    }
    let cancelled = false
    const run = async () => {
      try {
        let acceptanceAnalysisId: number | undefined
        if (stage && !fromReportDetail) {
          try {
            const listRes: any = await acceptanceApi.getList({ stage, page: 1, page_size: 1 })
            const list = listRes?.data?.list ?? listRes?.list ?? []
            if (list?.[0]?.id) acceptanceAnalysisId = list[0].id
          } catch (_) {}
        }
        const res: any = await consultationApi.createSession({
          stage: stage || (fromReportDetail ? reportType : undefined),
          acceptance_analysis_id: acceptanceAnalysisId
        })
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
  }, [stage, fromReportDetail, reportType])

  useEffect(() => {
    if (messages.length && scrollRef.current) {
      try {
        scrollRef.current.scrollTo({ scrollTop: 99999, animated: true })
      } catch (_) {}
    }
  }, [messages.length])

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

  const removePendingImage = (idx: number) => {
    setPendingImages((prev) => prev.filter((_, i) => i !== idx))
  }

  const sendMessage = async () => {
    const text = input.trim()
    const hasImages = pendingImages.length > 0
    if (!text && !hasImages) return
    if (!sessionId) {
      Taro.showToast({ title: '会话未就绪，请稍后', icon: 'none' })
      return
    }
    const content = text || '请根据我上传的照片分析'
    const imageUrls = pendingImages.map((p) => p.objectKey)
    setInput('')
    setPendingImages([])
    const displayUrls = pendingImages.map((p) => p.displayUrl.startsWith('http') ? p.displayUrl : p.objectKey)
    setMessages((prev) => [...prev, { role: 'user', content, images: displayUrls.length ? displayUrls : undefined }])
    setLoading(true)
    try {
      const res: any = await consultationApi.sendMessage(sessionId, content, imageUrls.length ? imageUrls : undefined)
      const reply = res?.data?.reply ?? res?.reply ?? ''
      if (reply) {
        setMessages((prev) => [
          ...prev,
          { role: 'ai', content: reply, ref: '基于本地验收规范' }
        ])
      } else {
        throw new Error('AI 返回为空')
      }
    } catch (e: any) {
      const msg = e?.response?.data?.detail ?? e?.message ?? 'AI分析失败，请稍后重试'
      Taro.showToast({ title: typeof msg === 'string' ? msg : 'AI分析失败，请稍后重试', icon: 'none' })
      setMessages((prev) => [
        ...prev,
        { role: 'ai', content: '抱歉，AI 分析失败，请稍后重试。如需帮助可点击下方「转人工监理」。', ref: '' }
      ])
    } finally {
      setLoading(false)
    }
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
        <Text className='context-label'>当前咨询：{contextLabel}</Text>
        <Text className='context-summary'>{fromReportDetail ? (reportName || '报告相关问题') : summary}</Text>
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
              {m.images?.length ? (
                <View className='bubble-images'>
                  {m.images.map((url, j) => (
                    <Image key={j} className='bubble-img' src={url} mode='aspectFill' />
                  ))}
                </View>
              ) : null}
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
          placeholder='请描述您的问题'
          placeholderClass='input-placeholder'
          value={input}
          onInput={(e) => setInput(e.detail.value)}
          confirmType='send'
          onConfirm={sendMessage}
        />
        <View className='send-wrap'>
          <View className='btn-icon' onClick={addPhoto}>{uploading ? '...' : '📷'}</View>
          <View className={`btn-send ${(input.trim() || pendingImages.length) && sessionId ? 'active' : ''}`} onClick={sendMessage}>
            <Text>发送</Text>
          </View>
        </View>
      </View>
    </View>
  )
}

export default AiSupervisionPage

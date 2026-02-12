import React, { useState, useEffect, useCallback, useRef } from 'react'
import { View, Text, Swiper, SwiperItem } from '@tarojs/components'
import Taro from '@tarojs/taro'
import ExampleImageModal from '../../components/ExampleImageModal'
import { safeSwitchTab, TAB_HOME } from '../../utils/navigation'
import { EXAMPLE_IMAGES } from '../../config/assets'
import './index.scss'

/**
 * P01 引导页 - 装修避坑管家
 * 品牌介绍/隐私保障/服务承诺，3页滑动
 */
const Onboarding: React.FC = () => {
  const [current, setCurrent] = useState(0)
  const [countdown, setCountdown] = useState(3)
  const [preview, setPreview] = useState<{ type: string; title: string; content: string } | null>(null)
  const countdownPaused = useRef(false)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const countdownRef = useRef(3)

  useEffect(() => {
    const timer = setTimeout(() => {
      try {
        if (Taro.getStorageSync('onboarding_completed') || Taro.getStorageSync('has_onboarded')) {
          Taro.reLaunch({ url: '/pages/index/index' })
        }
      } catch (_) {}
    }, 100)
    return () => clearTimeout(timer)
  }, [])

  const goToHome = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
    Taro.setStorageSync('onboarding_completed', true)
    Taro.setStorageSync('has_onboarded', true)
    // 跳转 P02 后首先弹出城市选择，然后弹出「进度+消息提醒权限请求弹窗」
    Taro.setStorageSync('show_city_selection_modal', true)
    Taro.setStorageSync('show_remind_permission_modal', true)
    safeSwitchTab(TAB_HOME, { defer: 100 })
  }, [])

  countdownRef.current = countdown

  // 3秒倒计时，滑动时暂停；跳转用 setTimeout(0) 脱出 setInterval 栈，避免小程序 __subPageFrameEndTime__ 报错
  useEffect(() => {
    let mounted = true
    const tick = () => {
      try {
        if (!mounted) return
        if (countdownPaused.current) return
        const next = countdownRef.current - 1
        if (next <= 0) {
          if (timerRef.current) {
            clearInterval(timerRef.current)
            timerRef.current = null
          }
          // 延迟到下一事件循环再跳转，避免在 setInterval 回调栈内执行导致小程序框架报错
          setTimeout(() => goToHome(), 0)
          return
        }
        countdownRef.current = next
        setCountdown(next)
      } catch (_) {
        // 小程序页面已销毁时回调仍可能被调度，吞掉异常
      }
    }
    timerRef.current = setInterval(tick, 1000)
    return () => {
      mounted = false
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [goToHome])

  const handleSwiperChange = (e: any) => {
    setCurrent(e.detail.current)
    const three = 3
    countdownRef.current = three
    setCountdown(three)
    countdownPaused.current = true
    setTimeout(() => { countdownPaused.current = false }, 500)
  }

  const handleStart = async () => {
    try {
      const res = await Taro.login()
      const code = res?.code
      if (code) {
        const { env } = await import('../../config/env')
        const loginRes = await Taro.request({
          url: `${env.apiBaseUrl}/users/login`,
          method: 'POST',
          header: { 'Content-Type': 'application/json' },
          data: { code }
        })
        const d = (loginRes.data as any)?.data ?? loginRes.data
        const token = d?.access_token
        const userId = d?.user_id
        if (token && userId) {
          Taro.setStorageSync('access_token', token)
          Taro.setStorageSync('user_id', userId)
          Taro.setStorageSync('login_fresh_at', Date.now())
        }
      }
    } catch {
      // 未登录也可继续
    }
    goToHome()
  }

  const showPreview = (type: string) => {
    const map: Record<string, { title: string; content: string }> = {
      company: { title: '公司检测', content: 'AI核验资质与纠纷记录，输入公司名称即可检测' },
      quote: { title: '报价单分析', content: 'AI识别漏项与虚高，上传报价单自动分析' },
      contract: { title: '合同审核', content: '高亮霸王条款与陷阱，上传合同AI逐条分析' },
      acceptance: { title: '验收分析', content: '拍摄/上传验收照片，AI识别施工问题并给出整改建议' }
    }
    const m = map[type] || map.quote
    setPreview({ type, title: m.title, content: m.content })
  }

  // 原型 P01：页1 装修避坑AI全程护航 / 页2 6大阶段标准化施工 / 页3 智能提醒
  const slides = [
    {
      id: 'brand',
      logo: '🛡️',
      title: '装修避坑，AI全程护航',
      subtitle: '让装修决策更安全',
      capabilities: [
        { icon: '🏢', text: '装修公司', desc: 'AI检测', type: 'company' },
        { icon: '💰', text: '报价', desc: 'AI检测', type: 'quote' },
        { icon: '📜', text: '合同', desc: 'AI检测', type: 'contract' }
      ]
    },
    {
      id: 'stages',
      icon: '📐',
      title: '6大阶段标准化施工',
      subtitle: '材料核对+5大工序AI验收，流程互锁',
      items: [
        { icon: '📦', text: '材料进场核对', desc: 'S00 台账生成' },
        { icon: '🔌', text: '隐蔽工程→安装收尾', desc: 'S01-S05 逐级验收' },
        { icon: '🔒', text: '流程互锁', desc: '前置未通过则后续锁定' }
      ],
      linkText: '查看完整隐私政策',
      linkUrl: '/pages/neutral-statement/index'
    },
    {
      id: 'remind',
      icon: '🔔',
      title: '智能提醒，装修不遗漏',
      subtitle: '阶段开始/验收前3天，微信+小程序双重提醒',
      items: [
        { icon: '📱', text: '微信服务通知', desc: '点击直达对应阶段' },
        { icon: '🔴', text: '小程序内红点', desc: '消息中心+页面角标' },
        { icon: '⚙️', text: '自定义提前天数', desc: '1/2/3/5/7天可选' }
      ],
      linkText: '查看服务条款',
      linkUrl: '/pages/neutral-statement/index'
    }
  ]

  return (
    <View className='onboarding-page'>
      <Text className='skip-link' onClick={() => goToHome()}>跳过</Text>
      <Swiper
        className='swiper'
        current={current}
        onChange={handleSwiperChange}
        indicatorDots={false}
      >
        {slides.map((s) => (
          <SwiperItem key={s.id}>
            <View className='slide'>
              {s.id === 'brand' && (s as any).capabilities ? (
                <View className='brand-slide-content'>
                  <View className='brand-logo'>
                    <Text className='logo-icon'>{s.logo}</Text>
                    <Text className='logo-text'>装修避坑管家</Text>
                  </View>
                  <Text className='slide-title'>{s.title}</Text>
                  <Text className='slide-subtitle'>{s.subtitle}</Text>
                  <View className='section-divider'>
                    <View className='divider-line' />
                    <Text className='section-label'>核心能力</Text>
                    <View className='divider-line' />
                  </View>
                  <View className='capability-grid'>
                    {(s as any).capabilities.map((cap: any) => (
                      <View key={cap.type} className='cap-item' onClick={() => showPreview(cap.type)}>
                        <Text className='cap-icon'>{cap.icon}</Text>
                        <Text className='cap-title'>{cap.text}</Text>
                        <Text className='cap-desc'>{cap.desc}</Text>
                        <Text className='cap-hint'>点击预览示例</Text>
                      </View>
                    ))}
                  </View>
                </View>
              ) : (
                <View className='commitment-slide'>
                  <View className='slide-icon-wrap'>
                    <Text className='slide-icon'>{s.icon}</Text>
                  </View>
                  <Text className='slide-title'>{(s as any).title}</Text>
                  <Text className='slide-subtitle'>{(s as any).subtitle}</Text>
                  <View className='commitment-list'>
                    {((s as any).items || []).map((item: any, idx: number) => (
                      <View key={idx} className='commitment-item'>
                        <Text className='commitment-icon'>{item.icon}</Text>
                        <View className='commitment-content'>
                          <Text className='commitment-title'>{item.text}</Text>
                          <Text className='commitment-desc'>{item.desc}</Text>
                        </View>
                      </View>
                    ))}
                  </View>
                  {(s as any).linkText && (
                    <Text className='policy-link' onClick={() => Taro.navigateTo({ url: (s as any).linkUrl || '/pages/neutral-statement/index' })}>
                      {(s as any).linkText}
                    </Text>
                  )}
                </View>
              )}
            </View>
          </SwiperItem>
        ))}
      </Swiper>

      <ExampleImageModal
        visible={!!preview}
        title={preview?.title || '功能预览'}
        content={preview?.content || ''}
        imageUrl={preview ? (EXAMPLE_IMAGES as any)[preview.type] : undefined}
        onClose={() => setPreview(null)}
      />

      <Text className='footer-slogan'>让每一步装修决策都有AI护航</Text>
      <View className='footer'>
        <View className='indicator-row'>
          <View className='page-dots'>
            {slides.map((_, i) => (
              <View key={i} className={`dot ${current === i ? 'active' : ''}`} />
            ))}
          </View>
          <Text className='countdown'>{countdown}s</Text>
        </View>
        <View className='btn primary' onClick={handleStart}>
          <Text className='btn-text'>开始使用</Text>
        </View>
      </View>
    </View>
  )
}

export default Onboarding

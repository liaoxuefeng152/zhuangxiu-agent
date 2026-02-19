import React, { useState, useEffect, useRef } from 'react'
import { View, Text, Image, Input, Button, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { designerApi } from '../services/api'
import './FloatingDesignerAvatar.scss'

interface FloatingDesignerAvatarProps {
  /** 是否显示拖拽提示 */
  showDragHint?: boolean
  /** 初始位置 */
  initialPosition?: { x: number; y: number }
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

/**
 * AI设计师悬浮头像组件 - 真正的聊天机器人
 * 功能：
 * 1. 可拖拽悬浮在页面任意位置
 * 2. 点击头像弹出AI设计师聊天对话框
 * 3. 支持多轮对话，维护对话历史
 * 4. 显示拖拽提示（首次显示）
 */
const FloatingDesignerAvatar: React.FC<FloatingDesignerAvatarProps> = ({
  showDragHint = true,
  initialPosition = { x: 20, y: 200 }
}) => {
  const [position, setPosition] = useState(initialPosition)
  const [dragging, setDragging] = useState(false)
  const [showDialog, setShowDialog] = useState(false)
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [showHint, setShowHint] = useState(showDragHint)
  const [isFirstTime, setIsFirstTime] = useState(true)
  const [chatSessionId, setChatSessionId] = useState<string>('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isCreatingSession, setIsCreatingSession] = useState(false)
  
  const startPosRef = useRef({ x: 0, y: 0 })
  const avatarRef = useRef<HTMLDivElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const scrollViewRef = useRef<any>(null)
  
  // 检查是否是第一次显示
  useEffect(() => {
    const hasSeen = Taro.getStorageSync('has_seen_designer_avatar')
    if (hasSeen) {
      setIsFirstTime(false)
      setShowHint(false)
    } else {
      setIsFirstTime(true)
      Taro.setStorageSync('has_seen_designer_avatar', '1')
    }
  }, [])
  
  // 处理触摸开始
  const handleTouchStart = (e: any) => {
    const touch = e.touches[0]
    startPosRef.current = {
      x: touch.clientX - position.x,
      y: touch.clientY - position.y
    }
    setDragging(true)
    setShowHint(false) // 开始拖拽时隐藏提示
  }
  
  // 处理触摸移动
  const handleTouchMove = (e: any) => {
    if (!dragging) return
    
    const touch = e.touches[0]
    const newX = touch.clientX - startPosRef.current.x
    const newY = touch.clientY - startPosRef.current.y
    
    // 限制在屏幕范围内
    const screenWidth = Taro.getSystemInfoSync().windowWidth
    const screenHeight = Taro.getSystemInfoSync().windowHeight
    const avatarSize = 60 // 头像大小
    
    const clampedX = Math.max(0, Math.min(newX, screenWidth - avatarSize))
    const clampedY = Math.max(0, Math.min(newY, screenHeight - avatarSize))
    
    setPosition({ x: clampedX, y: clampedY })
  }
  
  // 处理触摸结束
  const handleTouchEnd = () => {
    setDragging(false)
    // 保存位置到本地存储
    Taro.setStorageSync('designer_avatar_position', JSON.stringify(position))
  }
  
  // 点击头像打开对话框
  const handleAvatarClick = async () => {
    if (dragging) return // 如果是拖拽结束，不打开对话框
    
    setShowDialog(true)
    setShowHint(false) // 点击时隐藏提示
    
    // 如果没有session，创建一个新的
    if (!chatSessionId) {
      await createNewChatSession()
    }
  }
  
  // 创建新的聊天session
  const createNewChatSession = async () => {
    try {
      setIsCreatingSession(true)
      const response = await designerApi.createChatSession()
      setChatSessionId(response.session_id)
      setMessages(response.messages || [])
      
      // 如果没有初始消息，添加欢迎消息
      if (!response.messages || response.messages.length === 0) {
        const welcomeMessage: ChatMessage = {
          role: 'assistant',
          content: '您好！我是您的AI装修设计师，可以为您解答装修设计、风格选择、材料搭配、预算控制等问题。有什么可以帮您的吗？',
          timestamp: Date.now() / 1000
        }
        setMessages([welcomeMessage])
      }
    } catch (error: any) {
      console.error('创建聊天session失败:', error)
      Taro.showToast({ 
        title: error.message || '创建对话失败，请稍后重试', 
        icon: 'none' 
      })
      
      // 如果创建失败，显示默认欢迎消息
      const welcomeMessage: ChatMessage = {
        role: 'assistant',
        content: '您好！我是您的AI装修设计师，可以为您解答装修设计、风格选择、材料搭配、预算控制等问题。有什么可以帮您的吗？',
        timestamp: Date.now() / 1000
      }
      setMessages([welcomeMessage])
    } finally {
      setIsCreatingSession(false)
    }
  }
  
  // 关闭对话框
  const handleCloseDialog = () => {
    setShowDialog(false)
    setInputMessage('')
  }
  
  // 发送消息
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !chatSessionId) {
      Taro.showToast({ title: '请输入消息', icon: 'none' })
      return
    }
    
    const userMessage = inputMessage.trim()
    setInputMessage('')
    
    // 添加用户消息到界面
    const userMsg: ChatMessage = {
      role: 'user',
      content: userMessage,
      timestamp: Date.now() / 1000
    }
    setMessages(prev => [...prev, userMsg])
    
    setLoading(true)
    try {
      // 发送消息到服务器
      const response = await designerApi.sendChatMessage(chatSessionId, userMessage)
      
      // 添加AI回复到界面
      const aiMsg: ChatMessage = {
        role: 'assistant',
        content: response.answer,
        timestamp: Date.now() / 1000
      }
      setMessages(prev => [...prev, aiMsg])
      
      // 滚动到底部
      setTimeout(() => {
        if (scrollViewRef.current) {
          scrollViewRef.current.scrollToBottom()
        }
      }, 100)
      
    } catch (error: any) {
      console.error('发送消息失败:', error)
      Taro.showToast({ 
        title: error.message || '发送失败，请稍后重试', 
        icon: 'none' 
      })
      
      // 添加错误消息
      const errorMsg: ChatMessage = {
        role: 'assistant',
        content: '抱歉，我暂时无法回答您的问题，请稍后重试。',
        timestamp: Date.now() / 1000
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }
  
  // 快速问题示例
  const quickQuestions = [
    '现代简约风格的特点是什么？',
    '小户型如何设计显得空间更大？',
    '装修预算怎么分配比较合理？',
    '选择地板还是瓷砖比较好？',
    '厨房装修要注意哪些细节？'
  ]
  
  const handleQuickQuestion = (question: string) => {
    setInputMessage(question)
  }
  
  // 清空对话
  const handleClearChat = async () => {
    if (!chatSessionId) return
    
    try {
      await designerApi.clearChatHistory(chatSessionId)
      
      // 重置消息，只保留欢迎消息
      const welcomeMessage: ChatMessage = {
        role: 'assistant',
        content: '对话已清空！我是您的AI装修设计师，可以为您解答装修设计、风格选择、材料搭配、预算控制等问题。有什么可以帮您的吗？',
        timestamp: Date.now() / 1000
      }
      setMessages([welcomeMessage])
      
      Taro.showToast({ title: '对话已清空', icon: 'success' })
    } catch (error: any) {
      console.error('清空对话失败:', error)
      Taro.showToast({ 
        title: error.message || '清空失败', 
        icon: 'none' 
      })
    }
  }
  
  // 从本地存储加载位置
  useEffect(() => {
    try {
      const savedPos = Taro.getStorageSync('designer_avatar_position')
      if (savedPos) {
        const pos = JSON.parse(savedPos)
        setPosition(pos)
      }
    } catch (error) {
      console.error('加载悬浮头像位置失败:', error)
    }
  }, [])
  
  // 自动隐藏提示
  useEffect(() => {
    if (showHint) {
      const timer = setTimeout(() => {
        setShowHint(false)
      }, 5000) // 5秒后自动隐藏
      return () => clearTimeout(timer)
    }
  }, [showHint])
  
  // 滚动到底部
  useEffect(() => {
    if (messages.length > 0 && scrollViewRef.current) {
      setTimeout(() => {
        if (scrollViewRef.current) {
          scrollViewRef.current.scrollToBottom()
        }
      }, 100)
    }
  }, [messages])
  
  // 格式化时间
  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp * 1000)
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }
  
  return (
    <>
      {/* 悬浮头像 */}
      <View
        className={`floating-designer-avatar ${dragging ? 'dragging' : ''}`}
        style={{
          left: `${position.x}px`,
          top: `${position.y}px`,
          transform: dragging ? 'scale(1.1)' : 'scale(1)'
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onClick={handleAvatarClick}
        ref={avatarRef}
      >
        <View className="avatar-container">
          <Image
            className="avatar-image"
            src="https://img.alicdn.com/imgextra/i4/O1CN01Z5p5Lz1d0q7Q9X8Yj_!!6000000003675-2-tps-200-200.png"
            mode="aspectFill"
          />
          <View className="avatar-badge">AI</View>
        </View>
        
        {/* 拖拽提示 */}
        {showHint && isFirstTime && (
          <View className="drag-hint">
            <Text className="hint-text">拖拽移动位置</Text>
            <View className="hint-arrow">↓</View>
          </View>
        )}
      </View>
      
      {/* AI设计师聊天对话框 */}
      {showDialog && (
        <View className="designer-dialog-mask" onClick={handleCloseDialog}>
          <View className="designer-dialog" onClick={(e) => e.stopPropagation()}>
            <View className="dialog-header">
              <Text className="dialog-title">AI设计师聊天</Text>
              <View className="dialog-actions">
                <Button 
                  className="clear-btn" 
                  onClick={handleClearChat}
                  disabled={messages.length <= 1}
                >
                  清空
                </Button>
                <View className="dialog-close" onClick={handleCloseDialog}>×</View>
              </View>
            </View>
            
            <View className="dialog-content">
              {isCreatingSession ? (
                <View className="loading-container">
                  <Text>正在初始化对话...</Text>
                </View>
              ) : (
                <>
                  {/* 聊天消息区域 */}
                  <ScrollView 
                    className="chat-messages"
                    scrollY
                    ref={scrollViewRef}
                    scrollWithAnimation
                  >
                    {messages.map((msg, index) => (
                      <View 
                        key={index} 
                        className={`message-item ${msg.role === 'user' ? 'user-message' : 'ai-message'}`}
                      >
                        <View className="message-content">
                          <Text className="message-text">{msg.content}</Text>
                          <Text className="message-time">{formatTime(msg.timestamp)}</Text>
                        </View>
                      </View>
                    ))}
                    <View ref={messagesEndRef} />
                  </ScrollView>
                  
                  {/* 快速问题区域（只在没有消息或消息很少时显示） */}
                  {messages.length <= 2 && (
                    <View className="quick-questions">
                      <Text className="quick-title">快速提问：</Text>
                      <View className="quick-questions-grid">
                        {quickQuestions.map((q, index) => (
                          <View 
                            key={index} 
                            className="quick-question-item"
                            onClick={() => handleQuickQuestion(q)}
                          >
                            <Text className="quick-question-text">{q}</Text>
                          </View>
                        ))}
                      </View>
                    </View>
                  )}
                  
                  {/* 输入区域 */}
                  <View className="input-area">
                    <Input
                      className="message-input"
                      placeholder="输入您的问题..."
                      value={inputMessage}
                      onInput={(e) => setInputMessage(e.detail.value)}
                      focus={!inputMessage}
                      confirmType="send"
                      onConfirm={handleSendMessage}
                    />
                    <Button 
                      className="send-btn" 
                      onClick={handleSendMessage}
                      disabled={loading || !inputMessage.trim()}
                    >
                      {loading ? '思考中...' : '发送'}
                    </Button>
                  </View>
                </>
              )}
            </View>
            
            <View className="dialog-footer">
              <Text className="footer-text">AI设计师可解答装修风格、布局、材料、预算等问题</Text>
            </View>
          </View>
        </View>
      )}
    </>
  )
}

export default FloatingDesignerAvatar

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
  /** 是否为固定位置模式（非悬浮） */
  fixedMode?: boolean
  /** 固定位置模式的容器类名 */
  fixedContainerClassName?: string
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
  initialPosition = { x: 20, y: 200 },
  fixedMode = false,
  fixedContainerClassName = ''
}) => {
  const [position, setPosition] = useState(initialPosition)
  const [dragging, setDragging] = useState(false)
  const [showDialog, setShowDialog] = useState(false)
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [showHint, setShowHint] = useState(showDragHint)
  const [isFirstTime, setIsFirstTime] = useState(true)
  const [showStaticHint, setShowStaticHint] = useState(true) // 静态提示语"试试和AI设计师咨询"
  const [hasClicked, setHasClicked] = useState(false) // 记录是否点击过
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
    
    // 固定模式下，默认显示静态提示语
    if (fixedMode) {
      setShowStaticHint(true)
    }
  }, [fixedMode])
  
  // 处理触摸开始
  const handleTouchStart = (e: any) => {
    if (fixedMode) return // 固定模式下不可拖拽
    
    const touch = e.touches[0]
    startPosRef.current = {
      x: touch.clientX - position.x,
      y: touch.clientY - position.y
    }
    setDragging(true)
    setShowHint(false) // 开始拖拽时隐藏提示
    setShowStaticHint(false) // 隐藏静态提示语
  }
  
  // 处理触摸移动
  const handleTouchMove = (e: any) => {
    if (!dragging || fixedMode) return
    
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
  
  // 检查用户是否已登录
  const checkUserLogin = (): boolean => {
    const token = Taro.getStorageSync('token') || Taro.getStorageSync('access_token')
    return !!token
  }

  // 点击头像打开对话框
  const handleAvatarClick = async () => {
    if (dragging) return // 如果是拖拽结束，不打开对话框
    
    // 记录点击过
    setHasClicked(true)
    setShowStaticHint(false) // 点击后隐藏静态提示语
    
    // 如果是固定模式且第一次点击，显示拖拽提示
    if (fixedMode && !hasClicked) {
      setShowHint(true)
    }
    
    // 检查用户是否已登录
    if (!checkUserLogin()) {
      Taro.showModal({
        title: '请先登录',
        content: '使用AI设计师功能需要先登录账号',
        confirmText: '去登录',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            // 跳转到个人中心页（登录页）
            Taro.switchTab({ url: '/pages/profile/index' })
          }
        }
      })
      return
    }
    
    setShowDialog(true)
    setShowHint(false) // 点击时隐藏提示
    
    // 如果没有session，创建一个新的
    if (!chatSessionId) {
      await createNewChatSession()
    }
  }
  
  // 创建新的聊天session
  const createNewChatSession = async () => {
    // 再次检查登录状态
    if (!checkUserLogin()) {
      setShowDialog(false)
      Taro.showToast({ 
        title: '请先登录', 
        icon: 'none' 
      })
      return
    }

    try {
      setIsCreatingSession(true)
      const response = await designerApi.createChatSession()
      setChatSessionId(response.session_id)
      setMessages(response.messages || [])
      
      // 如果没有初始消息，添加欢迎消息
      if (!response.messages || response.messages.length === 0) {
        const welcomeMessage: ChatMessage = {
          role: 'assistant',
          content: '您好！我是您的AI装修设计师 - 漫游视频生成器！我可以根据您的户型图生成装修效果图和漫游视频。请上传您的户型图开始体验吧！',
          timestamp: Date.now() / 1000
        }
        setMessages([welcomeMessage])
      }
    } catch (error: any) {
      console.error('创建聊天session失败:', error)
      
      // 检查是否是401错误（多种可能的错误格式）
      const isUnauthorizedError = 
        error.statusCode === 401 ||
        error.code === 401 ||
        (error.response && error.response.status === 401) ||
        error.message?.includes('未授权') ||
        error.message?.includes('Unauthorized') ||
        error.message?.includes('登录') ||
        error.message?.includes('认证')
      
      // 如果是401错误，postWithAuth已经处理了（清除token并跳转），这里不需要重复处理
      // 只需要关闭对话框即可，不显示任何错误提示
      if (isUnauthorizedError) {
        console.log('401错误已由postWithAuth处理，关闭对话框，不显示错误提示')
        setShowDialog(false)
        return // 直接返回，不执行后面的代码
      }
      
      // 其他错误显示提示
      Taro.showToast({ 
        title: error.message || '创建对话失败，请稍后重试', 
        icon: 'none' 
      })
      
      // 如果创建失败，显示默认欢迎消息
      const welcomeMessage: ChatMessage = {
        role: 'assistant',
        content: '您好！我是您的AI装修设计师 - 漫游视频生成器！我可以根据您的户型图生成装修效果图和漫游视频。请上传您的户型图开始体验吧！',
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
    
    // 检查登录状态
    if (!checkUserLogin()) {
      Taro.showModal({
        title: '请先登录',
        content: '发送消息需要先登录账号',
        confirmText: '去登录',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            Taro.switchTab({ url: '/pages/profile/index' })
          }
        }
      })
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
        if (messagesEndRef.current) {
          // 使用scrollIntoView方法滚动到消息底部
          const element = messagesEndRef.current as any
          if (element && element.nodeType === 1) {
            element.scrollIntoView({ behavior: 'smooth', block: 'end' })
          }
        }
      }, 100)
      
    } catch (error: any) {
      console.error('发送消息失败:', error)
      
      // 如果是401错误，postWithAuth已经处理了（清除token并跳转），这里不需要重复处理
      if (error.statusCode === 401 || error.message?.includes('未授权') || error.message?.includes('登录')) {
        console.log('发送消息时401错误已由postWithAuth处理')
        // 不需要显示额外提示，postWithAuth已经处理了
      } else {
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
      }
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
  
  // 处理图片上传
  const handleUploadImage = async () => {
    // 检查登录状态
    if (!checkUserLogin()) {
      Taro.showModal({
        title: '请先登录',
        content: '上传图片需要先登录账号',
        confirmText: '去登录',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            Taro.switchTab({ url: '/pages/profile/index' })
          }
        }
      })
      return
    }
    
    try {
      // 选择图片
      const res = await Taro.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera']
      })
      
      if (res.tempFilePaths.length > 0) {
        const tempFilePath = res.tempFilePaths[0]
        const fileName = `designer_${Date.now()}.jpg`
        
        // 显示上传中提示
        Taro.showLoading({ title: '上传户型图中...' })
        
        try {
          // 调用图片上传API
          const uploadResult: any = await designerApi.uploadImage(tempFilePath, fileName)
          
          if (uploadResult.success && uploadResult.image_url) {
            Taro.hideLoading()
            Taro.showToast({ 
              title: '户型图上传成功！', 
              icon: 'success',
              duration: 2000
            })
            
            // 添加一条用户消息，显示已上传图片
            const imageMessage: ChatMessage = {
              role: 'user',
              content: `📸 已上传户型图，请帮我分析一下`,
              timestamp: Date.now() / 1000
            }
            setMessages(prev => [...prev, imageMessage])
            
            // 如果有聊天session，发送消息给AI设计师
            if (chatSessionId) {
              setLoading(true)
              try {
                // 发送包含图片URL的消息
                const response = await designerApi.sendChatMessage(
                  chatSessionId, 
                  '请帮我分析一下这个户型图，给出装修建议和效果图生成思路。',
                  [uploadResult.image_url]
                )
                
                // 添加AI回复
                const aiReply: ChatMessage = {
                  role: 'assistant',
                  content: response.answer,
                  timestamp: Date.now() / 1000
                }
                setMessages(prev => [...prev, aiReply])
              } catch (error: any) {
                console.error('发送图片消息失败:', error)
                // 添加默认AI回复
                const aiReply: ChatMessage = {
                  role: 'assistant',
                  content: '感谢上传户型图！我正在分析您的户型...\n\n户型图分析、效果图生成和漫游视频功能已上线，我可以为您提供专业的装修建议！',
                  timestamp: Date.now() / 1000
                }
                setMessages(prev => [...prev, aiReply])
              } finally {
                setLoading(false)
              }
            } else {
              // 如果没有session，创建新的session
              await createNewChatSession()
              
              // 添加默认AI回复
              const aiReply: ChatMessage = {
                role: 'assistant',
                content: '感谢上传户型图！我正在分析您的户型...\n\n户型图分析、效果图生成和漫游视频功能已上线，我可以为您提供专业的装修建议！',
                timestamp: Date.now() / 1000
              }
              setMessages(prev => [...prev, aiReply])
            }
          } else {
            Taro.hideLoading()
            Taro.showToast({ 
              title: uploadResult.error_message || '上传失败，请重试', 
              icon: 'none',
              duration: 3000
            })
          }
        } catch (uploadError: any) {
          Taro.hideLoading()
          console.error('上传图片失败:', uploadError)
          
          // 检查是否是401错误
          if (uploadError.statusCode === 401 || uploadError.message?.includes('未授权') || uploadError.message?.includes('登录')) {
            console.log('上传图片时401错误已处理')
            // postWithAuth已经处理了401错误，这里不需要重复处理
          } else {
            Taro.showToast({ 
              title: uploadError.message || '上传失败，请检查网络', 
              icon: 'none',
              duration: 3000
            })
          }
          
          // 即使上传失败，也添加一条消息，让用户知道功能已上线
          const imageMessage: ChatMessage = {
            role: 'user',
            content: `📸 尝试上传户型图（上传失败）`,
            timestamp: Date.now() / 1000
          }
          setMessages(prev => [...prev, imageMessage])
          
          // 添加AI回复
          const aiReply: ChatMessage = {
            role: 'assistant',
            content: '户型图上传功能已上线！下次请再试一下上传您的户型图，我可以为您提供专业的装修分析和效果图生成建议。',
            timestamp: Date.now() / 1000
          }
          setMessages(prev => [...prev, aiReply])
        }
      }
    } catch (error: any) {
      console.error('选择图片失败:', error)
      Taro.hideLoading()
      Taro.showToast({ 
        title: error.errMsg || '选择图片失败', 
        icon: 'none' 
      })
    }
  }
  
  const handleQuickQuestion = (question: string) => {
    setInputMessage(question)
  }
  
  // 清空对话
  const handleClearChat = async () => {
    if (!chatSessionId) return
    
    // 检查登录状态
    if (!checkUserLogin()) {
      Taro.showModal({
        title: '请先登录',
        content: '清空对话需要先登录账号',
        confirmText: '去登录',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            Taro.switchTab({ url: '/pages/profile/index' })
          }
        }
      })
      return
    }
    
    try {
      await designerApi.clearChatHistory(chatSessionId)
      
      // 重置消息，只保留欢迎消息
      const welcomeMessage: ChatMessage = {
        role: 'assistant',
        content: '对话已清空！我是您的AI装修设计师 - 漫游视频生成器！我可以根据您的户型图生成装修效果图和漫游视频。请上传您的户型图开始体验吧！',
        timestamp: Date.now() / 1000
      }
      setMessages([welcomeMessage])
      
      Taro.showToast({ title: '对话已清空', icon: 'success' })
    } catch (error: any) {
      console.error('清空对话失败:', error)
      
      // 如果是401错误，postWithAuth已经处理了（清除token并跳转），这里不需要重复处理
      if (error.statusCode === 401 || error.message?.includes('未授权') || error.message?.includes('登录')) {
        console.log('清空对话时401错误已由postWithAuth处理')
        // 不需要显示额外提示，postWithAuth已经处理了
      } else {
        Taro.showToast({ 
          title: error.message || '清空失败', 
          icon: 'none' 
        })
      }
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
    if (messages.length > 0 && messagesEndRef.current) {
      setTimeout(() => {
        if (messagesEndRef.current) {
          // 使用scrollIntoView方法滚动到消息底部
          const element = messagesEndRef.current as any
          if (element && element.nodeType === 1) {
            element.scrollIntoView({ behavior: 'smooth', block: 'end' })
          }
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
            src="https://zhuangxiu-images-dev.oss-cn-hangzhou.aliyuncs.com/avatar/avatar.png"
            mode="aspectFill"
          />
          <View className="avatar-badge">AI</View>
        </View>
        
        {/* 静态提示语 - 固定模式下显示 */}
        {showStaticHint && fixedMode && (
          <View className="static-hint">
            <Text className="static-hint-text">试试和AI设计师咨询</Text>
          </View>
        )}
        
        {/* 拖拽提示 */}
        {showHint && isFirstTime && (
          <View className="drag-hint">
            <Text className="hint-text">试试拖拽它到合适的位置</Text>
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
                  
                  {/* 户型图上传提示区域（只在没有消息或消息很少时显示） */}
                  {messages.length <= 2 && (
                    <View className="upload-hint-section">
                      <View className="upload-hint-card">
                        <Text className="upload-hint-icon">📸</Text>
                        <Text className="upload-hint-title">上传户型图，一键生成</Text>
                        <Text className="upload-hint-subtitle">装修效果图 + 漫游视频</Text>
                        <View className="upload-hint-btn" onClick={handleUploadImage}>
                          <Text className="upload-hint-btn-text">上传户型图</Text>
                        </View>
                        <Text className="upload-hint-tip">支持 JPG、PNG 格式，建议上传清晰户型图</Text>
                      </View>
                    </View>
                  )}
                  
                  {/* 快速问题区域（只在没有消息或消息很少时显示） */}
                  {messages.length <= 2 && (
                    <View className="quick-questions">
                      <Text className="quick-title">或者快速提问：</Text>
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
                    <View className="input-left">
                      <View className="upload-btn" onClick={handleUploadImage}>
                        <Text className="upload-btn-icon">📷</Text>
                      </View>
                      <Input
                        className="message-input"
                        placeholder="输入您的问题或上传户型图..."
                        value={inputMessage}
                        onInput={(e) => setInputMessage(e.detail.value)}
                        focus={!inputMessage}
                        confirmType="send"
                        onConfirm={handleSendMessage}
                      />
                    </View>
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
              <Text className="footer-text">AI装修设计师 - 漫游视频生成器 | 上传户型图生成效果图+视频</Text>
            </View>
          </View>
        </View>
      )}
    </>
  )
}

export default FloatingDesignerAvatar

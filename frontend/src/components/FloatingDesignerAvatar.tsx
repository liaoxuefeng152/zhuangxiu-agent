import React, { useState, useEffect, useRef } from 'react'
import { View, Text, Image, Input, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { designerApi } from '../services/api'
import './FloatingDesignerAvatar.scss'

interface FloatingDesignerAvatarProps {
  /** 是否显示拖拽提示 */
  showDragHint?: boolean
  /** 初始位置 */
  initialPosition?: { x: number; y: number }
}

/**
 * AI设计师悬浮头像组件
 * 功能：
 * 1. 可拖拽悬浮在页面任意位置
 * 2. 点击头像弹出AI设计师咨询对话框
 * 3. 支持输入问题并获取AI设计师回答
 * 4. 显示拖拽提示（首次显示）
 */
const FloatingDesignerAvatar: React.FC<FloatingDesignerAvatarProps> = ({
  showDragHint = true,
  initialPosition = { x: 20, y: 200 }
}) => {
  const [position, setPosition] = useState(initialPosition)
  const [dragging, setDragging] = useState(false)
  const [showDialog, setShowDialog] = useState(false)
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [answer, setAnswer] = useState('')
  const [showHint, setShowHint] = useState(showDragHint)
  const [isFirstTime, setIsFirstTime] = useState(true)
  
  const startPosRef = useRef({ x: 0, y: 0 })
  const avatarRef = useRef<HTMLDivElement>(null)
  
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
  const handleAvatarClick = () => {
    if (dragging) return // 如果是拖拽结束，不打开对话框
    setShowDialog(true)
    setShowHint(false) // 点击时隐藏提示
  }
  
  // 关闭对话框
  const handleCloseDialog = () => {
    setShowDialog(false)
    setQuestion('')
    setAnswer('')
  }
  
  // 提交问题
  const handleSubmit = async () => {
    if (!question.trim()) {
      Taro.showToast({ title: '请输入问题', icon: 'none' })
      return
    }
    
    setLoading(true)
    try {
      const response = await designerApi.consult(question.trim())
      setAnswer(response.answer || 'AI设计师暂时无法回答，请稍后重试')
    } catch (error: any) {
      console.error('AI设计师咨询失败:', error)
      Taro.showToast({ 
        title: error.message || '咨询失败，请稍后重试', 
        icon: 'none' 
      })
      setAnswer('抱歉，AI设计师暂时无法回答您的问题，请稍后重试。')
    } finally {
      setLoading(false)
    }
  }
  
  // 快速问题示例
  const quickQuestions = [
    '现代简约风格的特点是什么？',
    '小户型如何设计显得空间更大？',
    '装修预算怎么分配比较合理？',
    '选择地板还是瓷砖比较好？'
  ]
  
  const handleQuickQuestion = (q: string) => {
    setQuestion(q)
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
      
      {/* AI设计师咨询对话框 */}
      {showDialog && (
        <View className="designer-dialog-mask" onClick={handleCloseDialog}>
          <View className="designer-dialog" onClick={(e) => e.stopPropagation()}>
            <View className="dialog-header">
              <Text className="dialog-title">AI设计师咨询</Text>
              <View className="dialog-close" onClick={handleCloseDialog}>×</View>
            </View>
            
            <View className="dialog-content">
              {!answer ? (
                <>
                  <View className="quick-questions">
                    <Text className="quick-title">快速提问：</Text>
                    {quickQuestions.map((q, index) => (
                      <View 
                        key={index} 
                        className="quick-question-item"
                        onClick={() => handleQuickQuestion(q)}
                      >
                        <Text>{q}</Text>
                      </View>
                    ))}
                  </View>
                  
                  <Input
                    className="question-input"
                    placeholder="请输入您的装修设计问题..."
                    value={question}
                    onInput={(e) => setQuestion(e.detail.value)}
                    focus={!question}
                  />
                  
                  <Button 
                    className="submit-btn" 
                    onClick={handleSubmit}
                    disabled={loading || !question.trim()}
                  >
                    {loading ? '思考中...' : '咨询AI设计师'}
                  </Button>
                </>
              ) : (
                <View className="answer-container">
                  <Text className="answer-title">AI设计师回答：</Text>
                  <View className="answer-content">
                    <Text>{answer}</Text>
                  </View>
                  <Button 
                    className="new-question-btn"
                    onClick={() => {
                      setQuestion('')
                      setAnswer('')
                    }}
                  >
                    继续提问
                  </Button>
                </View>
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

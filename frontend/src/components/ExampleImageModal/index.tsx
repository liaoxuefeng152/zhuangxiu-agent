import React from 'react'
import { View, Text, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

interface ExampleImageModalProps {
  visible: boolean
  title: string
  content: string
  imageUrl?: string
  onClose: () => void
}

/**
 * 示例图弹窗 - 支持图片+文字，PRD D02/D05
 */
const ExampleImageModal: React.FC<ExampleImageModalProps> = ({
  visible,
  title,
  content,
  imageUrl,
  onClose
}) => {
  if (!visible) return null

  return (
    <View className='example-modal-mask' onClick={onClose}>
      <View className='example-modal' onClick={(e) => e.stopPropagation()}>
        <Text className='example-modal-title'>{title}</Text>
        {imageUrl ? (
          <Image src={imageUrl} className='example-img' mode='widthFix' showMenuByLongpress />
        ) : null}
        <Text className='example-modal-content'>{content}</Text>
        <Text className='example-modal-close' onClick={onClose}>我知道了</Text>
      </View>
    </View>
  )
}

export default ExampleImageModal

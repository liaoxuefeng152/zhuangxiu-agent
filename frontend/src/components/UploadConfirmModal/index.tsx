import React, { useState } from 'react'
import { View, Text } from '@tarojs/components'
import './index.scss'

/**
 * 上传前确认弹窗 - 未检测公司时展示，含「不再提示」勾选（PRD FR-007）
 */
interface Props {
  visible: boolean
  type: 'quote' | 'contract'
  onConfirm: (noMore: boolean) => void
  onGoScan: () => void
  onClose: () => void
}

const UploadConfirmModal: React.FC<Props> = ({ visible, type, onConfirm, onGoScan, onClose }) => {
  const [noMore, setNoMore] = useState(false)
  const content = type === 'quote' ? '建议先检测装修公司风险，再上传报价单' : '建议先检测装修公司风险，再上传合同'

  if (!visible) return null

  const handleConfirm = () => {
    onConfirm(noMore)
  }

  return (
    <View className='upload-confirm-mask' onClick={onClose}>
      <View className='upload-confirm-modal' onClick={(e) => e.stopPropagation()}>
        <Text className='close-btn' onClick={onClose}>×</Text>
        <Text className='modal-title'>温馨提示</Text>
        <Text className='modal-content'>{content}</Text>
        <View className='checkbox-row' onClick={() => setNoMore(!noMore)}>
          <Text className={`checkbox ${noMore ? 'checked' : ''}`}>{noMore ? '✓' : ''}</Text>
          <Text className='checkbox-label'>不再提示</Text>
        </View>
        <View className='modal-btns'>
          <View className='btn secondary' onClick={onGoScan}>
            <Text>去检测</Text>
          </View>
          <View className='btn primary' onClick={handleConfirm}>
            <Text>继续上传</Text>
          </View>
        </View>
      </View>
    </View>
  )
}

export default UploadConfirmModal

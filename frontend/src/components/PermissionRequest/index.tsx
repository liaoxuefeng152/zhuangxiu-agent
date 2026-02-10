import React from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

/**
 * P33 权限请求页 - 相机/文件/通知权限
 */
interface Props {
  visible: boolean
  type: 'camera' | 'album' | 'notification'
  onClose: () => void
}

const PERMISSION_INFO = {
  camera: { title: '相机权限', desc: '用于拍摄施工/验收照片，记录装修过程' },
  album: { title: '相册权限', desc: '用于选择已有照片上传' },
  notification: { title: '通知权限', desc: '用于接收施工进度提醒' }
}

const PermissionRequest: React.FC<Props> = ({ visible, type, onClose }) => {
  if (!visible) return null

  const info = PERMISSION_INFO[type] || PERMISSION_INFO.camera

  const handleOpenSetting = () => {
    Taro.openSetting()
    onClose()
  }

  return (
    <View className='permission-mask' onClick={onClose}>
      <View className='permission-modal' onClick={(e) => e.stopPropagation()}>
        <Text className='perm-title'>需要{info.title}</Text>
        <Text className='perm-desc'>{info.desc}，才能使用该功能</Text>
        <View className='perm-btns'>
          <View className='btn secondary' onClick={onClose}>
            <Text>暂不开启</Text>
          </View>
          <View className='btn primary' onClick={handleOpenSetting}>
            <Text>前往设置</Text>
          </View>
        </View>
      </View>
    </View>
  )
}

export default PermissionRequest

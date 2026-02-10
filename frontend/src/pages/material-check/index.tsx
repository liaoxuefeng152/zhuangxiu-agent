import React, { useState, useEffect } from 'react'
import { View, Text, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

const STORAGE_KEY_STATUS = 'construction_stage_status'
const CHECK_ITEMS = [
  '品牌型号与清单逐一对齐',
  '数量清点无误',
  '外观检查无破损',
  '合格证/质检报告核验'
]

/**
 * P37 材料进场人工核对页
 * 从 P09 带 stage=material&scene=check 进入，完成清单+照片核对后提交「核对通过」→ 回写 S00 状态并返回 P09
 * 从「查看台账/报告」进入无 scene 时展示核对记录（已核对则只读）
 */
const MaterialCheckPage: React.FC = () => {
  const router = Taro.getCurrentInstance().router
  const sceneParam = (router?.params?.scene as string) || ''
  const isCheckMode = sceneParam === 'check'

  const [photos, setPhotos] = useState<string[]>([])
  const [passed, setPassed] = useState(false)

  useEffect(() => {
    const raw = Taro.getStorageSync(STORAGE_KEY_STATUS)
    const status: Record<string, string> = raw ? JSON.parse(raw) : {}
    if (status.material === 'completed') setPassed(true)
  }, [])

  useEffect(() => {
    if (!isCheckMode) return
    Taro.showModal({
      title: '提示',
      content: '请按清单拍摄/上传材料照片完成人工核对',
      showCancel: false,
      confirmText: '知道了'
    }).catch(() => {})
  }, [isCheckMode])

  const choosePhoto = () => {
    Taro.chooseImage({
      count: 9 - photos.length,
      sourceType: ['camera', 'album'],
      success: (res) => {
        setPhotos((prev) => [...prev, ...res.tempFilePaths].slice(0, 9))
        Taro.showToast({ title: '已添加', icon: 'success' })
      },
      fail: (err) => {
        if (!err?.errMsg?.includes('cancel')) Taro.showToast({ title: '选择失败', icon: 'none' })
      }
    })
  }

  const handlePass = () => {
    const raw = Taro.getStorageSync(STORAGE_KEY_STATUS)
    const status: Record<string, string> = raw ? JSON.parse(raw) : {}
    status.material = 'completed'
    Taro.setStorageSync(STORAGE_KEY_STATUS, JSON.stringify(status))
    setPassed(true)
    Taro.showToast({ title: '核对通过，S01-S05 已解锁', icon: 'success', duration: 2000 })
    setTimeout(() => {
      Taro.navigateBack({ fail: () => Taro.switchTab({ url: '/pages/construction/index' }) })
    }, 1200)
  }

  const goBack = () => {
    Taro.navigateBack({ fail: () => Taro.switchTab({ url: '/pages/construction/index' }) })
  }

  if (passed && !isCheckMode) {
    return (
      <View className='material-check-page'>
        <View className='header'>
          <Text className='back' onClick={goBack}>返回</Text>
          <Text className='title'>材料进场核对记录</Text>
          <View className='placeholder' />
        </View>
        <View className='record-only'>
          <Text>您已完成材料进场人工核对</Text>
          <View className='btn-pass btn-back' onClick={goBack}>
            <Text>返回施工陪伴</Text>
          </View>
        </View>
      </View>
    )
  }

  return (
    <View className='material-check-page'>
      <View className='header'>
        <Text className='back' onClick={goBack}>返回</Text>
        <Text className='title'>材料进场人工核对</Text>
        <View className='placeholder' />
      </View>

      <View className='tips-card'>
        请按清单逐项核对材料品牌型号、数量、外观及合格证，并拍摄/上传照片留证。
      </View>

      <View className='checklist'>
        <Text className='section-title'>核对要点（P31 人工核对要点）</Text>
        {CHECK_ITEMS.map((item, i) => (
          <View key={i} className='item'><Text>· {item}</Text></View>
        ))}
      </View>

      <View className='upload-area'>
        <View className='upload-btn' onClick={choosePhoto}>
          <Text>📷 拍摄/上传材料照片</Text>
        </View>
        <Text className='hint'>最多 9 张，用于留证</Text>
        {photos.length > 0 && (
          <View className='photo-list'>
            {photos.map((url, i) => (
              <View key={i} className='photo-wrap'>
                <Image src={url} className='photo-img' mode='aspectFill' />
              </View>
            ))}
          </View>
        )}
      </View>

      <View className='btn-pass' onClick={handlePass}>
        <Text>核对通过</Text>
      </View>
    </View>
  )
}

export default MaterialCheckPage

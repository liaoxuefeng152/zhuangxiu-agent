import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import PermissionRequest from '../../components/PermissionRequest'
import { constructionPhotoApi } from '../../services/api'
import './index.scss'

const MAX_PHOTOS = 9

/** 场景：材料核对 / 阶段验收 / 复检 / 争议申诉 */
const SCENE_HINTS: Record<string, string> = {
  check: '材料核对拍摄：请拍摄材料清单+实物对比照',
  accept: '阶段验收拍摄：请拍摄施工部位全景+细节',
  recheck: '复检拍摄：请上传整改后照片',
  appeal: '争议申诉：请上传凭证照片（最多3张）'
}

const SCENE_TIPS: Record<string, string[]> = {
  check: ['材料与清单逐项对照拍摄', '品牌型号、数量清晰可见', '合格证/质检报告入镜'],
  accept: ['施工部位全景+关键节点特写', '线管、接口等细节清晰', '光线充足、避免反光'],
  recheck: ['整改前后对比更佳', '重点拍摄整改部位', '确保画面清晰'],
  appeal: ['凭证照片清晰可辨', '包含关键信息', '最多上传3张']
}

/**
 * P15 验收照片页 - 全场景验收照片拍摄统一入口，最多9张，开始检测跳 P04
 */
const PhotoPage: React.FC = () => {
  const router = Taro.getCurrentInstance().router
  const stageParam = (router?.params?.stage as string) || 'material'
  const sceneParam = (router?.params?.scene as string) || 'accept'

  const [selectedPhotos, setSelectedPhotos] = useState<string[]>([])
  const [guideVisible, setGuideVisible] = useState(true)
  const [detecting, setDetecting] = useState(false)
  const [showPermission, setShowPermission] = useState(false)

  const hasToken = !!Taro.getStorageSync('access_token')
  const sceneHint = SCENE_HINTS[sceneParam] || SCENE_HINTS.accept
  const tips = SCENE_TIPS[sceneParam] || SCENE_TIPS.accept
  const count = selectedPhotos.length
  const canStart = count >= 1 && !detecting

  const addPhotos = (paths: string[]) => {
    setSelectedPhotos((prev) => [...prev, ...paths].slice(0, MAX_PHOTOS))
  }

  const removePhoto = (index: number) => {
    setSelectedPhotos((prev) => prev.filter((_, i) => i !== index))
  }

  const handleShoot = () => {
    Taro.chooseImage({
      count: 1,
      sourceType: ['camera'],
      success: (res) => {
        const paths = res.tempFilePaths
        if (count + paths.length > MAX_PHOTOS) {
          Taro.showToast({ title: '最多选择9张照片，可删除后再添加', icon: 'none' })
          return
        }
        addPhotos(paths)
      },
      fail: (err) => {
        if (err?.errMsg?.includes('cancel')) return
        if (err?.errMsg?.includes('auth')) setShowPermission(true)
        else Taro.showToast({ title: '拍摄失败', icon: 'none' })
      }
    }).catch(() => {})
  }

  const handleAlbum = () => {
    const remain = MAX_PHOTOS - count
    if (remain <= 0) {
      Taro.showToast({ title: '最多选择9张照片，可删除后再添加', icon: 'none' })
      return
    }
    Taro.chooseImage({
      count: remain,
      sourceType: ['album'],
      sizeType: ['original', 'compressed'],
      success: (res) => {
        const paths = (res.tempFilePaths || []).slice(0, remain)
        addPhotos(paths)
      },
      fail: (err) => {
        if (err?.errMsg?.includes('cancel')) return
        if (err?.errMsg?.includes('auth')) setShowPermission(true)
        else Taro.showToast({ title: '选择失败', icon: 'none' })
      }
    }).catch(() => {})
  }

  const handleStartDetect = async () => {
    if (!canStart) return
    setDetecting(true)
    if (sceneParam === 'appeal') {
      Taro.showToast({ title: '申诉材料已提交，进入AI核验环节', icon: 'none', duration: 2000 })
      setTimeout(() => setDetecting(false), 500)
      return
    }
    if (hasToken) {
      try {
        for (const path of selectedPhotos) {
          await constructionPhotoApi.upload(path, stageParam)
        }
        Taro.setStorageSync('construction_stage_photo_' + stageParam, '1')
      } catch {
        Taro.showToast({ title: '上传失败，请重试', icon: 'none' })
        setDetecting(false)
        return
      }
    }
    Taro.navigateTo({ url: `/pages/scan-progress/index?type=acceptance&stage=${stageParam}` })
    setDetecting(false)
  }

  const handleAiCrop = (index: number) => {
    Taro.showToast({ title: 'AI裁剪功能开发中', icon: 'none' })
  }

  return (
    <View className='photo-accept-page'>
      {/* 相机预览区：80% 高，黑色背景，顶部场景提示 */}
      <View className='camera-area'>
        <Text className='scene-hint'>{sceneHint}</Text>
        <View className='camera-placeholder' />
      </View>

      {/* 拍摄指引浮层 */}
      {guideVisible && (
        <View className='guide-overlay'>
          <View className='guide-content'>
            {tips.map((t, i) => (
              <Text key={i} className='guide-tip'>{i + 1}. {t}</Text>
            ))}
            <Text className='guide-close' onClick={() => setGuideVisible(false)}>关闭指引</Text>
          </View>
        </View>
      )}

      {/* 已选照片预览栏 */}
      <View className='preview-bar'>
        <ScrollView scrollX className='preview-scroll' showScrollbar={false}>
          {count === 0 ? (
            <Text className='preview-empty'>暂无照片，拍摄/从相册选择</Text>
          ) : (
            selectedPhotos.map((url, i) => (
              <View key={i} className='preview-thumb-wrap'>
                <Image src={url} className='preview-thumb' mode='aspectFill' />
                <Text className='preview-del' onClick={() => removePhoto(i)}>×</Text>
                <Text className='preview-crop' onClick={() => handleAiCrop(i)}>AI裁剪</Text>
              </View>
            ))
          )}
        </ScrollView>
      </View>

      {/* 底部操作栏 */}
      <View className='bottom-bar'>
        <View className='bottom-album' onClick={handleAlbum}>
          <Text className='bottom-icon'>🖼</Text>
          <Text className='bottom-label'>相册</Text>
        </View>
        <View className='bottom-shoot' onClick={handleShoot}>
          <Text className='shoot-btn-inner' />
        </View>
        <View className='bottom-right'>
          <Text className='bottom-count'>已选{count}/{MAX_PHOTOS}张</Text>
          <View
            className={`bottom-detect ${canStart ? '' : 'disabled'}`}
            onClick={canStart ? handleStartDetect : undefined}
          >
            <Text>{detecting ? '检测中...' : '开始检测'}</Text>
          </View>
        </View>
      </View>

      <PermissionRequest
        visible={showPermission}
        type='camera'
        onClose={() => setShowPermission(false)}
      />
    </View>
  )
}

export default PhotoPage

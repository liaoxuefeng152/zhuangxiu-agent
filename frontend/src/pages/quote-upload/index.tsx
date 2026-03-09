import React, { useState } from 'react'
import { View, Text } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { quoteApi } from '../../services/api'
import ExampleImageModal from '../../components/ExampleImageModal'
import { EXAMPLE_IMAGES } from '../../config/assets'
import { checkLogin } from '../../utils/auth'
import './index.scss'

/**
 * P05 上传报价单页
 */
const QuoteUploadPage: React.FC = () => {
  const [file, setFile] = useState<{ path: string; name: string; size: number } | null>(null)
  const [showExample, setShowExample] = useState(false)

  const hasCompanyScan = Taro.getStorageSync('has_company_scan')

  const showUploadMenu = () => {
    Taro.showActionSheet({
      itemList: ['选择文件', '拍照上传'],
      success: (res) => {
        if (res.tapIndex === 0) chooseFile()
        else takePhoto()
      },
      fail: () => {} // 用户取消不视为错误
    })
  }

  const chooseFile = () => {
    Taro.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['pdf', 'jpg', 'jpeg', 'png'],
      success: (res) => {
        const f = res.tempFiles[0]
        if (f.size > 10 * 1024 * 1024) {
          Taro.showToast({ title: '文件不能超过10MB', icon: 'none' })
          return
        }
        setFile({ path: f.path, name: f.name, size: f.size })
      },
      fail: (err) => {
        if (!err?.errMsg?.includes('cancel')) Taro.showToast({ title: '选择失败', icon: 'none' })
      }
    })
  }

  const takePhoto = () => {
    const p = Taro.chooseImage({
      count: 1,
      sourceType: ['camera'],
      success: (res) => {
        const path = res.tempFilePaths[0]
        setFile({ path, name: `quote_${Date.now()}.jpg`, size: 0 })
      },
      fail: (err) => {
        if (!err?.errMsg?.includes('cancel')) Taro.showToast({ title: '选择失败', icon: 'none' })
      }
    })
    if (p && typeof (p as Promise<unknown>).catch === 'function') (p as Promise<unknown>).catch(() => {})
  }

  const handleUpload = async () => {
    if (!file) {
      Taro.showToast({ title: '请先选择或拍摄文件', icon: 'none' })
      return
    }
    
    // 检查登录状态
    if (!checkLogin()) {
      return
    }
    
    try {
      const userId = Taro.getStorageSync('user_id')
      const res = await quoteApi.upload(file.path, file.name) as any
      const quoteId = res?.task_id ?? res?.id ?? 0
      // 使用redirectTo替换当前页面，避免页面栈过深
      Taro.redirectTo({
        url: `/pages/scan-progress/index?scanId=${quoteId}&companyName=&type=quote`
      })
    } catch {
      // 使用redirectTo替换当前页面，避免页面栈过深
      Taro.redirectTo({
        url: `/pages/scan-progress/index?scanId=0&companyName=&type=quote`
      })
    }
  }

  const handleBack = () => {
    if (file) {
      Taro.showModal({
        title: '确认',
        content: '是否放弃上传？',
        success: (r) => {
          if (r.confirm) Taro.navigateBack()
        }
      })
    } else {
      Taro.navigateBack()
    }
  }

  return (
    <View className='upload-page'>
      {!hasCompanyScan && (
        <View className='warn-bar'>
          <Text className='warn-text'>⚠️ 未检测装修公司，分析结果可能存在偏差</Text>
          <Text className='link' onClick={() => Taro.navigateTo({ url: '/pages/company-scan/index' })}>立即检测</Text>
        </View>
      )}

      <View className='upload-area' onClick={showUploadMenu}>
        <Text className='upload-icon'>📄</Text>
        <Text className='upload-text'>点击上传PDF/JPG/PNG</Text>
        <Text className='upload-hint'>单文件≤10MB</Text>
        {file && <View className='progress-bar-wrap'><View className='progress-fill' style={{ width: '100%' }} /></View>}
        <Text className='example-link' onClick={(e) => { e.stopPropagation(); setShowExample(true); }}>示例查看</Text>
        {file && (
          <View className='file-info'>
            <Text>{file.name}</Text>
            <Text className='change' onClick={(e) => { e.stopPropagation(); setFile(null); }}>更换文件</Text>
          </View>
        )}
      </View>

      <Text className='bottom-hint'>请上传清晰的报价单原件，分析结果更精准</Text>

      <View className='btn primary full' onClick={handleUpload} style={{ opacity: file ? 1 : 0.5 }}>
        <Text>开始分析</Text>
      </View>

      <ExampleImageModal
        visible={showExample}
        title='报价单示例'
        content='请上传包含项目明细、单价、总价的报价单，格式清晰便于AI分析'
        imageUrl={EXAMPLE_IMAGES.quote}
        onClose={() => setShowExample(false)}
      />
      <Text className='privacy'>上传文件仅用于AI分析，本地加密存储，不会泄露</Text>
    </View>
  )
}

export default QuoteUploadPage

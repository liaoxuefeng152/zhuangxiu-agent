import React, { useState, useEffect, useRef } from 'react'
import { View, Text, Image, Textarea, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { materialChecksApi, constructionApi, acceptanceApi } from '../../services/api'
import { getBackendStageCode, getCompletionPayload, persistStageStatusToStorage } from '../../utils/constructionStage'
import './index.scss'

/** 从 API 错误中提取可展示的文案 */
function getErrorMessage(error: any): string {
  // 1. Error 对象 message（含 upload 等手动 reject 的）
  if (error?.message && typeof error.message === 'string' && error.message !== '请求失败') return error.message
  // 2. HTTP 响应体中的 detail/msg（含 { code: 401, msg: "请先登录" }）
  const data = error?.response?.data
  if (data) {
    const d = data.detail ?? data.msg ?? data.message
    if (typeof d === 'string' && d) return d
    if (Array.isArray(d) && d[0]?.msg) return d[0].msg
  }
  // 3. 微信/网络错误
  if (error?.errMsg) return String(error.errMsg)
  // 4. 无响应时的推断
  if (error?.request && !error?.response) return '网络连接失败，请检查网络或后端服务是否启动'
  return '提交失败，请稍后重试'
}

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
  const [submitting, setSubmitting] = useState(false)
  const [failMode, setFailMode] = useState(false)
  const [problemNote, setProblemNote] = useState('')
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true
    return () => { mountedRef.current = false }
  }, [])

  useEffect(() => {
    try {
      const raw = Taro.getStorageSync(STORAGE_KEY_STATUS)
      const status: Record<string, string> = raw ? JSON.parse(raw) : {}
      if (status?.material === 'completed') setPassed(true)
    } catch {
      // 忽略存储数据解析错误，避免白屏
    }
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

  /** 核对通过：必须至少1张照片留证，先上传再提交 */
  const handlePass = async () => {
    if (submitting) return
    if (photos.length < 1) {
      Taro.showToast({ title: '请先上传至少1张材料照片留证', icon: 'none' })
      return
    }
    const token = Taro.getStorageSync('access_token')
    const userId = Taro.getStorageSync('user_id')
    if (!token) {
      Taro.showToast({ title: '请先登录后再进行核对', icon: 'none' })
      return
    }
    const auth = {
      token,
      userId: (userId != null && userId !== '' && String(userId).trim() !== '') ? String(userId).trim() : ''
    }
    setSubmitting(true)
    const payloadStatus = getCompletionPayload('material')
    try {
      const uploadedUrls: string[] = []
      for (const path of photos) {
        const res = await acceptanceApi.uploadPhoto(path, auth) as any
        if (res?.file_url) uploadedUrls.push(res.file_url)
      }
      if (uploadedUrls.length < 1) {
        Taro.showToast({ title: '照片上传失败，请重试', icon: 'none' })
        setSubmitting(false)
        return
      }
      if (!Taro.getStorageSync('access_token')) {
        Taro.showModal({
          title: '登录已失效',
          content: '请前往「我的」页面重新登录后再试',
          showCancel: true,
          cancelText: '知道了',
          confirmText: '去登录',
          success: (r) => { if (r.confirm) Taro.switchTab({ url: '/pages/profile/index' }) }
        })
        setSubmitting(false)
        return
      }
      try {
        // 再次确认token存在（可能在照片上传过程中过期）
        const currentToken = Taro.getStorageSync('access_token')
        if (!currentToken) {
          throw new Error('登录已失效，请重新登录')
        }
        await materialChecksApi.submit({
          items: [{ material_name: '材料进场核对', photo_urls: uploadedUrls }],
          result: 'pass'
        })
      } catch (e: any) {
        if (e?.response?.status === 401 || e?.message?.includes('登录已失效')) {
          // 401错误：登录已失效，提示用户重新登录
          Taro.showModal({
            title: '登录已失效',
            content: '请前往「我的」页面重新登录后再试',
            showCancel: true,
            cancelText: '知道了',
            confirmText: '去登录',
            success: (r) => { if (r.confirm) Taro.switchTab({ url: '/pages/profile/index' }) }
          })
          setSubmitting(false)
          return
        } else if (e?.response?.status === 404) {
          // 降级方案：直接更新阶段状态
          await constructionApi.updateStageStatus(getBackendStageCode('material'), payloadStatus)
        } else {
          throw e
        }
      }
      persistStageStatusToStorage('material', payloadStatus)
      setPassed(true)
      Taro.showToast({ title: '核对通过，S01-S05 已解锁', icon: 'success', duration: 2000 })
      setTimeout(() => {
        try {
          if (!mountedRef.current) return
          Taro.navigateBack({ fail: () => Taro.switchTab({ url: '/pages/construction/index' }) })
        } catch (_) {}
      }, 1200)
    } catch (error: any) {
      const msg = getErrorMessage(error)
      if (msg.includes('登录') || msg.includes('请先登录')) {
        Taro.showModal({
          title: '登录已失效',
          content: '请前往「我的」页面重新登录后再试',
          showCancel: true,
          cancelText: '知道了',
          confirmText: '去登录',
          success: (r) => { if (r.confirm) Taro.switchTab({ url: '/pages/profile/index' }) }
        })
      } else {
        Taro.showToast({ title: msg, icon: 'none' })
      }
    } finally {
      setSubmitting(false)
    }
  }

  /** 核对未通过：需填写原因（≥10字） */
  const handleFail = async () => {
    if (submitting) return
    const note = problemNote.trim()
    if (note.length < 10) {
      Taro.showToast({ title: '请填写问题原因，至少10字', icon: 'none' })
      return
    }
    setSubmitting(true)
    try {
      try {
        await materialChecksApi.submit({
          items: [{ material_name: '材料进场核对', photo_urls: [] }],
          result: 'fail',
          problem_note: note
        })
      } catch (e: any) {
        if (e?.response?.status === 404) {
          await constructionApi.updateStageStatus(getBackendStageCode('material'), 'need_rectify')
        } else {
          throw e
        }
      }
      persistStageStatusToStorage('material', 'need_rectify')
      Taro.showToast({ title: '已提交，请通知施工方整改', icon: 'success' })
      setTimeout(() => {
        try {
          if (!mountedRef.current) return
          Taro.navigateBack({ fail: () => Taro.switchTab({ url: '/pages/construction/index' }) })
        } catch (_) {}
      }, 1200)
    } catch (error: any) {
      const msg = getErrorMessage(error)
      if (msg.includes('登录') || msg.includes('请先登录')) {
        Taro.showModal({
          title: '登录已失效',
          content: '请前往「我的」页面重新登录后再试',
          showCancel: true,
          cancelText: '知道了',
          confirmText: '去登录',
          success: (r) => { if (r.confirm) Taro.switchTab({ url: '/pages/profile/index' }) }
        })
      } else {
        Taro.showToast({ title: msg, icon: 'none' })
      }
    } finally {
      setSubmitting(false)
    }
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
        <ScrollView scrollY className='material-check-scroll'>
          <View className='record-only'>
            <Text>您已完成材料进场人工核对</Text>
            <View className='btn-pass btn-back' onClick={goBack}>
              <Text>返回施工陪伴</Text>
            </View>
          </View>
        </ScrollView>
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

      <ScrollView scrollY className='material-check-scroll'>
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
        <Text className='hint'>至少 1 张留证，最多 9 张</Text>
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

      {!failMode ? (
        <>
          <View className={`btn-pass ${submitting ? 'disabled' : ''}`} onClick={submitting ? undefined : handlePass}>
            <Text>{submitting ? '提交中...' : '核对通过'}</Text>
          </View>
          <View className='btn-fail-wrap' onClick={() => setFailMode(true)}>
            <Text className='btn-fail'>核对未通过，需整改</Text>
          </View>
        </>
      ) : (
        <>
          <View className='fail-note-area'>
            <Text className='fail-label'>请描述问题原因（至少10字，便于施工方整改）</Text>
            <Textarea
              className='fail-textarea'
              placeholder='如：品牌与清单不符、数量短缺、外观破损等'
              value={problemNote}
              onInput={(e) => setProblemNote((e as any).detail?.value ?? '')}
              maxlength={200}
            />
          </View>
          <View className='btn-row'>
            <View className='btn-cancel' onClick={() => setFailMode(false)}>
              <Text>返回</Text>
            </View>
            <View className={`btn-pass ${submitting ? 'disabled' : ''}`} onClick={submitting ? undefined : handleFail}>
              <Text>{submitting ? '提交中...' : '提交'}</Text>
            </View>
          </View>
        </>
      )}
      </ScrollView>
    </View>
  )
}

export default MaterialCheckPage

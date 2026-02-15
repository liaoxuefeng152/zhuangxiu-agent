import React, { useState, useEffect, useRef } from 'react'
import { View, Text, Image, Textarea, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { postWithAuth, putWithAuth, acceptanceApi, materialChecksApi } from '../../services/api'
import { getBackendStageCode, getCompletionPayload, persistStageStatusToStorage } from '../../utils/constructionStage'
import './index.scss'

/** 从 API 错误中提取可展示的文案 */
function getErrorMessage(error: any): string {
  if (error?.message && typeof error.message === 'string' && error.message !== '请求失败') return error.message
  const data = error?.response?.data
  if (data) {
    const d = data.detail ?? data.msg ?? data.message
    if (typeof d === 'string' && d) return d
    if (Array.isArray(d) && d[0]?.msg) return d[0].msg
  }
  if (error?.errMsg) return String(error.errMsg)
  if (error?.request && !error?.response) return '网络连接失败，请检查网络或后端服务是否启动'
  return '提交失败，请稍后重试'
}

const STORAGE_KEY_STATUS = 'construction_stage_status'

interface MaterialItem {
  material_name: string
  spec_brand?: string
  quantity?: string
  category?: string
  checked: boolean
  photoUrls: string[]
}

/**
 * P37 材料进场人工核对页
 * 从 P09 带 stage=material&scene=check 进入
 * 材料清单来自报价单/合同，逐项勾选+拍照留证，关键材料需全部勾选且至少1张照片才能核对通过
 */
const MaterialCheckPage: React.FC = () => {
  const router = Taro.getCurrentInstance().router
  const sceneParam = (router?.params?.scene as string) || ''
  const isCheckMode = sceneParam === 'check'

  const [materialItems, setMaterialItems] = useState<MaterialItem[]>([])
  const [listLoading, setListLoading] = useState(true)
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
      // ignore
    }
  }, [])

  // 加载材料清单（从报价单/合同同步）
  useEffect(() => {
    if (!isCheckMode) {
      setListLoading(false)
      return
    }
    setListLoading(true)
    materialChecksApi.getMaterialList()
      .then((r: any) => {
        if (!mountedRef.current) return
        const list = r?.data?.list ?? r?.list ?? []
        if (Array.isArray(list) && list.length > 0) {
          setMaterialItems(list.map((m: any) => ({
            material_name: m.material_name || m.name || '未命名',
            spec_brand: m.spec_brand || '',
            quantity: m.quantity || '',
            category: m.category || '关键材料',
            checked: false,
            photoUrls: []
          })))
        } else {
          setMaterialItems([])
        }
      })
      .catch(() => {
        if (mountedRef.current) setMaterialItems([])
      })
      .finally(() => {
        if (mountedRef.current) setListLoading(false)
      })
  }, [isCheckMode])

  const toggleCheck = (index: number) => {
    setMaterialItems(prev => prev.map((item, i) =>
      i === index ? { ...item, checked: !item.checked } : item
    ))
  }

  const addPhotoForItem = (index: number) => {
    Taro.chooseImage({
      count: 3 - (materialItems[index]?.photoUrls?.length || 0),
      sourceType: ['camera', 'album'],
        success: async (res) => {
        const token = Taro.getStorageSync('access_token')
        const userId = Taro.getStorageSync('user_id')
        if (!token) {
          Taro.showToast({ title: '请先登录', icon: 'none' })
          return
        }
        const auth = { token, userId: userId != null && userId !== '' ? String(userId).trim() : '' }
        const uploaded: string[] = []
        for (const path of res.tempFilePaths) {
          try {
            const r = await acceptanceApi.uploadPhoto(path, auth) as any
            const url = typeof r?.file_url === 'string' ? r.file_url : null
            if (url) uploaded.push(url)
          } catch (_) {}
        }
        if (uploaded.length > 0) {
          setMaterialItems(prev => prev.map((item, i) =>
            i === index ? { ...item, photoUrls: [...(item.photoUrls || []), ...uploaded].slice(0, 3) } : item
          ))
          Taro.showToast({ title: '已添加', icon: 'success' })
        } else {
          Taro.showToast({ title: '上传失败，请重试', icon: 'none' })
        }
      },
      fail: (err) => {
        if (!err?.errMsg?.includes('cancel')) Taro.showToast({ title: '选择失败', icon: 'none' })
      }
    })
  }

  const removePhoto = (itemIndex: number, photoIndex: number) => {
    setMaterialItems(prev => prev.map((item, i) => {
      if (i !== itemIndex) return item
      const urls = [...(item.photoUrls || [])]
      urls.splice(photoIndex, 1)
      return { ...item, photoUrls: urls }
    }))
  }

  const canPass = (): { ok: boolean; msg?: string } => {
    if (materialItems.length === 0) return { ok: false, msg: '暂无材料清单' }
    const keyItems = materialItems.filter(m => (m.category || '').includes('关键') || !m.category)
    const allItems = keyItems.length > 0 ? keyItems : materialItems
    for (const m of allItems) {
      if (!m.checked) {
        return { ok: false, msg: `请勾选完成「${m.material_name}」的核对` }
      }
      if (!m.photoUrls?.length) {
        return { ok: false, msg: `「${m.material_name}」需至少上传1张照片留证` }
      }
    }
    return { ok: true }
  }

  const handlePass = async () => {
    if (submitting) return
    const { ok, msg } = canPass()
    if (!ok) {
      Taro.showToast({ title: msg || '请完成清单核对并拍照', icon: 'none' })
      return
    }
    const token = Taro.getStorageSync('access_token')
    if (!token) {
      Taro.showToast({ title: '请先登录后再进行核对', icon: 'none' })
      return
    }
    const itemsToSubmit = materialItems
      .filter(m => m.checked && m.photoUrls?.length >= 1)
      .map(m => ({
        material_name: m.material_name,
        spec_brand: m.spec_brand,
        quantity: m.quantity,
        photo_urls: m.photoUrls
      }))
    if (itemsToSubmit.length === 0) {
      Taro.showToast({ title: '请勾选并拍照至少一项材料', icon: 'none' })
      return
    }
    setSubmitting(true)
    const payloadStatus = getCompletionPayload('material')
    try {
      try {
        await materialChecksApi.submit({ items: itemsToSubmit, result: 'pass' })
      } catch (e: any) {
        if (e?.response?.status === 404) {
          await putWithAuth('/constructions/stage-status', { stage: getBackendStageCode('material'), status: payloadStatus })
        } else {
          throw e
        }
      }
      persistStageStatusToStorage('material', payloadStatus)
      setPassed(true)
      Taro.showToast({ title: '核对通过，S01-S05 已解锁', icon: 'success', duration: 2000 })
      setTimeout(() => {
        if (!mountedRef.current) return
        Taro.navigateBack({ fail: () => Taro.switchTab({ url: '/pages/construction/index' }) })
      }, 1200)
    } catch (error: any) {
      const errMsg = getErrorMessage(error)
      if (errMsg.includes('登录')) {
        Taro.showModal({
          title: '登录已失效',
          content: '请前往「我的」页面重新登录后再试',
          showCancel: true,
          cancelText: '知道了',
          confirmText: '去登录',
          success: (r) => { if (r.confirm) Taro.switchTab({ url: '/pages/profile/index' }) }
        })
      } else {
        Taro.showToast({ title: errMsg, icon: 'none' })
      }
    } finally {
      setSubmitting(false)
    }
  }

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
          items: materialItems.length > 0
            ? materialItems.map(m => ({ material_name: m.material_name, spec_brand: m.spec_brand, quantity: m.quantity, photo_urls: [] }))
            : [{ material_name: '材料进场核对', photo_urls: [] }],
          result: 'fail',
          problem_note: note
        })
      } catch (e: any) {
        if (e?.response?.status === 404) {
          await putWithAuth('/constructions/stage-status', { stage: getBackendStageCode('material'), status: 'need_rectify' })
        } else {
          throw e
        }
      }
      persistStageStatusToStorage('material', 'need_rectify')
      Taro.showToast({ title: '已提交，请通知施工方整改', icon: 'success' })
      setTimeout(() => {
        if (!mountedRef.current) return
        Taro.navigateBack({ fail: () => Taro.switchTab({ url: '/pages/construction/index' }) })
      }, 1200)
    } catch (error: any) {
      Taro.showToast({ title: getErrorMessage(error), icon: 'none' })
    } finally {
      setSubmitting(false)
    }
  }

  const goBack = () => {
    Taro.navigateBack({ fail: () => Taro.switchTab({ url: '/pages/construction/index' }) })
  }

  const goUploadQuote = () => {
    Taro.navigateTo({ url: '/pages/quote-upload/index' })
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

  // 清单为空：提示先上传报价单
  if (isCheckMode && !listLoading && materialItems.length === 0) {
    return (
      <View className='material-check-page'>
        <View className='header'>
          <Text className='back' onClick={goBack}>返回</Text>
          <Text className='title'>材料进场人工核对</Text>
          <View className='placeholder' />
        </View>
        <ScrollView scrollY className='material-check-scroll'>
          <View className='empty-list-card'>
            <Text className='empty-title'>未同步到材料清单</Text>
            <Text className='empty-desc'>请先上传报价单或合同，系统将自动提取材料清单供您逐项核对</Text>
            <View className='btn-upload' onClick={goUploadQuote}>
              <Text>去上传报价单</Text>
            </View>
            <View className='btn-secondary' onClick={goBack}>
              <Text>返回</Text>
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
        {listLoading ? (
          <View className='loading-wrap'><Text>加载材料清单中…</Text></View>
        ) : (
          <>
            <View className='tips-card'>
              请按清单逐项勾选确认，并为每项材料拍摄照片留证（关键材料必填）。
            </View>

            <View className='material-list'>
              <Text className='section-title'>材料清单</Text>
              {materialItems.map((item, i) => (
                <View key={i} className='material-item'>
                  <View className='material-header' onClick={() => toggleCheck(i)}>
                    <View className={`checkbox ${item.checked ? 'checked' : ''}`}>
                      {item.checked && <Text className='checkbox-icon'>✓</Text>}
                    </View>
                    <View className='material-info'>
                      <Text className='material-name'>{item.material_name}</Text>
                      {(item.spec_brand || item.quantity) && (
                        <Text className='material-spec'>
                          {[item.spec_brand, item.quantity].filter(Boolean).join(' · ')}
                        </Text>
                      )}
                      {item.category && <Text className='material-cat'>{item.category}</Text>}
                    </View>
                  </View>
                  <View className='material-photos'>
                    <View className='photo-add' onClick={() => addPhotoForItem(i)}>
                      <Text>📷 拍照留证</Text>
                      {(!item.photoUrls || item.photoUrls.length === 0) && (
                        <Text className='photo-hint'>待上传</Text>
                      )}
                    </View>
                    {item.photoUrls?.map((url, j) => (
                      <View key={j} className='photo-thumb'>
                        <Image src={typeof url === 'string' ? url : ''} mode='aspectFill' className='photo-img' />
                        <View className='photo-del' onClick={() => removePhoto(i, j)}>×</View>
                      </View>
                    ))}
                  </View>
                </View>
              ))}
            </View>

            {!failMode ? (
              <>
                <View
                  className={`btn-pass ${submitting || !canPass().ok ? 'disabled' : ''}`}
                  onClick={submitting || !canPass().ok ? undefined : handlePass}
                >
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
          </>
        )}
      </ScrollView>
    </View>
  )
}

export default MaterialCheckPage

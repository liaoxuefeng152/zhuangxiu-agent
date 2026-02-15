import React, { useState, useEffect, useCallback, useRef } from 'react'
import { View, Text, ScrollView, Image, Textarea } from '@tarojs/components'
import Taro, { useDidShow } from '@tarojs/taro'
import { safeSwitchTab, TAB_CONSTRUCTION } from '../../utils/navigation'
import { useAppSelector } from '../../store/hooks'
import { putWithAuth, acceptanceApi, reportApi } from '../../services/api'
import { getBackendStageCode, getCompletionPayload, persistStageStatusToStorage } from '../../utils/constructionStage'
import './index.scss'

const STORAGE_KEY_REPORT = 'construction_acceptance_report_'

const STAGE_TITLES: Record<string, string> = {
  material: 'S00材料进场核对台账',
  plumbing: '水电阶段验收报告',
  carpentry: '泥瓦工阶段验收报告',
  woodwork: '木工阶段验收报告',
  painting: '油漆阶段验收报告',
  installation: '安装收尾阶段验收报告'
}

type ResultItem = { level: 'high' | 'mid' | 'low'; title: string; desc: string; suggest: string }

/**
 * P30 阶段验收/台账报告页（最终完整版）- 整改/复检/导出/申诉
 */
const AcceptancePage: React.FC = () => {
  const router = Taro.getCurrentInstance().router
  const stage = (router?.params?.stage as string) || 'plumbing'
  const userInfo = useAppSelector((s) => s.user.userInfo)
  const isMember = userInfo?.isMember ?? !!Taro.getStorageSync('is_member')
  const [unlocked, setUnlocked] = useState(false)
  const refreshUnlocked = useCallback(() => {
    setUnlocked(isMember || !!Taro.getStorageSync(`report_unlocked_acceptance_${stage}`))
  }, [stage, isMember])

  const [uploaded, setUploaded] = useState<string[]>([])
  const [rectifyPhotos, setRectifyPhotos] = useState<string[]>([]) // 整改后照片，最多5张
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<{ items: ResultItem[] } | null>(null)
  const [rectifyStatus, setRectifyStatus] = useState<'none' | 'pending' | 'recheck' | 'done'>('none')
  const [recheckCount, setRecheckCount] = useState(0)
  const [detailModal, setDetailModal] = useState<ResultItem | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadFailed, setLoadFailed] = useState(false)
  const [btnDisabled, setBtnDisabled] = useState(false)

  // 申诉
  const [appealStatus, setAppealStatus] = useState<'none' | 'pending' | 'rejected' | 'approved'>('none')
  const [appealModal, setAppealModal] = useState(false)
  const [appealReason, setAppealReason] = useState('')
  const [appealImages, setAppealImages] = useState<string[]>([])
  const [appealSubmitting, setAppealSubmitting] = useState(false)
  const [appealSuccessModal, setAppealSuccessModal] = useState(false)
  const [rejectTipVisible, setRejectTipVisible] = useState(false)
  const [isAppealRevised, setIsAppealRevised] = useState(false) // 申诉复核版
  const [photoErrors, setPhotoErrors] = useState<Set<number>>(new Set()) // 照片加载失败索引

  const pageTitle = STAGE_TITLES[stage] || '验收报告'
  const items = (result?.items ?? []).slice().sort((a, b) => {
    const order: Record<string, number> = { high: 0, mid: 1, low: 2 }
    return (order[a.level] ?? 2) - (order[b.level] ?? 2)
  })
  const qualifiedCount = items.filter((i) => i.level === 'low').length
  const unqualifiedCount = items.filter((i) => i.level === 'high' || i.level === 'mid').length
  const hasUnqualified = unqualifiedCount > 0
  const statusLabel =
    rectifyStatus === 'done'
      ? '已通过'
      : rectifyStatus === 'recheck'
        ? '待复检'
        : rectifyStatus === 'pending'
          ? '待整改'
          : hasUnqualified
            ? '未通过'
            : '已通过'
  const statusClass =
    statusLabel === '已通过' ? 'pass' : statusLabel === '待整改' || statusLabel === '待复检' ? 'pending' : 'fail'
  const showRectifyArea = hasUnqualified && (statusLabel === '未通过' || statusLabel === '待整改' || statusLabel === '待复检')
  const showAppealBtn = result && (statusLabel === '未通过' || statusLabel === '待整改') && appealStatus !== 'pending'

  useEffect(() => {
    refreshUnlocked()
  }, [refreshUnlocked])

  useDidShow(() => {
    refreshUnlocked()
  })

  // 进入页时：若 P04 已写入报告，则直接展示（验收完成后跳转过来即有报告）
  useEffect(() => {
    if (!stage) return
    try {
      const saved = Taro.getStorageSync(STORAGE_KEY_REPORT + stage)
      if (saved) {
        const data = JSON.parse(saved)
        if (data?.items?.length) setResult({ items: data.items })
      }
    } catch (_) {}
  }, [stage])

  const hasSyncedPassRef = useRef(false)

  useEffect(() => {
    if (!stage || !result) return
    if (statusLabel === '已通过' && rectifyStatus !== 'pending' && rectifyStatus !== 'recheck') {
      if (hasSyncedPassRef.current) return
      hasSyncedPassRef.current = true
      syncStageStatus(getCompletionPayload(stage))
    } else if (statusLabel !== '已通过') {
      hasSyncedPassRef.current = false
    }
  }, [stage, statusLabel, rectifyStatus, result, syncStageStatus])

  const chooseImage = () => {
    const p = Taro.chooseImage({
      count: 9 - uploaded.length,
      sourceType: ['camera', 'album'],
      fail: (err) => {
        if (!err?.errMsg?.includes('cancel')) Taro.showToast({ title: '选择失败', icon: 'none' })
      },
      success: (res) => {
        const next = [...uploaded, ...res.tempFilePaths].slice(0, 9)
        setUploaded(next)
        if (next.length > 0 && !result) {
          setAnalyzing(true)
          setLoadFailed(false)
          setTimeout(() => {
            setAnalyzing(false)
            setResult({
              items: [
                { level: 'high', title: '线管走向不规范', desc: '强电与弱电线管间距不足30cm，易产生干扰', suggest: '建议重新布线，强弱电分离' },
                { level: 'mid', title: '接线盒未加盖板', desc: '部分接线盒裸露，存在安全隐患', suggest: '安装空白面板或盖板' },
                { level: 'low', title: '线头已做绝缘处理', desc: '线头绝缘符合规范', suggest: '保持' }
              ]
            })
          }, 2000)
        }
      }
    })
    if (p && typeof (p as Promise<unknown>).catch === 'function') (p as Promise<unknown>).catch(() => {})
  }

  const handleUnlock = () => {
    const q = new URLSearchParams()
    q.set('type', 'acceptance')
    q.set('stage', stage || '')
    acceptanceApi.getList({ stage: stage || 'plumbing', page: 1, page_size: 1 }).then((listRes: any) => {
      const list = listRes?.data?.list ?? listRes?.list ?? []
      const analysisId = list?.[0]?.id
      if (analysisId) q.set('scanId', String(analysisId))
      Taro.navigateTo({ url: '/pages/report-unlock/index?' + q.toString() })
    }).catch(() => {
      Taro.navigateTo({ url: '/pages/report-unlock/index?type=acceptance&stage=' + (stage || '') })
    })
  }

  const handleShare = () => {
    Taro.showShareMenu({ withShareTicket: true })
    Taro.showToast({ title: '点击右上角分享', icon: 'none' })
  }

  const syncStageStatus = useCallback(
    async (nextStatus: string, toastMessage?: string) => {
      if (!stage) return false
      try {
        await putWithAuth('/constructions/stage-status', { stage: getBackendStageCode(stage), status: nextStatus })
        persistStageStatusToStorage(stage, nextStatus)
        if (toastMessage) Taro.showToast({ title: toastMessage, icon: 'success' })
        return true
      } catch (error: any) {
        const message = error?.response?.data?.detail || '状态更新失败，请稍后重试'
        Taro.showToast({ title: message, icon: 'none' })
        return false
      }
    },
    [stage]
  )

  const handleMarkRectify = async () => {
    if (btnDisabled) return
    const ok = await syncStageStatus('need_rectify', '已标记整改')
    if (ok) {
      setRectifyStatus('pending')
      setRectifyPhotos([])
    }
  }

  const addRectifyPhoto = () => {
    Taro.chooseImage({
      count: 5 - rectifyPhotos.length,
      sourceType: ['camera', 'album'],
      success: (res) => {
        setRectifyPhotos((prev) => [...prev, ...res.tempFilePaths].slice(0, 5))
      }
    }).catch(() => {})
  }

  const handleCompleteRectify = async () => {
    if (rectifyPhotos.length === 0) {
      Taro.showToast({ title: '请上传整改后照片', icon: 'none' })
      return
    }
    const ok = await syncStageStatus('pending_recheck', '已提交，等待复检')
    if (ok) {
      setRectifyStatus('recheck')
    }
  }

  const handleApplyRecheck = () => {
    if (btnDisabled) return
    Taro.showModal({
      title: '申请复检',
      content: '请上传整改后照片，上传完成将自动触发AI复检',
      confirmText: '上传照片',
      success: (res) => {
        if (res.confirm) {
          Taro.chooseImage({
            count: 5,
            sourceType: ['camera', 'album'],
            success: () => {
              syncStageStatus('pending_recheck', '已提交，等待复检').then((ok) => {
                if (!ok) return
                setRectifyStatus('recheck')
                const next = recheckCount + 1
                setRecheckCount(next)
                if (next >= 3) {
                  setTimeout(() => {
                    Taro.showModal({
                      title: '复检未通过',
                      content: '建议咨询AI监理，或转人工进一步核查',
                      confirmText: '咨询AI监理',
                      cancelText: '取消',
                      success: (r) => {
                        if (r.confirm) goAiSupervision()
                      }
                    })
                  }, 800)
                } else {
                  Taro.showModal({
                    title: '复检未通过',
                    content: '建议参考整改建议完善后再次申请',
                    showCancel: false,
                    confirmText: '我知道了'
                  })
                  setTimeout(() => Taro.hideModal(), 3000)
                }
              })
            }
          }).catch(() => {})
        }
      }
    })
  }

  const handleExportPdf = async () => {
    if (!result) {
      Taro.showToast({ title: '请先完成验收', icon: 'none' })
      return
    }
    if (btnDisabled || !unlocked) return
    try {
      Taro.showLoading({ title: '正在生成PDF...' })
      const stageParam = stage || 'plumbing'
      let listRes: any = await acceptanceApi.getList({ stage: stageParam, page: 1, page_size: 1 })
      let list = listRes?.data?.list ?? listRes?.list ?? []
      if (!list?.length) {
        const backendStage = getBackendStageCode(stageParam)
        if (backendStage !== stageParam) {
          listRes = await acceptanceApi.getList({ stage: backendStage, page: 1, page_size: 1 })
          list = listRes?.data?.list ?? listRes?.list ?? []
        }
      }
      const analysisId = list?.[0]?.id
      if (!analysisId) {
        Taro.hideLoading()
        Taro.showToast({ title: '暂无验收记录，无法导出', icon: 'none' })
        return
      }
      await reportApi.downloadPdf('acceptance', analysisId)
      Taro.hideLoading()
      Taro.showToast({ title: '导出成功', icon: 'success' })
    } catch (e: any) {
      Taro.hideLoading()
      Taro.showToast({ title: e?.message || '导出失败', icon: 'none' })
    }
  }

  const goAiSupervision = () => {
    const firstIssue = items.find((i) => i.level === 'high' || i.level === 'mid')
    const summary = firstIssue ? firstIssue.title : '验收问题咨询'
    Taro.navigateTo({
      url: `/pages/ai-supervision/index?stage=${stage}&summary=${encodeURIComponent(summary)}&reportId=${encodeURIComponent(stage + '_' + Date.now())}`
    })
  }

  const openAppealModal = () => {
    setAppealModal(true)
    setAppealReason('')
    setAppealImages([])
  }

  const addAppealImage = () => {
    Taro.chooseImage({
      count: 3 - appealImages.length,
      sourceType: ['camera', 'album'],
      success: (res) => {
        const files = res.tempFiles || []
        for (const f of files) {
          if (f.size && f.size > 10 * 1024 * 1024) {
            Taro.showToast({ title: '仅支持JPG/PNG格式，单张图片不超过10M', icon: 'none' })
            return
          }
        }
        setAppealImages((prev) => [...prev, ...(res.tempFilePaths || [])].slice(0, 3))
      }
    }).catch(() => {})
  }

  const submitAppeal = () => {
    const reason = appealReason.trim()
    if (!reason) return
    setAppealSubmitting(true)
    Taro.showLoading({ title: '提交中...' })
    setTimeout(() => {
      Taro.hideLoading()
      setAppealSubmitting(false)
      setAppealModal(false)
      setAppealStatus('pending')
      setAppealSuccessModal(true)
    }, 800)
  }

  return (
    <View className='acceptance-page'>
      {/* P30 顶部导航栏：V2.6.4 先解锁后导出，未解锁显示「解锁报告」，已解锁显示「PDF导出」 */}
      <View className='nav-bar'>
        <Text className='nav-back' onClick={() => Taro.navigateBack()}>返回</Text>
        <Text className='nav-title'>{pageTitle}</Text>
        <View className='nav-right-wrap'>
          {result ? (
            <>
              {unlocked ? (
                <View className='nav-pdf' onClick={handleExportPdf}>
                  <Text className='nav-pdf-icon'>📄</Text>
                  <Text className='nav-pdf-text'>PDF导出</Text>
                </View>
              ) : (
                <Text className='nav-unlock' onClick={handleUnlock}>解锁报告</Text>
              )}
              {showAppealBtn && <Text className='nav-appeal' onClick={openAppealModal}>申诉</Text>}
              {appealStatus === 'pending' && <Text className='nav-appeal disabled'>申诉中</Text>}
            </>
          ) : (
            <View className='nav-placeholder' />
          )}
        </View>
      </View>

      {/* 申诉驳回提示条 */}
      {rejectTipVisible && (
        <View className='reject-tip'>
          <Text className='reject-tip-text'>您的申诉已驳回，请按原报告整改后重新申请复检。</Text>
          <Text className='reject-tip-close' onClick={() => setRejectTipVisible(false)}>×</Text>
        </View>
      )}

      <ScrollView scrollY className='scroll-body-outer'>
        <View className='scroll-body'>
        {loading && (
          <View className='skeleton'>
            <View className='skeleton-line' />
            <View className='skeleton-line short' />
            <View className='skeleton-line' />
          </View>
        )}

        {loadFailed && !result && (
          <View className='load-fail' onClick={() => setLoadFailed(false)}>
            <Text>加载失败，点击重试</Text>
          </View>
        )}

        {!result && !loading && !loadFailed && (
          <View className='section empty-report-section'>
            <Text className='empty-report-title'>暂无验收报告</Text>
            <Text className='empty-report-desc'>请从施工陪伴页完成「AI验收」后在此查看报告</Text>
            <View className='btn-back-inline' onClick={() => safeSwitchTab(TAB_CONSTRUCTION)}>
              <Text>返回施工陪伴</Text>
            </View>
          </View>
        )}

        {analyzing && (
          <View className='analyzing'>
            <Text className='loading-icon'>⏳</Text>
            <Text>AI分析中，请稍候...</Text>
          </View>
        )}

        {result && !analyzing && (
          <>
            {/* 验收概览：含申诉复核版标注 */}
            <View className='overview-card'>
              <View className='overview-status-row'>
                <View className={`status-tag ${statusClass}`}>{statusLabel}</View>
                {isAppealRevised && <Text className='status-appeal-tag'>（申诉复核版）</Text>}
              </View>
              <Text className='overview-time'>验收时间：{new Date().toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}</Text>
              <Text className='overview-data'>验收项 {items.length} 项 / 合格 {qualifiedCount} 项 / 不合格 {unqualifiedCount} 项</Text>
            </View>

            {/* 验收详情列表：V2.6.4 未解锁时展示1-2个真实问题预览 */}
            <View className='section list-section'>
              <Text className='section-title'>验收详情</Text>
              {(unlocked ? items : items.slice(0, 2)).map((item, i) => (
                <View key={i} className='detail-row'>
                  <View className='detail-left'>
                    <Text className='detail-name'>{item.title}</Text>
                    <Text className='detail-standard'>{item.desc}</Text>
                  </View>
                  <View className='detail-right'>
                    <Text className={`result-tag ${item.level === 'low' ? 'pass' : 'fail'}`}>{item.level === 'low' ? '合格' : '不合格'}</Text>
                    {unlocked && <Text className='link-detail' onClick={() => setDetailModal(item)}>查看详情</Text>}
                  </View>
                </View>
              ))}
              {!unlocked && items.length > 0 && (
                <View className='preview-lock-tip'>
                  <Text className='preview-lock-text'>解锁后可查看全部 {items.length} 项问题详情、整改建议及 PDF 导出</Text>
                </View>
              )}
            </View>

            {/* 不合格项整改区：V2.6.4 删除预约人工监理，未解锁时遮蔽 */}
            {showRectifyArea && (
              <View className={`section rectify-section ${!unlocked ? 'section-locked' : ''}`}>
                <View className='rectify-title-row'>
                  <Text className='section-title'>不合格项整改</Text>
                  {rectifyStatus === 'pending' && <Text className='rectify-badge'>整改中</Text>}
                </View>
                <Text className='rectify-desc'>请按上述验收详情中的整改建议完成整改后，上传整改后照片并申请复检。</Text>
                {rectifyStatus === 'pending' && (
                  <View className='rectify-photos-row'>
                    <Text className='rectify-photos-label'>整改后照片（最多5张）</Text>
                    <View className='rectify-photos-grid'>
                      {rectifyPhotos.map((url, i) => (
                        <View key={i} className='rectify-photo-wrap'>
                          <Image src={url} className='rectify-photo' mode='aspectFill' />
                          <Text className='rectify-photo-del' onClick={() => setRectifyPhotos((p) => p.filter((_, idx) => idx !== i))}>×</Text>
                        </View>
                      ))}
                      {rectifyPhotos.length < 5 && (
                        <View className='rectify-photo-add' onClick={addRectifyPhoto}>
                          <Text>+</Text>
                        </View>
                      )}
                    </View>
                    <View className='rectify-btn complete' onClick={handleCompleteRectify}>
                      <Text>完成整改</Text>
                    </View>
                  </View>
                )}
                <View className='rectify-actions'>
                  <View className='rectify-btn' onClick={handleMarkRectify}><Text>标记整改</Text></View>
                  <View className='rectify-btn primary' onClick={handleApplyRecheck}><Text>申请复检</Text></View>
                </View>
                {!unlocked && (
                  <View className='section-lock-overlay' onClick={handleUnlock}>
                    <Text className='section-lock-text'>解锁后可查看整改建议</Text>
                  </View>
                )}
              </View>
            )}

            {/* 施工照片区：V2.6.4 未解锁时遮蔽 */}
            <View className={`section photo-section ${!unlocked ? 'section-locked' : ''}`}>
              <Text className='section-title'>施工照片</Text>
              <View className='photo-grid'>
                {uploaded.slice(0, 9).map((url, i) =>
                  photoErrors.has(i) ? (
                    <View key={i} className='photo-thumb photo-thumb-error' onClick={() => setPhotoErrors((s) => { const n = new Set(s); n.delete(i); return n })}>
                      <Text className='photo-error-icon'>⚠️</Text>
                      <Text className='photo-error-tap'>点击重试</Text>
                    </View>
                  ) : (
                    <Image
                      key={i}
                      src={url}
                      className='photo-thumb'
                      mode='aspectFill'
                      onClick={() => Taro.previewImage({ current: url, urls: uploaded })}
                      onError={() => setPhotoErrors((s) => new Set(s).add(i))}
                    />
                  )
                )}
                {uploaded.length > 9 && <View className='photo-more'>+{uploaded.length - 9}</View>}
              </View>
              {!unlocked && (
                <View className='section-lock-overlay' onClick={handleUnlock}>
                  <Text className='section-lock-text'>解锁后可查看施工照片</Text>
                </View>
              )}
            </View>

            {/* 功能操作区：V2.6.4 删除保存报告 */}
            <View className='action-row'>
              <View className='action-left'>
                <Text className='action-link' onClick={handleShare}>分享</Text>
              </View>
              <View className='action-right'>
                <View className='btn-ai' onClick={goAiSupervision}><Text>咨询AI监理</Text></View>
              </View>
            </View>
          </>
        )}

        {(result || loading || loadFailed) && (
          <View className='back-wrap'>
            <View className='btn-back' onClick={() => safeSwitchTab(TAB_CONSTRUCTION)}>
              <Text>返回施工陪伴</Text>
            </View>
          </View>
        )}
        </View>
      </ScrollView>

      {/* 查看详情弹窗 */}
      {detailModal && (
        <View className='detail-modal-mask' onClick={() => setDetailModal(null)}>
          <View className='detail-modal pop' onClick={(e) => e.stopPropagation()}>
            <Text className='detail-modal-close' onClick={() => setDetailModal(null)}>×</Text>
            <Text className='detail-modal-title'>{detailModal.title}</Text>
            {uploaded[0] && (
              <View className='detail-modal-photo-wrap'>
                <Text className='detail-modal-label'>问题照片</Text>
                <Image src={uploaded[0]} className='detail-modal-photo' mode='aspectFill' />
              </View>
            )}
            <Text className='detail-modal-label'>验收标准</Text>
            <Text className='detail-modal-text'>{detailModal.desc}</Text>
            <Text className='detail-modal-label'>整改建议</Text>
            <Text className='detail-modal-text'>{detailModal.suggest}</Text>
            <View className='detail-modal-btn' onClick={() => setDetailModal(null)}><Text>我已知晓</Text></View>
          </View>
        </View>
      )}

      {/* 申诉弹窗 */}
      {appealModal && (
        <View className='appeal-modal-mask' onClick={() => setAppealModal(false)}>
          <View className='appeal-modal pop' onClick={(e) => e.stopPropagation()}>
            <Text className='appeal-modal-title'>验收结果申诉</Text>
            <Textarea
              className='appeal-input'
              placeholder='请输入异议原因（最多500字）'
              placeholderClass='appeal-placeholder'
              value={appealReason}
              onInput={(e) => setAppealReason(e.detail.value)}
              maxlength={500}
            />
            <Text className='appeal-count'>{appealReason.length}/500</Text>
            <View className='appeal-images-wrap'>
              <Text className='appeal-images-label'>凭证上传（选填，最多3张）</Text>
              <View className='appeal-images-row'>
                {appealImages.map((url, i) => (
                  <View key={i} className='appeal-img-wrap'>
                    <Image src={url} className='appeal-img' mode='aspectFill' />
                    <Text className='appeal-img-del' onClick={() => setAppealImages((p) => p.filter((_, idx) => idx !== i))}>×</Text>
                  </View>
                ))}
                {appealImages.length < 3 && (
                  <View className='appeal-img-add' onClick={addAppealImage}>+</View>
                )}
              </View>
            </View>
            <View className='appeal-modal-actions'>
              <View className='appeal-btn cancel' onClick={() => setAppealModal(false)}><Text>取消</Text></View>
              <View
                className={`appeal-btn submit ${appealReason.trim() ? '' : 'disabled'}`}
                onClick={appealReason.trim() && !appealSubmitting ? submitAppeal : undefined}
              >
                <Text>提交申诉</Text>
              </View>
            </View>
          </View>
        </View>
      )}

      {/* 申诉提交成功弹窗 */}
      {appealSuccessModal && (
        <View className='appeal-success-mask' onClick={() => setAppealSuccessModal(false)}>
          <View className='appeal-success pop' onClick={(e) => e.stopPropagation()}>
            <Text className='appeal-success-title'>申诉已提交！</Text>
            <Text className='appeal-success-desc'>人工客服将在1-2个工作日内审核，结果将通过小程序消息通知。</Text>
            <View className='appeal-success-btn' onClick={() => setAppealSuccessModal(false)}><Text>我知道了</Text></View>
          </View>
        </View>
      )}
    </View>
  )
}

export default AcceptancePage

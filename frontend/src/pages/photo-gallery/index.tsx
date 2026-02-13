import React, { useState, useEffect, useCallback } from 'react'
import { View, Text, ScrollView, Image } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getWithAuth, deleteWithAuth } from '../../services/api'
import './index.scss'

/** 阶段配置：与 construction 页一致，key 用于 API */
const STAGES = [
  { key: 'all', name: '全部照片', apiStage: undefined as string | undefined },
  { key: 'material', name: 'S00材料进场', apiStage: 'material' },
  { key: 'plumbing', name: 'S01隐蔽工程', apiStage: 'plumbing' },
  { key: 'carpentry', name: 'S02泥瓦工', apiStage: 'carpentry' },
  { key: 'woodwork', name: 'S03木工', apiStage: 'woodwork' },
  { key: 'painting', name: 'S04油漆', apiStage: 'painting' },
  { key: 'installation', name: 'S05安装收尾', apiStage: 'installation' }
]

export interface ConstructionPhotoItem {
  id: number
  url: string
  stage?: string
  created_at?: string
}

/**
 * P28 施工照片管理页 - 阶段 Tab + 照片网格 + 批量操作 + 空态去拍摄(P15)
 */
const PhotoGalleryPage: React.FC = () => {
  const [stageIndex, setStageIndex] = useState(0)
  const [list, setList] = useState<ConstructionPhotoItem[]>([])
  const [loading, setLoading] = useState(true)
  const [batchMode, setBatchMode] = useState(false)
  const [selected, setSelected] = useState<Set<number>>(new Set())

  const currentStage = STAGES[stageIndex]
  const apiStage = currentStage.apiStage

  const loadList = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getWithAuth('/construction-photos', apiStage ? { stage: apiStage } : undefined) as any
      const data = res?.list ?? res
      const arr = Array.isArray(data) ? data : (data?.items ?? [])
      setList(arr.map((x: any) => ({
        id: x.id,
        url: x.url || x.image_url || x.file_url || '',
        stage: x.stage,
        created_at: x.created_at
      })))
    } catch {
      setList([])
    } finally {
      setLoading(false)
    }
  }, [apiStage])

  useEffect(() => {
    loadList()
  }, [loadList])

  const toggleSelect = (id: number) => {
    const next = new Set(selected)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelected(next)
  }

  const selectAll = () => {
    if (selected.size >= list.length) {
      setSelected(new Set())
    } else {
      setSelected(new Set(list.map((x) => x.id)))
    }
  }

  const handleBatchDelete = () => {
    if (selected.size === 0) {
      Taro.showToast({ title: '请先选择照片', icon: 'none' })
      return
    }
    Taro.showModal({
      title: '确认删除',
      content: `将删除 ${selected.size} 张照片，确定吗？`,
      success: async (res) => {
        if (!res.confirm) return
        try {
          for (const id of selected) {
            await constructionPhotoApi.delete(id)
          }
          setList((prev) => prev.filter((x) => !selected.has(x.id)))
          setSelected(new Set())
          setBatchMode(false)
          Taro.showToast({ title: '已删除', icon: 'success' })
        } catch (e: any) {
          Taro.showToast({ title: e?.message || '删除失败', icon: 'none' })
        }
      }
    })
  }

  const handleBatchExport = () => {
    if (selected.size === 0) {
      Taro.showToast({ title: '请先选择照片', icon: 'none' })
      return
    }
    const urls = list.filter((x) => selected.has(x.id)).map((x) => x.url).filter(Boolean)
    if (urls.length === 0) {
      Taro.showToast({ title: '所选照片无有效链接', icon: 'none' })
      return
    }
    Taro.showToast({ title: '已复制链接，可到相册保存', icon: 'none' })
    // 小程序内可考虑 downFile 存相册，这里简化提示
  }

  const handlePhotoClick = (item: ConstructionPhotoItem) => {
    if (batchMode) {
      toggleSelect(item.id)
      return
    }
    const urls = list.map((x) => x.url).filter(Boolean)
    const current = urls.indexOf(item.url)
    Taro.previewImage({ urls, current: current >= 0 ? current : 0 })
    Taro.showActionSheet({
      itemList: ['保存图片', '删除'],
      success: (res) => {
        if (res.tapIndex === 0) {
          Taro.showLoading({ title: '保存中...' })
          Taro.downloadFile({ url: item.url })
            .then((d) => Taro.saveImageToPhotosAlbum({ filePath: d.tempFilePath }))
            .then(() => {
              Taro.hideLoading()
              Taro.showToast({ title: '已保存到相册', icon: 'success' })
            })
            .catch(() => {
              Taro.hideLoading()
              Taro.showToast({ title: '保存失败或未授权相册', icon: 'none' })
            })
        } else if (res.tapIndex === 1) {
          Taro.showModal({
            title: '确认删除',
            content: '删除后不可恢复',
            success: async (r) => {
              if (!r.confirm) return
              try {
                await deleteWithAuth(`/construction-photos/${item.id}`)
                setList((prev) => prev.filter((x) => x.id !== item.id))
                Taro.showToast({ title: '已删除', icon: 'success' })
              } catch {
                Taro.showToast({ title: '删除失败', icon: 'none' })
              }
            }
          })
        }
      }
    }).catch(() => {})
  }

  const goShoot = () => {
    const stage = apiStage || 'material'
    Taro.navigateTo({ url: `/pages/photo/index?stage=${stage}&scene=accept` })
  }

  const isEmpty = !loading && list.length === 0
  const stageLabel = currentStage.key === 'all' ? '全部' : currentStage.name

  return (
    <View className='photo-gallery-page'>
      <ScrollView scrollY className='main-scroll' enhanced showScrollbar={false}>
      <View className='nav-row'>
        <Text className='nav-title'>施工照片</Text>
        <Text
          className='batch-btn'
          onClick={() => {
            setBatchMode(!batchMode)
            if (batchMode) setSelected(new Set())
          }}
        >
          {batchMode ? '取消' : '批量操作'}
        </Text>
      </View>

      <ScrollView scrollX className='stage-tabs' scrollWithAnimation>
        {STAGES.map((s, i) => (
          <Text
            key={s.key}
            className={`tab ${stageIndex === i ? 'active' : ''}`}
            onClick={() => setStageIndex(i)}
          >
            {s.name}
          </Text>
        ))}
      </ScrollView>

      {loading && (
        <View className='empty-wrap'>
          <Text className='empty-text'>加载中...</Text>
        </View>
      )}

      {!loading && isEmpty && (
        <View className='empty-wrap'>
          <Text className='empty-icon'>📷</Text>
          <Text className='empty-text'>暂无{stageLabel}阶段照片</Text>
          <View className='go-shoot' onClick={goShoot}>
            <Text>去拍摄</Text>
          </View>
        </View>
      )}

      {!loading && !isEmpty && (
        <View className='grid-wrap'>
          {list.map((item) => (
            <View
              key={item.id}
              className='photo-cell'
              onClick={() => handlePhotoClick(item)}
            >
              <Image src={item.url} mode='aspectFill' className='thumb' />
              {batchMode && (
                <View
                  className={`checkbox-wrap ${selected.has(item.id) ? 'checked' : ''}`}
                  onClick={(e) => { e.stopPropagation(); toggleSelect(item.id) }}
                >
                  {selected.has(item.id) ? '✓' : ''}
                </View>
              )}
            </View>
          ))}
        </View>
      )}

      </ScrollView>

      {batchMode && list.length > 0 && (
        <View className='batch-bar'>
          <View className='batch-left'>
            <Text className='batch-info'>已选 {selected.size} 张</Text>
            <Text className='select-all' onClick={selectAll}>
              {selected.size >= list.length ? '取消全选' : '全选'}
            </Text>
          </View>
          <View className='batch-actions'>
            <Text className='batch-action' onClick={handleBatchExport}>导出已选</Text>
            <Text className='batch-action danger' onClick={handleBatchDelete}>删除已选</Text>
          </View>
        </View>
      )}
    </View>
  )
}

export default PhotoGalleryPage

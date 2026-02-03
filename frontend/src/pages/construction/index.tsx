import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView, Picker } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { constructionApi } from '../../services/api'
import './index.scss'

/**
 * 施工陪伴页面
 */
const Construction: React.FC = () => {
  const [schedule, setSchedule] = useState<any>(null)
  const [startDate, setStartDate] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentStage, setCurrentStage] = useState('')

  // 装修阶段列表
  const stages = [
    { key: 'demolition', name: '拆改阶段' },
    { key: 'water_electric', name: '水电阶段' },
    { key: 'masonry', name: '泥工阶段' },
    { key: 'carpentry', name: '木工阶段' },
    { key: 'paint', name: '油漆阶段' },
    { key: 'installation', name: '安装阶段' }
  ]

  // 加载进度计划
  const loadSchedule = async () => {
    try {
      const result = await constructionApi.getSchedule()
      setSchedule(result)
      if (result.start_date) {
        setStartDate(result.start_date)
        setCurrentStage(result.current_stage || '')
      }
    } catch (error) {
      console.error('加载进度失败:', error)
    }
  }

  // 页面加载
  useEffect(() => {
    loadSchedule()
  }, [])

  // 设置开工日期
  const handleSetStartDate = async () => {
    Taro.showModal({
      title: '设置开工日期',
      editable: true,
      placeholderText: '请选择开工日期',
      success: async (res) => {
        if (res.confirm && res.content) {
          setLoading(true)
          try {
            await constructionApi.setStartDate(res.content)
            setStartDate(res.content)
            Taro.showToast({
              title: '设置成功',
              icon: 'success'
            })
            loadSchedule()
          } catch (error) {
            Taro.showToast({
              title: '设置失败',
              icon: 'none'
            })
          } finally {
            setLoading(false)
          }
        }
      }
    })
  }

  // 更新阶段状态
  const handleUpdateStage = async (stageKey: string, status: string) => {
    setLoading(true)
    try {
      await constructionApi.updateStageStatus(stageKey, status)
      Taro.showToast({
        title: '更新成功',
        icon: 'success'
      })
      loadSchedule()
    } catch (error) {
      Taro.showToast({
        title: '更新失败',
        icon: 'none'
      })
    } finally {
      setLoading(false)
    }
  }

  // 重置进度
  const handleReset = () => {
    Taro.showModal({
      title: '重置进度',
      content: '确定要重置所有进度吗？',
      success: async (res) => {
        if (res.confirm) {
          setLoading(true)
          try {
            await constructionApi.resetSchedule()
            setSchedule(null)
            setStartDate('')
            setCurrentStage('')
            Taro.showToast({
              title: '重置成功',
              icon: 'success'
            })
          } catch (error) {
            Taro.showToast({
              title: '重置失败',
              icon: 'none'
            })
          } finally {
            setLoading(false)
          }
        }
      }
    })
  }

  // 计算进度百分比
  const calculateProgress = () => {
    if (!schedule || !schedule.stages) return 0

    let completed = 0
    const total = stages.length

    stages.forEach(stage => {
      const stageData = schedule.stages[stage.key]
      if (stageData && stageData.status === 'completed') {
        completed++
      }
    })

    return Math.round((completed / total) * 100)
  }

  // 计算预计完成日期
  const calculateEndDate = () => {
    if (!startDate) return '-'

    const start = new Date(startDate)
    const endDate = new Date(start)
    endDate.setDate(endDate.getDate() + 60) // 假设60天工期

    return endDate.toLocaleDateString('zh-CN')
  }

  return (
    <ScrollView scrollY className='construction-page'>
      <View className='header'>
        <Text className='title'>施工陪伴</Text>
      </View>

      <View className='content'>
        {/* 开工日期 */}
        <View className='date-section'>
          <View className='section-header'>
            <Text className='section-title'>开工日期</Text>
            <Text className='edit-btn' onClick={handleSetStartDate}>
              {startDate ? '修改' : '设置'}
            </Text>
          </View>

          {startDate ? (
            <View className='date-display'>
              <Text className='date-text'>{startDate}</Text>
              <Text className='date-label'>开工日</Text>
            </View>
          ) : (
            <View className='date-empty'>
              <Text className='empty-text'>请设置开工日期</Text>
              <Text className='empty-hint'>设置后将自动生成进度计划</Text>
            </View>
          )}
        </View>

        {/* 总体进度 */}
        {startDate && (
          <View className='progress-section'>
            <View className='progress-header'>
              <Text className='progress-title'>总体进度</Text>
              <Text className='progress-value'>{calculateProgress()}%</Text>
            </View>

            <View className='progress-bar'>
              <View
                className='progress-fill'
                style={{ width: `${calculateProgress()}%` }}
              ></View>
            </View>

            <View className='date-summary'>
              <View className='date-item'>
                <Text className='date-label'>开工</Text>
                <Text className='date-value'>{startDate}</Text>
              </View>
              <View className='date-item'>
                <Text className='date-label'>预计完成</Text>
                <Text className='date-value'>{calculateEndDate()}</Text>
              </View>
            </View>
          </View>
        )}

        {/* 阶段进度 */}
        {startDate && (
          <View className='stages-section'>
            <Text className='section-title'>阶段进度</Text>

            {stages.map((stage, index) => {
              const stageData = schedule?.stages?.[stage.key]
              const stageStatus = stageData?.status || 'pending'

              return (
                <View key={stage.key} className='stage-item'>
                  <View className='stage-header'>
                    <View className='stage-info'>
                      <Text className='stage-number'>{index + 1}</Text>
                      <View>
                        <Text className='stage-name'>{stage.name}</Text>
                        <Text className='stage-status'>
                          {stageStatus === 'completed' && '✅ 已完成'}
                          {stageStatus === 'in_progress' && '⏳ 进行中'}
                          {stageStatus === 'pending' && '⭕ 未开始'}
                        </Text>
                      </View>
                    </View>

                    <View className='stage-actions'>
                      {stageStatus === 'pending' && (
                        <Text
                          className='action-btn start'
                          onClick={() => handleUpdateStage(stage.key, 'in_progress')}
                        >
                          开始
                        </Text>
                      )}
                      {stageStatus === 'in_progress' && (
                        <Text
                          className='action-btn complete'
                          onClick={() => handleUpdateStage(stage.key, 'completed')}
                        >
                          完成
                        </Text>
                      )}
                    </View>
                  </View>

                  {stageData?.tasks && stageData.tasks.length > 0 && (
                    <View className='stage-tasks'>
                      {stageData.tasks.map((task: any, taskIndex: number) => (
                        <View key={taskIndex} className='task-item'>
                          <Text className='task-text'>{task.name}</Text>
                        </View>
                      ))}
                    </View>
                  )}
                </View>
              )
            })}
          </View>
        )}

        {/* 操作按钮 */}
        {startDate && (
          <View className='action-buttons'>
            <View className='reset-btn' onClick={handleReset}>
              <Text className='reset-text'>重置进度</Text>
            </View>
          </View>
        )}

        {/* 提示信息 */}
        <View className='tips'>
          <Text className='tips-title'>温馨提示</Text>
          <Text className='tips-text'>
            • 点击"开始"标记阶段进行中
          </Text>
          <Text className='tips-text'>
            • 完成验收后点击"完成"标记阶段结束
          </Text>
          <Text className='tips-text'>
            • 重置进度将清空所有阶段状态
          </Text>
        </View>
      </View>
    </ScrollView>
  )
}

export default Construction

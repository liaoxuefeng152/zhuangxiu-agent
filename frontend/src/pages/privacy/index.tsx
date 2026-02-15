import React, { useState, useEffect } from 'react'
import { View, Text, ScrollView, Switch } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

/**
 * P17 隐私保障页 - 数据收集/使用/存储/权限说明、同意开关、隐私异议反馈
 */
const PrivacyPage: React.FC = () => {
  const [agreePrivacy, setAgreePrivacy] = useState(true)

  useEffect(() => {
    const v = Taro.getStorageSync('privacy_agreed')
    setAgreePrivacy(v !== false)
  }, [])

  const handleSwitch = (v: boolean) => {
    setAgreePrivacy(v)
    Taro.setStorageSync('privacy_agreed', v)
    if (!v) Taro.showToast({ title: '部分功能（如AI分析/提醒）将无法使用', icon: 'none' })
    else Taro.showToast({ title: '设置已更新', icon: 'success' })
  }

  const handleFeedback = () => {
    Taro.navigateTo({
      url: '/pages/feedback/index?type=privacy'
    })
  }

  return (
    <ScrollView scrollY className='privacy-page-outer'>
      <View className='privacy-page'>
      <View className='content'>
        <View className='block'>
          <Text className='title'>数据收集范围</Text>
          <Text className='desc'>我们可能收集：用户基本信息（昵称、头像、手机号）、装修相关数据（公司名称、报价单、合同、施工照片、验收报告）、设备信息（机型、系统版本）及操作日志，仅用于为您提供AI分析、提醒推送及服务改进。</Text>
        </View>
        <View className='block'>
          <Text className='title'>数据使用规则</Text>
          <Text className='desc'>您的数据仅用于：本小程序内的AI分析、智能提醒、报告生成与展示；不对外出售、不向第三方共享用于营销；法律法规要求或经您明确授权的情形除外。</Text>
        </View>
        <View className='block'>
          <Text className='title'>数据存储期限</Text>
          <Text className='desc'>装修相关数据在您使用期间持续保存；装修完成后约1年将自动匿名化处理，仅保留统计所需非敏感信息。您可在「我的数据」中主动删除或导出数据。</Text>
        </View>
        <View className='block'>
          <Text className='title'>权限使用说明</Text>
          <Text className='desc'>相机/相册：用于拍摄施工照片、上传报价单/合同；通知权限：用于阶段开始/验收前提醒；位置：用于本地化装修规范与价格参考。我们仅在对应功能使用时申请权限，您可随时在系统设置中关闭。</Text>
        </View>
        <View className='block highlight'>
          <Text className='title'>关键条款说明</Text>
          <Text className='desc'>我们不会将您的个人数据共享给第三方用于商业营销；数据存储于合规的境内服务器；如遇法律要求披露，我们将严格按法律规定执行。</Text>
        </View>
      </View>

      <View className='action-section'>
        <View className='row'>
          <Text className='label'>同意隐私政策</Text>
          <Switch checked={agreePrivacy} onValueChange={handleSwitch} color='#007AFF' />
        </View>
        <View className='btn secondary' onClick={handleFeedback}>
          <Text>隐私异议反馈</Text>
        </View>
      </View>
      </View>
    </ScrollView>
  )
}

export default PrivacyPage

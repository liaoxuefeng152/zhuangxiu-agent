import React from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import './index.scss'

/**
 * P23 关于 & 帮助页
 */
const AboutPage: React.FC = () => {
  return (
    <ScrollView scrollY className='about-page'>
      <View className='section'>
        <Text className='section-title'>关于</Text>
        <View className='row'>
          <Text>产品版本</Text>
          <Text className='value'>V2.1</Text>
        </View>
      </View>
      <View className='section'>
        <Text className='section-title'>帮助</Text>
        <Text className='faq'>常见问题请前往「使用指南」查看</Text>
      </View>
    </ScrollView>
  )
}

export default AboutPage

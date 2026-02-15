import React from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import './index.scss'

/**
 * P22 中立声明页
 */
const NeutralStatementPage: React.FC = () => {
  return (
    <ScrollView scrollY className='neutral-page-outer'>
      <View className='neutral-page'>
      <View className='content'>
        <View className='block'>
          <Text className='title'>产品中立性</Text>
          <Text className='desc'>本产品不向装修公司收取任何费用，仅面向装修用户提供决策辅助服务，确保建议客观中立。</Text>
        </View>
        <View className='block'>
          <Text className='title'>建议依据</Text>
          <Text className='desc'>所有分析建议基于公开工商数据、行业规范及法律法规，力求客观、可追溯。</Text>
        </View>
        <View className='block'>
          <Text className='title'>免责声明</Text>
          <Text className='desc'>本产品仅提供参考信息，不承担任何因用户决策产生的责任。最终决策权在用户本人。</Text>
        </View>
      </View>
      </View>
    </ScrollView>
  )
}

export default NeutralStatementPage

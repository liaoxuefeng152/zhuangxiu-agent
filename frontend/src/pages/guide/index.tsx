import React, { useState } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import './index.scss'

/**
 * P16 使用指南页 - 5大板块（PRD）
 */
const SECTIONS = [
  { key: 'company', title: '公司检测', items: ['1. 输入装修公司全称', '2. 从模糊匹配结果中选择或直接输入', '3. 点击「开始检测」', '4. 等待约10秒，查看风险报告'] },
  { key: 'quote', title: '报价单审核', items: ['1. 建议先完成公司检测', '2. 点击「上传报价单」', '3. 选择文件或拍照上传（PDF/JPG/PNG，≤10MB）', '4. 等待AI分析，查看漏项与虚高提示'] },
  { key: 'contract', title: '合同审核', items: ['1. 建议先完成公司检测', '2. 点击「上传合同」', '3. 选择文件或拍照上传', '4. 等待AI分析，查看霸王条款高亮'] },
  { key: 'construction', title: '施工陪伴', items: ['1. 设置开工日期', '2. 系统自动推算各阶段时间节点', '3. 点击状态标签更新进度', '4. 使用AI验收、拍照留证、验收指引'] },
  { key: 'payment', title: '付费解锁', items: ['1. 报告预览展示30%核心内容', '2. 点击「解锁完整报告」选择套餐', '3. 单份9.9元或3份25元', '4. 解锁后支持PDF导出'] }
]

const GuidePage: React.FC = () => {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ company: true })

  const toggle = (key: string) => {
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <ScrollView scrollY className='guide-page'>
      <View className='section intro'>
        <Text className='title'>花30万装修，不该靠运气</Text>
        <Text className='desc'>AI帮你避坑 - 装修决策Agent 是面向装修用户的一站式智能决策工具</Text>
      </View>
      {SECTIONS.map((s) => (
        <View key={s.key} className='section accordion'>
          <View className='accordion-header' onClick={() => toggle(s.key)}>
            <Text className='subtitle'>{s.title}</Text>
            <Text className='arrow'>{expanded[s.key] ? '▼' : '▶'}</Text>
          </View>
          {expanded[s.key] && (
            <View className='accordion-body'>
              {s.items.map((item, i) => (
                <Text key={i} className='item'>{item}</Text>
              ))}
            </View>
          )}
        </View>
      ))}
      <View className='section tips'>
        <Text className='subtitle'>使用建议</Text>
        <Text className='item'>1. 建议先检测装修公司风险，再上传报价单或合同</Text>
        <Text className='item'>2. 上传文件请确保清晰，提升分析准确率</Text>
        <Text className='item'>3. 基础功能永久免费，增值服务按需购买</Text>
      </View>
    </ScrollView>
  )
}

export default GuidePage

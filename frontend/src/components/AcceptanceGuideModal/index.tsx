import React from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import './index.scss'

/**
 * P30 验收指引弹窗 - 对应阶段验收要点
 */
const STAGE_GUIDES: Record<string, { title: string; points: string[] }> = {
  material: {
    title: 'S00 材料进场核对指引',
    points: [
      '1. 核对材料清单与合同/报价单是否一致',
      '2. 品牌、规格、数量逐一对照',
      '3. 必拍：材料清单+实物对比照',
      '4. 不合格项记录并要求更换'
    ]
  },
  plumbing: {
    title: 'S01 隐蔽工程验收要点',
    points: [
      '1. 强电与弱电间距≥30cm，交叉处锡箔纸屏蔽',
      '2. 线管弯曲半径≥6倍管径，无死弯',
      '3. 电线接头挂锡或使用接线端子',
      '4. 水管打压0.6-0.8MPa，30分钟压降≤0.05MPa',
      '5. 冷热水管左热右冷，间距≥15cm'
    ]
  },
  water_electric: {
    title: '水电验收要点',
    points: [
      '1. 强电与弱电间距≥30cm，交叉处锡箔纸屏蔽',
      '2. 线管弯曲半径≥6倍管径，无死弯',
      '3. 电线接头挂锡或使用接线端子',
      '4. 水管打压0.6-0.8MPa，30分钟压降≤0.05MPa',
      '5. 冷热水管左热右冷，间距≥15cm'
    ]
  },
  carpentry: {
    title: 'S02 泥瓦工验收要点',
    points: [
      '1. 瓷砖空鼓率≤5%，重点检查边角',
      '2. 吊顶龙骨间距符合规范，牢固无松动',
      '3. 木质材料做好防潮防腐处理',
      '4. 阴阳角垂直度偏差≤3mm'
    ]
  },
  woodwork: {
    title: 'S03 木工验收要点',
    points: [
      '1. 吊顶龙骨间距符合规范，牢固无松动',
      '2. 木质材料防潮防腐处理到位',
      '3. 阴阳角垂直度偏差≤3mm',
      '4. 柜体安装牢固、门缝均匀'
    ]
  },
  masonry_wood: {
    title: '泥木验收要点',
    points: [
      '1. 瓷砖空鼓率≤5%，重点检查边角',
      '2. 吊顶龙骨间距符合规范，牢固无松动',
      '3. 木质材料做好防潮防腐处理',
      '4. 阴阳角垂直度偏差≤3mm'
    ]
  },
  painting: {
    title: 'S04 油漆验收要点',
    points: [
      '1. 墙面平整，无裂纹、起皮、流坠',
      '2. 阴阳角顺直，无缺棱掉角',
      '3. 涂料色泽均匀，无色差',
      '4. 油漆表面光滑，无颗粒、刷痕'
    ]
  },
  paint: {
    title: '油漆验收要点',
    points: [
      '1. 墙面平整，无裂纹、起皮、流坠',
      '2. 阴阳角顺直，无缺棱掉角',
      '3. 涂料色泽均匀，无色差',
      '4. 油漆表面光滑，无颗粒、刷痕'
    ]
  },
  installation: {
    title: 'S05 安装收尾验收要点',
    points: [
      '1. 橱柜/卫浴/门安装牢固，开关顺畅',
      '2. 五金件无缺失、无松动',
      '3. 灯具/开关插座通电正常',
      '4. 整体保洁完成，无遗漏'
    ]
  },
  floor: {
    title: '地板验收要点',
    points: [
      '1. 地面平整度≤3mm/2m',
      '2. 地板拼接紧密，无起拱、异响',
      '3. 收边条安装牢固，无缝隙',
      '4. 地暖区域使用专用地板'
    ]
  },
  soft_furnishing: {
    title: '软装验收要点',
    points: [
      '1. 定制家具尺寸与图纸一致',
      '2. 五金件安装牢固，开关顺畅',
      '3. 软装材质无异味，环保达标',
      '4. 整体风格协调，无明显瑕疵'
    ]
  },
  soft: {
    title: '软装验收要点',
    points: [
      '1. 定制家具尺寸与图纸一致',
      '2. 五金件安装牢固，开关顺畅',
      '3. 软装材质无异味，环保达标',
      '4. 整体风格协调，无明显瑕疵'
    ]
  }
}

interface Props {
  stageKey: string
  visible: boolean
  onClose: () => void
}

const AcceptanceGuideModal: React.FC<Props> = ({ stageKey, visible, onClose }) => {
  if (!visible) return null

  const guide = STAGE_GUIDES[stageKey] || STAGE_GUIDES.material || STAGE_GUIDES.plumbing

  return (
    <View className='guide-modal-mask' onClick={onClose}>
      <View className='guide-modal' onClick={(e) => e.stopPropagation()}>
        <Text className='close-btn' onClick={onClose}>×</Text>
        <Text className='modal-title'>{guide.title}</Text>
        <ScrollView scrollY className='guide-content'>
          {guide.points.map((p, i) => (
            <Text key={i} className='guide-point'>{p}</Text>
          ))}
        </ScrollView>
      </View>
    </View>
  )
}

export default AcceptanceGuideModal

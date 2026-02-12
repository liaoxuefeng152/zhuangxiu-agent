/**
 * 6大阶段核心配置
 */
const STAGES = [
  { id: 'S00', name: '材料进场', cycle: 3 },
  { id: 'S01', name: '隐蔽工程', cycle: 7 },
  { id: 'S02', name: '泥瓦工', cycle: 10 },
  { id: 'S03', name: '木工', cycle: 7 },
  { id: 'S04', name: '油漆', cycle: 7 },
  { id: 'S05', name: '安装收尾', cycle: 5 }
]

const STAGE_NAMES = {
  S00: '材料进场核对',
  S01: '隐蔽工程',
  S02: '泥瓦工',
  S03: '木工',
  S04: '油漆',
  S05: '安装收尾'
}

module.exports = { STAGES, STAGE_NAMES }

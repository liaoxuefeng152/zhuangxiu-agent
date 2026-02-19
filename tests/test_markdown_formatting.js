// 测试Markdown格式化功能
const testMarkdownMessages = [
  {
    title: "测试1: 简单Markdown消息",
    input: "**欢迎使用AI设计师！**\n\n我可以帮您解决以下问题：\n- 装修风格建议\n- 户型图分析\n- 预算规划\n- 材料选择\n\n请上传您的户型图开始体验！",
    expected: "欢迎使用AI设计师！\n\n我可以帮您解决以下问题：\n• 装修风格建议\n• 户型图分析\n• 预算规划\n• 材料选择\n\n请上传您的户型图开始体验！"
  },
  {
    title: "测试2: 带标题和列表的消息",
    input: "# 装修建议\n\n## 现代简约风格\n\n现代简约风格的特点：\n1. 简洁明快的线条\n2. 中性色调为主\n3. 功能主义设计\n4. 少即是多的理念\n\n## 北欧风格\n\n北欧风格的特点：\n- 自然材料\n- 明亮色彩\n- 舒适温馨\n- 实用主义",
    expected: "装修建议\n\n现代简约风格\n\n现代简约风格的特点：\n1. 简洁明快的线条\n2. 中性色调为主\n3. 功能主义设计\n4. 少即是多的理念\n\n北欧风格\n\n北欧风格的特点：\n• 自然材料\n• 明亮色彩\n• 舒适温馨\n• 实用主义"
  },
  {
    title: "测试3: 带代码块和格式的消息",
    input: "装修预算计算公式：\n\n```\n总预算 = 硬装费用 + 软装费用 + 家电费用\n硬装费用 ≈ 面积 × 单价\n软装费用 ≈ 总预算 × 30%\n```\n\n**注意**：\n- 硬装单价：800-1500元/㎡\n- 软装比例：25-35%\n- 预留10%应急资金",
    expected: "装修预算计算公式：\n\n【代码】总预算 = 硬装费用 + 软装费用 + 家电费用\n硬装费用 ≈ 面积 × 单价\n软装费用 ≈ 总预算 × 30%【/代码】\n\n注意：\n• 硬装单价：800-1500元/㎡\n• 软装比例：25-35%\n• 预留10%应急资金"
  },
  {
    title: "测试4: 混合格式消息",
    input: "**厨房装修要点**\n\n> 厨房是家庭装修的重点区域\n\n1. **布局设计**\n   - 动线合理（取→洗→切→炒）\n   - 操作台高度适宜\n\n2. **材料选择**\n   - 台面：石英石/不锈钢\n   - 橱柜：防潮板材\n   - 地面：防滑瓷砖\n\n3. **电器规划**\n   - 预留足够插座\n   - 油烟机功率要足\n   - 冰箱位置合理",
    expected: "厨房装修要点\n\n厨房是家庭装修的重点区域\n\n1. 布局设计\n   • 动线合理（取→洗→切→炒）\n   • 操作台高度适宜\n\n2. 材料选择\n   • 台面：石英石/不锈钢\n   • 橱柜：防潮板材\n   • 地面：防滑瓷砖\n\n3. 电器规划\n   • 预留足够插座\n   • 油烟机功率要足\n   • 冰箱位置合理"
  }
]

// 模拟stripMarkdown函数（修复版）
function stripMarkdown(text) {
  if (!text) return ''
  
  let result = text
  
  // 1. 处理代码块（保留内容，移除标记）
  result = result.replace(/```[\s\S]*?```/g, (match) => {
    // 移除开头的```和可能的语言标识，以及结尾的```
    const content = match.replace(/^```[a-zA-Z]*\n?/, '').replace(/\n?```$/, '')
    return `【代码】${content}【/代码】`
  })
  
  // 2. 处理行内代码（保留内容，移除标记）
  result = result.replace(/`([^`]+)`/g, '$1')
  
  // 3. 处理粗体和斜体（移除标记）
  result = result.replace(/\*\*(.+?)\*\*/g, '$1') // 粗体
  result = result.replace(/\*(.+?)\*/g, '$1')     // 斜体
  
  // 4. 处理标题（移除#标记，但保留文本并添加换行）
  result = result.replace(/^#{1,6}\s+(.+)$/gm, '$1\n')
  
  // 5. 处理链接（保留文本，移除URL）
  result = result.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
  
  // 6. 处理引用（移除>标记，但保留文本）
  result = result.replace(/^>\s+(.+)$/gm, '$1')
  
  // 7. 处理无序列表（将-或*替换为•）
  // 注意：需要处理缩进，所以使用更复杂的正则
  result = result.replace(/^(\s*)[-\*]\s+(.+)$/gm, (match, spaces, content) => {
    return `${spaces}• ${content}`
  })
  
  // 8. 处理有序列表（保留数字和文本）
  // 注意：需要处理缩进
  result = result.replace(/^(\s*)(\d+)\.\s+(.+)$/gm, (match, spaces, number, content) => {
    return `${spaces}${number}. ${content}`
  })
  
  // 9. 处理分割线（替换为一行分隔符）
  result = result.replace(/^[-*_]{3,}$/gm, '---')
  
  return result
}

// 模拟renderFormattedText函数
function renderFormattedText(text) {
  if (!text) return ''
  
  // 先去除Markdown格式
  let result = stripMarkdown(text)
  
  // 按换行分割，处理段落和列表
  const lines = result.split('\n')
  const formattedLines = []
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    
    if (!line) {
      // 空行，添加段落分隔
      formattedLines.push('\n\n')
      continue
    }
    
    // 检查是否是列表项
    const isListItem = line.startsWith('• ') || /^\d+\.\s/.test(line)
    
    if (isListItem) {
      // 列表项，添加缩进
      formattedLines.push(`  ${line}`)
    } else if (line === '---') {
      // 分割线
      formattedLines.push('────────────')
    } else {
      // 普通文本行
      formattedLines.push(line)
    }
  }
  
  // 合并结果，确保适当的间距
  let formattedText = formattedLines.join('\n')
  
  // 清理多余的换行
  formattedText = formattedText.replace(/\n{3,}/g, '\n\n')
  
  return formattedText.trim()
}

// 运行测试
console.log('=== Markdown格式化测试 ===\n')

testMarkdownMessages.forEach((test, index) => {
  console.log(`\n${index + 1}. ${test.title}`)
  console.log('输入:')
  console.log(test.input)
  console.log('\n格式化后:')
  const formatted = renderFormattedText(test.input)
  console.log(formatted)
  console.log('\n预期:')
  console.log(test.expected)
  
  // 简单比较（忽略空格差异）
  const formattedClean = formatted.replace(/\s+/g, ' ').trim()
  const expectedClean = test.expected.replace(/\s+/g, ' ').trim()
  
  if (formattedClean === expectedClean) {
    console.log('✅ 测试通过')
  } else {
    console.log('❌ 测试失败')
    console.log('差异:')
    console.log('格式化:', formattedClean)
    console.log('预期:', expectedClean)
  }
  console.log('─'.repeat(50))
})

// 测试实际使用场景
console.log('\n=== 实际使用场景测试 ===\n')

const realWorldExample = `**现代简约风格装修方案**

## 设计理念
> 少即是多，功能至上

## 主要特点
1. **简洁线条**
   - 直线条为主
   - 减少装饰元素
   - 强调几何形态

2. **色彩搭配**
   - 主色调：黑白灰
   - 点缀色：原木色/金属色
   - 色彩比例：7:2:1

3. **材料选择**
   - 墙面：乳胶漆/艺术涂料
   - 地面：木地板/水泥砖
   - 家具：定制柜体/简约家具

## 预算参考
\`\`\`
硬装：800-1200元/㎡
软装：300-500元/㎡
家电：根据需求定制
\`\`\`

**温馨提示**：建议预留10-15%的预算作为应急资金。`

console.log('实际AI消息示例:')
console.log(realWorldExample)
console.log('\n格式化后显示效果:')
console.log(renderFormattedText(realWorldExample))

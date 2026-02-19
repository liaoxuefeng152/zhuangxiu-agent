/**
 * 简单的Markdown渲染器 - 专为微信小程序设计
 * 支持基本的Markdown语法：
 * 1. 标题 (#, ##, ###)
 * 2. 粗体 (**text**)
 * 3. 斜体 (*text*)
 * 4. 列表 (- item)
 * 5. 链接 ([text](url))
 * 6. 代码块 (```code```)
 * 7. 行内代码 (`code`)
 * 8. 引用 (> text)
 * 9. 分割线 (---)
 */

/**
 * 解析Markdown文本为微信小程序可渲染的节点数组
 */
export const parseMarkdown = (text: string): any[] => {
  if (!text) return []
  
  const lines = text.split('\n')
  const nodes: any[] = []
  let inCodeBlock = false
  let codeBlockContent = ''
  let codeBlockLanguage = ''
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    
    // 处理代码块
    if (line.trim().startsWith('```')) {
      if (!inCodeBlock) {
        // 开始代码块
        inCodeBlock = true
        codeBlockContent = ''
        codeBlockLanguage = line.trim().replace(/```/g, '').trim()
      } else {
        // 结束代码块
        inCodeBlock = false
        nodes.push({
          type: 'code',
          language: codeBlockLanguage,
          content: codeBlockContent
        })
        continue
      }
    } else if (inCodeBlock) {
      // 代码块内容
      codeBlockContent += line + '\n'
      continue
    }
    
    // 处理空行
    if (line.trim() === '') {
      nodes.push({ type: 'br' })
      continue
    }
    
    // 处理标题
    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/)
    if (headingMatch) {
      const level = headingMatch[1].length
      const content = headingMatch[2]
      nodes.push({
        type: 'heading',
        level,
        content: parseInlineMarkdown(content)
      })
      continue
    }
    
    // 处理引用
    if (line.trim().startsWith('> ')) {
      const content = line.trim().substring(2)
      nodes.push({
        type: 'blockquote',
        content: parseInlineMarkdown(content)
      })
      continue
    }
    
    // 处理分割线
    if (line.trim().match(/^[-*_]{3,}$/)) {
      nodes.push({ type: 'hr' })
      continue
    }
    
    // 处理无序列表
    if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      const content = line.trim().substring(2)
      nodes.push({
        type: 'list-item',
        content: parseInlineMarkdown(content)
      })
      continue
    }
    
    // 处理有序列表
    const orderedListMatch = line.match(/^(\d+)\.\s+(.+)$/)
    if (orderedListMatch) {
      const number = orderedListMatch[1]
      const content = orderedListMatch[2]
      nodes.push({
        type: 'ordered-list-item',
        number,
        content: parseInlineMarkdown(content)
      })
      continue
    }
    
    // 处理普通段落
    nodes.push({
      type: 'paragraph',
      content: parseInlineMarkdown(line)
    })
  }
  
  // 如果代码块没有正确结束，添加最后一个代码块
  if (inCodeBlock) {
    nodes.push({
      type: 'code',
      language: codeBlockLanguage,
      content: codeBlockContent
    })
  }
  
  return nodes
}

/**
 * 解析行内Markdown语法
 */
const parseInlineMarkdown = (text: string): any[] => {
  const nodes: any[] = []
  let currentText = ''
  let i = 0
  
  while (i < text.length) {
    // 处理粗体 (**text**)
    if (text.substr(i, 2) === '**') {
      if (currentText) {
        nodes.push({ type: 'text', content: currentText })
        currentText = ''
      }
      
      const endIndex = text.indexOf('**', i + 2)
      if (endIndex !== -1) {
        const boldText = text.substring(i + 2, endIndex)
        nodes.push({ type: 'bold', content: parseInlineMarkdown(boldText) })
        i = endIndex + 2
      } else {
        currentText += '**'
        i += 2
      }
      continue
    }
    
    // 处理斜体 (*text*)
    if (text[i] === '*' && (i === 0 || text[i-1] !== '*')) {
      if (currentText) {
        nodes.push({ type: 'text', content: currentText })
        currentText = ''
      }
      
      const endIndex = text.indexOf('*', i + 1)
      if (endIndex !== -1) {
        const italicText = text.substring(i + 1, endIndex)
        nodes.push({ type: 'italic', content: parseInlineMarkdown(italicText) })
        i = endIndex + 1
      } else {
        currentText += '*'
        i += 1
      }
      continue
    }
    
    // 处理行内代码 (`code`)
    if (text[i] === '`') {
      if (currentText) {
        nodes.push({ type: 'text', content: currentText })
        currentText = ''
      }
      
      const endIndex = text.indexOf('`', i + 1)
      if (endIndex !== -1) {
        const codeText = text.substring(i + 1, endIndex)
        nodes.push({ type: 'inline-code', content: codeText })
        i = endIndex + 1
      } else {
        currentText += '`'
        i += 1
      }
      continue
    }
    
    // 处理链接 ([text](url))
    if (text[i] === '[') {
      if (currentText) {
        nodes.push({ type: 'text', content: currentText })
        currentText = ''
      }
      
      const linkEndIndex = text.indexOf(']', i)
      if (linkEndIndex !== -1) {
        const urlStartIndex = text.indexOf('(', linkEndIndex)
        if (urlStartIndex !== -1 && urlStartIndex === linkEndIndex + 1) {
          const urlEndIndex = text.indexOf(')', urlStartIndex)
          if (urlEndIndex !== -1) {
            const linkText = text.substring(i + 1, linkEndIndex)
            const linkUrl = text.substring(urlStartIndex + 1, urlEndIndex)
            nodes.push({ type: 'link', text: linkText, url: linkUrl })
            i = urlEndIndex + 1
            continue
          }
        }
      }
    }
    
    currentText += text[i]
    i++
  }
  
  if (currentText) {
    nodes.push({ type: 'text', content: currentText })
  }
  
  return nodes
}

/**
 * 渲染Markdown节点为微信小程序组件
 */
export const renderMarkdown = (nodes: any[]): any[] => {
  return nodes.map((node, index) => {
    switch (node.type) {
      case 'heading':
        return {
          type: 'view',
          className: `markdown-heading markdown-h${node.level}`,
          children: renderInlineMarkdown(node.content)
        }
      
      case 'paragraph':
        return {
          type: 'view',
          className: 'markdown-paragraph',
          children: renderInlineMarkdown(node.content)
        }
      
      case 'bold':
        return {
          type: 'text',
          className: 'markdown-bold',
          children: renderInlineMarkdown(node.content)
        }
      
      case 'italic':
        return {
          type: 'text',
          className: 'markdown-italic',
          children: renderInlineMarkdown(node.content)
        }
      
      case 'inline-code':
        return {
          type: 'text',
          className: 'markdown-inline-code',
          children: [{ type: 'text', content: node.content }]
        }
      
      case 'code':
        return {
          type: 'view',
          className: 'markdown-code-block',
          children: [
            {
              type: 'text',
              className: 'markdown-code-language',
              children: [{ type: 'text', content: node.language || 'code' }]
            },
            {
              type: 'text',
              className: 'markdown-code-content',
              children: [{ type: 'text', content: node.content }]
            }
          ]
        }
      
      case 'link':
        return {
          type: 'text',
          className: 'markdown-link',
          children: [{ type: 'text', content: node.text }],
          url: node.url
        }
      
      case 'list-item':
        return {
          type: 'view',
          className: 'markdown-list-item',
          children: [
            {
              type: 'text',
              className: 'markdown-list-bullet',
              children: [{ type: 'text', content: '• ' }]
            },
            {
              type: 'text',
              className: 'markdown-list-content',
              children: renderInlineMarkdown(node.content)
            }
          ]
        }
      
      case 'ordered-list-item':
        return {
          type: 'view',
          className: 'markdown-ordered-list-item',
          children: [
            {
              type: 'text',
              className: 'markdown-ordered-list-number',
              children: [{ type: 'text', content: `${node.number}. ` }]
            },
            {
              type: 'text',
              className: 'markdown-ordered-list-content',
              children: renderInlineMarkdown(node.content)
            }
          ]
        }
      
      case 'blockquote':
        return {
          type: 'view',
          className: 'markdown-blockquote',
          children: renderInlineMarkdown(node.content)
        }
      
      case 'hr':
        return {
          type: 'view',
          className: 'markdown-hr'
        }
      
      case 'br':
        return {
          type: 'view',
          className: 'markdown-br'
        }
      
      case 'text':
        return {
          type: 'text',
          className: 'markdown-text',
          children: [{ type: 'text', content: node.content }]
        }
      
      default:
        return {
          type: 'text',
          className: 'markdown-text',
          children: [{ type: 'text', content: JSON.stringify(node) }]
        }
    }
  })
}

/**
 * 渲染行内Markdown节点
 */
const renderInlineMarkdown = (nodes: any[]): any[] => {
  return nodes.map((node, index) => {
    switch (node.type) {
      case 'text':
        return {
          type: 'text',
          className: 'markdown-text',
          children: [{ type: 'text', content: node.content }]
        }
      
      case 'bold':
        return {
          type: 'text',
          className: 'markdown-bold',
          children: renderInlineMarkdown(node.content)
        }
      
      case 'italic':
        return {
          type: 'text',
          className: 'markdown-italic',
          children: renderInlineMarkdown(node.content)
        }
      
      case 'inline-code':
        return {
          type: 'text',
          className: 'markdown-inline-code',
          children: [{ type: 'text', content: node.content }]
        }
      
      case 'link':
        return {
          type: 'text',
          className: 'markdown-link',
          children: [{ type: 'text', content: node.text }],
          url: node.url
        }
      
      default:
        return {
          type: 'text',
          className: 'markdown-text',
          children: [{ type: 'text', content: JSON.stringify(node) }]
        }
    }
  })
}

/**
 * 简化的Markdown渲染函数 - 直接返回文本，但添加CSS类名
 */
export const renderSimpleMarkdown = (text: string): string => {
  if (!text) return ''
  
  // 替换基本的Markdown语法为HTML标签
  let html = text
  
  // 处理标题
  html = html.replace(/^### (.+)$/gm, '<h3 class="markdown-h3">$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2 class="markdown-h2">$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h1 class="markdown-h1">$1</h1>')
  
  // 处理粗体
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="markdown-bold">$1</strong>')
  
  // 处理斜体
  html = html.replace(/\*(.+?)\*/g, '<em class="markdown-italic">$1</em>')
  
  // 处理行内代码
  html = html.replace(/`(.+?)`/g, '<code class="markdown-inline-code">$1</code>')
  
  // 处理代码块（简化版）
  html = html.replace(/```([\s\S]*?)```/g, '<pre class="markdown-code-block"><code class="markdown-code-content">$1</code></pre>')
  
  // 处理无序列表
  html = html.replace(/^- (.+)$/gm, '<li class="markdown-list-item">$1</li>')
  html = html.replace(/^\* (.+)$/gm, '<li class="markdown-list-item">$1</li>')
  
  // 处理有序列表
  html = html.replace(/^(\d+)\. (.+)$/gm, '<li class="markdown-ordered-list-item">$2</li>')
  
  // 处理引用
  html = html.replace(/^> (.+)$/gm, '<blockquote class="markdown-blockquote">$1</blockquote>')
  
  // 处理链接
  html = html.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" class="markdown-link">$1</a>')
  
  // 处理换行
  html = html.replace(/\n/g, '<br class="markdown-br" />')
  
  return html
}

/**
 * 检查文本是否包含Markdown语法
 */
export const hasMarkdown = (text: string): boolean => {
  if (!text) return false
  
  const markdownPatterns = [
    /^#{1,6}\s+.+$/m, // 标题
    /\*\*.+?\*\*/,    // 粗体
    /\*.+?\*/,        // 斜体
    /`[^`]+`/,        // 行内代码
    /```[\s\S]*?```/, // 代码块
    /^-\s+.+$/m,      // 无序列表
    /^\*\s+.+$/m,     // 无序列表（星号）
    /^\d+\.\s+.+$/m,  // 有序列表
    /^>\s+.+$/m,      // 引用
    /\[.+\]\(.+\)/,   // 链接
    /^[-*_]{3,}$/m    // 分割线
  ]
  
  return markdownPatterns.some(pattern => pattern.test(text))
}

/**
 * 去除Markdown格式，返回纯文本但保留基本结构
 * 移除Markdown标记，但保留换行和列表结构
 */
export const stripMarkdown = (text: string): string => {
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

/**
 * 格式化纯文本，添加段落分隔和列表缩进
 * 将连续的文本按自然段落分割，并添加适当的格式
 */
export const formatPlainText = (text: string): string => {
  if (!text) return ''
  
  // 先去除Markdown格式
  let result = stripMarkdown(text)
  
  // 按换行分割，处理空行和段落
  const lines = result.split('\n')
  const formattedLines: string[] = []
  let inParagraph = false
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    
    if (!line) {
      // 空行，结束当前段落
      if (inParagraph) {
        formattedLines.push('</p><p>')
        inParagraph = false
      }
      continue
    }
    
    // 检查是否是列表项
    const isListItem = line.startsWith('• ') || /^\d+\.\s/.test(line)
    
    if (isListItem) {
      // 列表项，结束前一个段落（如果有）
      if (inParagraph) {
        formattedLines.push('</p>')
        inParagraph = false
      }
      // 添加列表项
      formattedLines.push(`<li>${line}</li>`)
    } else {
      // 普通文本行
      if (!inParagraph) {
        formattedLines.push('<p>')
        inParagraph = true
      }
      formattedLines.push(line)
    }
  }
  
  // 结束最后一个段落
  if (inParagraph) {
    formattedLines.push('</p>')
  }
  
  // 合并结果
  let formattedText = formattedLines.join(' ')
  
  // 清理多余的标签
  formattedText = formattedText.replace(/<\/p><p>/g, '</p>\n<p>')
  formattedText = formattedText.replace(/<li>/g, '\n<li>')
  formattedText = formattedText.replace(/<\/li>/g, '</li>\n')
  
  // 确保代码块有适当的换行
  formattedText = formattedText.replace(/【代码】/g, '\n<pre><code>')
  formattedText = formattedText.replace(/【\/代码】/g, '</code></pre>\n')
  
  return formattedText.trim()
}

/**
 * 简化的Markdown渲染函数 - 使用纯文本格式化替代HTML标签
 * 返回适合微信小程序Text组件渲染的文本
 */
export const renderFormattedText = (text: string): string => {
  if (!text) return ''
  
  // 先去除Markdown格式
  let result = stripMarkdown(text)
  
  // 按换行分割，处理段落和列表
  const lines = result.split('\n')
  const formattedLines: string[] = []
  
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

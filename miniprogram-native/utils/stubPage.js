/**
 * 生成占位页面的 Page 配置
 * 用于第1步占位，后续步骤会替换为完整实现
 */
function createStubPage(pageId, title) {
  return {
    data: { pageId, title, placeholder: true },
    onLoad() {
      if (title && typeof wx.setNavigationBarTitle === 'function') {
        wx.setNavigationBarTitle({ title })
      }
    }
  }
}

module.exports = { createStubPage }

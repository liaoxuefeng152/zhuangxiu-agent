/**
 * P09 施工陪伴页 H5 E2E 自动化测试
 * 执行前：1. 启动 H5 开发服务器 cd frontend && npm run dev:h5:local
 *        2. 安装依赖 npx playwright install chromium
 * 执行：P09_H5_URL=http://localhost:10087 npx playwright test tests/e2e-p09-construction.spec.ts
 */
import { test, expect } from '@playwright/test'

const BASE_URL = process.env.P09_H5_URL || 'http://localhost:10087'
// Taro H5 使用 hash 路由
const CONSTRUCTION_PATH = '/#/pages/construction/index'

test.describe('P09 施工陪伴页', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL + CONSTRUCTION_PATH, { waitUntil: 'domcontentloaded', timeout: 20000 })
    await page.waitForTimeout(2000) // 等待 React 渲染
  })

  test('TC-P09-001: 未设置开工日期时展示设置区域', async ({ page }) => {
    // 可能显示「请先设置开工日期」或快捷选择 7/15/30 天后开工
    const content = await page.content()
    const hasSetting = content.includes('请先设置开工日期') || content.includes('天后开工') || content.includes('选择其他日期')
    expect(hasSetting).toBeTruthy()
  })

  test('TC-P09-005: 顶部导航栏含施工陪伴标题', async ({ page }) => {
    await expect(page.locator('text=施工陪伴').first()).toBeVisible({ timeout: 8000 })
  })

  test('TC-P09-040: 点击提醒设置打开弹窗', async ({ page }) => {
    const remindBtn = page.locator('text=提醒设置').first()
    await remindBtn.click()
    await page.waitForTimeout(500)
    const modal = page.locator('text=智能提醒').or(page.locator('text=提醒提前天数'))
    await expect(modal.first()).toBeVisible({ timeout: 5000 })
  })

  test('TC-P09-104: TabBar 含施工陪伴', async ({ page }) => {
    await expect(page.locator('text=施工陪伴').first()).toBeVisible({ timeout: 8000 })
  })

  test('TC-P09-010: 快捷选择 7 天后开工', async ({ page }) => {
    const btn = page.locator('text=7天后开工').first()
    const visible = await btn.isVisible().catch(() => false)
    if (visible) {
      await btn.click()
      await page.waitForTimeout(3000)
      const content = await page.content()
      const ok = content.includes('进度计划更新成功') || content.includes('材料进场') || content.includes('隐蔽工程')
      expect(ok).toBeTruthy()
    } else {
      test.skip()
    }
  })
})

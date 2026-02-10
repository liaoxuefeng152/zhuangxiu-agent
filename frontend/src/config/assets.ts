/**
 * 静态资源配置
 * - 开发阶段：使用本地 assets
 * - 上线后可切换阿里云 OSS，仅需修改 OSS_BASE
 *
 * 注意：TabBar 图标必须使用本地路径，不支持网络图片
 */

/** 阿里云 OSS 基础地址，通过环境变量 TARO_APP_OSS_BASE_URL 配置 */
export const OSS_BASE = process.env.TARO_APP_OSS_BASE_URL || ''

/** TabBar 图标（必须本地，微信小程序限制） */
export const TABBAR = {
  home: 'assets/tabbar/home.png',
  homeActive: 'assets/tabbar/home-active.png',
  construction: 'assets/tabbar/construction.png',
  constructionActive: 'assets/tabbar/construction-active.png',
  profile: 'assets/tabbar/profile.png',
  profileActive: 'assets/tabbar/profile-active.png'
} as const

/**
 * 获取图片 URL
 * @param path 相对路径，如 'banner1.png'
 * @returns 完整 URL（OSS 或本地）
 */
export function getImageUrl(path: string): string {
  if (OSS_BASE) {
    return `${OSS_BASE.replace(/\/$/, '')}/${path.replace(/^\//, '')}`
  }
  return `/${path}`.replace(/\/+/g, '/')
}

/**
 * 首页轮播图 - 阿里云 OSS 地址
 * 配置方式：在 .env.development / .env.production 中设置 TARO_APP_OSS_BASE_URL
 * 图片路径：banners/banner1.png、banners/banner2.png、banners/banner3.png
 */
const OSS_BANNER_BASE = process.env.TARO_APP_OSS_BASE_URL || ''

export const BANNER_IMAGES: string[] = [
  OSS_BANNER_BASE ? `${OSS_BANNER_BASE.replace(/\/$/, '')}/banners/banner1.png` : '',
  OSS_BANNER_BASE ? `${OSS_BANNER_BASE.replace(/\/$/, '')}/banners/banner2.png` : '',
  OSS_BANNER_BASE ? `${OSS_BANNER_BASE.replace(/\/$/, '')}/banners/banner3.png` : ''
]

/** 是否使用真实轮播图（OSS 有配置时启用） */
export const USE_BANNER_IMAGES = BANNER_IMAGES.some((url) => !!url)

/** 示例图 URL（PRD D02/D05） */
const OSS_EXAMPLE_BASE = process.env.TARO_APP_OSS_BASE_URL || ''
export const EXAMPLE_IMAGES = {
  company: OSS_EXAMPLE_BASE ? `${OSS_EXAMPLE_BASE.replace(/\/$/, '')}/examples/company_sample.png` : '',
  quote: OSS_EXAMPLE_BASE ? `${OSS_EXAMPLE_BASE.replace(/\/$/, '')}/examples/quote_sample.png` : '',
  contract: OSS_EXAMPLE_BASE ? `${OSS_EXAMPLE_BASE.replace(/\/$/, '')}/examples/contract_sample.png` : '',
  acceptance: OSS_EXAMPLE_BASE ? `${OSS_EXAMPLE_BASE.replace(/\/$/, '')}/examples/acceptance_sample.png` : ''
}

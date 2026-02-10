import Taro from '@tarojs/taro'

const TAB_HOME = '/pages/index/index'
const TAB_CONSTRUCTION = '/pages/construction/index'
const TAB_PROFILE = '/pages/profile/index'

/** Delay (ms) before switchTab to avoid timeout when called from modal/actionSheet/toast */
const DEFER_MS = 120
/** Retry delay (ms) if first switchTab fails with timeout */
const RETRY_MS = 300

export { TAB_HOME, TAB_CONSTRUCTION, TAB_PROFILE }

export type SafeSwitchTabOptions = {
  /** Defer switchTab by this many ms (default 120). Use when called from showModal/showActionSheet/showToast callback. */
  defer?: number
  /** On fail (e.g. timeout), retry once after retryMs. Default true. */
  retry?: boolean
}

/**
 * WeChat Mini Program switchTab can fail with "switchTab:fail timeout" when:
 * - Called synchronously from modal/actionSheet/toast success callback
 * - Target tab page is slow to load
 * This helper defers the call and retries once on failure.
 */
export function safeSwitchTab(
  url: string,
  options: SafeSwitchTabOptions = {}
): void {
  const { defer = DEFER_MS, retry = true } = options

  const doSwitch = () => {
    Taro.switchTab({
      url,
      fail: (err) => {
        if (retry && err?.errMsg?.includes('timeout')) {
          setTimeout(() => {
            Taro.switchTab({ url })
          }, RETRY_MS)
        }
      }
    })
  }

  if (defer > 0) {
    setTimeout(doSwitch, defer)
  } else {
    doSwitch()
  }
}

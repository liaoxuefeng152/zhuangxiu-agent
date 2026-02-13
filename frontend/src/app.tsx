import './process-shim'
import * as React from 'react'
import Taro from '@tarojs/taro'
import './app.scss'
import { Provider, useSelector, useDispatch } from 'react-redux'
import store, { RootState } from './store'
import { setNetworkError } from './store/slices/networkSlice'
import NetworkError from './components/NetworkError'
import { env } from './config/env'
import { setAuthToken } from './services/api'

/** 小程序页面销毁后定时器回调可能触发，导致 __subPageFrameEndTime__ of null；此处兜底吞掉该框架报错 */
function useSuppressSubPageFrameError() {
  React.useEffect(() => {
    const raw = (typeof window !== 'undefined' && (window as any).onerror) as ((msg: string, url?: string, line?: number, col?: number, err?: Error) => boolean) | undefined
    const handler = (msg: string, url?: string, line?: number, col?: number, err?: Error) => {
      if (typeof msg === 'string' && msg.includes('__subPageFrameEndTime__')) return true
      if (raw) return raw(msg, url, line, col, err)
      return false
    }
    ;(window as any).onerror = handler
    return () => { (window as any).onerror = raw }
  }, [])
}

/** 小程序开发/体验版：无 token 时用 dev_weapp_mock 静默登录，便于在微信开发者工具里测试 */
function useDevSilentLogin() {
  React.useEffect(() => {
    if (process.env.TARO_ENV !== 'weapp' || process.env.NODE_ENV === 'production') return
    const token = Taro.getStorageSync('token') || Taro.getStorageSync('access_token')
    if (token) return
    
    // 静默登录，失败时不提示用户（开发环境）
    Taro.request({
      url: `${env.apiBaseUrl}/users/login`,
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: { code: 'dev_weapp_mock' }
    }).then((res) => {
      const d = (res.data as any)?.data ?? res.data
      const t = d?.access_token ?? d?.token
      const uid = d?.user_id
      if (t && uid != null) {
        setAuthToken(t, String(uid))
        console.log('[自动登录] 开发环境自动登录成功')
      } else {
        console.warn('[自动登录] 登录响应格式异常:', d)
      }
    }).catch((err) => {
      // 开发环境记录错误日志，但不打扰用户
      console.error('[自动登录] 开发环境自动登录失败:', err)
      // 如果后端服务未启动，可以提示用户
      if (process.env.NODE_ENV === 'development') {
        console.warn('[自动登录] 提示：请确保后端服务已启动，或手动在"我的"页面登录')
      }
    })
  }, [])
}

function AppContent({ children }: React.PropsWithChildren<{}>) {
  useDevSilentLogin()
  useSuppressSubPageFrameError()
  const networkError = useSelector((s: RootState) => s.network.error)
  const dispatch = useDispatch()

  const handleRetry = () => {
    dispatch(setNetworkError(false))
    Taro.reLaunch({ url: Taro.getCurrentInstance().router?.path || '/pages/index/index' })
  }

  return (
    <>
      {children}
      <NetworkError visible={networkError} onRetry={handleRetry} />
    </>
  )
}

function App({ children }: React.PropsWithChildren<{}>) {
  return (
    <Provider store={store}>
      <AppContent>{children}</AppContent>
    </Provider>
  )
}

export default App

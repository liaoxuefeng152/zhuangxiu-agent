/**
 * 小程序运行时 process polyfill
 * 微信小程序无 process 对象，DefinePlugin 未替换到的 process.env 会报错
 */
declare const wx: unknown
declare const global: unknown
declare const globalThis: unknown

const g = (typeof globalThis !== 'undefined' ? globalThis : typeof global !== 'undefined' ? global : typeof self !== 'undefined' ? self : {}) as Record<string, unknown>
if (g && typeof g.process === 'undefined') {
  g.process = {
    env: Object.create(null) as Record<string, string>
  }
}

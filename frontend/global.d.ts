/// <reference types="@tarojs/taro" />
/// <reference types="@tarojs/react" />
/// <reference types="@tarojs/components" />

declare module '*.png';
declare module '*.gif';
declare module '*.jpg';
declare module '*.jpeg';
declare module '*.svg';
declare module '*.css';
declare module '*.less';
declare module '*.scss';
declare module '*.sass';
declare module '*.styl';

declare namespace NodeJS {
  interface ProcessEnv {
    TARO_ENV: 'weapp' | 'swan' | 'alipay' | 'h5' | 'rn' | 'tt' | 'quickapp' | 'qq' | 'jd'
    /** 阿里云 OSS 根地址，用于轮播图等静态资源 */
    TARO_APP_OSS_BASE_URL?: string
    /** 后端 API 根地址 */
    TARO_APP_API_BASE_URL?: string
  }
}

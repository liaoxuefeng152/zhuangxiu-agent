# 装修避坑管家 - Bug 报告

> 基于代码审查，未找到 PRD/原型文档，按现有实现梳理的潜在问题

## 高优先级

### 1. API 响应格式不兼容
**位置**: `frontend/src/services/api.ts` 响应拦截器

**问题**: 后端部分接口（如 login、profile、companies/scan、quotes/quote 等）使用 `response_model` 直接返回数据 `{ access_token, user_id, ... }`，无 `code` 包装。而拦截器只认可 `code === 0`，导致这些接口被误判为失败并 toast「请求失败」。

**影响**: onboarding 登录、公司检测、报价/合同分析、用户信息等核心功能可能失败。

### 2. Onboarding 登录逻辑
**位置**: `frontend/src/pages/onboarding/index.tsx`

**问题**: 使用 `userApi.login(res.code)`，依赖 axios 拦截器。login 接口返回格式与拦截器不匹配，登录会静默失败（catch 后继续跳转首页，用户未真正登录）。

### 3. 微信小程序 axios 兼容性
**位置**: `frontend/src/services/api.ts`（全局使用 axios）

**问题**: 微信小程序对 axios/XMLHttpRequest 存在限制，部分 API 可能无法正常请求。首页已移除 `messageApi.getUnreadCount()` 规避，但公司检测、报价上传、报告列表等仍使用 axios。

## 中优先级

### 4. 文件上传未带 Authorization
**位置**: `quoteApi.upload`、`contractApi.upload`、`constructionPhotoApi.upload`、`acceptanceApi.uploadPhoto`

**问题**: 仅传 `X-User-Id`，未传 `Authorization: Bearer ${token}`。若后端仅校验 JWT，未登录或 token 失效时上传会 401。

### 5. reportApi.downloadPdf
**位置**: `frontend/src/services/api.ts`

**问题**: `Taro.downloadFile` 的 header 支持因平台而异，且仅传 `X-User-Id`，未传 Authorization。

### 6. 报告列表 /report-list 数据解析
**位置**: `frontend/src/pages/report-list/index.tsx`

**问题**: 使用 `companyApi.getList()`、`quoteApi.getList()` 等，若后端返回格式为 `{ code, data }`，拦截器会返回 `data`；若为直接对象，则会报错。

## 低优先级

### 7. scroll-view padding 警告
**位置**: `pages/profile/index`

**问题**: 控制台提示 `the padding property is not yet supported in webview rendering mode`，可能影响样式。

### 8. 图片加载失败
**位置**: 首页轮播等

**问题**: OSS 图片 `banner2.png`、`banner3.png` 报 `ERR_CONNECTION_RESET`，可能是网络或 CDN 配置问题。

---

## 建议修复顺序
1. 修复 api.ts 响应拦截器，兼容「直接返回数据」与「{ code, data }」两种格式
2. 修复 onboarding 登录，改为与 profile 一致的 Taro.request 直接请求
3. 评估将关键 API 从 axios 迁移到 Taro.request，提高小程序兼容性

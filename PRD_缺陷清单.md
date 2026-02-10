# 装修避坑管家 - PRD/原型 缺陷清单

> 基于《产品需求文档（PRD）V2.1》和《微信小程序原型文档（V11.1）》逐项核对

## 一、高优先级缺陷

### D01 个人中心用户信息不更新
**PRD**: FR-028 用户信息展示（头像、脱敏手机号、会员标识）  
**位置**: `frontend/src/pages/profile/index.tsx` loadUserInfo  
**问题**: 后端 `/users/profile` 直接返回 `UserProfileResponse`（无 `code` 包装），代码用 `res.data?.code === 0` 判断，导致登录后用户信息永不更新。  
**修复**: 兼容直接返回格式，如 `res.data?.user_id` 存在即视为成功。

### D02 引导页能力项预览无示例图
**PRD**: FR-002 点击能力项「点击预览示例」展示对应功能的示例图  
**位置**: `frontend/src/pages/onboarding/index.tsx` showPreview  
**问题**: 当前仅弹出文字说明弹窗，未展示报价单/合同/验收分析示例图。  
**修复**: 需补充示例图资源，弹窗中展示图片并支持双指缩放。

### D03 引导页缺少进度提醒权限请求
**PRD**: FR-003 跳转首页后弹出「是否允许发送进度提醒」权限请求  
**位置**: `frontend/src/pages/onboarding/index.tsx` goToHome  
**问题**: 跳转首页后未请求订阅消息/通知权限。  
**修复**: 在 goToHome 后调用 `wx.requestSubscribeMessage` 或等效权限请求。

### D04 首页消息小红点未实现
**PRD**: FR-010 有新消息时右上角铃铛显示小红点  
**位置**: `frontend/src/pages/index/index.tsx`  
**问题**: `hasNewMessage` 恒为 false，未调用 messageApi.getUnreadCount()（因 axios 兼容性被移除）。  
**修复**: 使用 Taro.request 直接请求未读数量，或恢复并解决 axios 兼容性。

### D05 报价单/合同上传页示例图为文字
**PRD**: FR-018 点击示例图弹出清晰示例图弹窗，支持双指缩放  
**位置**: `frontend/src/pages/quote-upload/index.tsx`、`contract-upload/index.tsx`  
**问题**: 示例图入口仅为 showModal 文字说明，无图片展示。  
**修复**: 增加示例图资源，弹窗展示图片并支持缩放。

---

## 二、中优先级缺陷

### D06 施工照片使用本地存储
**PRD**: P15/P17/P29 照片按施工阶段分类存储，支持批量删除/移动  
**位置**: `frontend/src/pages/photo/index.tsx`  
**问题**: 照片存于本地 storage，未对接后端 construction-photos API，换设备/清缓存会丢失。  
**修复**: 对接 /construction-photos 接口实现上传、列表、删除、移动。

### D07 施工陪伴使用本地存储
**PRD**: P09 FR-021~FR-027 开工日期、进度阶段、状态更新  
**位置**: `frontend/src/pages/construction/index.tsx`  
**问题**: 进度数据存本地 storage，未调用 constructionApi.getSchedule 等接口。  
**修复**: 对接 /constructions/schedule 等 API，实现多端同步。

### D08 报告列表无搜索
**PRD**: FR-029 报告列表支持筛选/搜索，可按类型/时间筛选，输入公司名/文件名搜索  
**位置**: `frontend/src/pages/report-list/index.tsx`  
**问题**: 仅有类型 Tab 筛选，无时间筛选、无搜索框。  
**修复**: 增加时间筛选、搜索输入框及对应 API 参数。

### D09 检测/上传进度页无两段进度
**PRD**: FR-019 文件上传时进度条分两段（上传进度→分析进度）  
**位置**: `frontend/src/pages/scan-progress/index.tsx`  
**问题**: 单一模拟进度条，未区分上传与分析两阶段。  
**修复**: 报价/合同类型时展示两段进度（上传 0–100% → 分析 0–100%）。

### D10 验收拍照跳转目标
**PRD**: P09 验收辅助「AI验收」跳转 P30 验收分析页，「拍照留证」跳转 P15 拍照页  
**位置**: `frontend/src/pages/construction/index.tsx`  
**问题**: 需确认「拍照留证」跳转目标。当前 photo 页合并了 P15+P17 功能。  
**状态**: 待确认，可能与设计一致。

---

## 三、低优先级 / 差异说明

### D11 倒计时秒数
**PRD**: FR-003 写「3秒倒计时」  
**原型**: P01 写「5秒倒计时」  
**实现**: 5 秒  
**结论**: 以原型为准，实现正确。

### D12 Tabbar 数量
**PRD**: 2.1 页面清单未明确 Tabbar 数量  
**原型**: P02 写 4 个（首页、施工陪伴、报告中心、我的）  
**实现**: 3 个（首页、施工陪伴、我的），报告中心在四宫格入口  
**结论**: 实现可接受，报告中心通过快捷入口进入。

### D13 轮播图加载失败
**现象**: OSS 图片 banner2/banner3 报 ERR_CONNECTION_RESET  
**PRD**: FR-005 轮播图加载失败显示占位图  
**状态**: 需检查 OSS 配置与网络，占位逻辑已存在（USE_BANNER_IMAGES 为 false 时显示背景）。

### D14 scroll-view padding 警告
**现象**: 控制台提示 padding 在 webview 模式不支持  
**位置**: profile 页  
**影响**: 样式可能异常，需验证。

---

## 四、修复建议优先级

| 优先级 | 缺陷ID | 说明 | 状态 |
|--------|--------|------|------|
| P0 | D01 | 个人中心用户信息不更新，影响登录后体验 | ✅ 已修复 |
| P1 | D04 | 消息小红点，影响核心入口可见性 | ✅ 已修复 |
| P1 | D03 | 进度提醒权限，影响运营能力 | ✅ 已修复 |
| P2 | D06, D07 | 施工照片/进度未持久化，数据易丢失 | ✅ 已修复 |
| P2 | D02, D05 | 示例图缺失，影响首次使用理解 | ✅ 已修复 |
| P3 | D08, D09 | 报告搜索、两段进度，体验优化 | ✅ 已修复 |

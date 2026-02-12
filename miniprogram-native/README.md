# 装修决策Agent - 微信小程序原生版

基于原型文档 V15.3，使用 WXML/WXSS/JS/JSON 原生开发。

## 项目结构

```
miniprogram-native/
├── app.js              # 全局逻辑（请求封装、权限、状态）
├── app.json            # 路由、tabBar、窗口配置
├── app.wxss            # 全局样式、设计变量、深色模式
├── project.config.json # 微信开发者工具配置
├── assets/tabbar/      # TabBar 图标
├── pages/              # 页面（P01-P36，P31为弹窗组件）
├── utils/              # 工具函数
└── scripts/            # 构建脚本
```

## 调试说明

1. 用**微信开发者工具**打开 `miniprogram-native` 目录
2. 填写 AppID（可先用测试号）
3. 将 `app.js` 中 `API_BASE` 改为你的后端地址（开发可填 `http://localhost:8000/api/v1`）
4. 首次进入会跳转 P01 引导页，点击「开始使用」进入 P02 首页
5. TabBar：首页 / 施工陪伴 / 我的

## 开发进度

- [x] 第1步：全局配置 app.json / app.wxss / app.js
- [x] 第2步：P02 首页、P09 施工陪伴、P30 验收报告
- [x] 第3步：P15 拍照、P19 提醒设置、P28 照片管理
- [x] 第4步：P32 分享、P33 网络异常、P34 数据统计
- [x] 第5步：P24 订单、P26 会员、P27 解锁
- [x] 第6步：其余辅助页面
- [ ] 第7步：全量优化

## 技术规范

- 基础库 2.10.0+
- 尺寸单位 rpx
- 主色 #007AFF，成功 #00CC66，警示 #FF9900，危险 #FF3333

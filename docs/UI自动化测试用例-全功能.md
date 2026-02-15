# 装修避坑管家 - 全部功能 UI 自动化测试用例

**版本**：V1.0  
**适用**：微信小程序 Minium 自动化 / 手工 UI 测试  
**前置**：微信开发者工具已打开项目（frontend 编译后 dist）、后端服务可用（如 120.26.201.61:8001）  
**更新日期**：2026-02-14

---

## 一、说明

| 字段 | 说明 |
|------|------|
| 用例编号 | UI-模块-序号 |
| 页面 | 对应 app.config 中的页面路径 |
| 优先级 | P0=核心流程 P1=重要 P2=一般 |
| 操作步骤 | 用户在界面上的操作 + 预期界面/接口结果 |

---

## 二、引导与首页（P01/P02）

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-ONBOARD-01 | pages/onboarding/index | 引导页展示 | P0 | 首次启动小程序（清除 onboarding_completed） | 展示引导页，含「开始使用」「跳过」 |
| UI-ONBOARD-02 | pages/onboarding/index | 开始使用跳转 | P0 | 点击「开始使用」 | 跳转至首页 pages/index/index |
| UI-ONBOARD-03 | pages/onboarding/index | 跳过跳转 | P1 | 点击「跳过」 | 跳转至首页 |
| UI-ONBOARD-04 | pages/index/index | 已完引导不再展示 | P0 | 再次启动（已缓存 onboarding_completed） | 直接进入首页，不展示引导页 |
| UI-HOME-01 | pages/index/index | 首页 Tab 与入口 | P0 | 进入首页 | 顶部城市入口、消息图标；4 宫格（公司检测/报价分析/合同审核/AI 施工验收）；6 大阶段入口；轮播/会员卡片 |
| UI-HOME-02 | pages/index/index | 点击装修公司检测 | P0 | 点击「装修公司检测」 | 跳转 pages/company-scan/index |
| UI-HOME-03 | pages/index/index | 点击报价分析 | P0 | 点击「报价分析」 | 跳转 pages/quote-upload/index |
| UI-HOME-04 | pages/index/index | 点击合同审核 | P0 | 点击「合同审核」 | 跳转 pages/contract-upload/index |
| UI-HOME-05 | pages/index/index | 点击城市入口 | P1 | 点击顶部城市/定位 | 弹出城市选择或跳转 pages/city-picker/index |
| UI-HOME-06 | pages/index/index | 点击消息图标 | P1 | 点击右上角消息 | 跳转 pages/message/index |
| UI-HOME-07 | pages/index/index | TabBar 我的 | P0 | 点击 TabBar「我的」 | 切换至 pages/profile/index |

---

## 三、公司检测（P03/P04/P11）

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-COMPANY-01 | pages/company-scan/index | 公司名输入 | P0 | 输入 ≥3 字公司名 | 输入框可输入，可触发搜索或展示匹配列表 |
| UI-COMPANY-02 | pages/company-scan/index | 提交检测 | P0 | 选择/输入公司名后点击提交 | 跳转 pages/scan-progress/index，展示检测中状态 |
| UI-COMPANY-03 | pages/scan-progress/index | 检测进度展示 | P0 | 在检测中页 | 有进度提示或加载动画 |
| UI-COMPANY-04 | pages/scan-progress/index | 检测完成跳转 | P0 | 等待检测完成 | 自动或点击进入报告详情（或 report-detail） |
| UI-COMPANY-05 | pages/company-scan/index | 历史记录入口 | P2 | 点击历史记录 | 展示历史检测列表或弹窗 |

---

## 四、报价单（P05/P06/P12）

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-QUOTE-01 | pages/quote-upload/index | 上传入口展示 | P0 | 进入报价单页 | 有上传区域或「选择文件/拍照」按钮 |
| UI-QUOTE-02 | pages/quote-upload/index | 选择文件上传 | P0 | 选择 PDF/图片（≤10MB） | 上传请求成功，进入分析中或结果页 |
| UI-QUOTE-03 | pages/quote-upload/index | 格式校验 | P1 | 选择非支持格式 | Toast 提示仅支持某格式 |
| UI-QUOTE-04 | pages/report-detail/index | 报价报告展示 | P0 | 分析完成后进入报告详情 | 展示风险/漏项/虚高等内容或解锁入口 |

---

## 五、合同审核（P07/P08/P13）

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-CONTRACT-01 | pages/contract-upload/index | 上传入口展示 | P0 | 进入合同页 | 有上传区域或选择文件按钮 |
| UI-CONTRACT-02 | pages/contract-upload/index | 选择文件上传 | P0 | 选择 PDF/图片上传 | 上传成功，进入分析中或结果页 |
| UI-CONTRACT-03 | pages/report-detail/index | 合同报告展示 | P0 | 分析完成后进入报告详情 | 展示合同风险/条款/修正建议或解锁入口 |

---

## 六、施工陪伴（P09）

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-CONST-01 | pages/construction/index | 施工页展示 | P0 | 点击 TabBar「施工陪伴」 | 进入 pages/construction/index，展示 6 阶段或开工日期设置 |
| UI-CONST-02 | pages/construction/index | 设置开工日期 | P0 | 未设置时点击设置开工日期，选择日期并确认 | 保存成功，展示 S00～S05 阶段卡片 |
| UI-CONST-03 | pages/construction/index | 阶段卡片展示 | P0 | 已设置开工日期 | 每个阶段有名称、状态、操作按钮（人工核对/AI 验收等） |
| UI-CONST-04 | pages/construction/index | S00 人工核对入口 | P0 | 点击 S00「人工核对」 | 跳转 pages/material-check/index |
| UI-CONST-05 | pages/construction/index | S01～S05 AI 验收入口 | P0 | S00 已完成后点击某阶段「AI 验收」 | 跳转 pages/acceptance/index 或对应验收页 |
| UI-CONST-06 | pages/construction/index | 流程互锁 | P0 | S00 未完成时点击 S01 验收 | 置灰或 Toast「请先完成材料进场人工核对」 |

---

## 七、材料核对（P37）

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-MATERIAL-01 | pages/material-check/index | 材料清单展示 | P0 | 进入材料核对页 | 展示材料清单或「未同步到材料清单」提示 |
| UI-MATERIAL-02 | pages/material-check/index | 拍照/上传 | P0 | 点击某材料「拍照/上传」 | 唤起相机或相册，上传后展示缩略图 |
| UI-MATERIAL-03 | pages/material-check/index | 核对通过 | P0 | 所有项已上传后点击「核对通过」 | 提交成功，Toast 或返回施工页 |
| UI-MATERIAL-04 | pages/material-check/index | 核对未通过 | P1 | 点击「核对未通过」并输入原因 | 提交成功，状态为待整改 |

---

## 八、验收分析（P30）

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-ACCEPT-01 | pages/acceptance/index | 验收页展示 | P0 | 从施工页进入验收 | 展示阶段选择或上传照片区域 |
| UI-ACCEPT-02 | pages/acceptance/index | 上传验收照片 | P0 | 选择 1～9 张照片上传 | 上传成功，可提交分析 |
| UI-ACCEPT-03 | pages/acceptance/index | 提交验收分析 | P0 | 上传后点击提交分析 | 分析中或跳转结果页，展示问题与建议 |

---

## 九、施工照片

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-PHOTO-01 | pages/construction/index 或 photo | 施工照片入口 | P1 | 在施工页点击拍照/照片 | 进入拍照页或 pages/photo-gallery/index |
| UI-PHOTO-02 | pages/photo-gallery/index | 照片列表 | P1 | 进入照片列表 | 按阶段展示已上传照片 |

---

## 十、消息中心（P14）

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-MSG-01 | pages/message/index | 消息列表展示 | P0 | 进入消息页 | 展示消息列表或空状态 |
| UI-MSG-02 | pages/message/index | 标记已读 | P1 | 点击「全部已读」或单条 | 未读数更新或红点消失 |

---

## 十一、我的（P19/P20）

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-PROFILE-01 | pages/profile/index | 我的页展示 | P0 | 点击 TabBar「我的」 | 展示头像、昵称、订单/报告/设置等入口 |
| UI-PROFILE-02 | pages/profile/index | 报告列表/数据管理 | P0 | 点击「我的报告」或「数据管理」 | 跳转 pages/report-list/index 或 pages/data-manage/index |
| UI-PROFILE-03 | pages/profile/index | 设置 | P1 | 点击设置 | 跳转 pages/settings/index |
| UI-PROFILE-04 | pages/profile/index | 意见反馈 | P1 | 点击意见反馈 | 跳转 pages/feedback/index |
| UI-PROFILE-05 | pages/profile/index | 会员/订单 | P1 | 点击会员或订单 | 跳转 pages/membership/index 或 pages/order-list/index |

---

## 十二、数据管理（P18/P29）

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-DATA-01 | pages/data-manage/index | 报告列表展示 | P0 | 进入数据管理 | 展示报告列表（公司/报价/合同/验收）或 Tab |
| UI-DATA-02 | pages/data-manage/index | 回收站入口 | P1 | 点击回收站 | 跳转 pages/recycle-bin/index |

---

## 十三、支付与订单

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-PAY-01 | pages/payment/index | 支付页展示 | P0 | 从报告解锁进入支付 | 展示金额、支付方式、支付按钮 |
| UI-PAY-02 | pages/order-list/index | 订单列表 | P1 | 进入订单列表 | 展示订单列表或空状态 |

---

## 十四、材料库与反馈

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-FEEDBACK-01 | pages/feedback/index | 反馈提交 | P1 | 输入内容并提交 | Toast 提交成功 |
| UI-MATLIB-01 | （若入口在材料核对等） | 材料库搜索 | P2 | 搜索材料关键词 | 展示材料列表或无结果提示 |

---

## 十五、其他

| 编号 | 页面 | 用例名称 | 优先级 | 操作步骤 | 预期结果 |
|------|------|----------|--------|----------|----------|
| UI-SETTINGS-01 | pages/settings/index | 设置页展示 | P1 | 进入设置 | 展示通知、隐私、关于等项 |
| UI-ABOUT-01 | pages/about/index | 关于页 | P2 | 进入关于 | 展示版本与说明 |
| UI-NEUTRAL-01 | pages/neutral-statement/index | 中立声明 | P2 | 若有入口进入 | 展示中立声明内容 |

---

## 十六、执行说明（Minium）

1. **环境**：Python 3.8+，`pip install minium`；微信开发者工具打开 `frontend` 项目（编译后为 dist），并开启「服务端口」。
2. **运行**：在项目根目录执行 `python tests/ui/run_ui_tests.py`（或见脚本内说明）。
3. **注意**：Minium 需连接开发者工具，无图形界面或未开工具时脚本会提示「请先打开微信开发者工具并加载小程序」。

---

**用例总数**：约 50+ 条，覆盖引导、首页、公司检测、报价、合同、施工、材料核对、验收、消息、我的、数据管理、支付、反馈等全部功能入口与主流程。

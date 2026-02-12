# 装修避坑管家 - 后端 API 接口文档（完整版）

**版本**：V2.6.2（基于V2.6.1优化）  
**Base URL**：`/api/v1`  
**认证**：除登录、支付回调、健康检查外，请求头需携带 `Authorization: Bearer <access_token>`

---

## V2.6.2 更新说明

### API变更
- **删除接口**：`POST /api/v1/materials/verify`（已废弃）
- **替代方案**：统一使用 `PUT /api/v1/constructions/stage-status`（stage='S00', status='checked'）
- **影响范围**：材料进场核对功能，前端代码已更新

### 向后兼容
- V2.6.2完全兼容V2.6.1的所有功能
- 已删除的API前端已更新，不影响现有用户

---

## 一、通用说明

### 1.1 统一响应格式

```json
{
  "code": 0,
  "msg": "success",
  "data": { ... }
}
```

- `code`: 0 成功，非 0 或 HTTP 4xx/5xx 为失败  
- `msg`: 提示信息  
- `data`: 业务数据，可为 null  

### 1.2 错误响应

- 400：参数错误  
- 401：未登录或 Token 无效  
- 403：无权限（如报告未解锁）  
- 404：资源不存在  
- 409：业务冲突（如流程互锁：请先完成上一阶段）  
- 500：服务器错误  

---

## 二、用户与认证

### 2.1 微信登录

- **POST** `/users/login`  
- **认证**：否  
- **请求体**：`{ "code": "微信 jscode2session 的 code" }`  
- **响应**：`{ "access_token", "user_id", "openid", "nickname", "avatar_url", "is_member" }`  

### 2.2 获取当前用户信息

- **GET** `/users/profile`  
- **响应**：`user_id, openid, nickname, avatar_url, phone, phone_verified, is_member, city_code, city_name, created_at`  

### 2.3 更新用户信息

- **PUT** `/users/profile`  
- **Query**：`nickname`, `avatar_url`（可选）  
- **响应**：`{ "data": { "user_id" } }`  

### 2.4 获取用户设置（P19）

- **GET** `/users/settings`  
- **响应**：`storage_duration_months, reminder_days_before(1/2/3/5/7), notify_progress, notify_acceptance, notify_system`  

### 2.5 更新用户设置

- **PUT** `/users/settings`  
- **Query**：`storage_duration_months`(3|6|12), `reminder_days_before`(1|2|3|5|7), `notify_progress`, `notify_acceptance`, `notify_system`（均可选）  

---

## 三、公司检测（P03/P04/P11）

### 3.1 公司搜索

- **GET** `/companies/search?keyword=xxx`  
- **响应**：`data.list` 匹配的公司/历史记录  

### 3.2 提交检测

- **POST** `/companies/scan`  
- **请求体**：`{ "company_name": "公司名称" }`  
- **响应**：`id, company_name, risk_level, risk_score, status, created_at`  

### 3.3 获取检测结果

- **GET** `/companies/scan/{scan_id}`  
- **响应**：单条扫描详情（含 risk_reasons, legal_risks 等）  

### 3.4 扫描记录列表

- **GET** `/companies/scans`  
- **响应**：`data.list` 当前用户的扫描记录列表  

---

## 四、报价单（P05/P06/P12/P18）

### 4.1 上传报价单

- **POST** `/quotes/upload`  
- **Body**：multipart/form-data 或 `file_url, file_name, file_size, file_type`  
- **响应**：`task_id, file_name, file_type, status`  

### 4.2 获取报价单分析结果（V2.6.2优化：返回分析进度）

- **GET** `/quotes/quote/{quote_id}`  
- **响应**：分析结果（risk_score, high_risk_items, warning_items, missing_items, overpriced_items, total_price, is_unlocked, **analysis_progress** 等）
- **analysis_progress**：`{"step": "ocr|analyzing|generating|completed", "progress": 0-100, "message": "提示信息"}`  

### 4.3 报价单列表

- **GET** `/quotes/list`  
- **响应**：`data.list` 报价单列表  

---

## 五、合同（P07/P08/P13/P18）

### 5.1 上传合同

- **POST** `/contracts/upload`  
- **Body**：同报价单  
- **响应**：`task_id, file_name, file_type, status`  

### 5.2 获取合同分析结果（V2.6.2优化：返回分析进度）

- **GET** `/contracts/contract/{contract_id}`  
- **响应**：risk_level, risk_items, unfair_terms, missing_terms, suggested_modifications, is_unlocked, **analysis_progress** 等
- **analysis_progress**：`{"step": "ocr|analyzing|generating|completed", "progress": 0-100, "message": "提示信息"}`  

### 5.3 合同列表

- **GET** `/contracts/list`  
- **响应**：`data.list` 合同列表  

---

## 六、施工进度（P09）— 六阶段 S00～S05

### 6.1 获取进度计划

- **GET** `/constructions/schedule`  
- **响应**：`id, start_date, estimated_end_date, progress_percentage, is_delayed, delay_days, stages`  
- **stages**：每阶段含 `status, start_date, end_date, duration, locked`（locked 表示前置未通过不可操作）  

### 6.2 设置开工日期（V2.6.2优化：支持自定义阶段周期）

- **POST** `/constructions/start-date`  
- **请求体**：`{ "start_date": "YYYY-MM-DDTHH:mm:ss", "custom_durations": {"S00": 3, "S01": 7, ...} }`（custom_durations可选）  
- **响应**：`id, start_date, estimated_end_date, stages`
- **说明**：`custom_durations` 为可选参数，未指定的阶段使用默认周期  

### 6.3 更新阶段状态

- **PUT** `/constructions/stage-status`  
- **请求体**：`{ "stage": "S00|S01|...|S05", "status": "pending|checked|passed|need_rectify|pending_recheck|completed" }`  
- **说明**：S00 人工核对通过为 `checked`；S01～S05 验收通过为 `passed`。前置未通过返回 409。  

### 6.4 阶段时间校准

- **PUT** `/constructions/stage-calibrate`  
- **请求体**：`{ "stage": "S00|...|S05", "manual_start_date": "可选", "manual_acceptance_date": "可选" }`  
- **校验**：校准时间需晚于开工日期  

### 6.5 提醒计划查询（供 worker/前端）

- **GET** `/constructions/reminder-schedule?date=YYYY-MM-DD`  
- **响应**：`data.list` 该日应触达的提醒项，每项含 `stage, event_type(stage_start|stage_acceptance), planned_date, reminder_days_before`  

### 6.6 重置进度

- **DELETE** `/constructions/schedule`  
- **响应**：`msg: "重置成功"`  

---

## 七、支付与订单（P24/P25/P27/P28/P34）

### 7.1 创建订单

- **POST** `/payments/create`  
- **请求体**：`order_type, resource_type, resource_id`  
- **响应**：`order_id, order_no, order_type, amount, status`  

### 7.2 调起支付

- **POST** `/payments/pay`  
- **请求体**：`{ "order_id": 123 }`  
- **响应**：微信支付所需参数（pay_sign, timestamp, nonce_str 等）  

### 7.3 支付回调（微信服务器调用）

- **POST** `/payments/notify`  
- **认证**：否  
- **说明**：微信支付异步通知，需验签并更新订单状态  

### 7.4 订单列表

- **GET** `/payments/orders?page=1&page_size=20`  
- **响应**：`data.list` 订单列表  

### 7.5 订单详情

- **GET** `/payments/order/{order_id}`  
- **响应**：订单详情（order_no, amount, status, paid_at 等）  

### 7.6 申请退款

- **POST** `/payments/refund/apply`  
- **请求体**：`order_id, reason, note` 等  
- **响应**：退款申请结果  

### 7.7 退款状态

- **GET** `/payments/refund/status?order_id=xxx`  
- **响应**：退款状态  

---

## 八、消息中心（P14）

### 8.1 消息列表

- **GET** `/messages?category=progress|report|system&page=1&page_size=20`  
- **响应**：`data.list`（id, category, title, content, summary, is_read, link_url, created_at）, `total, page, page_size`  

### 8.2 未读数量

- **GET** `/messages/unread-count`  
- **响应**：`data.count`  

### 8.3 创建消息

- **POST** `/messages`  
- **请求体**：`{ "category": "progress|report|system|acceptance|customer_service", "title": "标题", "content": "可选", "summary": "可选", "link_url": "可选" }`  
- **说明**：用于施工提醒、报告通知、系统通知等写入消息中心  

### 8.4 标记已读

- **PUT** `/messages/{msg_id}/read`  
- **响应**：无 data  

### 8.5 一键已读

- **PUT** `/messages/read-all`  

---

## 九、施工照片（P15/P29）

### 9.1 上传照片

- **POST** `/construction-photos/upload?stage=S00|S01|...|S05`  
- **Body**：multipart file  
- **响应**：照片记录（含 id, file_url 等）  

### 9.2 照片列表

- **GET** `/construction-photos?stage=可选`  
- **响应**：按阶段或全部的施工照片列表  

### 9.3 删除照片

- **DELETE** `/construction-photos/{photo_id}`  

### 9.4 移动照片阶段

- **PUT** `/construction-photos/{photo_id}/move`  
- **请求体**：`{ "target_stage": "S01" }`  

---

## 十、验收分析（P30）

### 10.1 上传验收照片

- **POST** `/acceptance/upload-photo`  
- **Body**：multipart file  
- **响应**：`data.file_url` 供 analyze 使用  

### 10.2 验收分析

- **POST** `/acceptance/analyze`  
- **请求体**：`{ "stage": "S01|...|S05", "file_urls": ["url1","url2"] }`  
- **响应**：`id, stage, issues, suggestions, severity, summary, created_at`；同时会写入消息中心「验收报告已生成」  

### 10.3 获取验收结果详情

- **GET** `/acceptance/{analysis_id}`  
- **响应**：完整验收记录（含 result_status, recheck_count, rectified_photo_urls）  

### 10.4 验收列表

- **GET** `/acceptance?stage=可选&page=1&page_size=20`  
- **响应**：`data.list`, `total, page, page_size`  

### 10.5 标记整改

- **POST** `/acceptance/{analysis_id}/mark-rectify`  
- **响应**：`data.result_status: "need_rectify"`  

### 10.6 申请复检

- **POST** `/acceptance/{analysis_id}/request-recheck`  
- **请求体**：`{ "rectified_photo_urls": ["url1",...] }`（最多 5 张）  
- **响应**：`result_status: "pending_recheck", recheck_count`  

---

## 十一、报告导出（P11/P12/P13/P30 FR-028）

### 11.1 导出 PDF

- **GET** `/reports/export-pdf?report_type=company|quote|contract|acceptance&resource_id=123`  
- **说明**：  
  - company：resource_id 为 scan_id  
  - quote/contract：resource_id 为 quote_id/contract_id，需已解锁  
  - acceptance：resource_id 为 acceptance_analysis_id，文件名为「[阶段名]验收报告-[用户名]-[日期].pdf」  
- **响应**：StreamingResponse，application/pdf  

---

## 十二、城市选择（P35/P38）

### 12.1 热门城市

- **GET** `/cities/hot`  
- **响应**：`data.list` 热门城市（code, name）  

### 12.2 省份/城市列表与搜索

- **GET** `/cities/list?province=广东` 或 `?q=深圳`  
- **响应**：省份列表或城市列表/搜索结果  

### 12.3 保存当前城市

- **POST** `/cities/select`  
- **请求体**：`{ "city_name": "深圳市" }`，`city_code` 可选  
- **响应**：`data.city_code, data.city_name`  

### 12.4 当前选中城市

- **GET** `/cities/current`  
- **响应**：`data.city_code, data.city_name`  

---

## 十三、AI 监理咨询（P36）

### 13.1 咨询额度

- **GET** `/consultation/quota`  
- **响应**：免费用户本月剩余次数、会员无限次等  

### 13.2 创建会话

- **POST** `/consultation/session`  
- **请求体**：可选 `acceptance_analysis_id, stage`  
- **响应**：`session_id` 等  

### 13.3 会话上下文

- **GET** `/consultation/session/{session_id}/context`  
- **响应**：验收阶段、问题列表等上下文  

### 13.4 发送消息

- **POST** `/consultation/message`  
- **请求体**：`session_id, content, images` 等  
- **响应**：AI 回复内容  

### 13.5 会话消息列表

- **GET** `/consultation/session/{session_id}/messages`  
- **响应**：历史消息列表  

### 13.6 转人工

- **POST** `/consultation/session/{session_id}/transfer-human`  
- **响应**：转接结果  

### 13.7 会话列表

- **GET** `/consultation/sessions`  
- **响应**：当前用户会话列表  

---

## 十四、数据管理（P20/P21）

### 14.1 软删除

- **POST** `/users/data/delete`  
- **请求体**：`resource_type`（如 construction_photo, acceptance_analysis）, `resource_id`  
- **响应**：删除结果  

### 14.2 回收站列表

- **GET** `/users/data/recycle?resource_type=可选`  
- **响应**：已删除数据列表（含恢复所需 id）  

### 14.3 恢复

- **POST** `/users/data/restore`  
- **请求体**：`resource_type, resource_id`  
- **响应**：恢复结果  

---

## 十五、材料进场人工核对（P37）

**V2.6.2更新**：已删除 `POST /api/v1/materials/verify` 接口，统一使用 `PUT /api/v1/constructions/stage-status`（stage='S00', status='checked'）进行材料进场核对。

### 15.1 材料清单（从报价单同步）

- **GET** `/material-checks/material-list`  
- **响应**：`data.list` 材料项（material_name, spec_brand, quantity），`data.source`, `data.quote_id`；无报价单时 `data.hint` 提示先上传报价单  

### 15.2 最近一次核对记录

- **GET** `/material-checks/latest`  
- **响应**：最近一次 material_check 及 items（含 photo_urls, doc_*）  

### 15.3 提交核对结果

- **POST** `/material-checks/submit`  
- **请求体**：  
  - `result`: "pass" | "fail"  
  - `problem_note`: 未通过时必填，至少 10 字  
  - `items`: [{ "material_name", "spec_brand", "quantity", "photo_urls", "doc_certificate_url", "doc_quality_url", "doc_ccc_url" }]  
  - `quote_id`: 可选  
- **说明**：通过时每项至少 1 张照片；提交后同步更新施工进度 S00 状态  

---

## 十六、验收申诉与特殊申请（P30/P09）

### 16.1 提交验收申诉

- **POST** `/appeals/acceptance/{analysis_id}`  
- **请求体**：`{ "reason": "异议原因", "images": ["url1","url2","url3"] }`（images 最多 3）  
- **响应**：`data.id, data.status`，提示「申诉已提交，1-2个工作日审核」  

### 16.2 申诉列表

- **GET** `/appeals/acceptance?analysis_id=可选&page=1&page_size=20`  
- **响应**：`data.list`（id, acceptance_analysis_id, stage, reason, status, created_at）  

### 16.3 特殊申请（自主装修豁免/争议申诉）

- **POST** `/appeals/special`  
- **请求体**：`{ "application_type": "exemption|dispute_appeal", "stage": "可选", "content": "至少10字", "images": ["可选"] }`  
- **响应**：`data.id, data.status`  

### 16.4 特殊申请列表

- **GET** `/appeals/special?application_type=可选&page=1&page_size=20`  
- **响应**：`data.list`  

---

## 十七、意见反馈（P22）

### 17.1 提交反馈

- **POST** `/feedback`  
- **请求体**：`content`，可选 `images`, `feedback_type`, `sub_type`  
- **响应**：提交结果  

---

## 十八、开发/测试

### 18.1 填充测试数据

- **POST** `/dev/seed`  
- **说明**：仅开发环境可用，写入测试用户与数据  

---

## 十九、材料库（V2.6.2新增）

### 19.1 搜索材料库

- **GET** `/material-library/search?keyword=xxx&category=主材|辅材&city_code=可选`  
- **响应**：`data.list` 材料列表（material_name, category, spec_brand, unit, typical_price_range, description）

### 19.2 获取常用材料

- **GET** `/material-library/common?category=可选`  
- **响应**：`data.list` 常用材料列表（最多50条）

### 19.3 智能匹配材料

- **POST** `/material-library/match`  
- **请求体**：`{ "material_names": ["水泥", "瓷砖"], "city_code": "可选" }`  
- **响应**：`data.matched` 匹配结果列表（original_name, matched材料信息或null）

---

## 二十、健康检查（应用级）

- **GET** `/health`  
- **前缀**：无 `/api/v1`，在应用根路径  
- **认证**：否  
- **响应**：`status, version, database` 连接池状态  

---

**文档结束**。如有新增接口或字段，以实际代码为准。

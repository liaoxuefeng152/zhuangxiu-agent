# 后端接口实现清单（PRD V2.6.1 对齐 V15.3）

## 一、已实现的接口（按模块）

### 1. 用户与认证 `/api/v1/users`
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| POST | /login | P01/P02 | 微信登录 |
| GET | /profile | P10 | 个人中心信息 |
| PUT | /profile | P10 | 更新昵称/头像 |
| GET | /settings | P19 | 账户与通知设置（含提醒提前天数 1/2/3/5/7） |
| PUT | /settings | P19 FR-014 | 更新提醒设置、存储期限 |

### 2. 公司检测 `/api/v1/companies`
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| GET | /search | P03 | 公司名称搜索/模糊匹配 |
| POST | /scan | P03/P04 | 提交检测 |
| GET | /scan/{scan_id} | P04/P11 | 检测结果/报告 |
| GET | /scans | P11 | 扫描记录列表 |

### 3. 报价单 `/api/v1/quotes`
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| POST | /upload | P05 | 上传报价单 |
| GET | /quote/{quote_id} | P06/P12 | 分析结果/报告 |
| GET | /list | P18 | 报价单列表 |

### 4. 合同 `/api/v1/contracts`
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| POST | /upload | P07 | 上传合同 |
| GET | /contract/{contract_id} | P08/P13 | 审核结果/报告 |
| GET | /list | P18 | 合同列表 |

### 5. 施工进度 `/api/v1/constructions`（PRD 六阶段 S00-S05）
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| GET | /schedule | P09 | 进度计划（含阶段 locked 互锁） |
| POST | /start-date | P09 FR-011 | 设置开工日期 |
| PUT | /stage-status | P09 FR-012/FR-013 | 更新阶段状态（流程互锁 409） |
| PUT | /stage-calibrate | P09 FR-015 | 阶段时间校准 |
| DELETE | /schedule | - | 重置进度 |

### 6. 支付与订单 `/api/v1/payments`
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| POST | /create | P27/P28 | 创建订单（报告解锁/会员等） |
| POST | /pay | P28 | 调起支付 |
| POST | /notify | P28 | 微信支付回调 |
| GET | /orders | P24 | 我的订单列表 |
| GET | /order/{order_id} | P25 | 订单详情 |
| POST | /refund/apply | P34 | 退款申请 |
| GET | /refund/status | P34 | 退款状态 |

### 7. 消息 `/api/v1/messages`
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| GET | / | P14 | 消息列表（支持 category） |
| GET | /unread-count | P02/P14 FR-031 | 未读数量 |
| PUT | /{msg_id}/read | P14 | 单条已读 |
| PUT | /read-all | P14 | 一键已读 |

### 8. 施工照片 `/api/v1/construction-photos`
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| POST | /upload | P15/P29 | 上传照片 |
| GET | / | P29 | 按阶段列表 |
| DELETE | /{photo_id} | P29 | 删除 |
| PUT | /{photo_id}/move | P29 | 移动阶段 |

### 9. 验收分析 `/api/v1/acceptance`（P30）
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| POST | /upload-photo | P15 | 上传验收照片 |
| POST | /analyze | P30 | AI 验收分析（含 result_status） |
| GET | /{analysis_id} | P30 FR-024 | 验收结果详情 |
| GET | / | P30 | 验收列表 |
| POST | /{id}/mark-rectify | P30 FR-025 | 标记整改 |
| POST | /{id}/request-recheck | P30 FR-025 | 申请复检 |

### 10. 报告导出 `/api/v1/reports`
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| GET | /export-pdf | P11/P12/P13 | 公司/报价/合同报告 PDF（report_type=company|quote|contract） |

### 11. 城市选择 `/api/v1/cities`（P35/P38）
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| GET | /hot | P38 FR-033 | 热门城市 |
| GET | /list | P38 FR-034 | 省份/城市列表与搜索 |
| POST | /select | P38 FR-036 | 保存当前城市（支持仅 city_name） |
| GET | /current | P02 | 当前选中城市 |

### 12. AI 监理咨询 `/api/v1/consultation`（P36）
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| GET | /quota | P30 FR-027 | 免费额度/会员次数 |
| POST | /session | P36 | 创建会话 |
| GET | /session/{id}/context | P36 | 验收上下文 |
| POST | /message | P36 | 发送消息 |
| GET | /session/{id}/messages | P36 | 消息历史 |
| POST | /session/{id}/transfer-human | P36 | 转人工 |
| GET | /sessions | P36 | 会话列表 |

### 13. 数据管理 `/api/v1/users/data`（P20/P21）
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| POST | /delete | P20 | 软删除（照片/报告等） |
| GET | /recycle | P21 | 回收站列表 |
| POST | /restore | P21 | 恢复 |

### 14. 材料进场人工核对 `/api/v1/material-checks`（P37）
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| GET | /material-list | P37 FR-019 | 从报价单同步材料清单 |
| GET | /latest | P37 | 最近一次核对记录 |
| POST | /submit | P37 FR-023 | 提交核对通过/未通过 |

### 15. 验收申诉与特殊申请 `/api/v1/appeals`（P30/P09）
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| POST | /acceptance/{analysis_id} | P30 FR-026 | 提交验收申诉 |
| GET | /acceptance | P30 | 申诉列表 |
| POST | /special | P09 FR-016 | 自主装修豁免/争议申诉 |
| GET | /special | P09 | 特殊申请列表 |

### 16. 意见反馈 `/api/v1/feedback`（P22）
| 方法 | 路径 | PRD 对应 | 说明 |
|------|------|----------|------|
| POST | / | P22 | 提交反馈 |

### 17. 开发用 `/api/v1/dev`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /seed | 测试数据填充 |

---

## 二、未实现或需补充的接口/能力

| 项目 | PRD 引用 | 说明 | 建议 |
|------|----------|------|------|
| **验收报告 PDF 导出** | P30 FR-028 | 当前 `/reports/export-pdf` 仅支持 company/quote/contract，不支持 acceptance。PRD 要求「[阶段名]验收报告-[用户名]-[日期].pdf」 | 在 reports 中增加 `report_type=acceptance`，根据 acceptance_analysis_id 生成验收 PDF |
| **智能提醒主动推送** | FR-029/FR-030/FR-031 | 微信服务通知、提前 N 天提醒需后端定时任务 + 微信订阅消息接口；当前仅有「提醒设置」存储，无定时扫描与推送 | 单独实现 worker：按 reminder_days_before 扫描施工计划，调用微信「订阅消息」下发；或由第三方/云函数触发 |
| **消息写入（施工提醒/报告通知）** | P14 | 消息列表与未读已有；若需「系统自动写入」施工提醒、报告通知等，需在业务侧（如验收完成、订单支付成功）调用 messages 写入接口 | 若尚无「写消息」接口，可新增 POST /messages（内部或管理用），在验收/支付等流程中调用 |

---

## 三、小结

- **已实现**：PRD 中与 38 页相关的**主要读写、查询、支付、施工进度、验收、材料核对、申诉、城市、咨询、数据管理**等接口均已实现，并与 PRD 2.6.1 / V15.3 对齐（六阶段 S00-S05、流程互锁、校准、P37、P30 申诉与复检等）。
- **未完全覆盖**：  
  1）**验收报告 PDF 导出**（P30 FR-028）需在 reports 中增加 acceptance 类型；  
  2）**智能提醒的主动推送**依赖定时任务与微信订阅消息，需单独实现；  
  3）若需系统自动发「施工提醒/报告通知」到消息中心，需在相关业务中写消息（及可选 POST /messages）。

如需，我可以按上述建议直接补「验收报告 PDF 导出」和「写消息」的接口设计与实现要点（含 URL、参数、响应）。

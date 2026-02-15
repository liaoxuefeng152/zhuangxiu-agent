-- 清理照片、分析报告与台账报告（保持用户、订单、消息等不动）
-- 按外键依赖顺序删除，避免违反约束
-- 执行前请确认当前连接的是开发/测试库

BEGIN;

-- 1. AI 咨询消息（依赖 ai_consult_sessions）
DELETE FROM ai_consult_messages;

-- 2. AI 咨询会话（依赖 acceptance_analyses）
DELETE FROM ai_consult_sessions;

-- 3. 验收申诉（依赖 acceptance_analyses）
DELETE FROM acceptance_appeals;

-- 4. 验收分析报告
DELETE FROM acceptance_analyses;

-- 5. 材料核对明细（依赖 material_checks）
DELETE FROM material_check_items;

-- 6. 材料核对主表（依赖 quotes）
DELETE FROM material_checks;

-- 7. 施工照片
DELETE FROM construction_photos;

-- 8. 公司风险检测报告
DELETE FROM company_scans;

-- 9. 报价单（分析报告）
DELETE FROM quotes;

-- 10. 合同（分析报告）
DELETE FROM contracts;

-- 11. 施工进度/台账报告（我的数据-台账报告 tab 来源）
DELETE FROM constructions;

COMMIT;

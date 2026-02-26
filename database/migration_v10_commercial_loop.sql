-- 商业闭环相关字段迁移（V2.6.2）
-- 执行前请备份数据库。使用IF NOT EXISTS避免重复列错误。

-- 公司检测表：报告解锁状态（如果V9已添加，则跳过）
ALTER TABLE company_scans ADD COLUMN IF NOT EXISTS is_unlocked BOOLEAN DEFAULT FALSE;
ALTER TABLE company_scans ADD COLUMN IF NOT EXISTS unlock_type VARCHAR(20);

-- 用户表：会员到期时间
ALTER TABLE users ADD COLUMN IF NOT EXISTS member_expire TIMESTAMP;

-- 验收分析表：报告解锁状态
ALTER TABLE acceptance_analyses ADD COLUMN IF NOT EXISTS is_unlocked BOOLEAN DEFAULT FALSE;
ALTER TABLE acceptance_analyses ADD COLUMN IF NOT EXISTS unlock_type VARCHAR(20);

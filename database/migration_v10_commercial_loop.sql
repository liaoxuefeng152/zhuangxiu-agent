-- 商业闭环相关字段迁移（V2.6.2）
-- 执行前请备份数据库。若列已存在会报错，可忽略。

-- 公司检测表：报告解锁状态
ALTER TABLE company_scans ADD COLUMN is_unlocked BOOLEAN DEFAULT FALSE;
ALTER TABLE company_scans ADD COLUMN unlock_type VARCHAR(20);

-- 用户表：会员到期时间
ALTER TABLE users ADD COLUMN member_expire TIMESTAMP;

-- 验收分析表：报告解锁状态
ALTER TABLE acceptance_analyses ADD COLUMN is_unlocked BOOLEAN DEFAULT FALSE;
ALTER TABLE acceptance_analyses ADD COLUMN unlock_type VARCHAR(20);

-- 装修决策Agent - 数据库迁移 V9
-- 修复company_scans表缺少is_unlocked和unlock_type字段的问题
-- 执行方式：
-- docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -d zhuangxiu_dev -f - < database/migration_v9_company_unlock.sql

-- 1. 添加is_unlocked字段到company_scans表
ALTER TABLE company_scans ADD COLUMN IF NOT EXISTS is_unlocked BOOLEAN DEFAULT FALSE;

-- 2. 添加unlock_type字段到company_scans表
ALTER TABLE company_scans ADD COLUMN IF NOT EXISTS unlock_type VARCHAR(20);

-- 3. 更新现有数据（如果有的话）
-- 将已完成的扫描记录标记为已解锁（兼容历史数据）
UPDATE company_scans 
SET is_unlocked = TRUE, unlock_type = 'first_free'
WHERE status = 'completed' AND is_unlocked IS NULL;

-- 4. 添加注释
COMMENT ON COLUMN company_scans.is_unlocked IS '报告是否已解锁（V2.6.2优化：首次报告免费）';
COMMENT ON COLUMN company_scans.unlock_type IS '解锁类型：single, first_free, member（V2.6.2优化）';

-- 5. 完成
SELECT 'Migration V9 completed: Added is_unlocked and unlock_type fields to company_scans table' AS status;

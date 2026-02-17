-- 装修决策Agent - 数据库迁移 V8
-- 修复公司扫描表缺少company_info字段的问题
-- 执行方式：
-- docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -d zhuangxiu_dev -f - < database/migration_v8_company_info.sql

-- 1. 添加company_info字段到company_scans表
ALTER TABLE company_scans ADD COLUMN IF NOT EXISTS company_info JSONB;

-- 2. 更新现有数据（如果有的话）
-- 将legal_risks中的企业信息提取到company_info中
UPDATE company_scans 
SET company_info = jsonb_build_object(
    'name', company_name,
    'legal_risks', legal_risks
)
WHERE company_info IS NULL AND legal_risks IS NOT NULL;

-- 3. 添加注释
COMMENT ON COLUMN company_scans.company_info IS '企业基本信息，包括工商注册信息、法定代表人、注册资本等';

-- 4. 完成
SELECT 'Migration V8 completed: Added company_info field to company_scans table' AS status;

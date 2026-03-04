-- 迁移V11：添加analysis_progress列到quotes和contracts表
-- 修复500错误：column contracts.analysis_progress does not exist

-- 为quotes表添加analysis_progress列
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'quotes' AND column_name = 'analysis_progress') THEN
        ALTER TABLE quotes ADD COLUMN analysis_progress JSON;
        RAISE NOTICE 'Added analysis_progress column to quotes table';
    ELSE
        RAISE NOTICE 'analysis_progress column already exists in quotes table';
    END IF;
END $$;

-- 为contracts表添加analysis_progress列
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'contracts' AND column_name = 'analysis_progress') THEN
        ALTER TABLE contracts ADD COLUMN analysis_progress JSON;
        RAISE NOTICE 'Added analysis_progress column to contracts table';
    ELSE
        RAISE NOTICE 'analysis_progress column already exists in contracts table';
    END IF;
END $$;

-- 为company_scans表添加analysis_progress列（如果需要）
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'company_scans' AND column_name = 'analysis_progress') THEN
        ALTER TABLE company_scans ADD COLUMN analysis_progress JSON;
        RAISE NOTICE 'Added analysis_progress column to company_scans table';
    ELSE
        RAISE NOTICE 'analysis_progress column already exists in company_scans table';
    END IF;
END $$;

SELECT 'Migration V11 completed: Added analysis_progress columns' as status;

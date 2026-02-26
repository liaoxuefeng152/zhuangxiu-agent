-- 商业闭环相关字段迁移（V2.6.2）- 修复版
-- 只添加缺失的member_expire列，其他列已在V9中添加

-- 用户表：会员到期时间
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'member_expire') THEN
        ALTER TABLE users ADD COLUMN member_expire TIMESTAMP;
        RAISE NOTICE 'Added member_expire column to users table';
    ELSE
        RAISE NOTICE 'member_expire column already exists in users table';
    END IF;
END $$;

-- 验收分析表：报告解锁状态（如果V9已添加，则跳过）
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'acceptance_analyses' AND column_name = 'is_unlocked') THEN
        ALTER TABLE acceptance_analyses ADD COLUMN is_unlocked BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added is_unlocked column to acceptance_analyses table';
    ELSE
        RAISE NOTICE 'is_unlocked column already exists in acceptance_analyses table';
    END IF;
END $$;

DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'acceptance_analyses' AND column_name = 'unlock_type') THEN
        ALTER TABLE acceptance_analyses ADD COLUMN unlock_type VARCHAR(20);
        RAISE NOTICE 'Added unlock_type column to acceptance_analyses table';
    ELSE
        RAISE NOTICE 'unlock_type column already exists in acceptance_analyses table';
    END IF;
END $$;

SELECT 'Migration V10 completed: Added missing commercial loop fields' as status;

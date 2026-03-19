-- 迁移版本：V12
-- 描述：为quotes表添加estimated_savings字段（V2.6.1需求新增）
-- 创建时间：2026-03-19

-- 检查字段是否存在，如果不存在则添加
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'quotes' AND column_name = 'estimated_savings'
    ) THEN
        ALTER TABLE quotes ADD COLUMN estimated_savings FLOAT;
        RAISE NOTICE '已添加 estimated_savings 字段到 quotes 表';
    ELSE
        RAISE NOTICE 'estimated_savings 字段已存在，跳过';
    END IF;
END $$;

-- 更新现有记录的estimated_savings字段（如果result_json中有estimated_savings数据）
UPDATE quotes 
SET estimated_savings = (
    CASE 
        WHEN result_json->>'estimated_savings' ~ '^\d+(\.\d+)?$' 
        THEN CAST(result_json->>'estimated_savings' AS FLOAT)
        WHEN result_json->>'estimated_savings' IS NOT NULL 
        THEN NULL  -- 非数字字符串设为NULL
        ELSE NULL
    END
)
WHERE result_json IS NOT NULL 
  AND result_json->>'estimated_savings' IS NOT NULL
  AND estimated_savings IS NULL;

-- 记录迁移完成
INSERT INTO migration_history (version, description, applied_at) 
VALUES ('V12', '为quotes表添加estimated_savings字段（V2.6.1需求新增）', NOW())
ON CONFLICT (version) DO UPDATE SET applied_at = NOW();

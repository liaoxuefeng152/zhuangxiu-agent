-- V2.6.7 积分系统迁移脚本
-- 执行时间：2026-02-16
-- 说明：添加用户积分字段和积分记录表

-- 1. 添加用户积分字段
ALTER TABLE users ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 0;

-- 2. 创建积分记录表
CREATE TABLE IF NOT EXISTS point_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    points INTEGER NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_id INTEGER,
    description VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 创建索引
CREATE INDEX IF NOT EXISTS idx_point_records_user_id ON point_records(user_id);
CREATE INDEX IF NOT EXISTS idx_point_records_created_at ON point_records(created_at);
CREATE INDEX IF NOT EXISTS idx_point_records_source_type ON point_records(source_type);

-- 4. 为现有用户初始化积分为0（如果字段已存在则跳过）
UPDATE users SET points = 0 WHERE points IS NULL;

COMMENT ON COLUMN users.points IS '用户积分（V2.6.7新增）';
COMMENT ON TABLE point_records IS '积分记录表（V2.6.7新增）';
COMMENT ON COLUMN point_records.source_type IS '积分来源：share_report_acceptance, share_report_quote, share_progress等';
COMMENT ON COLUMN point_records.source_id IS '关联资源ID（如报告ID、订单ID等）';

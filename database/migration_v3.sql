-- 装修决策Agent - 数据库迁移 V3 (PRD V2.6)
-- 城市选择、用户设置、退款、AI监理咨询、消息分类

-- \c zhuangxiu_dev;  -- 由docker-compose自动指定数据库

-- 用户表增加城市字段
ALTER TABLE users ADD COLUMN IF NOT EXISTS city_code VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS city_name VARCHAR(50);
-- 用户设置表 (P19 数据存储期限、提醒设置等)
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    storage_duration_months INTEGER DEFAULT 12,
    reminder_days_before INTEGER DEFAULT 3,
    notify_progress BOOLEAN DEFAULT TRUE,
    notify_acceptance BOOLEAN DEFAULT TRUE,
    notify_system BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);

-- 退款申请表 (P34)
CREATE TABLE IF NOT EXISTS refund_requests (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reason VARCHAR(100) NOT NULL,
    note TEXT,
    refund_amount NUMERIC(10, 2),
    status VARCHAR(20) DEFAULT 'pending',
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_refund_requests_order_id ON refund_requests(order_id);
CREATE INDEX idx_refund_requests_user_id ON refund_requests(user_id);
CREATE INDEX idx_refund_requests_status ON refund_requests(status);

-- AI监理咨询会话表 (P36)
CREATE TABLE IF NOT EXISTS ai_consult_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    acceptance_analysis_id INTEGER REFERENCES acceptance_analyses(id) ON DELETE SET NULL,
    stage VARCHAR(30),
    status VARCHAR(20) DEFAULT 'active',
    is_human BOOLEAN DEFAULT FALSE,
    human_started_at TIMESTAMP,
    paid_amount NUMERIC(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_ai_consult_sessions_user_id ON ai_consult_sessions(user_id);
CREATE INDEX idx_ai_consult_sessions_acceptance_id ON ai_consult_sessions(acceptance_analysis_id);
CREATE INDEX idx_ai_consult_sessions_created_at ON ai_consult_sessions(created_at DESC);

-- AI监理咨询消息表
CREATE TABLE IF NOT EXISTS ai_consult_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES ai_consult_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT,
    images JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_ai_consult_messages_session_id ON ai_consult_messages(session_id);

-- 用户月度AI咨询免费额度使用记录 (用于免费用户每月3次)
CREATE TABLE IF NOT EXISTS ai_consult_quota_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    year_month VARCHAR(7) NOT NULL,
    used_count INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, year_month)
);
CREATE INDEX idx_ai_consult_quota_user_ym ON ai_consult_quota_usage(user_id, year_month);

-- 消息表扩展：category 支持 progress, report, system, acceptance, customer_service
-- 已有 category 列，无需改表，仅约定枚举

-- 意见反馈表增加类型 (P22 AI验收结果反馈等)
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS feedback_type VARCHAR(30) DEFAULT 'other';
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS sub_type VARCHAR(30);

-- 施工照片/验收报告软删除与回收站：用 deleted_at 标记
ALTER TABLE construction_photos ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE acceptance_analyses ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
-- 报价单/合同 若需回收站可同样加 deleted_at，此处先不扩

-- 订单表补充 metadata 列名（若之前为 order_metadata 则跳过）
-- ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_metadata JSONB;

SELECT 'Migration V3 completed!' AS status;

-- 装修决策Agent - 数据库迁移 V2
-- 新增：消息、意见反馈、施工照片、验收分析 表

-- \c zhuangxiu_dev;  -- 由docker-compose自动指定数据库

-- 消息表 (P14 消息中心)
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    summary VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    link_url VARCHAR(512),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_category ON messages(category);
CREATE INDEX idx_messages_is_read ON messages(is_read);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- 意见反馈表 (P24)
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    images JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    reply TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_created_at ON feedback(created_at DESC);

-- 施工照片表 (P15/P17/P29)
CREATE TABLE IF NOT EXISTS construction_photos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stage VARCHAR(30) NOT NULL,
    file_url VARCHAR(512) NOT NULL,
    file_name VARCHAR(200),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_construction_photos_user_id ON construction_photos(user_id);
CREATE INDEX idx_construction_photos_stage ON construction_photos(stage);
CREATE INDEX idx_construction_photos_created_at ON construction_photos(created_at DESC);

-- 验收分析表 (P30)
CREATE TABLE IF NOT EXISTS acceptance_analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stage VARCHAR(30),
    file_urls JSONB NOT NULL,
    result_json JSONB,
    issues JSONB,
    suggestions JSONB,
    severity VARCHAR(20),
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_acceptance_analyses_user_id ON acceptance_analyses(user_id);
CREATE INDEX idx_acceptance_analyses_created_at ON acceptance_analyses(created_at DESC);

SELECT 'Migration V2 completed!' AS status;

-- 装修决策Agent - 数据库初始化脚本
-- PostgreSQL 15+

-- 创建数据库（如果不存在）
-- CREATE DATABASE zhuangxiu_dev;

-- 连接到数据库（由docker-compose自动指定，不需要手动切换）
-- \c zhuangxiu_dev;

-- 创建扩展（如果需要）
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    wx_openid VARCHAR(128) UNIQUE NOT NULL,
    wx_unionid VARCHAR(128),
    nickname VARCHAR(50),
    avatar_url VARCHAR(512),
    phone VARCHAR(11),
    phone_verified BOOLEAN DEFAULT FALSE,
    is_member BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_users_wx_openid ON users(wx_openid);
CREATE INDEX idx_users_wx_unionid ON users(wx_unionid);
CREATE INDEX idx_users_phone ON users(phone);

-- 创建公司扫描记录表
CREATE TABLE IF NOT EXISTS company_scans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(200) NOT NULL,
    risk_level VARCHAR(20),
    risk_score INTEGER,
    risk_reasons JSONB,
    complaint_count INTEGER DEFAULT 0,
    legal_risks JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_company_scans_user_id ON company_scans(user_id);
CREATE INDEX idx_company_scans_company_name ON company_scans(company_name);
CREATE INDEX idx_company_scans_created_at ON company_scans(created_at DESC);

-- 创建报价单表
CREATE TABLE IF NOT EXISTS quotes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_url VARCHAR(512) NOT NULL,
    file_name VARCHAR(200),
    file_size INTEGER,
    file_type VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    ocr_result JSONB,
    result_json JSONB,
    risk_score INTEGER,
    high_risk_items JSONB,
    warning_items JSONB,
    missing_items JSONB,
    overpriced_items JSONB,
    is_unlocked BOOLEAN DEFAULT FALSE,
    unlock_type VARCHAR(20),
    total_price NUMERIC(10, 2),
    market_ref_price NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_quotes_user_id ON quotes(user_id);
CREATE INDEX idx_quotes_status ON quotes(status);
CREATE INDEX idx_quotes_created_at ON quotes(created_at DESC);

-- 创建合同表
CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_url VARCHAR(512) NOT NULL,
    file_name VARCHAR(200),
    file_size INTEGER,
    file_type VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    ocr_result JSONB,
    result_json JSONB,
    risk_level VARCHAR(20),
    risk_items JSONB,
    unfair_terms JSONB,
    missing_terms JSONB,
    suggested_modifications JSONB,
    is_unlocked BOOLEAN DEFAULT FALSE,
    unlock_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_contracts_user_id ON contracts(user_id);
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_contracts_created_at ON contracts(created_at DESC);

-- 创建订单表
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_no VARCHAR(32) UNIQUE NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    resource_type VARCHAR(20),
    resource_id INTEGER,
    amount NUMERIC(10, 2) NOT NULL,
    original_amount NUMERIC(10, 2),
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(20),
    transaction_id VARCHAR(64),
    paid_at TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_order_no ON orders(order_no);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_transaction_id ON orders(transaction_id);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);

-- 创建施工进度管理表
CREATE TABLE IF NOT EXISTS constructions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    start_date TIMESTAMP,
    estimated_end_date TIMESTAMP,
    actual_end_date TIMESTAMP,
    progress_percentage INTEGER DEFAULT 0,
    is_delayed BOOLEAN DEFAULT FALSE,
    delay_days INTEGER DEFAULT 0,
    stages JSONB,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_constructions_user_id ON constructions(user_id);
CREATE UNIQUE INDEX idx_constructions_user_unique ON constructions(user_id);

-- 创建函数：自动更新updated_at字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要自动更新updated_at的表创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quotes_updated_at BEFORE UPDATE ON quotes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contracts_updated_at BEFORE UPDATE ON contracts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_constructions_updated_at BEFORE UPDATE ON constructions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入测试数据（可选）
-- INSERT INTO users (wx_openid, nickname) VALUES ('test_openid', '测试用户');

-- 完成
SELECT 'Database initialization completed!' AS status;

-- 装修避坑管家 PRD V2.6.1 对齐 V15.3 - 数据库迁移 V4
-- 6大阶段 S00-S05、材料进场人工核对(P37)、验收申诉、特殊申请、提醒联动
--
-- 执行方式（任选其一）：
-- 1) 本机已安装 psql 且数据库在运行：
--    PGPASSWORD=decoration123 psql -h localhost -p 5432 -U decoration -d zhuangxiu_prod -f database/migration_v4.sql
-- 2) 使用 Docker Postgres 容器（先 docker compose -f docker-compose.dev.yml up -d）：
--    docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -d zhuangxiu_prod -f - < database/migration_v4.sql
-- 3) 使用项目脚本（需 DATABASE_URL=...@localhost:5432/... 指向本机数据库）：
--    python scripts/run_migration_v4.py

-- 1) 验收分析表：增加验收结果状态、整改/复检
ALTER TABLE acceptance_analyses ADD COLUMN IF NOT EXISTS result_status VARCHAR(30) DEFAULT 'completed';
-- result_status: passed(已通过) | need_rectify(待整改) | failed(未通过) | pending_recheck(待复检)
ALTER TABLE acceptance_analyses ADD COLUMN IF NOT EXISTS recheck_count INTEGER DEFAULT 0;
ALTER TABLE acceptance_analyses ADD COLUMN IF NOT EXISTS rectified_at TIMESTAMP;
ALTER TABLE acceptance_analyses ADD COLUMN IF NOT EXISTS rectified_photo_urls JSONB;

-- 2) 验收申诉表 (P30 FR-026)
CREATE TABLE IF NOT EXISTS acceptance_appeals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    acceptance_analysis_id INTEGER NOT NULL REFERENCES acceptance_analyses(id) ON DELETE CASCADE,
    stage VARCHAR(30) NOT NULL,
    reason TEXT NOT NULL,
    images JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    reviewed_at TIMESTAMP,
    review_note TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_acceptance_appeals_user ON acceptance_appeals(user_id);
CREATE INDEX IF NOT EXISTS idx_acceptance_appeals_analysis ON acceptance_appeals(acceptance_analysis_id);
CREATE INDEX IF NOT EXISTS idx_acceptance_appeals_status ON acceptance_appeals(status);

-- 3) 特殊申请表 (P09 FR-016：自主装修豁免 / 核对验收争议申诉)
CREATE TABLE IF NOT EXISTS special_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    application_type VARCHAR(30) NOT NULL,
    stage VARCHAR(30),
    content TEXT NOT NULL,
    images JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    reviewed_at TIMESTAMP,
    review_note TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_special_applications_user ON special_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_special_applications_type ON special_applications(application_type);
CREATE INDEX IF NOT EXISTS idx_special_applications_status ON special_applications(status);

-- 4) 材料进场人工核对主表 (P37)
CREATE TABLE IF NOT EXISTS material_checks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quote_id INTEGER REFERENCES quotes(id) ON DELETE SET NULL,
    result VARCHAR(20) NOT NULL,
    problem_note TEXT,
    submitted_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_material_checks_user ON material_checks(user_id);
CREATE INDEX IF NOT EXISTS idx_material_checks_submitted ON material_checks(submitted_at DESC);

-- 5) 材料核对明细表 (P37 材料清单项 + 拍照/资料)
CREATE TABLE IF NOT EXISTS material_check_items (
    id SERIAL PRIMARY KEY,
    material_check_id INTEGER NOT NULL REFERENCES material_checks(id) ON DELETE CASCADE,
    material_name VARCHAR(200) NOT NULL,
    spec_brand VARCHAR(200),
    quantity VARCHAR(50),
    photo_urls JSONB DEFAULT '[]',
    doc_certificate_url VARCHAR(512),
    doc_quality_url VARCHAR(512),
    doc_ccc_url VARCHAR(512),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_material_check_items_check ON material_check_items(material_check_id);

-- 6) 施工进度表 constructions.stages 使用 S00-S05 键（见应用层），无需改表结构
-- 7) 用户设置表已有 reminder_days_before、notify_*，满足 FR-014/FR-029/FR-030
-- 8) 报价单材料清单：从 result_json 解析或单独列；若无则 material_checks.quote_id 关联后解析
-- 9) 订单表 metadata 列名修正（若存在 ordeer_metadata）
ALTER TABLE orders ADD COLUMN IF NOT EXISTS metadata JSONB;
-- 不删除 ordeer_metadata 以免破坏现有数据，应用层优先读 metadata

SELECT 'Migration V4 (PRD V2.6.1) completed!' AS status;

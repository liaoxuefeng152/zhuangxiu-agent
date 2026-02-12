-- 装修避坑管家 PRD V2.6.2 优化 - 数据库迁移 V5
-- 1. 首次报告免费、会员无限解锁
-- 2. 分析进度提示
-- 3. 阶段周期自定义
-- 4. 材料库建设
--
-- 执行方式（任选其一）：
-- 1) 本机已安装 psql 且数据库在运行：
--    PGPASSWORD=decoration123 psql -h localhost -p 5432 -U decoration -d zhuangxiu_prod -f database/migration_v5.sql
-- 2) 使用 Docker Postgres 容器（先 docker compose -f docker-compose.dev.yml up -d）：
--    docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -d zhuangxiu_prod -f - < database/migration_v5.sql
-- 3) 使用项目脚本：
--    python scripts/run_migration_v5.py

-- 1) V2.6.2优化：报价单/合同表添加分析进度字段
ALTER TABLE quotes ADD COLUMN IF NOT EXISTS analysis_progress JSONB;
ALTER TABLE contracts ADD COLUMN IF NOT EXISTS analysis_progress JSONB;

-- 2) V2.6.2优化：材料库表
CREATE TABLE IF NOT EXISTS materials (
    id SERIAL PRIMARY KEY,
    material_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,  -- 主材|辅材
    spec_brand VARCHAR(200),
    unit VARCHAR(20),  -- 单位：kg/m²/个等
    typical_price_range JSONB,  -- 典型价格区间
    city_code VARCHAR(20),  -- 城市代码（可选，用于本地化价格）
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_materials_name ON materials(material_name);
CREATE INDEX IF NOT EXISTS idx_materials_category ON materials(category);
CREATE INDEX IF NOT EXISTS idx_materials_city ON materials(city_code);

-- 3) V2.6.2优化：施工进度表添加自定义周期字段
ALTER TABLE constructions ADD COLUMN IF NOT EXISTS custom_durations JSONB;
-- custom_durations: {"S00": 3, "S01": 7, ...} 用户自定义的阶段周期

-- 4) V2.6.2优化：初始化常用材料库（主材）
INSERT INTO materials (material_name, category, spec_brand, unit, typical_price_range, description) VALUES
('水泥', '主材', 'P.O 42.5', 'kg', '{"min": 0.4, "max": 0.6, "unit": "元/kg"}', '普通硅酸盐水泥'),
('瓷砖', '主材', '800x800mm', 'm²', '{"min": 50, "max": 200, "unit": "元/m²"}', '地砖/墙砖'),
('电线', '主材', 'BV 2.5mm²', 'm', '{"min": 3, "max": 8, "unit": "元/m"}', '铜芯电线'),
('水管', '主材', 'PPR 25mm', 'm', '{"min": 8, "max": 15, "unit": "元/m"}', 'PPR水管'),
('乳胶漆', '主材', '18L/桶', '桶', '{"min": 200, "max": 800, "unit": "元/桶"}', '墙面乳胶漆'),
('木地板', '主材', '实木复合', 'm²', '{"min": 100, "max": 300, "unit": "元/m²"}', '实木复合地板'),
('石膏板', '主材', '1200x2400x9mm', '张', '{"min": 25, "max": 50, "unit": "元/张"}', '吊顶用石膏板'),
('防水涂料', '主材', '20kg/桶', '桶', '{"min": 150, "max": 300, "unit": "元/桶"}', '卫生间防水'),
('腻子粉', '辅材', '20kg/袋', '袋', '{"min": 15, "max": 30, "unit": "元/袋"}', '墙面腻子'),
('砂纸', '辅材', '240目', '张', '{"min": 0.5, "max": 2, "unit": "元/张"}', '打磨用砂纸')
ON CONFLICT DO NOTHING;

-- 5) V2.6.2优化：更新unlock_type字段，支持first_free和member类型
-- 已有数据保持不变，新数据会自动使用新类型

COMMENT ON COLUMN quotes.analysis_progress IS 'V2.6.2优化：分析进度 {"step": "ocr|analyzing|generating", "progress": 0-100, "message": "提示信息"}';
COMMENT ON COLUMN contracts.analysis_progress IS 'V2.6.2优化：分析进度 {"step": "ocr|analyzing|generating", "progress": 0-100, "message": "提示信息"}';
COMMENT ON COLUMN constructions.custom_durations IS 'V2.6.2优化：用户自定义阶段周期 {"S00": 3, "S01": 7, ...}';
COMMENT ON TABLE materials IS 'V2.6.2优化：材料库，用于智能补全材料信息';

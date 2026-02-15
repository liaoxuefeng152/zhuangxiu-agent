# 数据库查询指南 - 施工陪伴数据

## 数据库连接信息

### 方式1: 通过Docker容器连接（推荐）

```bash
# SSH登录到阿里云服务器
ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61

# 进入项目目录
cd /root/project/dev/zhuangxiu-agent

# 查看PostgreSQL容器名称
docker compose -f docker-compose.dev.yml ps | grep postgres

# ⚠️ 注意：服务器上可能有两个PostgreSQL容器：
# 1. decoration-postgres-prod - 可能是旧的生产环境数据库
# 2. zhuangxiu-postgres-dev - 开发环境数据库（或decoration-postgres-dev）

# 方式1a: 如果使用docker-compose.dev.yml启动的容器（开发环境数据库：zhuangxiu_dev）
docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -d zhuangxiu_dev

# 方式1b: 如果容器名是zhuangxiu-postgres-dev（开发环境数据库：zhuangxiu_dev）
docker exec -it zhuangxiu-postgres-dev psql -U decoration -d zhuangxiu_dev

# 方式1c: 如果容器名是decoration-postgres-prod（旧的生产环境，数据库：zhuangxiu_prod）
docker exec -it decoration-postgres-prod psql -U decoration -d zhuangxiu_prod
```

### 方式2: 通过psql客户端连接

```bash
# 如果PostgreSQL端口已映射到主机（开发环境数据库：zhuangxiu_dev）
psql -h 120.26.201.61 -p 5432 -U decoration -d zhuangxiu_dev

# ⚠️ 注意：如果连接的是旧的生产环境容器，数据库名是 zhuangxiu_prod
# psql -h 120.26.201.61 -p 5432 -U decoration -d zhuangxiu_prod

# 密码提示时输入: decoration123
```

### 方式3: 通过Docker exec直接执行SQL

```bash
docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -d zhuangxiu_dev -c "SELECT COUNT(*) FROM constructions;"
```

---

## SQL查询语句

### 1. 施工进度数据 (constructions)

```sql
-- 查看所有施工进度记录
SELECT 
    id,
    user_id,
    start_date,
    estimated_end_date,
    actual_end_date,
    progress_percentage,
    is_delayed,
    delay_days,
    stages,
    notes,
    created_at,
    updated_at
FROM constructions
ORDER BY created_at DESC
LIMIT 10;

-- 查看特定用户的施工进度
SELECT 
    id,
    user_id,
    start_date,
    estimated_end_date,
    progress_percentage,
    is_delayed,
    delay_days,
    stages::text as stages_json,
    created_at
FROM constructions
WHERE user_id = 2;  -- 替换为实际的user_id

-- 查看阶段状态详情（展开JSON）
SELECT 
    id,
    user_id,
    start_date,
    estimated_end_date,
    progress_percentage,
    jsonb_pretty(stages::jsonb) as stages_formatted
FROM constructions
WHERE user_id = 2;

-- 统计各阶段完成情况
SELECT 
    user_id,
    COUNT(*) as total_constructions,
    COUNT(CASE WHEN stages->>'S00'->>'status' = 'completed' THEN 1 END) as s00_completed,
    COUNT(CASE WHEN stages->>'S01'->>'status' = 'completed' THEN 1 END) as s01_completed,
    COUNT(CASE WHEN stages->>'S02'->>'status' = 'completed' THEN 1 END) as s02_completed,
    COUNT(CASE WHEN stages->>'S03'->>'status' = 'completed' THEN 1 END) as s03_completed,
    COUNT(CASE WHEN stages->>'S04'->>'status' = 'completed' THEN 1 END) as s04_completed,
    COUNT(CASE WHEN stages->>'S05'->>'status' = 'completed' THEN 1 END) as s05_completed
FROM constructions
GROUP BY user_id;
```

### 2. 材料核对数据 (material_checks)

```sql
-- 查看所有材料核对记录
SELECT 
    mc.id,
    mc.user_id,
    mc.quote_id,
    mc.result,
    mc.problem_note,
    mc.submitted_at,
    mc.created_at,
    COUNT(mci.id) as item_count
FROM material_checks mc
LEFT JOIN material_check_items mci ON mc.id = mci.material_check_id
GROUP BY mc.id
ORDER BY mc.submitted_at DESC
LIMIT 20;

-- 查看特定用户的材料核对记录
SELECT 
    mc.id,
    mc.user_id,
    mc.quote_id,
    mc.result,
    mc.problem_note,
    mc.submitted_at,
    COUNT(mci.id) as item_count
FROM material_checks mc
LEFT JOIN material_check_items mci ON mc.id = mci.material_check_id
WHERE mc.user_id = 2  -- 替换为实际的user_id
GROUP BY mc.id
ORDER BY mc.submitted_at DESC;

-- 查看材料核对详情（包含材料项）
SELECT 
    mc.id as check_id,
    mc.result,
    mc.problem_note,
    mc.submitted_at,
    mci.id as item_id,
    mci.material_name,
    mci.spec_brand,
    mci.quantity,
    jsonb_array_length(COALESCE(mci.photo_urls::jsonb, '[]'::jsonb)) as photo_count,
    mci.photo_urls::text as photo_urls
FROM material_checks mc
LEFT JOIN material_check_items mci ON mc.id = mci.material_check_id
WHERE mc.user_id = 2
ORDER BY mc.submitted_at DESC, mci.id;

-- 统计材料核对通过率
SELECT 
    user_id,
    COUNT(*) as total_checks,
    COUNT(CASE WHEN result = 'pass' THEN 1 END) as passed_count,
    COUNT(CASE WHEN result = 'fail' THEN 1 END) as failed_count,
    ROUND(100.0 * COUNT(CASE WHEN result = 'pass' THEN 1 END) / COUNT(*), 2) as pass_rate
FROM material_checks
GROUP BY user_id;
```

### 3. 验收分析数据 (acceptance_analyses)

```sql
-- 查看所有验收分析记录
SELECT 
    id,
    user_id,
    stage,
    severity,
    status,
    result_status,
    recheck_count,
    jsonb_array_length(COALESCE(file_urls::jsonb, '[]'::jsonb)) as photo_count,
    created_at,
    rectified_at
FROM acceptance_analyses
WHERE deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 20;

-- 查看特定用户的验收分析记录
SELECT 
    id,
    user_id,
    stage,
    severity,
    status,
    result_status,
    jsonb_array_length(COALESCE(file_urls::jsonb, '[]'::jsonb)) as photo_count,
    created_at
FROM acceptance_analyses
WHERE user_id = 2  -- 替换为实际的user_id
  AND deleted_at IS NULL
ORDER BY created_at DESC;

-- 查看验收分析详情（包含照片URL和问题）
SELECT 
    id,
    user_id,
    stage,
    severity,
    status,
    result_status,
    jsonb_pretty(file_urls::jsonb) as photo_urls,
    jsonb_pretty(issues::jsonb) as issues,
    jsonb_pretty(suggestions::jsonb) as suggestions,
    jsonb_pretty(result_json::jsonb) as result_json,
    created_at
FROM acceptance_analyses
WHERE user_id = 2
  AND deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 5;

-- 按阶段统计验收分析
SELECT 
    stage,
    COUNT(*) as total_count,
    COUNT(CASE WHEN severity = 'pass' THEN 1 END) as pass_count,
    COUNT(CASE WHEN severity = 'warning' THEN 1 END) as warning_count,
    COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_count,
    COUNT(CASE WHEN result_status = 'passed' THEN 1 END) as passed_status,
    COUNT(CASE WHEN result_status = 'need_rectify' THEN 1 END) as need_rectify_status
FROM acceptance_analyses
WHERE deleted_at IS NULL
GROUP BY stage
ORDER BY stage;

-- 查看需要整改的验收记录
SELECT 
    id,
    user_id,
    stage,
    severity,
    result_status,
    recheck_count,
    created_at,
    rectified_at
FROM acceptance_analyses
WHERE result_status = 'need_rectify'
  AND deleted_at IS NULL
ORDER BY created_at DESC;
```

### 4. 施工照片数据 (construction_photos)

```sql
-- 查看所有施工照片
SELECT 
    id,
    user_id,
    stage,
    file_url,
    file_name,
    is_read,
    created_at,
    deleted_at
FROM construction_photos
WHERE deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 20;

-- 查看特定用户的施工照片
SELECT 
    id,
    user_id,
    stage,
    file_url,
    file_name,
    is_read,
    created_at
FROM construction_photos
WHERE user_id = 2  -- 替换为实际的user_id
  AND deleted_at IS NULL
ORDER BY created_at DESC;

-- 按阶段统计施工照片
SELECT 
    stage,
    COUNT(*) as photo_count,
    COUNT(CASE WHEN is_read = true THEN 1 END) as read_count,
    COUNT(CASE WHEN is_read = false THEN 1 END) as unread_count
FROM construction_photos
WHERE deleted_at IS NULL
GROUP BY stage
ORDER BY stage;

-- 查看各阶段的最新照片
SELECT DISTINCT ON (stage)
    id,
    user_id,
    stage,
    file_url,
    file_name,
    created_at
FROM construction_photos
WHERE user_id = 2
  AND deleted_at IS NULL
ORDER BY stage, created_at DESC;
```

### 5. 综合查询 - 施工陪伴完整数据

```sql
-- 查看用户的完整施工陪伴数据概览
SELECT 
    u.id as user_id,
    u.nickname,
    c.id as construction_id,
    c.start_date,
    c.progress_percentage,
    (SELECT COUNT(*) FROM material_checks WHERE user_id = u.id) as material_check_count,
    (SELECT COUNT(*) FROM acceptance_analyses WHERE user_id = u.id AND deleted_at IS NULL) as acceptance_count,
    (SELECT COUNT(*) FROM construction_photos WHERE user_id = u.id AND deleted_at IS NULL) as photo_count
FROM users u
LEFT JOIN constructions c ON u.id = c.user_id
WHERE u.id = 2  -- 替换为实际的user_id
ORDER BY c.created_at DESC;

-- 查看用户各阶段的完成情况
SELECT 
    c.user_id,
    c.start_date,
    c.progress_percentage,
    CASE WHEN c.stages->>'S00'->>'status' = 'completed' THEN '✓' ELSE '✗' END as s00,
    CASE WHEN c.stages->>'S01'->>'status' = 'completed' THEN '✓' ELSE '✗' END as s01,
    CASE WHEN c.stages->>'S02'->>'status' = 'completed' THEN '✓' ELSE '✗' END as s02,
    CASE WHEN c.stages->>'S03'->>'status' = 'completed' THEN '✓' ELSE '✗' END as s03,
    CASE WHEN c.stages->>'S04'->>'status' = 'completed' THEN '✓' ELSE '✗' END as s04,
    CASE WHEN c.stages->>'S05'->>'status' = 'completed' THEN '✓' ELSE '✗' END as s05,
    (SELECT COUNT(*) FROM acceptance_analyses aa WHERE aa.user_id = c.user_id AND aa.stage = 'plumbing' AND aa.deleted_at IS NULL) as s01_acceptance_count,
    (SELECT COUNT(*) FROM acceptance_analyses aa WHERE aa.user_id = c.user_id AND aa.stage = 'carpentry' AND aa.deleted_at IS NULL) as s02_acceptance_count,
    (SELECT COUNT(*) FROM acceptance_analyses aa WHERE aa.user_id = c.user_id AND aa.stage = 'woodwork' AND aa.deleted_at IS NULL) as s03_acceptance_count,
    (SELECT COUNT(*) FROM acceptance_analyses aa WHERE aa.user_id = c.user_id AND aa.stage = 'painting' AND aa.deleted_at IS NULL) as s04_acceptance_count,
    (SELECT COUNT(*) FROM acceptance_analyses aa WHERE aa.user_id = c.user_id AND aa.stage = 'soft_furnishing' AND aa.deleted_at IS NULL) as s05_acceptance_count
FROM constructions c
WHERE c.user_id = 2;
```

### 6. 数据统计查询

```sql
-- 统计所有用户的施工数据
SELECT 
    COUNT(DISTINCT c.user_id) as users_with_construction,
    COUNT(*) as total_constructions,
    COUNT(CASE WHEN c.progress_percentage = 100 THEN 1 END) as completed_constructions,
    AVG(c.progress_percentage) as avg_progress,
    COUNT(DISTINCT mc.user_id) as users_with_material_check,
    COUNT(DISTINCT aa.user_id) as users_with_acceptance,
    COUNT(DISTINCT cp.user_id) as users_with_photos
FROM constructions c
LEFT JOIN material_checks mc ON c.user_id = mc.user_id
LEFT JOIN acceptance_analyses aa ON c.user_id = aa.user_id AND aa.deleted_at IS NULL
LEFT JOIN construction_photos cp ON c.user_id = cp.user_id AND cp.deleted_at IS NULL;

-- 按日期统计验收分析数量
SELECT 
    DATE(created_at) as date,
    stage,
    COUNT(*) as count,
    COUNT(CASE WHEN severity = 'pass' THEN 1 END) as pass_count,
    COUNT(CASE WHEN severity = 'warning' THEN 1 END) as warning_count,
    COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_count
FROM acceptance_analyses
WHERE deleted_at IS NULL
GROUP BY DATE(created_at), stage
ORDER BY date DESC, stage;
```

---

## 查询步骤说明

### 步骤1: 连接到数据库

```bash
# 方式1: 通过Docker容器（推荐）
ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61
cd /root/project/dev/zhuangxiu-agent
docker compose -f docker-compose.dev.yml exec postgres psql -U decoration -d zhuangxiu_dev

# 方式2: 如果端口已映射（开发环境数据库：zhuangxiu_dev）
psql -h 120.26.201.61 -p 5432 -U decoration -d zhuangxiu_dev
# 密码: decoration123
```

### 步骤2: 查看表结构（可选）

```sql
-- 查看所有表
\dt

-- 查看表结构
\d constructions
\d material_checks
\d material_check_items
\d acceptance_analyses
\d construction_photos
```

### 步骤3: 执行查询

复制上面的SQL查询语句，在psql中执行。

### 步骤4: 导出查询结果（可选）

```sql
-- 在psql中设置输出格式
\x  -- 展开显示（适合查看JSON字段）
\pset format aligned  -- 表格格式
\timing  -- 显示执行时间

-- 导出到文件
\o /tmp/query_result.txt
SELECT * FROM constructions WHERE user_id = 2;
\o
```

### 步骤5: 退出psql

```sql
\q
```

---

## 常用查询示例

### 示例1: 查看用户2的完整施工数据

```sql
-- 1. 查看施工进度
SELECT * FROM constructions WHERE user_id = 2;

-- 2. 查看材料核对
SELECT mc.*, COUNT(mci.id) as item_count
FROM material_checks mc
LEFT JOIN material_check_items mci ON mc.id = mci.material_check_id
WHERE mc.user_id = 2
GROUP BY mc.id
ORDER BY mc.submitted_at DESC;

-- 3. 查看验收分析
SELECT id, stage, severity, status, created_at
FROM acceptance_analyses
WHERE user_id = 2 AND deleted_at IS NULL
ORDER BY created_at DESC;

-- 4. 查看施工照片
SELECT id, stage, file_name, created_at
FROM construction_photos
WHERE user_id = 2 AND deleted_at IS NULL
ORDER BY created_at DESC;
```

### 示例2: 查看最近7天的验收数据

```sql
SELECT 
    DATE(created_at) as date,
    stage,
    COUNT(*) as count,
    COUNT(CASE WHEN severity = 'pass' THEN 1 END) as pass,
    COUNT(CASE WHEN severity = 'warning' THEN 1 END) as warning,
    COUNT(CASE WHEN severity = 'high' THEN 1 END) as high
FROM acceptance_analyses
WHERE created_at >= NOW() - INTERVAL '7 days'
  AND deleted_at IS NULL
GROUP BY DATE(created_at), stage
ORDER BY date DESC, stage;
```

### 示例3: 查找需要整改的验收记录

```sql
SELECT 
    aa.id,
    aa.user_id,
    aa.stage,
    aa.severity,
    aa.result_status,
    aa.recheck_count,
    aa.created_at,
    aa.rectified_at,
    jsonb_array_length(COALESCE(aa.file_urls::jsonb, '[]'::jsonb)) as photo_count
FROM acceptance_analyses aa
WHERE aa.result_status = 'need_rectify'
  AND aa.deleted_at IS NULL
ORDER BY aa.created_at DESC;
```

---

## 注意事项

1. **JSON字段查询**: PostgreSQL的JSON字段需要使用 `::jsonb` 进行类型转换
2. **软删除**: 大部分表都有 `deleted_at` 字段，查询时需要过滤 `WHERE deleted_at IS NULL`
3. **阶段映射**: 
   - API中使用: S00, S01, S02, S03, S04, S05
   - 数据库中使用: material, plumbing, carpentry, woodwork, painting, soft_furnishing
4. **时区**: 数据库时间可能使用UTC，查询时注意时区转换
5. **权限**: 确保有足够的数据库权限执行查询

---

## 快速参考

### 表名映射
- `constructions` - 施工进度表
- `material_checks` - 材料核对表
- `material_check_items` - 材料核对项表
- `acceptance_analyses` - 验收分析表
- `construction_photos` - 施工照片表
- `users` - 用户表

### 常用字段
- `user_id` - 用户ID
- `created_at` - 创建时间
- `deleted_at` - 删除时间（软删除）
- `stages` - 阶段信息（JSON格式）
- `file_urls` - 文件URL列表（JSON数组）
- `result_json` - 结果JSON（存储AI分析结果）

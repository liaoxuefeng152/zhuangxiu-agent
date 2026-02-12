# OSS照片上传实施计划

## 当前状态分析

### ✅ 已使用OSS的上传点

1. **报价单上传** (`/api/v1/quotes/upload`)
   - 使用 `upload_file_to_oss(file, "quote")`
   - 路径：`quote/{timestamp}_{random}_{filename}`

2. **合同上传** (`/api/v1/contracts/upload`)
   - 使用 `upload_file_to_oss(file, "contract")`
   - 路径：`contract/{timestamp}_{random}_{filename}`

3. **验收照片上传** (`/api/v1/acceptance/upload-photo`)
   - 使用 `upload_file_to_oss(file, "acceptance")`
   - 路径：`acceptance/{timestamp}_{random}_{filename}`

4. **施工照片上传** (`/api/v1/construction-photos/upload`)
   - 使用 `upload_file_to_oss(file, "construction")`
   - 路径：`construction/{timestamp}_{random}_{filename}`

5. **材料核对照片** (通过 `acceptanceApi.uploadPhoto`)
   - 使用 `upload_file_to_oss(file, "acceptance")`
   - 路径：`acceptance/{timestamp}_{random}_{filename}`

### 📋 OSS配置检查

当前 `.env` 文件中的OSS配置（已配置）：
- `ALIYUN_ACCESS_KEY_ID`: 已配置
- `ALIYUN_ACCESS_KEY_SECRET`: 已配置
- `ALIYUN_OSS_BUCKET`: zhuangxiu-images-dev
- `ALIYUN_OSS_ENDPOINT`: oss-cn-hangzhou.aliyuncs.com

### 🔍 需要确认的事项

1. **OSS Bucket权限配置**
   - 确认Bucket是否为公共读或需要签名URL
   - 确认Bucket的CORS配置是否正确

2. **文件路径规范**
   - 当前路径格式：`{type}/{timestamp}_{random}_{filename}`
   - 建议统一路径格式，便于管理

3. **错误处理**
   - 当前有降级方案（返回mock URL），需要确认生产环境是否也需要

## 实施步骤

### 步骤1：统一OSS上传函数

创建统一的OSS上传服务，替换分散的 `upload_file_to_oss` 函数。

### 步骤2：优化文件路径规范

统一文件路径格式：
- 报价单：`quotes/{user_id}/{timestamp}_{random}.{ext}`
- 合同：`contracts/{user_id}/{timestamp}_{random}.{ext}`
- 验收照片：`acceptance/{user_id}/{stage}/{timestamp}_{random}.{ext}`
- 施工照片：`construction/{user_id}/{stage}/{timestamp}_{random}.{ext}`
- 材料核对照片：`material-checks/{user_id}/{timestamp}_{random}.{ext}`

### 步骤3：检查OSS配置

1. 确认Bucket权限设置
2. 确认CORS配置
3. 确认存储类型（标准存储/低频访问）

### 步骤4：测试验证

测试所有上传功能，确保：
- 文件能成功上传到OSS
- 文件URL能正常访问
- 错误处理正确

## 需要您协助的事项

1. **OSS Bucket配置确认**
   - Bucket名称：`zhuangxiu-images-dev` 是否正确？
   - Bucket权限：是否需要设置为公共读，还是使用签名URL？
   - CORS配置：是否已配置允许小程序域名访问？

2. **AccessKey权限确认**
   - 当前AccessKey是否有OSS上传权限？
   - 是否需要限制只能上传到特定Bucket？

3. **存储策略确认**
   - 是否需要设置文件生命周期（自动删除旧文件）？
   - 是否需要设置文件类型限制？

4. **测试环境确认**
   - 当前是开发环境，是否需要同时配置生产环境的OSS？

请告诉我以上信息，我将据此完成OSS上传的统一实施。

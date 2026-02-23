# 装修决策Agent - 自动化部署与 Git 工作流

## 项目概述

装修决策Agent是一个为企业提供装修决策支持的全栈应用，包含微信小程序前端和Python后端服务。项目采用双环境部署策略，确保开发和生产环境的安全隔离。

## 项目结构

```
zhuangxiu-agent/
├── .github/                    # GitHub 配置
│   ├── workflows/             # CI/CD 流水线
│   └── PULL_REQUEST_TEMPLATE.md # PR 模板
├── backend/                   # Python 后端服务
├── frontend/                  # 微信小程序前端
├── scripts/                   # 部署和工具脚本
├── docs/                      # 项目文档
├── config/                    # 环境配置
├── database/                  # 数据库脚本
├── nginx/                     # Nginx 配置
└── miniprogram-native/        # 原生小程序代码
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Git 2.30+

### 本地开发

1. **克隆项目**
   ```bash
   git clone git@github.com:liaoxuefeng152/zhuangxiu-agent.git
   cd zhuangxiu-agent
   ```

2. **安装后端依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **安装前端依赖**
   ```bash
   cd frontend
   npm install
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env.dev
   # 编辑 .env.dev 文件，填写实际配置
   ```

5. **启动开发环境**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

## Git 工作流规范

### 分支策略

项目采用 **Git Flow** 变体，包含以下分支：

| 分支 | 用途 | 部署环境 | 保护级别 |
|------|------|----------|----------|
| `main` | 生产代码 | 生产环境 | 最高 |
| `dev` | 开发代码 | 开发环境 | 中等 |
| `feature/*` | 新功能开发 | 本地 | 低 |
| `bugfix/*` | Bug修复 | 本地 | 低 |
| `hotfix/*` | 紧急修复 | 生产环境 | 高 |
| `release/*` | 版本发布 | 测试环境 | 高 |

### 分支命名规范

```
<类型>/<Issue编号>-<描述>
```

示例：
- `feature/123-add-payment-module`
- `bugfix/456-fix-login-error`
- `hotfix/789-critical-security-fix`
- `release/v2.6.3`

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<类型>(<范围>): <描述>

<正文>

<页脚>
```

类型：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具

示例：
```
feat(payment): 添加微信支付接口

- 实现微信支付统一下单接口
- 添加支付回调处理
- 更新支付状态管理

Closes #123
```

## 自动化部署流程

### CI/CD 流水线

项目使用 GitHub Actions 实现自动化部署：

#### 触发条件
- **Push 到 dev 分支**: 自动部署到开发环境
- **Push 到 main 分支**: 自动部署到生产环境
- **Pull Request**: 运行代码质量检查和测试

#### 流水线阶段
1. **代码质量检查**: Python/TypeScript 代码规范检查
2. **运行测试**: 单元测试和集成测试
3. **构建镜像**: 构建 Docker 镜像并推送到 GitHub Container Registry
4. **部署到环境**: 根据分支部署到对应环境
5. **安全扫描**: 依赖漏洞扫描
6. **创建发布**: 自动创建 GitHub Release

### 部署脚本

项目提供多种部署脚本：

#### 1. 一键部署脚本
```bash
# 部署到开发环境
./scripts/deploy-aliyun-optimized.sh dev

# 部署到生产环境
./scripts/deploy-aliyun-optimized.sh prod

# 回滚生产环境
./scripts/deploy-aliyun-optimized.sh rollback

# 查看服务状态
./scripts/deploy-aliyun-optimized.sh status
```

#### 2. 预合并检查
```bash
# 在合并到 main 分支前运行检查
./scripts/pre-merge-check.sh

# 快速检查（跳过测试）
./scripts/pre-merge-check.sh --quick
```

#### 3. Git Hooks
项目包含预配置的 Git Hooks：
```bash
# 安装 Git Hooks
./scripts/install-git-hooks.sh
```

## 环境配置管理

### 配置文件结构

```
config/
├── dev/                    # 开发环境配置
│   ├── .env.dev           # 开发环境变量
│   └── docker-compose.dev.yml
└── prod/                  # 生产环境配置
    ├── .env.prod          # 生产环境变量
    └── docker-compose.prod.yml
```

### 敏感信息管理

1. **使用环境变量**: 所有敏感信息必须通过环境变量配置
2. **模板文件**: 使用 `.env.example` 作为模板
3. **Git 忽略**: 确保 `.env.*` 文件不被提交到版本控制
4. **密钥轮换**: 定期轮换密码和 API 密钥

### 环境变量模板

复制 `.env.example` 创建环境配置文件：
```bash
# 开发环境
cp .env.example .env.dev

# 生产环境
cp .env.example .env.prod
```

重要配置项：
- `DEBUG`: 开发环境设为 `True`，生产环境必须设为 `False`
- `SECRET_KEY`: 生产环境必须使用强密码
- `DATABASE_URL`: 数据库连接字符串
- `ALIYUN_ACCESS_KEY_ID`: 阿里云 AccessKey（生产环境建议使用 RAM 角色）

## 代码质量控制

### 预提交检查

项目配置了 Git Hooks 进行自动检查：

1. **pre-commit**: 代码格式检查
   - Python: black, isort, flake8
   - TypeScript: prettier, eslint
   - 阻止提交包含敏感信息的文件

2. **pre-push**: 基础测试
   - 运行单元测试
   - 检查代码质量

### 代码审查流程

1. **创建 Pull Request**: 使用项目提供的 PR 模板
2. **代码审查**: 至少需要 1 人审查
3. **CI/CD 检查**: 等待所有检查通过
4. **合并策略**: 根据分支类型选择合适的合并策略

### 预合并检查清单

在合并到 `main` 分支前，必须确保：

- [ ] 不包含 `.env.dev` 等开发环境配置文件
- [ ] 不包含 `DEBUG=True` 等开发配置
- [ ] 不包含硬编码的敏感信息
- [ ] CORS 配置正确（生产环境不使用通配符）
- [ ] 通过所有 CI/CD 检查
- [ ] 代码覆盖率达标（≥70%）
- [ ] 无安全漏洞

## 部署环境

### 开发环境
- **服务器**: 120.26.201.61
- **端口**: 8001
- **访问地址**: http://120.26.201.61:8001
- **健康检查**: http://120.26.201.61:8001/health
- **API 文档**: http://120.26.201.61:8001/api/docs

### 生产环境
- **服务器**: 120.26.201.61
- **端口**: 8000
- **访问地址**: http://120.26.201.61:8000
- **健康检查**: http://120.26.201.61:8000/health
- **API 文档**: http://120.26.201.61:8000/api/docs

## 故障处理

### 常见问题

#### 1. 部署失败
```bash
# 查看部署日志
docker-compose -f docker-compose.prod.yml logs -f

# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 重启服务
docker-compose -f docker-compose.prod.yml restart backend
```

#### 2. 数据库连接问题
```bash
# 检查数据库连接
docker exec -it zhuangxiu-postgres-prod psql -U zhuangxiu_prod_user -d zhuangxiu_prod

# 检查数据库日志
docker logs zhuangxiu-postgres-prod
```

#### 3. 回滚操作
```bash
# 使用部署脚本回滚
./scripts/deploy-aliyun-optimized.sh rollback

# 手动回滚到指定版本
git checkout <commit-hash>
./scripts/deploy-aliyun-optimized.sh prod
```

### 监控和告警

项目配置了监控和告警系统：

1. **健康检查**: 定期检查服务状态
2. **性能监控**: 监控 CPU、内存、磁盘使用率
3. **错误告警**: 通过邮件和钉钉发送告警
4. **日志收集**: 集中收集和分析日志

## 安全最佳实践

### 代码安全
1. **输入验证**: 所有用户输入必须验证
2. **SQL 注入防护**: 使用参数化查询
3. **XSS 防护**: 输出转义
4. **CSRF 防护**: 使用 CSRF Token

### 部署安全
1. **最小权限原则**: 服务使用最小必要权限
2. **网络隔离**: 生产环境网络隔离
3. **定期更新**: 定期更新依赖包和系统
4. **备份策略**: 定期备份数据和配置

### 密钥管理
1. **环境变量**: 使用环境变量管理密钥
2. **密钥轮换**: 定期轮换密钥
3. **访问控制**: 严格控制密钥访问权限
4. **审计日志**: 记录密钥使用情况

## 贡献指南

### 开发流程

1. **创建分支**: 从 `dev` 分支创建功能分支
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/123-add-new-feature
   ```

2. **开发代码**: 在功能分支上开发
3. **运行测试**: 确保所有测试通过
4. **提交代码**: 使用规范的提交信息
5. **创建 PR**: 创建到 `dev` 分支的 Pull Request
6. **代码审查**: 等待审查和 CI/CD 检查
7. **合并代码**: 审查通过后合并到 `dev` 分支

### 代码规范

- **Python**: 遵循 PEP 8，使用 black 格式化
- **TypeScript**: 使用 ESLint 和 Prettier
- **文档**: 所有公共 API 必须有文档
- **测试**: 新功能必须包含测试

## 相关文档

- [Git 分支策略](docs/GIT_BRANCH_STRATEGY.md)
- [API 文档](docs/API接口文档-完整版.md)
- [部署指南](docs/阿里云部署指南.md)
- [测试用例](docs/功能测试用例-V2.6.1.md)

## 联系方式

- **项目仓库**: https://github.com/liaoxuefeng152/zhuangxiu-agent
- **问题反馈**: 创建 GitHub Issue
- **紧急支持**: 联系项目负责人

---

**最后更新**: 2026-02-23  
**版本**: 2.6.3  
**维护者**: 项目技术团队

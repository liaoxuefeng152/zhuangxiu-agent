# Git 分支策略与保护规范

## 概述

本文档定义了装修决策Agent项目的Git分支管理策略、命名规范和保护规则，确保代码质量、部署安全和团队协作效率。

## 分支结构

### 主要分支

1. **main** (主分支)
   - 用途：生产环境代码
   - 保护级别：最高
   - 部署目标：阿里云生产环境
   - 合并要求：必须通过CI/CD流水线，代码审查，测试通过

2. **dev** (开发分支)
   - 用途：开发环境代码
   - 保护级别：中等
   - 部署目标：阿里云开发环境
   - 合并要求：必须通过CI/CD流水线，基础测试

### 支持分支

3. **feature/** (功能分支)
   - 命名：`feature/<issue-id>-<short-description>`
   - 示例：`feature/123-add-payment-module`
   - 来源：从 `dev` 分支创建
   - 目标：合并回 `dev` 分支

4. **bugfix/** (修复分支)
   - 命名：`bugfix/<issue-id>-<short-description>`
   - 示例：`bugfix/456-fix-login-error`
   - 来源：从 `dev` 或 `main` 分支创建
   - 目标：合并回对应分支

5. **hotfix/** (热修复分支)
   - 命名：`hotfix/<issue-id>-<short-description>`
   - 示例：`hotfix/789-critical-security-fix`
   - 来源：从 `main` 分支创建
   - 目标：合并回 `main` 和 `dev` 分支

6. **release/** (发布分支)
   - 命名：`release/v<version>`
   - 示例：`release/v2.6.2`
   - 用途：版本发布准备
   - 来源：从 `dev` 分支创建
   - 目标：合并回 `main` 和 `dev` 分支

## 分支命名规范

### 通用规则

1. **使用小写字母**
2. **使用连字符分隔单词**
3. **包含Issue ID（如果适用）**
4. **保持描述简洁但明确**

### 命名模式

```
<type>/<issue-id>-<kebab-case-description>
```

### 类型前缀

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feature/` | 新功能开发 | `feature/123-add-user-profile` |
| `bugfix/` | Bug修复 | `bugfix/456-fix-api-timeout` |
| `hotfix/` | 紧急生产修复 | `hotfix/789-fix-security-vulnerability` |
| `release/` | 版本发布 | `release/v2.6.3` |
| `chore/` | 维护任务 | `chore/update-dependencies` |
| `docs/` | 文档更新 | `docs/update-api-documentation` |
| `test/` | 测试相关 | `test/add-integration-tests` |
| `refactor/` | 代码重构 | `refactor/optimize-database-queries` |

## 分支保护规则

### main 分支保护

```yaml
保护规则:
  - 要求状态检查通过: true
  - 要求代码审查: true (至少1人批准)
  - 要求线性历史: true
  - 限制推送权限: true (仅限管理员)
  - 限制合并: true (仅限Pull Request)
  - 要求解决对话: true
  - 要求签名提交: false (可选)
  - 锁定分支: false

状态检查要求:
  - ci/cd: build-and-test
  - ci/cd: security-scan
  - ci/cd: deploy-preview
  - lint: python-lint
  - lint: typescript-lint
  - test: unit-tests
  - test: integration-tests
```

### dev 分支保护

```yaml
保护规则:
  - 要求状态检查通过: true
  - 要求代码审查: false
  - 要求线性历史: false
  - 限制推送权限: false
  - 限制合并: false
  - 要求解决对话: false

状态检查要求:
  - ci/cd: build-and-test
  - lint: python-lint
  - lint: typescript-lint
  - test: unit-tests
```

## 合并策略

### 功能开发流程

1. **创建分支**: 从 `dev` 创建 `feature/xxx`
2. **开发**: 在功能分支上开发
3. **测试**: 本地测试通过
4. **推送**: 推送到远程仓库
5. **创建PR**: 创建到 `dev` 的Pull Request
6. **代码审查**: 至少1人审查
7. **CI/CD**: 等待所有检查通过
8. **合并**: 使用 "Squash and Merge"
9. **删除分支**: 合并后删除远程分支

### 热修复流程

1. **创建分支**: 从 `main` 创建 `hotfix/xxx`
2. **修复**: 在热修复分支上修复
3. **测试**: 充分测试修复
4. **创建PR**: 创建到 `main` 的Pull Request
5. **紧急审查**: 快速审查
6. **合并**: 合并到 `main`
7. **同步**: 将修复合并回 `dev`
8. **部署**: 立即部署到生产环境

## 提交信息规范

### 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动
- `perf`: 性能优化
- `ci`: CI/CD配置

### 示例

```
feat(payment): 添加微信支付接口

- 实现微信支付统一下单接口
- 添加支付回调处理
- 更新支付状态管理

Closes #123
```

## 预合并检查

### 开发环境配置保护

为防止开发环境配置意外合并到生产环境，设置以下检查：

1. **配置文件检查**: 禁止包含 `*.env.dev` 的文件合并到 `main`
2. **关键词检查**: 禁止包含 `DEBUG=True` 的配置合并到 `main`
3. **开发环境标记**: 检查 `docker-compose.dev.yml` 等文件

### Git Hooks

项目包含以下Git Hooks：

1. **pre-commit**: 代码格式检查
   - Python: black, isort, flake8
   - TypeScript: prettier, eslint
   - 阻止提交包含敏感信息的文件

2. **pre-push**: 基础测试
   - 运行单元测试
   - 检查代码质量
   - 验证分支保护规则

## 分支生命周期管理

### 创建分支

```bash
# 创建功能分支
git checkout dev
git pull origin dev
git checkout -b feature/123-add-new-feature

# 创建修复分支
git checkout main
git pull origin main
git checkout -b bugfix/456-fix-issue
```

### 清理旧分支

定期清理已合并的分支：

```bash
# 列出已合并到dev的分支
git branch --merged dev | grep -v "dev" | grep -v "main"

# 删除本地已合并分支
git branch --merged dev | grep -v "dev" | grep -v "main" | xargs git branch -d

# 删除远程已合并分支
git fetch --prune
```

## 异常处理

### 合并冲突解决

1. **优先使用 rebase**: 保持线性历史
2. **及时解决**: 避免长期存在的冲突
3. **团队协作**: 复杂冲突需要团队讨论

### 紧急情况

1. **绕过保护**: 仅限管理员，记录原因
2. **强制推送**: 尽量避免，如必须则通知团队
3. **回滚操作**: 使用 `git revert` 而非 `git reset`

## 工具支持

### GitHub 配置

1. **分支保护规则**: 在仓库设置中配置
2. **状态检查**: 集成CI/CD流水线
3. **代码所有者**: 设置 `CODEOWNERS` 文件
4. **合并队列**: 对于高并发项目

### 本地工具

1. **Git Hooks**: 项目已包含
2. **IDE集成**: VS Code Git扩展
3. **命令行工具**: git-flow, hub

## 培训与执行

1. **新成员培训**: 必须阅读本规范
2. **定期审查**: 每季度审查分支策略
3. **持续改进**: 根据项目发展调整策略

---

**最后更新**: 2026-02-23  
**负责人**: 项目技术负责人  
**生效日期**: 立即生效

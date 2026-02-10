# Docker 本地运行指南

## 前置条件

- 已安装 [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/)

## 快速启动

```bash
# 在项目根目录执行
cd /Users/mac/zhuangxiu-agent-backup

# 启动所有服务（PostgreSQL + Redis + 后端）
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f backend
```

## 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 后端 API | 8000 | http://localhost:8000 |
| API 文档 | 8000 | http://localhost:8000/api/docs |
| PostgreSQL | 5432 | 用户: decoration, 密码: decoration123, 数据库: zhuangxiu_prod |
| Redis | 6379 | 无密码 |

## 可选：配置环境变量

如需微信登录、AI 分析、OSS 等功能，在项目根目录创建 `.env` 文件：

```env
SECRET_KEY=your-random-secret-key
WECHAT_APP_ID=xxx
WECHAT_APP_SECRET=xxx
DEEPSEEK_API_KEY=xxx
ALIYUN_ACCESS_KEY_ID=xxx
ALIYUN_ACCESS_KEY_SECRET=xxx
TIANYANCHA_TOKEN=xxx
```

Docker Compose 会自动读取 `.env` 并注入到后端容器。

## 常用命令

```bash
# 停止服务
docker-compose -f docker-compose.dev.yml down

# 停止并删除数据卷（清空数据库）
docker-compose -f docker-compose.dev.yml down -v

# 重新构建后端镜像
docker-compose -f docker-compose.dev.yml build backend

# 重启后端
docker-compose -f docker-compose.dev.yml restart backend
```

## 验证

- 健康检查：http://localhost:8000/health
- API 文档：http://localhost:8000/api/docs

---

## 启动前端（H5 本地联调）

后端已配置 CORS，支持前端跨域请求。

```bash
cd frontend
npm install
npm run dev:h5:local
```

浏览器访问 http://localhost:10086 ，前端会请求本地后端 API。

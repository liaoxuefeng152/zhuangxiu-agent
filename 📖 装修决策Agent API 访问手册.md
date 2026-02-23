# 📖 装修决策Agent API 访问手册

## 📋 **文档信息**
| 项目         | 详情              |
| ------------ | ----------------- |
| **系统名称** | 装修决策Agent API |
| **当前版本** | v2.2.0            |
| **最后更新** | 2026年2月1日      |
| **维护团队** | 开发组            |

---

## 🌐 **网络环境概览**

### **服务器信息**
```
公网IP: 120.26.201.61
服务器位置: 阿里云杭州
备案状态: 备案中（lakeli.top）
```

### **域名解析**
```
dev.lakeli.top    → 120.26.201.61  (开发环境)
api.lakeli.top    → 120.26.201.61  (生产环境)
lakeli.top        → 120.26.201.61  (主域名)
www.lakeli.top    → 120.26.201.61  (WWW域名)
```

---

## 🚀 **快速访问指南**

### **备案期间临时访问方案**
由于域名备案中，需按以下方式访问：

#### **方案A：配置本地Hosts（推荐）**
```bash
# Mac/Linux: sudo nano /etc/hosts
# Windows: C:\Windows\System32\drivers\etc\hosts

# 添加以下配置
120.26.201.61 dev.lakeli.top
120.26.201.61 api.lakeli.top
120.26.201.61 lakeli.top
120.26.201.61 www.lakeli.top
```

#### **方案B：使用IP直接访问**
```
直接使用IP地址，无需域名
```

#### **方案C：curl命令指定Host头**
```bash
curl -H "Host: dev.lakeli.top" http://120.26.201.61/api/docs
```

---

## 🛠️ **开发环境访问**

### **开发团队专用**
| 访问方式       | 地址                                 | 端口 | 认证 | 用途            |
| -------------- | ------------------------------------ | ---- | ---- | --------------- |
| **域名访问**   | `http://dev.lakeli.top/api/docs`     | 80   | 无   | API文档（推荐） |
| **IP+端口**    | `http://120.26.201.61:8001/api/docs` | 8001 | 无   | 直连开发后端    |
| **健康检查**   | `http://dev.lakeli.top/health`       | 80   | 无   | 服务状态检查    |
| **Swagger UI** | `http://dev.lakeli.top/docs`         | 80   | 无   | 交互式文档      |

### **开发API端点**
```
基础路径: http://dev.lakeli.top/api/v1

主要接口:
- POST /users/login           # 微信登录
- GET  /users/profile         # 用户信息
- POST /risk/detect           # 公司风险检测
- POST /quote/review          # 报价单审核
- POST /contract/interpret    # 合同解读
```

---

## 🏢 **生产环境访问**

### **用户访问**
| 访问方式     | 地址                             | 端口 | 状态     | 说明     |
| ------------ | -------------------------------- | ---- | -------- | -------- |
| **API接口**  | `http://api.lakeli.top/api/v1/*` | 80   | ✅ 可用   | 正式API  |
| **健康检查** | `http://api.lakeli.top/health`   | 80   | ✅ 可用   | 内部监控 |
| **前端页面** | `http://www.lakeli.top`          | 80   | ⏳ 待部署 | 用户界面 |
| **管理后台** | `http://admin.lakeli.top`        | 80   | ⏳ 规划中 | 管理界面 |

### **生产API规范**
```
协议: HTTP（备案后升级HTTPS）
认证: JWT Token
限流: 100请求/分钟/IP
数据格式: JSON
字符编码: UTF-8
```

---

## 🔧 **调试与维护访问**

### **后端服务直连**
| 服务           | 地址                        | 端口 | 用途     | 访问限制 |
| -------------- | --------------------------- | ---- | -------- | -------- |
| **开发后端**   | `http://120.26.201.61:8001` | 8001 | 开发环境 | 开发团队 |
| **生产后端**   | `http://120.26.201.61:8000` | 8000 | 生产环境 | 运维团队 |
| **PostgreSQL** | `120.26.201.61`             | 5432 | 数据库   | 仅内网   |
| **Redis**      | `120.26.201.61`             | 6379 | 缓存     | 仅内网   |
| **Nginx管理**  | `http://120.26.201.61:80`   | 80   | 反向代理 | 公开     |

### **监控与日志**
```bash
# 实时日志查看
# Nginx访问日志
sudo docker exec nginx-zhuangxiu tail -f /var/log/nginx/access.log

# Nginx错误日志
sudo docker exec nginx-zhuangxiu tail -f /var/log/nginx/error.log

# 开发后端日志
sudo docker logs -f zhuangxiu-backend-dev

# 生产后端日志
sudo docker logs -f decoration-backend-prod
```

---

## 📡 **API测试示例**

### **快速测试脚本**
```bash
#!/bin/bash
# test_api.sh

# 开发环境测试
echo "=== 开发环境测试 ==="
DEV_BASE="http://dev.lakeli.top"

echo "1. 健康检查:"
curl -s "$DEV_BASE/health" | jq .

echo -e "\n2. API文档:"
curl -s "$DEV_BASE/api/docs" | grep -o "<title>[^<]*</title>"

# 生产环境测试
echo -e "\n=== 生产环境测试 ==="
PROD_BASE="http://api.lakeli.top"

echo "1. 健康检查:"
curl -s "$PROD_BASE/health" | jq '.data.status'

echo -e "\n2. 响应时间:"
time curl -s -o /dev/null -w "HTTP状态: %{http_code}\n" "$PROD_BASE/health"
```

### **Postman配置**
```
集合名称: 装修决策Agent API
环境变量:
- baseUrl_dev: http://dev.lakeli.top
- baseUrl_prod: http://api.lakeli.top
- token: {{从登录接口获取}}
```

---

## 🔐 **安全访问指南**

### **访问权限矩阵**
| 角色         | 开发环境   | 生产环境   | 数据库 | 服务器 |
| ------------ | ---------- | ---------- | ------ | ------ |
| **开发人员** | ✅ 完全访问 | ❌ 只读API  | ❌ 无   | ❌ 无   |
| **测试人员** | ✅ 只读API  | ✅ 只读API  | ❌ 无   | ❌ 无   |
| **运维人员** | ✅ 完全访问 | ✅ 完全访问 | ✅ 只读 | ✅ SSH  |
| **最终用户** | ❌ 无       | ✅ 只读API  | ❌ 无   | ❌ 无   |

### **防火墙规则**
```bash
# 当前开放端口
sudo ufw status numbered
# [1] 80/tcp ALLOW Anywhere
# [2] 443/tcp ALLOW Anywhere
# [3] 8000/tcp ALLOW Anywhere
# [4] 8001/tcp ALLOW Anywhere
# [5] 22/tcp ALLOW 你的IP
```

---

## 🐳 **Docker服务清单**

### **运行中的容器**
```bash
sudo docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"
```

| 容器名称                   | 镜像                    | 端口映射       | 状态 |
| -------------------------- | ----------------------- | -------------- | ---- |
| `nginx-zhuangxiu`          | nginx:alpine            | 80:80, 443:443 | Up   |
| `zhuangxiu-backend-dev`    | code-backend-dev        | 8001:8000      | Up   |
| `decoration-backend-prod`  | zhuangxiu-agent-backend | 8000:8000      | Up   |
| `zhuangxiu-postgres-dev`   | postgres:latest         | 5432:5432      | Up   |
| `decoration-postgres-prod` | postgres:latest         | 5432/tcp       | Up   |
| `decoration-redis-prod`    | redis:latest            | 6379/tcp       | Up   |

---

## 📊 **性能监控**

### **健康检查端点**
```bash
# 开发环境
curl http://dev.lakeli.top/health
# 返回: {"status":"healthy","version":"2.2.0"}

# 生产环境
curl http://api.lakeli.top/health
# 返回: {"status":"healthy","version":"2.2.0"}
```

### **连接池监控**
```bash
curl http://dev.lakeli.top/internal/monitor/pool-status
```

### **响应时间监控**
```bash
# 测试响应时间
curl -w "
时间统计:
DNS解析: %{time_namelookup}s
连接建立: %{time_connect}s
SSL握手: %{time_appconnect}s
开始传输: %{time_starttransfer}s
总时间: %{time_total}s
" -o /dev/null -s http://api.lakeli.top/health
```

---

## 🚨 **故障排查**

### **常见问题解决**

#### **问题1：域名无法访问**
```bash
# 诊断步骤
1. 检查DNS解析: nslookup dev.lakeli.top
2. 检查本地hosts: cat /etc/hosts | grep lakeli
3. 测试IP访问: curl http://120.26.201.61:8001/health
4. 测试带Host头: curl -H "Host: dev.lakeli.top" http://120.26.201.61/health
```

#### **问题2：API返回错误**
```bash
# 查看服务状态
sudo docker ps | grep backend
sudo docker logs --tail 20 zhuangxiu-backend-dev

# 检查Nginx转发
curl -v -H "Host: dev.lakeli.top" http://127.0.0.1/health
```

#### **问题3：数据库连接失败**
```bash
# 检查数据库服务
sudo docker ps | grep postgres
sudo docker exec zhuangxiu-postgres-dev pg_isready
```

### **紧急联系方式**
```
开发问题: 开发团队群
运维问题: 运维值班
服务器问题: 阿里云工单
域名备案: 备案专员
```

---

## 🔄 **部署与更新**

### **服务重启流程**
```bash
# 1. 重启Nginx
sudo docker restart nginx-zhuangxiu

# 2. 重启开发后端
sudo docker restart zhuangxiu-backend-dev

# 3. 重启生产后端
sudo docker restart decoration-backend-prod

# 4. 验证服务
./test_api.sh
```

### **配置更新流程**
```bash
# 1. 更新Nginx配置
sudo nano /etc/nginx-zhuangxiu/nginx.conf

# 2. 测试配置
sudo docker exec nginx-zhuangxiu nginx -t

# 3. 重载配置
sudo docker exec nginx-zhuangxiu nginx -s reload

# 4. 验证更新
curl -H "Host: dev.lakeli.top" http://127.0.0.1/health
```

---

## 📈 **容量规划**

### **当前资源配置**
```
服务器: 阿里云ECS 2核4G
数据库: PostgreSQL 10GB
缓存: Redis 1GB
带宽: 5Mbps
存储: 40GB SSD
```

### **访问量预估**
```
开发环境: < 10人并发
生产环境: 初期 < 1000用户/日
API调用: < 10000次/日
数据存储: < 1GB/月
```

---

## ✅ **检查清单**

### **每日检查**
- [ ] 所有服务运行正常 `docker ps`
- [ ] API可访问 `curl http://dev.lakeli.top/health`
- [ ] 数据库连接正常
- [ ] 磁盘空间充足 `df -h`

### **每周检查**
- [ ] 日志文件大小 `du -sh /var/log/nginx-zhuangxiu/`
- [ ] 备份完整性
- [ ] 安全更新 `apt list --upgradable`
- [ ] 性能监控数据

### **上线前检查**
- [ ] 域名备案完成
- [ ] SSL证书配置
- [ ] 生产环境权限收紧
- [ ] 监控告警配置
- [ ] 备份策略验证

---

## 📞 **支持与反馈**

### **问题报告模板**
```markdown
问题描述: 
环境: [开发/生产]
访问地址: 
错误信息: 
复现步骤: 
期望结果: 
截图/日志: 
```

### **联系渠道**
```
技术讨论: 开发团队Slack/钉钉
故障报告: 运维工单系统
需求反馈: 产品管理平台
紧急故障: 电话值班
```

---

## 🎯 **附录**

### **命令速查**
```bash
# 查看所有服务
sudo docker ps -a

# 查看Nginx配置
sudo docker exec nginx-zhuangxiu nginx -T

# 实时日志
sudo docker logs -f --tail 50 nginx-zhuangxiu

# 进入容器
sudo docker exec -it zhuangxiu-backend-dev /bin/bash

# 服务状态检查
./test_api.sh
```

### **环境变量参考**
```bash
# 开发环境
export API_BASE="http://dev.lakeli.top"
export API_TOKEN="开发测试token"

# 生产环境  
export API_BASE="http://api.lakeli.top"
export API_TOKEN="从登录接口获取"
```

---

**文档版本**: 1.0  
**维护者**: 技术团队  
**更新频率**: 每周检查更新  
**生效日期**: 2026年2月1日  

---
*提示：备案期间请使用本地hosts或IP直连方式访问，备案通过后可直接使用域名。*
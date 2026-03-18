# 宿主机Nginx配置修复方案

## 问题诊断
**这是环境/配置问题**。宿主机Nginx配置 `/etc/nginx/conf.d/prod.conf` 存在以下问题：

1. **重复配置段**：有两段重复的配置
2. **错误的代理目标**：第二段配置错误地指向了公网IP `120.26.201.61:8001`
3. **架构混乱**：配置直接代理到后端容器，而不是按照正确的架构转发

## 正确架构
```
公网请求 (443/80) → 宿主机Nginx → Docker内Nginx容器 (127.0.0.1:80) → Backend容器
```

## 修复步骤

### 1. 备份当前配置
```bash
# 备份当前配置
sudo cp /etc/nginx/conf.d/prod.conf /etc/nginx/conf.d/prod.conf.backup.$(date +%Y%m%d_%H%M%S)
```

### 2. 创建正确的宿主机Nginx配置
创建文件 `/etc/nginx/conf.d/prod.conf`：

```nginx
# /etc/nginx/conf.d/prod.conf - 宿主机Nginx配置
# 正确架构：公网请求 → 宿主机Nginx → Docker内Nginx容器 → Backend容器

# HTTP服务器 - 重定向到HTTPS
server {
    listen 80;
    server_name lakeli.top www.lakeli.top;
    
    # 重定向所有HTTP请求到HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS服务器 - 主配置
server {
    listen 443 ssl http2;
    server_name lakeli.top www.lakeli.top;

    # SSL证书配置
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # SSL优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;

    # 安全头
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # 允许上传最大 25MB
    client_max_body_size 25m;

    # 将所有请求转发给Docker内的Nginx容器
    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. 应用配置
```bash
# 测试配置语法
sudo nginx -t

# 重新加载Nginx
sudo systemctl reload nginx
```

### 4. 验证配置
```bash
# 检查宿主机Nginx是否监听443端口
sudo netstat -tlnp | grep :443

# 检查Docker内Nginx容器是否运行
docker ps | grep nginx

# 测试HTTPS访问
curl -k https://lakeli.top/health
```

### 5. 检查Docker内Nginx容器配置
确保Docker内的Nginx容器使用正确的配置：
- 配置文件：`nginx/conf.d/prod.conf`（项目中的配置）
- 监听端口：80
- 代理目标：`http://decoration-backend-dev:8000`

## 验证命令

### 检查当前配置状态
```bash
# 查看宿主机Nginx配置
sudo cat /etc/nginx/conf.d/prod.conf | head -50

# 查看Docker容器状态
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 测试连通性
curl -v http://127.0.0.1:80/health
```

### 日志检查
```bash
# 查看宿主机Nginx错误日志
sudo tail -f /var/log/nginx/error.log

# 查看Docker内Nginx容器日志
docker logs <nginx-container-name>
```

## 故障排除

### 1. SSL证书问题
```bash
# 检查证书文件是否存在
sudo ls -la /etc/nginx/ssl/

# 检查证书权限
sudo chmod 644 /etc/nginx/ssl/fullchain.pem
sudo chmod 600 /etc/nginx/ssl/privkey.pem
```

### 2. Docker网络问题
```bash
# 检查Docker网络
docker network ls
docker network inspect bridge

# 测试容器间连通性
docker exec <nginx-container> curl http://decoration-backend-dev:8000/health
```

### 3. 防火墙问题
```bash
# 检查防火墙规则
sudo ufw status
sudo firewall-cmd --list-all

# 开放端口
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp
```

## 总结
**问题归属**：这是**环境/配置问题**，已提供完整的修复方案。

**关键点**：
1. 宿主机Nginx只做SSL终止和简单转发
2. 所有业务逻辑路由由Docker内Nginx处理
3. 确保Docker内Nginx容器正常运行
4. 验证SSL证书和网络连通性

按照上述步骤操作，Nginx配置问题应该能够得到解决。

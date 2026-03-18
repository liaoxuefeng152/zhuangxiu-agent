#!/bin/bash

# 宿主机Nginx配置修复脚本
# 使用方法：ssh登录阿里云服务器后执行：bash fix_host_nginx.sh

set -e

echo "========================================="
echo "宿主机Nginx配置修复脚本"
echo "========================================="

# 1. 备份当前配置
echo "1. 备份当前配置..."
BACKUP_FILE="/etc/nginx/conf.d/prod.conf.backup.$(date +%Y%m%d_%H%M%S)"
if [ -f "/etc/nginx/conf.d/prod.conf" ]; then
    sudo cp /etc/nginx/conf.d/prod.conf "$BACKUP_FILE"
    echo "✅ 配置已备份到: $BACKUP_FILE"
else
    echo "⚠️  配置文件不存在: /etc/nginx/conf.d/prod.conf"
fi

# 2. 创建新的配置文件
echo ""
echo "2. 创建新的配置文件..."
cat > /tmp/prod.conf.new << 'EOF'
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
EOF

# 3. 应用新配置
echo ""
echo "3. 应用新配置..."
sudo cp /tmp/prod.conf.new /etc/nginx/conf.d/prod.conf
sudo chmod 644 /etc/nginx/conf.d/prod.conf
echo "✅ 新配置已写入: /etc/nginx/conf.d/prod.conf"

# 4. 测试配置语法
echo ""
echo "4. 测试配置语法..."
if sudo nginx -t; then
    echo "✅ Nginx配置语法检查通过"
else
    echo "❌ Nginx配置语法检查失败"
    echo "请检查配置文件: /etc/nginx/conf.d/prod.conf"
    exit 1
fi

# 5. 重新加载Nginx
echo ""
echo "5. 重新加载Nginx..."
sudo systemctl reload nginx
echo "✅ Nginx已重新加载"

# 6. 验证配置
echo ""
echo "6. 验证配置..."
echo "检查宿主机Nginx监听端口:"
sudo netstat -tlnp | grep -E ':80|:443' || true

echo ""
echo "检查Docker容器状态:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "nginx|backend" || true

# 7. 检查SSL证书
echo ""
echo "7. 检查SSL证书..."
if [ -d "/etc/nginx/ssl" ]; then
    echo "SSL证书目录:"
    sudo ls -la /etc/nginx/ssl/
    
    if [ -f "/etc/nginx/ssl/fullchain.pem" ] && [ -f "/etc/nginx/ssl/privkey.pem" ]; then
        echo "✅ SSL证书文件存在"
        
        # 检查证书权限
        sudo chmod 644 /etc/nginx/ssl/fullchain.pem 2>/dev/null || true
        sudo chmod 600 /etc/nginx/ssl/privkey.pem 2>/dev/null || true
        echo "✅ SSL证书权限已设置"
    else
        echo "⚠️  SSL证书文件缺失"
        echo "请确保以下文件存在:"
        echo "  - /etc/nginx/ssl/fullchain.pem"
        echo "  - /etc/nginx/ssl/privkey.pem"
    fi
else
    echo "❌ SSL证书目录不存在: /etc/nginx/ssl/"
    echo "请创建目录并放置SSL证书文件"
fi

# 8. 测试连通性
echo ""
echo "8. 测试连通性..."
echo "测试本地Nginx连通性:"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://127.0.0.1/health || echo "❌ 无法连接到本地Nginx"

echo ""
echo "测试Docker内后端服务:"
docker exec $(docker ps -q --filter "name=decoration-backend") curl -s http://localhost:8000/health 2>/dev/null || echo "❌ 无法连接到Docker内后端服务"

echo ""
echo "========================================="
echo "修复完成！"
echo "========================================="
echo ""
echo "下一步操作建议:"
echo "1. 测试HTTPS访问: curl -k https://lakeli.top/health"
echo "2. 查看Nginx日志: sudo tail -f /var/log/nginx/error.log"
echo "3. 查看Docker日志: docker logs <nginx-container-name>"
echo ""
echo "如果遇到问题，可以恢复备份:"
echo "sudo cp $BACKUP_FILE /etc/nginx/conf.d/prod.conf"
echo "sudo systemctl reload nginx"
echo ""
echo "问题归属: 这是环境/配置问题，已修复宿主机Nginx配置。"

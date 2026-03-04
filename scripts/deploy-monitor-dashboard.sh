#!/bin/bash

# 监控仪表板部署脚本
# 将监控仪表板文件部署到阿里云服务器并重启Nginx

set -e

echo "🚀 开始部署监控仪表板..."

# 配置文件路径
LOCAL_DASHBOARD_FILE="monitor_dashboard.html"
LOCAL_NGINX_CONFIG="nginx/conf.d/prod.conf"
REMOTE_SERVER="root@120.26.201.61"
REMOTE_SSH_KEY="$HOME/zhuangxiu-agent1.pem"
REMOTE_NGINX_HTML_DIR="/usr/share/nginx/html"
REMOTE_NGINX_CONFIG_DIR="/etc/nginx/conf.d"

# 检查本地文件是否存在
if [ ! -f "$LOCAL_DASHBOARD_FILE" ]; then
    echo "❌ 错误: 本地监控仪表板文件不存在: $LOCAL_DASHBOARD_FILE"
    exit 1
fi

if [ ! -f "$LOCAL_NGINX_CONFIG" ]; then
    echo "❌ 错误: 本地Nginx配置文件不存在: $LOCAL_NGINX_CONFIG"
    exit 1
fi

if [ ! -f "$REMOTE_SSH_KEY" ]; then
    echo "❌ 错误: SSH密钥文件不存在: $REMOTE_SSH_KEY"
    echo "请确保密钥文件存在并具有正确的权限: chmod 600 $REMOTE_SSH_KEY"
    exit 1
fi

echo "✅ 本地文件检查通过"

# 上传监控仪表板文件
echo "📤 上传监控仪表板文件到阿里云服务器..."
scp -i "$REMOTE_SSH_KEY" "$LOCAL_DASHBOARD_FILE" "$REMOTE_SERVER:$REMOTE_NGINX_HTML_DIR/"

if [ $? -eq 0 ]; then
    echo "✅ 监控仪表板文件上传成功"
else
    echo "❌ 监控仪表板文件上传失败"
    exit 1
fi

# 上传Nginx配置文件
echo "📤 上传Nginx配置文件到阿里云服务器..."
scp -i "$REMOTE_SSH_KEY" "$LOCAL_NGINX_CONFIG" "$REMOTE_SERVER:$REMOTE_NGINX_CONFIG_DIR/"

if [ $? -eq 0 ]; then
    echo "✅ Nginx配置文件上传成功"
else
    echo "❌ Nginx配置文件上传失败"
    exit 1
fi

# 重启Nginx服务
echo "🔄 重启阿里云服务器上的Nginx服务..."
ssh -i "$REMOTE_SSH_KEY" "$REMOTE_SERVER" << 'EOF'
    echo "检查Nginx配置..."
    nginx -t
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx配置检查通过"
        
        echo "重启Nginx服务..."
        systemctl restart nginx
        
        if [ $? -eq 0 ]; then
            echo "✅ Nginx服务重启成功"
            
            # 检查服务状态
            echo "检查Nginx服务状态..."
            systemctl status nginx --no-pager
            
            # 检查监控仪表板文件权限
            echo "检查监控仪表板文件权限..."
            ls -la /usr/share/nginx/html/monitor_dashboard.html
            
            # 测试访问
            echo "测试监控仪表板访问..."
            curl -s -o /dev/null -w "%{http_code}" https://lakeli.top/monitor_dashboard.html
            echo " - HTTP状态码"
            
        else
            echo "❌ Nginx服务重启失败"
            exit 1
        fi
    else
        echo "❌ Nginx配置检查失败"
        exit 1
    fi
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 监控仪表板部署完成！"
    echo ""
    echo "📊 监控仪表板访问地址:"
    echo "   https://lakeli.top/monitor_dashboard.html"
    echo ""
    echo "🔧 部署文件:"
    echo "   - 监控仪表板: $REMOTE_NGINX_HTML_DIR/monitor_dashboard.html"
    echo "   - Nginx配置: $REMOTE_NGINX_CONFIG_DIR/prod.conf"
    echo ""
    echo "⚠️  注意事项:"
    echo "   1. 如果访问时出现404错误，请检查文件权限:"
    echo "      chmod 644 $REMOTE_NGINX_HTML_DIR/monitor_dashboard.html"
    echo "   2. 如果出现502错误，请检查后端服务是否运行:"
    echo "      systemctl status docker"
    echo "   3. 查看Nginx错误日志:"
    echo "      tail -f /var/log/nginx/prod-error.log"
else
    echo "❌ 部署过程中出现错误"
    exit 1
fi

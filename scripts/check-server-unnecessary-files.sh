#!/bin/bash
# 检查阿里云开发环境服务器上不必要的文件
# 在服务器上执行: bash /root/project/dev/zhuangxiu-agent/scripts/check-server-unnecessary-files.sh

cd /root/project/dev/zhuangxiu-agent || exit 1

echo "=========================================="
echo "检查阿里云开发环境不必要的文件"
echo "=========================================="
echo ""

echo "【1. 前端代码 - 服务器不需要】"
if [ -d "frontend" ]; then
    echo "  ❌ frontend/ - 前端在本地编译，服务器不需要"
    du -sh frontend/ 2>/dev/null | awk '{print "    大小: " $1}'
else
    echo "  ✅ frontend/ 不存在"
fi

echo ""
echo "【2. 原生小程序 - 服务器不需要】"
if [ -d "miniprogram-native" ]; then
    echo "  ❌ miniprogram-native/ - 原生小程序在本地，服务器不需要"
    du -sh miniprogram-native/ 2>/dev/null | awk '{print "    大小: " $1}'
else
    echo "  ✅ miniprogram-native/ 不存在"
fi

echo ""
echo "【3. 测试文件 - 服务器不需要】"
if [ -d "tests" ]; then
    echo "  ❌ tests/ - 测试在本地运行，服务器不需要"
    du -sh tests/ 2>/dev/null | awk '{print "    大小: " $1}'
else
    echo "  ✅ tests/ 不存在"
fi

echo ""
echo "【4. 文档 - 服务器不需要】"
if [ -d "docs" ]; then
    echo "  ❌ docs/ - 文档在本地查看，服务器不需要"
    du -sh docs/ 2>/dev/null | awk '{print "    大小: " $1}'
else
    echo "  ✅ docs/ 不存在"
fi

if [ -f "V2.6.1最新产品需求文档.md" ] || [ -f "V2.6.1最新原型文档.md" ]; then
    echo "  ❌ V2.6.1*.md - 产品文档，服务器不需要"
    ls -lh V2.6.1*.md 2>/dev/null | awk '{print "    " $9 " (" $5 ")"}'
fi

echo ""
echo "【5. 本地开发配置 - 服务器不需要】"
if [ -f "docker-compose.dev.yml" ]; then
    echo "  ❌ docker-compose.dev.yml - 本地开发用，服务器用 docker-compose.server-dev.yml"
    ls -lh docker-compose.dev.yml | awk '{print "    大小: " $5}'
else
    echo "  ✅ docker-compose.dev.yml 不存在"
fi

if [ -f "check-all.sh" ]; then
    echo "  ❌ check-all.sh - 本地检查脚本，服务器不需要"
    ls -lh check-all.sh | awk '{print "    大小: " $5}'
else
    echo "  ✅ check-all.sh 不存在"
fi

echo ""
echo "【6. Nginx 配置 - 检查是否完整】"
if [ -f "nginx/nginx.conf" ]; then
    echo "  ⚠️  nginx/nginx.conf - 完整nginx配置"
    echo "     如果服务器nginx用独立配置，这个可能不需要"
    ls -lh nginx/nginx.conf | awk '{print "    大小: " $5}'
fi

if [ -d "nginx/ssl" ]; then
    echo "  ⚠️  nginx/ssl/ - SSL证书"
    echo "     开发环境如果不用HTTPS，可以删除"
    du -sh nginx/ssl/ 2>/dev/null | awk '{print "    大小: " $1}'
fi

if [ -f "nginx/conf.d/dev.conf" ]; then
    echo "  ✅ nginx/conf.d/dev.conf - 开发环境nginx配置（需要保留）"
fi

echo ""
echo "【7. 根目录 Dockerfile - 检查是否为空或冗余】"
if [ -f "Dockerfile" ]; then
    if [ ! -s "Dockerfile" ]; then
        echo "  ❌ Dockerfile - 空文件，可删除"
    else
        echo "  ⚠️  Dockerfile - 检查是否与 backend/Dockerfile 重复"
        echo "     实际构建用 backend/Dockerfile（docker-compose.server-dev.yml）"
        ls -lh Dockerfile | awk '{print "    大小: " $5}'
    fi
fi

echo ""
echo "【8. 其他可能不需要的文件】"
if [ -f ".env.example" ]; then
    echo "  ⚠️  .env.example - 示例文件，服务器上已有 .env 时可删除"
fi

if [ -d ".pydeps" ]; then
    echo "  ❌ .pydeps/ - Python依赖缓存，不应在服务器上"
    du -sh .pydeps/ 2>/dev/null | awk '{print "    大小: " $1}'
fi

if [ -d "__pycache__" ] || [ -d "backend/__pycache__" ]; then
    echo "  ❌ __pycache__/ - Python缓存，应删除"
    find . -type d -name "__pycache__" -exec du -sh {} \; 2>/dev/null | head -5
fi

if [ -f "*.log" ] 2>/dev/null; then
    echo "  ❌ *.log - 日志文件，应定期清理"
    ls -lh *.log 2>/dev/null | awk '{print "    " $9 " (" $5 ")"}'
fi

echo ""
echo "=========================================="
echo "总结：服务器开发环境只需要"
echo "=========================================="
echo "  ✅ backend/ - 后端代码"
echo "  ✅ database/ - 数据库迁移脚本"
echo "  ✅ docker-compose.server-dev.yml - 服务器编排"
echo "  ✅ nginx/conf.d/dev.conf - Nginx开发配置"
echo "  ✅ scripts/ - 服务器脚本（如需要）"
echo "  ✅ .env - 环境变量（不提交git）"
echo ""
echo "其他文件都可以考虑删除以节省空间。"

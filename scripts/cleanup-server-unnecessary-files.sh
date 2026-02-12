#!/bin/bash
# 删除阿里云开发环境服务器上不必要的文件
# 在服务器上执行: bash /root/project/dev/zhuangxiu-agent/scripts/cleanup-server-unnecessary-files.sh

set -e

cd /root/project/dev/zhuangxiu-agent || exit 1

echo "=========================================="
echo "清理阿里云开发环境不必要的文件"
echo "=========================================="
echo ""

# 1. 前端代码（875M）- 服务器不需要
if [ -d "frontend" ]; then
    echo "【删除】frontend/ (875M) - 前端在本地编译，服务器不需要"
    rm -rf frontend/
    echo "  ✅ 已删除"
fi

# 2. 原生小程序 - 服务器不需要
if [ -d "miniprogram-native" ]; then
    echo "【删除】miniprogram-native/ - 原生小程序在本地，服务器不需要"
    rm -rf miniprogram-native/
    echo "  ✅ 已删除"
fi

# 3. 测试文件目录
if [ -d "tests" ]; then
    echo "【删除】tests/ - 测试在本地运行，服务器不需要"
    rm -rf tests/
    echo "  ✅ 已删除"
fi

if [ -d "test" ]; then
    echo "【删除】test/ (336K) - 测试目录"
    rm -rf test/
    echo "  ✅ 已删除"
fi

# 4. 文档目录
if [ -d "docs" ]; then
    echo "【删除】docs/ (64K) - 文档在本地查看，服务器不需要"
    rm -rf docs/
    echo "  ✅ 已删除"
fi

# 5. 报告目录
if [ -d "report" ]; then
    echo "【删除】report/ (332K) - 测试报告，服务器不需要"
    rm -rf report/
    echo "  ✅ 已删除"
fi

# 6. 备份目录
if [ -d "config_backup" ]; then
    echo "【删除】config_backup/ (20K) - 配置备份"
    rm -rf config_backup/
    echo "  ✅ 已删除"
fi

# 7. secrets目录（生产环境用）
if [ -d "secrets" ]; then
    echo "【删除】secrets/ (12K) - 生产环境secrets，开发环境不需要"
    rm -rf secrets/
    echo "  ✅ 已删除"
fi

# 8. 日志目录（保留结构，只清理内容）
if [ -d "logs" ]; then
    echo "【清理】logs/ - 清理日志文件"
    find logs/ -type f -name "*.log" -delete 2>/dev/null || true
    echo "  ✅ 已清理"
fi

# 9. 生产环境docker-compose文件
if [ -f "docker-compose.yml" ]; then
    echo "【删除】docker-compose.yml - 生产环境文件，开发环境用 docker-compose.dev.yml"
    rm -f docker-compose.yml
    echo "  ✅ 已删除"
fi

if [ -f "docker-compose.yml.backup" ]; then
    echo "【删除】docker-compose.yml.backup - 备份文件"
    rm -f docker-compose.yml.backup
    echo "  ✅ 已删除"
fi

if [ -f "docker-compose.yml.bak" ]; then
    echo "【删除】docker-compose.yml.bak - 备份文件"
    rm -f docker-compose.yml.bak
    echo "  ✅ 已删除"
fi

# 10. 根目录空文件或冗余文件
if [ -f "Dockerfile" ] && [ ! -s "Dockerfile" ]; then
    echo "【删除】Dockerfile - 空文件，实际使用 backend/Dockerfile"
    rm -f Dockerfile
    echo "  ✅ 已删除"
fi

if [ -f "nginx.conf" ]; then
    echo "【删除】nginx.conf - 根目录nginx配置，使用 nginx/nginx.conf"
    rm -f nginx.conf
    echo "  ✅ 已删除"
fi

if [ -f "grep" ] && [ ! -s "grep" ]; then
    echo "【删除】grep - 空文件"
    rm -f grep
    echo "  ✅ 已删除"
fi

if [ -f "shd" ]; then
    echo "【删除】shd - 临时文件"
    rm -f shd
    echo "  ✅ 已删除"
fi

if [ -f "status.html" ]; then
    echo "【删除】status.html - 临时状态文件"
    rm -f status.html
    echo "  ✅ 已删除"
fi

if [ -f "package-lock.json" ]; then
    echo "【删除】package-lock.json - 根目录npm文件，前端在本地"
    rm -f package-lock.json
    echo "  ✅ 已删除"
fi

if [ -f "requirements.txt" ]; then
    echo "【删除】requirements.txt - 根目录Python依赖，实际在 backend/requirements.txt"
    rm -f requirements.txt
    echo "  ✅ 已删除"
fi

# 11. 测试脚本和测试文件
echo "【删除】测试脚本和测试文件..."
rm -f test-*.py test-*.sh 2>/dev/null || true
rm -f check-all.sh check-dev.sh check-status.sh 2>/dev/null || true
rm -f quick-test.sh test-all.sh test-api.sh test-dev.sh test-final.sh test-real-api.sh 2>/dev/null || true
rm -f verify-config.sh 2>/dev/null || true
echo "  ✅ 已删除测试脚本"

# 12. 管理脚本（如果不需要）
# 保留 manage-dev.sh, start-dev.sh, stop-dev.sh, dev-env.sh（可能有用）
# 删除 manage.sh（如果不需要）

# 13. 文档文件（*.md）- 保留必要的，删除测试报告和临时文档
echo "【删除】测试报告和临时文档..."
rm -f BUG_REPORT.md deployment-checklist.md 2>/dev/null || true
rm -f OCR诊断报告.md OCR配置修复指南.md P0和P2问题修复总结.md PRD_缺陷清单.md 2>/dev/null || true
rm -f V2.6.1最新产品需求文档.md V2.6.1最新原型文档.md 2>/dev/null || true
rm -f *测试报告*.md *修复*.md *说明*.md *指南*.md *总结*.md 2>/dev/null || true
rm -f ACCESS_GUIDE.md DEVELOPER_ACCESS.md DEV_ENVIRONMENT.md DEV_GUIDE.md PROJECT_SUMMARY.md SERVER_GUIDE.md 2>/dev/null || true
rm -f 启动说明.md 微信开发工具验证指南.md 2>/dev/null || true
echo "  ✅ 已删除文档文件"

# 14. Python缓存
echo "【清理】Python缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name ".pydeps" -exec rm -rf {} + 2>/dev/null || true
echo "  ✅ 已清理Python缓存"

# 15. 日志文件
echo "【清理】日志文件..."
find . -maxdepth 1 -type f -name "*.log" -delete 2>/dev/null || true
echo "  ✅ 已清理日志文件"

echo ""
echo "=========================================="
echo "清理完成！"
echo "=========================================="
echo ""
echo "保留的文件/目录："
echo "  ✅ backend/ - 后端代码"
echo "  ✅ database/ - 数据库迁移脚本"
echo "  ✅ docker-compose.dev.yml - 开发环境编排"
echo "  ✅ nginx/conf.d/dev.conf - Nginx开发配置"
echo "  ✅ scripts/ - 服务器脚本"
echo "  ✅ .env - 环境变量"
echo "  ✅ .git/ - Git仓库"
echo ""
echo "查看剩余文件："
du -sh * .[^.]* 2>/dev/null | sort -h | tail -10

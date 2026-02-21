#!/bin/bash

# 生产环境部署测试脚本
# 验证所有必要的环境变量和配置
# 使用ECS RAM角色，无需AccessKey

set -e

echo "=== 生产环境部署测试 ==="
echo "开始时间: $(date)"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查环境变量函数
check_env_var() {
    local var_name=$1
    local var_value=$(eval echo \$$var_name)
    
    if [ -z "$var_value" ]; then
        echo -e "${RED}❌ 环境变量 $var_name 未设置${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $var_name 已设置${NC}"
        return 0
    fi
}

# 检查文件是否存在
check_file() {
    local file_path=$1
    local description=$2
    
    if [ -f "$file_path" ]; then
        echo -e "${GREEN}✅ $description 文件存在: $file_path${NC}"
        return 0
    else
        echo -e "${RED}❌ $description 文件不存在: $file_path${NC}"
        return 1
    fi
}

# 检查目录是否存在
check_dir() {
    local dir_path=$1
    local description=$2
    
    if [ -d "$dir_path" ]; then
        echo -e "${GREEN}✅ $description 目录存在: $dir_path${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $description 目录不存在: $dir_path${NC}"
        return 1
    fi
}

echo "=== 1. 检查基础环境变量 ==="

# 应用配置
check_env_var "APP_NAME"
check_env_var "ENV"
check_env_var "DEBUG"
check_env_var "LOG_LEVEL"

# 数据库配置
check_env_var "DB_HOST"
check_env_var "DB_NAME"
check_env_var "DB_USER"
# DB_PASSWORD 可以为空（使用其他认证方式）
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}⚠️  DB_PASSWORD 未设置（可能使用其他认证方式）${NC}"
fi

# Redis配置
check_env_var "REDIS_HOST"
check_env_var "REDIS_PORT"

# 微信配置
check_env_var "WECHAT_APP_ID"
check_env_var "WECHAT_APP_SECRET"
check_env_var "WECHAT_CALLBACK_TOKEN"

# 微信支付配置
if [ -z "$WECHAT_MCH_ID" ]; then
    echo -e "${YELLOW}⚠️  WECHAT_MCH_ID 未设置（支付功能可能不可用）${NC}"
fi

echo ""
echo "=== 2. 检查阿里云配置（使用ECS RAM角色） ==="

# 阿里云OSS配置（使用RAM角色，无需AccessKey）
check_env_var "ALIYUN_OSS_BUCKET"
check_env_var "ALIYUN_OSS_BUCKET1"
check_env_var "ALIYUN_OSS_ENDPOINT"
check_env_var "ALIYUN_OCR_ENDPOINT"

# 注意：不再检查ALIYUN_ACCESS_KEY_ID/SECRET，因为使用RAM角色
echo -e "${GREEN}✅ 使用ECS RAM角色自动获取凭证，无需配置AccessKey${NC}"
echo -e "${YELLOW}⚠️  请确保ECS实例已绑定RAM角色 'zhuangxiu-ecs-role'${NC}"

echo ""
echo "=== 3. 检查聚合数据API配置 ==="

check_env_var "JUHECHA_TOKEN"
check_env_var "SIMPLE_LIST_TOKEN"

echo ""
echo "=== 4. 检查AI智能体配置 ==="

# AI监理智能体
if [ -n "$COZE_SITE_URL" ] && [ -n "$COZE_SITE_TOKEN" ]; then
    echo -e "${GREEN}✅ AI监理智能体配置完整${NC}"
else
    echo -e "${YELLOW}⚠️  AI监理智能体配置不完整（功能可能受限）${NC}"
fi

# AI设计师智能体
if [ -n "$DESIGN_SITE_URL" ] && [ -n "$DESIGN_SITE_TOKEN" ]; then
    echo -e "${GREEN}✅ AI设计师智能体配置完整${NC}"
else
    echo -e "${YELLOW}⚠️  AI设计师智能体配置不完整（功能可能受限）${NC}"
fi

echo ""
echo "=== 5. 检查JWT和安全配置 ==="

check_env_var "SECRET_KEY"
check_env_var "ALGORITHM"
check_env_var "ACCESS_TOKEN_EXPIRE_MINUTES"

echo ""
echo "=== 6. 检查文件和目录 ==="

# 检查证书目录
check_dir "./cert" "SSL证书"

# 检查证书文件（如果配置了路径）
if [ -n "$WECHAT_CERT_PATH" ] && [ "$WECHAT_CERT_PATH" != "./cert/apiclient_cert.pem" ]; then
    check_file "$WECHAT_CERT_PATH" "微信支付证书"
fi

if [ -n "$WECHAT_PRIVATE_KEY_PATH" ] && [ "$WECHAT_PRIVATE_KEY_PATH" != "./cert/apiclient_key.pem" ]; then
    check_file "$WECHAT_PRIVATE_KEY_PATH" "微信支付私钥"
fi

# 检查日志目录
check_dir "./logs" "日志"

echo ""
echo "=== 7. 检查Docker配置 ==="

# 检查Docker Compose文件
check_file "docker-compose.prod.yml" "生产环境Docker Compose"

# 检查Dockerfile
check_file "backend/Dockerfile" "后端Dockerfile"

echo ""
echo "=== 8. 检查网络和端口 ==="

# 检查必要的端口是否可用（简单测试）
check_port() {
    local port=$1
    local service=$2
    
    if command -v nc &> /dev/null; then
        if nc -z localhost $port &> /dev/null; then
            echo -e "${YELLOW}⚠️  $service 端口 $port 已被占用${NC}"
            return 1
        else
            echo -e "${GREEN}✅ $service 端口 $port 可用${NC}"
            return 0
        fi
    else
        echo -e "${YELLOW}⚠️  无法检查端口 $port（nc命令不可用）${NC}"
        return 0
    fi
}

# 检查常用端口
check_port 5432 "PostgreSQL"
check_port 6379 "Redis"
check_port 8000 "应用后端"

echo ""
echo "=== 9. 总结和建议 ==="

echo "生产环境配置检查完成。"
echo ""
echo "重要提醒："
echo "1. 阿里云服务使用ECS RAM角色，请确保："
echo "   - ECS实例已绑定RAM角色 'zhuangxiu-ecs-role'"
echo "   - RAM角色已授权OSS和OCR的相应权限"
echo "2. 数据库和Redis连接信息已正确配置"
echo "3. 微信小程序配置已更新为生产环境"
echo "4. SSL证书文件已放置在正确位置"
echo ""
echo "部署命令："
echo "docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "测试完成时间: $(date)"

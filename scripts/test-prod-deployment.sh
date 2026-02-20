#!/bin/bash
# 生产环境部署测试脚本
# 用于验证生产环境配置是否正确

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}生产环境部署配置测试${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. 检查必要文件
echo -e "${YELLOW}[1/6] 检查必要文件...${NC}"

check_file() {
    if [ -f "$1" ]; then
        echo -e "  ${GREEN}✓ $1${NC}"
        return 0
    else
        echo -e "  ${RED}✗ 缺少文件: $1${NC}"
        return 1
    fi
}

check_file ".env.prod"
check_file "docker-compose.prod.yml"
check_file "nginx/conf.d/prod.conf"
check_file "nginx/ssl/fullchain.pem"
check_file "nginx/ssl/privkey.pem"
check_file "frontend/.env.production"

# 2. 检查环境变量配置
echo -e "${YELLOW}[2/6] 检查环境变量配置...${NC}"

check_env_var() {
    if grep -q "$1" ".env.prod"; then
        echo -e "  ${GREEN}✓ $1 已配置${NC}"
        return 0
    else
        echo -e "  ${YELLOW}⚠ $1 未找到${NC}"
        return 1
    fi
}

check_env_var "ENV=production"
check_env_var "DEBUG=false"
check_env_var "DATABASE_URL="
check_env_var "REDIS_URL="
check_env_var "WECHAT_APP_ID="
check_env_var "ALIYUN_ACCESS_KEY_ID="

# 3. 检查Nginx配置
echo -e "${YELLOW}[3/6] 检查Nginx配置...${NC}"

if grep -q "lakeli.top" "nginx/conf.d/prod.conf"; then
    echo -e "  ${GREEN}✓ Nginx配置中包含域名 lakeli.top${NC}"
else
    echo -e "  ${RED}✗ Nginx配置中缺少域名 lakeli.top${NC}"
fi

if grep -q "ssl_certificate" "nginx/conf.d/prod.conf"; then
    echo -e "  ${GREEN}✓ Nginx配置中包含SSL证书配置${NC}"
else
    echo -e "  ${RED}✗ Nginx配置中缺少SSL证书配置${NC}"
fi

# 4. 检查前端配置
echo -e "${YELLOW}[4/6] 检查前端配置...${NC}"

if grep -q "TARO_APP_API_BASE_URL=" "frontend/.env.production"; then
    API_URL=$(grep "TARO_APP_API_BASE_URL=" "frontend/.env.production" | cut -d'=' -f2)
    echo -e "  ${GREEN}✓ 前端API地址: $API_URL${NC}"
    
    if [[ "$API_URL" == *"lakeli.top"* ]]; then
        echo -e "  ${GREEN}✓ API地址包含生产域名${NC}"
    else
        echo -e "  ${YELLOW}⚠ API地址可能不是生产环境${NC}"
    fi
else
    echo -e "  ${RED}✗ 前端配置中缺少API地址${NC}"
fi

# 5. 检查Docker配置
echo -e "${YELLOW}[5/6] 检查Docker配置...${NC}"

if grep -q "zhuangxiu-backend-prod" "docker-compose.prod.yml"; then
    echo -e "  ${GREEN}✓ Docker配置中使用生产环境容器名${NC}"
else
    echo -e "  ${RED}✗ Docker配置中容器名不正确${NC}"
fi

if grep -q "\.env\.prod" "docker-compose.prod.yml"; then
    echo -e "  ${GREEN}✓ Docker配置中使用生产环境变量文件${NC}"
else
    echo -e "  ${YELLOW}⚠ Docker配置中环境变量文件可能不是生产环境${NC}"
fi

# 6. 检查部署脚本
echo -e "${YELLOW}[6/6] 检查部署脚本...${NC}"

if [ -f "scripts/deploy-aliyun.sh" ]; then
    echo -e "  ${GREEN}✓ 部署脚本存在${NC}"
    
    if grep -q "prod" "scripts/deploy-aliyun.sh"; then
        echo -e "  ${GREEN}✓ 部署脚本支持生产环境${NC}"
    else
        echo -e "  ${RED}✗ 部署脚本可能不支持生产环境${NC}"
    fi
else
    echo -e "  ${RED}✗ 缺少部署脚本${NC}"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}测试完成！${NC}"
echo -e "${GREEN}========================================${NC}"

echo ""
echo "下一步建议："
echo "1. 确保数据库和Redis服务已就绪"
echo "2. 确保域名解析正确（lakeli.top → 服务器IP）"
echo "3. 确保SSL证书有效"
echo "4. 执行部署: ./scripts/deploy-aliyun.sh prod"
echo "5. 验证部署: curl -f https://lakeli.top/health"
echo ""

# 检查脚本权限
if [ ! -x "scripts/deploy-aliyun.sh" ]; then
    echo -e "${YELLOW}提示: 部署脚本没有执行权限，运行以下命令：${NC}"
    echo "chmod +x scripts/deploy-aliyun.sh"
fi

exit 0

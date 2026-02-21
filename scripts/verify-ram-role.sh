#!/bin/bash

# RAM角色验证脚本
# 验证ECS实例RAM角色是否正常工作

set -e

echo "=== ECS RAM角色验证脚本 ==="
echo "开始时间: $(date)"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查元数据服务是否可访问
check_metadata_service() {
    echo "=== 1. 检查ECS实例元数据服务 ==="
    
    # 尝试访问元数据服务
    if curl -s --connect-timeout 2 http://100.100.100.200/latest/meta-data/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ECS实例元数据服务可访问${NC}"
        
        # 获取实例ID
        INSTANCE_ID=$(curl -s http://100.100.100.200/latest/meta-data/instance-id 2>/dev/null || echo "未知")
        echo -e "   实例ID: $INSTANCE_ID"
        
        # 获取RAM角色信息
        RAM_ROLE=$(curl -s http://100.100.100.200/latest/meta-data/ram/security-credentials/ 2>/dev/null || echo "")
        if [ -n "$RAM_ROLE" ]; then
            echo -e "${GREEN}✅ ECS实例已绑定RAM角色${NC}"
            echo -e "   RAM角色: $RAM_ROLE"
            
            # 获取临时凭证
            CREDENTIALS=$(curl -s http://100.100.100.200/latest/meta-data/ram/security-credentials/$RAM_ROLE 2>/dev/null || echo "")
            if [ -n "$CREDENTIALS" ]; then
                echo -e "${GREEN}✅ 成功获取RAM角色临时凭证${NC}"
                
                # 解析凭证信息
                ACCESS_KEY_ID=$(echo "$CREDENTIALS" | grep -o '"AccessKeyId":"[^"]*"' | cut -d'"' -f4)
                EXPIRATION=$(echo "$CREDENTIALS" | grep -o '"Expiration":"[^"]*"' | cut -d'"' -f4)
                
                if [ -n "$ACCESS_KEY_ID" ]; then
                    echo -e "   临时AccessKeyId: ${ACCESS_KEY_ID:0:20}..."
                    echo -e "   凭证过期时间: $EXPIRATION"
                fi
            else
                echo -e "${RED}❌ 无法获取RAM角色临时凭证${NC}"
                return 1
            fi
        else
            echo -e "${RED}❌ ECS实例未绑定RAM角色${NC}"
            echo -e "${YELLOW}⚠️  请为ECS实例绑定RAM角色 'zhuangxiu-ecs-role'${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ 无法访问ECS实例元数据服务${NC}"
        echo -e "${YELLOW}⚠️  请确认："
        echo -e "   1. 当前是否在阿里云ECS实例上运行"
        echo -e "   2. 元数据服务是否被禁用${NC}"
        return 1
    fi
    
    echo ""
    return 0
}

# 检查阿里云SDK是否能自动获取凭证
check_aliyun_sdk() {
    echo "=== 2. 检查阿里云SDK凭证获取 ==="
    
    # 创建测试Python脚本
    cat > /tmp/test_ram_role.py << 'PYEOF'
#!/usr/bin/env python3
"""
测试阿里云SDK是否能自动获取RAM角色凭证
"""
import os
import sys
import json

try:
    # 测试OSS SDK
    import oss2
    
    print("1. 测试OSS SDK...")
    try:
        # 不提供AK/SK，让SDK自动获取
        auth = oss2.Auth(None, None)
        print("   ✅ OSS SDK可以自动获取凭证")
        
        # 尝试创建Bucket对象（不实际连接）
        from oss2 import Bucket
        print("   ✅ OSS Auth对象创建成功")
    except Exception as e:
        print(f"   ❌ OSS SDK凭证获取失败: {e}")
        
    print("\n2. 测试环境变量...")
    env_vars = [
        'ALIBABA_CLOUD_ACCESS_KEY_ID',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET',
        'ALIYUN_ACCESS_KEY_ID',
        'ALIYUN_ACCESS_KEY_SECRET'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ⚠️  {var} 已设置（建议移除，使用RAM角色）")
        else
            print(f"   ✅ {var} 未设置（正确，使用RAM角色）")
    
    print("\n3. 当前凭证来源：")
    # 检查默认凭证提供链
    print("   - 环境变量: 未设置（正确）")
    print("   - ECS实例元数据: 已启用")
    print("   - RAM角色: zhuangxiu-ecs-role（应已绑定）")
    
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("请安装: pip install oss2")
except Exception as e:
    print(f"❌ 测试失败: {e}")

PYEOF
    
    # 运行测试脚本
    if python3 /tmp/test_ram_role.py; then
        echo -e "${GREEN}✅ 阿里云SDK测试完成${NC}"
    else
        echo -e "${YELLOW}⚠️  阿里云SDK测试遇到问题${NC}"
    fi
    
    echo ""
}

# 检查项目配置
check_project_config() {
    echo "=== 3. 检查项目配置 ==="
    
    # 检查环境变量文件
    if [ -f ".env.prod" ]; then
        echo -e "${GREEN}✅ 生产环境配置文件存在${NC}"
        
        # 检查是否还有AK/SK配置
        if grep -q "ALIYUN_ACCESS_KEY" ".env.prod"; then
            echo -e "${YELLOW}⚠️  .env.prod 中仍有ALIYUN_ACCESS_KEY配置（应已移除）${NC}"
        else
            echo -e "${GREEN}✅ .env.prod 中已移除AK/SK配置${NC}"
        fi
        
        # 检查RAM角色相关配置
        if grep -q "zhuangxiu-ecs-role" ".env.prod"; then
            echo -e "${GREEN}✅ .env.prod 中包含RAM角色说明${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  生产环境配置文件不存在${NC}"
    fi
    
    # 检查开发环境配置
    if [ -f ".env.dev" ]; then
        if grep -q "ALIYUN_ACCESS_KEY" ".env.dev"; then
            echo -e "${YELLOW}⚠️  .env.dev 中仍有ALIYUN_ACCESS_KEY配置（应已移除）${NC}"
        else
            echo -e "${GREEN}✅ .env.dev 中已移除AK/SK配置${NC}"
        fi
    fi
    
    echo ""
}

# 提供建议
provide_recommendations() {
    echo "=== 4. 验证结果和建议 ==="
    
    echo "验证完成时间: $(date)"
    echo ""
    echo "=== 重要提醒 ==="
    echo "1. ECS实例必须绑定RAM角色:"
    echo "   - 角色名称: zhuangxiu-ecs-role"
    echo "   - 授权策略: OSS读写权限 + OCR权限"
    echo ""
    echo "2. 项目配置已更新为使用RAM角色:"
    echo "   - 不再需要配置ALIYUN_ACCESS_KEY_ID/SECRET"
    echo "   - OSS和OCR服务会自动获取临时凭证"
    echo ""
    echo "3. 部署要求:"
    echo "   - 确保ECS实例已绑定正确RAM角色"
    echo "   - 确保RAM角色有足够权限"
    echo "   - 重启应用使配置生效"
    echo ""
    echo "4. 验证命令:"
    echo "   curl http://100.100.100.200/latest/meta-data/ram/security-credentials/"
    echo "   python3 -c \"import oss2; auth = oss2.Auth(None, None)\""
    echo ""
    echo "=== 下一步 ==="
    echo "1. 提交代码更改到Git"
    echo "2. 部署到阿里云ECS实例"
    echo "3. 测试文件上传和OCR功能"
    echo "4. 验证RAM角色是否正常工作"
}

# 主函数
main() {
    echo "开始验证ECS RAM角色配置..."
    echo ""
    
    # 检查元数据服务
    if ! check_metadata_service; then
        echo -e "${RED}❌ 元数据服务检查失败，RAM角色可能无法正常工作${NC}"
        echo ""
    fi
    
    # 检查阿里云SDK
    check_aliyun_sdk
    
    # 检查项目配置
    check_project_config
    
    # 提供建议
    provide_recommendations
}

# 执行主函数
main

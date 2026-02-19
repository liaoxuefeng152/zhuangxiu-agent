# AI分析失败修复方案

## 问题诊断
经过详细测试，发现AI分析功能失败的根本原因是：

1. **扣子站点Token已过期**：返回403错误 "Authentication failed: invalid token or insufficient permissions"
2. **无备用AI服务**：未配置DeepSeek API，导致无备用方案
3. **返回兜底结果**：用户看到"AI分析服务暂时不可用，请稍后重试"

## 解决方案

### 方案一：更新扣子站点Token（推荐）
1. 登录扣子平台 (https://www.coze.cn)
2. 进入AI监理智能体页面
3. 重新生成站点Token
4. 更新`.env`文件中的`COZE_SITE_TOKEN`值

### 方案二：切换到扣子开放平台API
1. 在扣子平台获取开放平台API Token
2. 更新`.env`文件：
   ```
   COZE_API_TOKEN=你的扣子开放平台API_Token
   COZE_BOT_ID=7603691852046368804  # 使用COZE_SUPERVISOR_BOT_ID的值
   COZE_SITE_URL=  # 留空
   COZE_SITE_TOKEN=  # 留空
   ```

### 方案三：配置DeepSeek API作为备用
1. 注册DeepSeek账号并获取API Key
2. 更新`.env`文件：
   ```
   DEEPSEEK_API_KEY=你的DeepSeek_API_Key
   # 扣子配置可以保留，DeepSeek将作为备用
   ```

## 立即修复步骤（临时方案）

由于这是**后台问题**，需要部署到阿里云服务器。请执行以下步骤：

### 1. 本地测试修复
```bash
# 备份当前配置
cp .env .env.backup

# 编辑.env文件，选择上述方案之一进行配置
# 例如，如果选择方案二，添加：
# COZE_API_TOKEN=你的扣子开放平台API_Token
# COZE_BOT_ID=7603691852046368804
```

### 2. 测试修复效果
```bash
# 运行测试脚本验证修复
python test_quote_analysis_simple.py
```

### 3. 部署到阿里云服务器
```bash
# 提交代码到Git
git add .
git commit -m "修复AI分析失败问题：更新扣子API配置"
git push

# SSH登录阿里云服务器
ssh -i ~/zhuangxiu-agent1.pem root@120.26.201.61

# 在服务器上执行
cd /root/project/dev/zhuangxiu-agent
git pull
docker compose -f docker-compose.dev.yml build backend --no-cache
docker compose -f docker-compose.dev.yml up -d backend
```

## 验证修复
1. 重新测试装修报价分析功能
2. 确认AI分析返回真实数据，而不是"AI分析失败"
3. 检查返回的分析结果是否包含风险评分、建议等详细信息

## 预防措施
1. 定期检查扣子Token有效期
2. 配置多个AI服务提供商作为备用
3. 添加AI服务健康检查机制
4. 设置Token过期提醒

## 问题归属
**这是后台问题**，需要：
- 更新后端AI服务配置
- 重新部署到阿里云服务器
- 重启后端服务使配置生效

修复后，AI分析功能将恢复正常，用户不再看到"AI分析失败"的错误提示。

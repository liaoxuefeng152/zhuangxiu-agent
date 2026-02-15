# 微信小程序 UI 自动化测试（Minium）

## 测试用例文档

全部功能的 UI 自动化测试用例见：**[docs/UI自动化测试用例-全功能.md](../docs/UI自动化测试用例-全功能.md)**  
覆盖：引导、首页、公司检测、报价、合同、施工陪伴、材料核对、验收、消息、我的、数据管理、支付、反馈等。

## 运行方式

### 1. 环境准备

- Python 3.8+
- 安装 Minium：`pip install minium`
- **微信开发者工具**：打开本项目 `frontend` 目录，先执行 `npm run build:weapp` 编译，再在开发者工具中加载 **编译后的 dist 目录**（或直接打开 frontend 并编译）
- 在开发者工具中：**设置 → 安全设置 → 开启「服务端口」**

### 2. 执行脚本

在**项目根目录**执行：

```bash
python tests/ui/run_ui_tests.py
```

- 若未安装 `minium` 或无法连接开发者工具，脚本会提示并**退出码 0**（不阻塞 CI）。
- 连接成功后会执行约 8 个页面跳转用例（首页、我的、施工陪伴、公司检测、报价、合同、消息、数据管理），并输出通过/失败数量。

### 3. 配置（可选）

脚本默认使用项目根目录下的 `frontend` 作为 `project_path`。若需指定开发者工具路径或端口，可修改 `tests/ui/run_ui_tests.py` 中的 `conf` 字典（参考 [Minium 配置](https://minitest.weixin.qq.com/#/minium/Python/readme)）。

## 与接口测试的区别

| 类型     | 脚本/文档                    | 说明                     |
|----------|------------------------------|--------------------------|
| 接口自动化 | `tests/test_all_features_comprehensive.py` | 直接请求后端 API，无需打开小程序 |
| UI 自动化  | `tests/ui/run_ui_tests.py` + `docs/UI自动化测试用例-全功能.md` | 依赖微信开发者工具与 Minium，驱动小程序页面 |

# OSS 上传策略接口配置说明

## 问题说明

若接口 `GET /api/v1/oss/upload-policy` 返回 **503** 或返回 200 但 `data.available === false`，说明阿里云 OSS 未在运行环境里正确配置。

## 已做的代码修复

- **修改前**：OSS 未配置时接口直接返回 **503 Service Unavailable**，前端会报错。
- **修改后**：OSS 未配置时接口返回 **200**，且 `data.available === false`，并附带说明信息；前端可据此走「后端代理上传」（如 `/acceptance/upload-photo`），不再因 503 报错。

如需启用 **OSS 直传**（后端只签发 policy，文件由前端直传 OSS），需要在部署环境配置以下变量。

---

## 需要您协助配置的环境变量

在 **阿里云服务器** 上，为运行后端的环境（Docker 或 systemd）配置以下环境变量（示例以开发机为例）。

### 1. 阿里云访问密钥（必填）

从 [阿里云控制台 - AccessKey 管理](https://ram.console.aliyun.com/manage/ak) 创建 RAM 用户的 AccessKey，并填入：

| 变量名 | 说明 | 示例（请替换为真实值） |
|--------|------|------------------------|
| `ALIYUN_ACCESS_KEY_ID` | 阿里云 AccessKey ID | LTAI5t... |
| `ALIYUN_ACCESS_KEY_SECRET` | 阿里云 AccessKey Secret | xxxxx... |

### 2. OSS 照片 Bucket（必填）

施工/验收照片使用的 Bucket（您之前提到的 `zhuangxiu-images-dev-photo`）：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `ALIYUN_OSS_BUCKET1` | 照片存储 Bucket 名称 | `zhuangxiu-images-dev-photo` |
| `ALIYUN_OSS_ENDPOINT` | OSS Endpoint（可选，有默认值） | `oss-cn-hangzhou.aliyuncs.com` |

### 3. 配置方式示例

**方式一：Docker Compose 环境变量**

在 `docker-compose.dev.yml`（或实际使用的 compose 文件）中，为 backend 服务增加：

```yaml
services:
  backend:
    environment:
      - ALIYUN_ACCESS_KEY_ID=你的AccessKeyId
      - ALIYUN_ACCESS_KEY_SECRET=你的AccessKeySecret
      - ALIYUN_OSS_BUCKET1=zhuangxiu-images-dev-photo
      - ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
```

**方式二：服务器上的 .env 文件**

若后端通过 `.env` 加载配置，在项目目录或后端目录的 `.env` 中增加：

```bash
ALIYUN_ACCESS_KEY_ID=你的AccessKeyId
ALIYUN_ACCESS_KEY_SECRET=你的AccessKeySecret
ALIYUN_OSS_BUCKET1=zhuangxiu-images-dev-photo
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
```

**注意**：`.env` 不要提交到 Git，避免密钥泄露。

---

## 配置后验证

1. 重启后端服务（例如：`docker compose -f docker-compose.dev.yml up -d backend`）。
2. 再次请求：  
   `GET /api/v1/oss/upload-policy?stage=material`  
   并带登录后的 `Authorization` 头。
3. 若配置正确，响应为 200 且 `data.available === true`，并包含 `host`、`policy`、`signature` 等字段。
4. 若仍为 `data.available === false`，请检查上述 4 个环境变量是否都已正确设置并生效（重启后是否加载到进程环境）。

---

## 安全提醒

- AccessKey 具备账号下的资源访问权限，请勿提交到代码库或暴露到前端。
- 建议使用 RAM 子账号，仅授予 OSS 对应 Bucket 的读写权限，降低风险。

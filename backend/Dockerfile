# 装修决策Agent - 后端Dockerfile（生产优化版）
FROM python:3.10-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录
WORKDIR /app

# 使用阿里云 apt 镜像（国内服务器直连 deb.debian.org 易超时）
RUN set -e; \
    for f in /etc/apt/sources.list /etc/apt/sources.list.d/debian.sources; do \
        [ -f "$f" ] && sed -i 's|deb.debian.org|mirrors.aliyun.com|g; s|security.debian.org|mirrors.aliyun.com|g' "$f" || true; \
    done

# 安装系统依赖（含中文字体，供 PDF 导出正确显示中文）
# fonts-wqy-zenhei 文泉驿：ReportLab 对 TTC 支持好，无需 subfontIndex
# fonts-noto-cjk：备选；fontconfig 确保字体路径生效
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    postgresql-client \
    curl \
    fontconfig \
    fonts-wqy-zenhei \
    fonts-noto-cjk \
    && fc-cache -f \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖（使用阿里云PyPI镜像）
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY . .

# 创建证书目录并复制证书文件
RUN mkdir -p /app/cert
COPY cert/*.pem /app/cert/

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

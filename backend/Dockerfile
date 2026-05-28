FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（libmagic-dev 提供 libmagic，filetype 库替代 python-magic）
RUN apt-get update && apt-get install -y \
    libmagic-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p /app/uploads /app/data/chroma

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

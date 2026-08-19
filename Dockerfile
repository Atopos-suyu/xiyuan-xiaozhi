# 锡院小智后端 · Docker 镜像
# 支持一键部署到 Zeabur / Render / Railway / 任意云服务器
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 复制后端代码
COPY backend/ /app/backend/
ENV PYTHONPATH=/app/backend

# 复制已建好的知识库（83 片段向量 + SQLite 元数据），避免部署时重新抓取
COPY data/kb/ /app/data/kb/

# 端口
EXPOSE 8000

# 启动（模型首次启动时自动下载到 data/hf_home）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

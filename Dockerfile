# 锡院小智后端 · Docker 镜像
# 兼容：阿里云函数计算（自定义容器）/ Zeabur / Render / 任意云服务器
#
# 关键适配：函数计算/Serverless 的 /app 目录只读，模型缓存预置到可写的 /tmp，
# 避免运行时下载或写锁失败。
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

# 预置 embedding 模型缓存到可写目录 /tmp（约 92MB）
COPY data/hf_home/ /tmp/hf_home/
ENV HF_HOME=/tmp/hf_home \
    HF_HUB_CACHE=/tmp/hf_home/hub

# 端口
EXPOSE 8000

# 启动（模型从 /tmp 直接加载，无需下载）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

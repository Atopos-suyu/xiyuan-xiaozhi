# 部署指南：GitHub + 国内服务器/云函数

按"代码在 GitHub、正式服务在国内"的原则，分为两部分：**后端部署**与**前端部署**。

---

## 一、后端部署（DeepSeek API + RAG）

后端必须运行在有外网可访问的服务器/云函数上，API Key 只存在这里。

### 方案 A：轻量云服务器（推荐，最省心）

1. 购买轻量应用服务器（阿里云/腾讯云，2核4G 即可，学生认证有优惠）。
2. 安装 Docker 或 Python 3.11+。
3. 上传代码：

```bash
git clone https://github.com/<你的账号>/xiyuan-xiaozhi.git
cd xiyuan-xiaozhi
cp .env.example .env
vim .env            # 填入 DEEPSEEK_API_KEY
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_kb.py   # 建库（首次下载 embedding 模型）
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/xiaozhi.log 2>&1 &
```

4. 安全组开放 8000 端口；建议用 Nginx 反代 + HTTPS（免费证书）。

### 方案 B：云函数（Serverless，成本更低）

- 腾讯云 SCF / 阿里云函数计算：将 `backend/` 打包为函数，入口 `app.main.app`。
- 注意：模型加载与建库适合放在"初始化阶段"（函数冷启动时加载，预留 512MB–1GB 内存）。
- 云函数默认域名可公网访问；正式使用建议绑定自定义域名。

### 环境变量（.env）

| 变量 | 说明 |
|---|---|
| `DEEPSEEK_API_KEY` | DeepSeek 控制台申请的 Key（必填） |
| `ALLOWED_ORIGINS` | 前端来源白名单，多个逗号分隔 |
| `EMBED_MODEL` | 默认 BAAI/bge-small-zh-v1.5，可换 |
| `TOP_K` | 检索片段数 |

---

## 二、前端部署

纯静态文件（`frontend/`），任何静态托管都可部署。

### 方式 1：GitHub Pages（免费，演示/开源展示）

1. 推送代码到 GitHub 仓库。
2. Settings → Pages → Source 选择分支目录 `frontend/`（或根目录）。
3. 访问 `https://<账号>.github.io/xiyuan-xiaozhi/`。
4. 用户点击右上角 ⚙️，填写后端地址（如 `https://api.你的域名.com`）。
   - ⚠️ 后端 CORS 需允许该 Pages 域名（`ALLOWED_ORIGINS` 中加入）。

### 方式 2：国内静态托管（正式推荐）

GitHub Pages 国内访问不稳定，正式给新生使用时，将 `frontend/` 部署到：

- 腾讯云开发 CloudBase 静态托管 / 阿里云 OSS + CDN / 微信云开发
- 绑定已备案域名后，与后端同域或配置 CORS。

---

## 三、上线前检查清单

- [ ] 后端 `DEEPSEEK_API_KEY` 已配置，且未提交到 GitHub（检查 `.gitignore`）
- [ ] 知识库已建库：`GET /api/health` 返回 `kb_ready: true`
- [ ] 前端可正常对话，来源链接可点开
- [ ] CORS 白名单包含实际前端域名
- [ ] HTTPS 已配置（公众号/网页强制要求）
- [ ] 域名 ICP 备案完成（国内）
- [ ] 见 `docs/COMPLIANCE.md` 完成合规确认

## 四、GitHub 仓库初始化

```bash
cd xiyuan-xiaozhi
git init
git add .
git commit -m "feat: 锡院小智新生AI助手 v0.1"
git branch -M main
git remote add origin git@github.com:<你的账号>/xiyuan-xiaozhi.git
git push -u origin main
```

> 注意：`.gitignore` 已排除 `.env`、`data/kb/`、`__pycache__` 等，切勿强制提交含 Key 的文件。

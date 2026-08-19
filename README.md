# 锡院小智 · 无锡学院新生 AI 助手

由无锡学院官方授权开发（待校方确认授权声明），服务新生群体的智能问答助手。
基于 DeepSeek 大模型 + 官方网页知识库检索（RAG），回答严格锚定官方信息，不编造、不越界。

## 功能特性

- 🎯 严格知识锚定：回答基于官方网页/文档知识库，无法确认时给出官方查询路径
- 🔒 隐私保护：不索取敏感信息，自动拦截身份证/银行卡/验证码等输入并警告
- 🚧 安全边界：非校园问题礼貌引导回正题，涉政/违法内容直接拒绝
- 📚 RAG 检索：抓取官方网页 → 切片 → 向量化（本地 BGE 模型）→ 检索增强回答，回复附带来源链接
- 📱 移动端友好的纯静态对话页（GitHub Pages 可直接部署）
- 🧩 管理友好：知识库可增量重建，日志记录便于审计

## 架构

```
官方网页 URL 清单 (scripts/seed_urls.txt)
        │ 抓取·清洗·切片 (rag/loader.py, chunker.py)
        ▼
  知识库向量库 (data/kb, SQLite + numpy)
        │ 查询向量化 + 余弦检索 (rag/retriever.py)
        ▼
  FastAPI 后端 (app/main.py)
        │ 安全过滤 → 组装提示词 → DeepSeek API
        ▼
  纯静态前端 (frontend/) ──► GitHub Pages / 国内静态托管
```

## 快速开始

> 环境要求：Python 3.9+（已做版本兼容，3.9 也可运行）。首次使用需申请 DeepSeek API Key。

### 1. 后端

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # 填入 DEEPSEEK_API_KEY
# 首次运行会自动下载 BGE 中文 embedding 模型（约 100MB，仅一次）
python scripts/build_kb.py   # 按 seed_urls.txt 建库（需先放入官方 URL）
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. 前端

```bash
cd frontend
python -m http.server 8080   # 本地预览，页面右上角可配置后端地址
```

### 3. 测试（无需 API Key）

```bash
cd backend
.venv/bin/python -m pytest test_smoke.py -v   # 11 项冒烟测试
# 无 Key 联调：用演示数据建库，验证 RAG 检索链路
.venv/bin/python scripts/build_kb.py --from-dir scripts/sample_kb
.venv/bin/uvicorn app.main:app --port 8000    # 然后访问 http://127.0.0.1:8000/
```

> `scripts/sample_kb/` 为**演示数据**（标注"待替换"），用于验证链路；正式使用请换成官方网页抓取（`seed_urls.txt`）或官方手册转出的文本。

### 4. 上线

见 [docs/DEPLOY.md](docs/DEPLOY.md)（GitHub Pages + 国内服务器/云函数）与 [docs/COMPLIANCE.md](docs/COMPLIANCE.md)（生成式 AI 合规）。

## 目录结构

```
xiyuan-xiaozhi/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI 入口（/api/chat, /api/health）
│   │   ├── config.py         # 环境变量配置
│   │   ├── system_prompt.py  # 系统提示词（知识锚定与边界规则）
│   │   ├── llm.py            # DeepSeek 调用（OpenAI 兼容）
│   │   ├── safety.py         # 隐私保护与安全边界
│   │   ├── models.py         # 请求/响应数据模型
│   │   └── rag/              # 知识库：loader/chunker/embedder/store/retriever
│   └── scripts/
│       ├── build_kb.py       # 建库脚本
│       └── seed_urls.txt     # 官方 URL 清单（需填写）
├── frontend/                 # 纯静态对话页
├── data/kb/                  # 知识库产物（gitignore）
├── docs/                     # 部署与合规文档
├── .env.example
└── README.md
```

## ⚠️ 重要提示

- 本项目为技术实现；正式对外服务前，请完成：学校官方授权、生成式 AI 合规通道（见 docs/COMPLIANCE.md）、域名与内容审核。
- `DEEPSEEK_API_KEY` 只可放在后端环境变量中，**严禁**写入前端代码或提交到 GitHub。
- 知识库内容来自学校官方公开网页，请遵守目标站点 robots 协议与版权要求。

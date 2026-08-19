"""FastAPI 主入口：/api/chat 对话、/api/health 健康检查。"""
from __future__ import annotations
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from . import llm, safety
from .config import settings
from .models import ChatRequest, ChatResponse, HealthResponse, Source
from .rag import retriever, store
from .system_prompt import SYSTEM_PROMPT

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("main")

app = FastAPI(title="锡院小智 · 无锡学院新生AI助手", version="0.1.0")

# CORS：允许前端（GitHub Pages / 本地静态服务器 / 国内静态托管）跨域调用
_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 会话历史（内存版，重启清空；正式环境可换 Redis/数据库）
_session_history: dict[str, list[dict]] = {}
MAX_HISTORY_TURNS = 6


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        kb_chunks=store.count_chunks(),
        kb_ready=store.count_chunks() > 0,
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    message = req.message.strip()

    # 1. 输入安全检查（隐私/违规/边界）
    check = safety.check_input(message)
    if check.blocked:
        logger.info("输入被拦截：%s", check.reason)
        return ChatResponse(reply=check.reply, boundary=True)

    # 2. RAG 检索
    results = retriever.search(message)
    context = retriever.format_context(results) if results else "（知识库中未检索到相关资料）"
    sources = [
        Source(title=chunk.title, url=chunk.url)
        for chunk, _ in results
    ][:3]

    # 3. 组装消息
    history = _session_history.get(req.session_id or "", [])[-MAX_HISTORY_TURNS:]
    history_text = "\n".join(
        f"{'用户' if m['role'] == 'user' else '助手'}：{m['content']}" for m in history
    ) or "（无）"
    system_prompt = SYSTEM_PROMPT.format(
        context=context, history=history_text, question=message
    )
    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": message}
    ]

    # 4. 调用 DeepSeek
    try:
        reply = llm.chat(messages)
    except Exception as exc:  # noqa: BLE001
        logger.exception("LLM 调用失败")
        reply = (
            "抱歉，我暂时遇到了一点问题，请稍后再试。"
            "如果持续无法使用，请联系学校信息中心或辅导员反馈。"
        )
        return ChatResponse(reply=reply, boundary=True)

    # 5. 输出安全检查（防止回显敏感信息）
    reply = safety.check_output(reply, message)

    # 6. 记录历史
    sid = req.session_id or "default"
    hist = _session_history.setdefault(sid, [])
    hist.append({"role": "user", "content": message})
    hist.append({"role": "assistant", "content": reply})
    _session_history[sid] = hist[-MAX_HISTORY_TURNS * 2:]

    return ChatResponse(reply=reply, sources=sources)


# ---------- 本地静态文件服务（可选：后端直接托管前端） ----------
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


# 静态资源（前端 css/js）
from fastapi.staticfiles import StaticFiles  # noqa: E402

for _sub in ("css", "js"):
    _dir = FRONTEND_DIR / _sub
    if _dir.is_dir():
        app.mount(f"/{_sub}", StaticFiles(directory=_dir), name=_sub)

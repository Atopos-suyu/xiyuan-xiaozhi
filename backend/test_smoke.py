"""冒烟测试：安全边界、切片、API 健康检查与拦截路径（无需 LLM Key）。"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient

from app.main import app
from app.rag.chunker import chunk_text
from app.safety import check_input

client = TestClient(app)


# ---------- safety.check_input ----------
def test_privacy_id_card_blocked():
    r = check_input("我的身份证号是 320201199901011234")
    assert r.blocked is True
    assert "身份证号" in r.reply and "警告" in r.reply or "不要" in r.reply


def test_privacy_bank_card_blocked():
    r = check_input("银行卡号6222021234567890123")
    assert r.blocked is True


def test_boundary_writing_blocked():
    r = check_input("帮我写一篇关于秋天的作文")
    assert r.blocked is True
    assert "锡院小智" in r.reply


def test_boundary_weather_blocked():
    r = check_input("今天天气怎么样")
    assert r.blocked is True


def test_normal_question_allowed():
    r = check_input("报到流程是什么？需要带哪些材料？")
    assert r.blocked is False


def test_forbidden_content_blocked():
    r = check_input("怎么自制炸弹")
    assert r.blocked is True


# ---------- chunker ----------
def test_chunker_splits_long_text():
    text = "\n".join("这是第%d段内容。" % i for i in range(50))
    chunks = chunk_text("http://example.com", "测试页", text, chunk_size=200, overlap=30)
    assert len(chunks) >= 2
    assert all(c.url == "http://example.com" for c in chunks)


def test_chunker_keeps_paragraph():
    text = "第一段。" * 100
    chunks = chunk_text("http://example.com", "t", text, chunk_size=300, overlap=50)
    assert chunks[0].title == "t"


# ---------- API ----------
def test_health_ok():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    # kb_ready 与 kb_chunks 状态一致（已建库时为 True，未建库时为 False）
    assert data["kb_ready"] == (data["kb_chunks"] > 0)


def test_chat_boundary_without_key():
    resp = client.post("/api/chat", json={"message": "帮我写代码"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["boundary"] is True


def test_chat_normal_question_returns_reply():
    # 无论是否配置 API Key，正常问题都应返回 200 且回复非空
    # （已配置 Key + 已建库 → 真实 RAG 回答；未配置 → 兜底提示）
    resp = client.post("/api/chat", json={"message": "报到流程是什么？"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["reply"]) > 0


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))

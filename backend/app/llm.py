"""DeepSeek 对话调用（OpenAI 兼容接口）。"""
from __future__ import annotations
import logging
from typing import Iterable

from openai import OpenAI

from .config import settings

logger = logging.getLogger("llm")

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.DEEPSEEK_API_KEY:
            raise RuntimeError(
                "未配置 DEEPSEEK_API_KEY，请在项目根目录 .env 文件中填写。"
            )
        _client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            timeout=60.0,
            max_retries=2,
        )
    return _client


def chat(
    messages: Iterable[dict],
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """调用 DeepSeek 并返回文本回复。"""
    client = get_client()
    resp = client.chat.completions.create(
        model=settings.DEEPSEEK_MODEL,
        messages=list(messages),
        temperature=settings.TEMPERATURE if temperature is None else temperature,
        max_tokens=settings.MAX_TOKENS if max_tokens is None else max_tokens,
        stream=False,
    )
    text = (resp.choices[0].message.content or "").strip()
    logger.info("LLM 调用完成，回复长度=%s 字符", len(text))
    return text

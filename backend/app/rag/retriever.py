"""检索：查询向量化 + 余弦相似度 Top-K。"""
from __future__ import annotations
import logging

import numpy as np

from ..config import settings
from .chunker import Chunk
from .embedder import embed_query
from . import store

logger = logging.getLogger("retriever")


def search(query: str, top_k: int | None = None) -> list[tuple[Chunk, float]]:
    """返回 (片段, 相似度) 列表，按相似度降序。知识库为空时返回空列表。"""
    top_k = top_k or settings.TOP_K
    chunks, vectors = store.load_all()
    if not chunks:
        logger.warning("知识库为空，请先运行 scripts/build_kb.py 建库")
        return []

    qv = np.array(embed_query(query), dtype=np.float32)
    # 向量已归一化，点积即余弦相似度
    scores = vectors @ qv
    top_idx = np.argsort(scores)[::-1][:top_k]

    results = []
    for i in top_idx:
        score = float(scores[i])
        if score < 0.3:  # 相似度过低视为不相关
            continue
        results.append((chunks[i], score))
    return results


def format_context(results: list[tuple[Chunk, float]]) -> str:
    """把检索结果格式化为系统提示词中的 context 段落。"""
    parts = []
    for i, (chunk, score) in enumerate(results, start=1):
        parts.append(
            f"[资料{i}] 来源：{chunk.title}（{chunk.url}）\n{chunk.text}"
        )
    return "\n\n".join(parts)

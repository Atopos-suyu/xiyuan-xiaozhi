"""知识库存储：SQLite 记录元数据 + numpy 保存向量矩阵。"""
from __future__ import annotations
import json
import logging
import sqlite3
from pathlib import Path

import numpy as np

from ..config import settings
from .chunker import Chunk

logger = logging.getLogger("store")

DB_NAME = "kb.sqlite3"
VECTORS_FILE = "vectors.npy"


def _db_path() -> Path:
    settings.KB_DIR.mkdir(parents=True, exist_ok=True)
    return settings.KB_DIR / DB_NAME


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            text TEXT NOT NULL
        )
        """
    )
    return conn


def save_chunks(chunks: list[Chunk], vectors: list[list[float]]) -> None:
    """全量重建：清空旧数据后写入新数据。"""
    conn = _conn()
    try:
        conn.execute("DELETE FROM chunks")
        conn.executemany(
            "INSERT INTO chunks (url, title, text) VALUES (?, ?, ?)",
            [(c.url, c.title, c.text) for c in chunks],
        )
        conn.commit()
    finally:
        conn.close()

    # 保存向量矩阵
    arr = np.array(vectors, dtype=np.float32)
    np.save(settings.KB_DIR / VECTORS_FILE, arr)
    logger.info("知识库重建完成：%d 个片段，向量维度 %s", len(chunks), arr.shape)


def load_all() -> tuple[list[Chunk], np.ndarray]:
    """加载全部片段与向量矩阵。知识库为空时返回空。"""
    conn = _conn()
    try:
        rows = conn.execute("SELECT url, title, text FROM chunks ORDER BY id").fetchall()
    finally:
        conn.close()

    vec_file = settings.KB_DIR / VECTORS_FILE
    if not rows or not vec_file.exists():
        return [], np.zeros((0, 0), dtype=np.float32)

    chunks = [Chunk(url=r[0], title=r[1], text=r[2]) for r in rows]
    vectors = np.load(vec_file)
    return chunks, vectors


def count_chunks() -> int:
    conn = _conn()
    try:
        row = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()

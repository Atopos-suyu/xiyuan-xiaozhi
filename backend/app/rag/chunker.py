"""文本切片：按段落聚合 + 重叠，保留来源信息。"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Chunk:
    url: str
    title: str
    text: str


def chunk_text(
    url: str,
    title: str,
    text: str,
    chunk_size: int = 400,
    overlap: int = 60,
) -> list[Chunk]:
    """按段落切块，必要时按字符长度截断并保留重叠。

    chunk_size/overlap 单位为字符（中文场景）。
    """
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: list[Chunk] = []
    current: list[str] = []
    current_len = 0

    def flush():
        nonlocal current, current_len
        if current:
            chunks.append(Chunk(url=url, title=title, text="\n".join(current)))
        current = []
        current_len = 0

    for para in paragraphs:
        # 超长段落直接截断
        while len(para) > chunk_size:
            flush()
            chunks.append(
                Chunk(url=url, title=title, text=para[:chunk_size])
            )
            para = para[chunk_size - overlap:]
        if current_len + len(para) > chunk_size and current:
            flush()
        current.append(para)
        current_len += len(para) + 1

    flush()
    return chunks

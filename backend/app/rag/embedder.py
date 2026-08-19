"""文本向量化：本地 BGE 中文模型（sentence-transformers）。

首次运行会自动从 HuggingFace 下载模型（约 100MB），缓存到项目内
data/hf_home（可用环境变量 HF_HOME 覆盖；沙箱/服务器无家目录写权限时尤其必要）。
如无法直连 HuggingFace，可改用镜像：HF_ENDPOINT=https://hf-mirror.com
"""
from __future__ import annotations
import logging
import os
from functools import lru_cache

from ..config import settings

logger = logging.getLogger("embedder")

# 在导入 sentence-transformers 前设置缓存路径，避免写系统家目录失败
os.environ.setdefault("HF_HOME", str(settings.KB_DIR.parent / "hf_home"))
os.environ.setdefault("HF_HUB_CACHE", str(settings.KB_DIR.parent / "hf_home" / "hub"))


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    logger.info("加载 embedding 模型: %s (device=%s)", settings.EMBED_MODEL, settings.EMBED_DEVICE)
    return SentenceTransformer(settings.EMBED_MODEL, device=settings.EMBED_DEVICE)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """批量向量化。空输入返回空列表。"""
    if not texts:
        return []
    model = _model()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=32,
    )
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]

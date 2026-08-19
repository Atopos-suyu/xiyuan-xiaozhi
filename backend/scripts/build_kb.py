"""建库脚本：网页抓取（seed_urls.txt）或本地文件导入，切片→向量化→入库。

用法：
    cd backend
    # 方式一：网页抓取
    python scripts/build_kb.py --urls scripts/seed_urls.txt [--limit N]
    # 方式二：本地文本导入（.txt/.md，适合手册转出的文本）
    python scripts/build_kb.py --from-dir scripts/sample_kb
"""
from __future__ import annotations
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag import chunker, embedder, loader, store  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("build_kb")


def read_urls(path: Path) -> list[str]:
    if not path.exists():
        logger.error("未找到 URL 清单: %s", path)
        sys.exit(1)
    urls = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls


def load_from_dir(directory: Path) -> list[chunker.Chunk]:
    """从目录读取 .txt/.md 文件并切片（每个文件视为一个来源页面）。"""
    if not directory.is_dir():
        logger.error("目录不存在: %s", directory)
        sys.exit(1)
    chunks: list[chunker.Chunk] = []
    for f in sorted(directory.glob("*")):
        if f.suffix.lower() not in (".txt", ".md"):
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        url = f"file://{f.resolve()}"
        title = f.stem
        chunks.extend(chunker.chunk_text(url, title, text))
        logger.info("导入 %s → %d 字符", f.name, len(text))
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", default="scripts/seed_urls.txt")
    parser.add_argument("--from-dir", default=None, help="从本地目录导入 .txt/.md（与 --urls 互斥）")
    parser.add_argument("--limit", type=int, default=0, help="最多抓取 N 页（0=全部）")
    parser.add_argument("--no-save", action="store_true", help="只切片不写库（调试用）")
    args = parser.parse_args()

    if args.from_dir:
        all_chunks = load_from_dir(Path(args.from_dir))
    else:
        urls = read_urls(Path(args.urls))
        if args.limit > 0:
            urls = urls[: args.limit]
        logger.info("待抓取 URL 数量: %d", len(urls))
        all_chunks = []
        ok = 0
        for i, url in enumerate(urls, 1):
            page = loader.fetch_page(url)
            if page is None:
                continue
            chunks = chunker.chunk_text(page.url, page.title, page.text)
            all_chunks.extend(chunks)
            ok += 1
            logger.info("[%d/%d] %s → %d 个片段", i, len(urls), page.title[:40], len(chunks))
            loader.sleep_between()
        logger.info("抓取完成：成功 %d 页", ok)

    logger.info("共 %d 个片段", len(all_chunks))
    if args.no_save or not all_chunks:
        return

    logger.info("开始向量化（首次运行会下载 embedding 模型，约 100MB）…")
    texts = [c.text for c in all_chunks]
    vectors = embedder.embed_texts(texts)
    store.save_chunks(all_chunks, vectors)
    logger.info("建库完成 ✓ 片段数=%d，请启动服务验证 /api/health", len(all_chunks))


if __name__ == "__main__":
    main()

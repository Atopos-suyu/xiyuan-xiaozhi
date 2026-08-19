"""网页采集与解析：抓取官方网页，提取标题与正文。

使用 urllib 标准库实现（某些环境 httpx 连接异常，urllib 更稳定）。
"""
from __future__ import annotations
import logging
import re
import time
import urllib.request
from dataclasses import dataclass

from bs4 import BeautifulSoup

logger = logging.getLogger("loader")

USER_AGENT = (
    "Mozilla/5.0 (Xiaomi XiaoZhi/1.0; +https://example.com/bot) "
    "compatible; educational KB crawler"
)

# 通常与正文无关的标签
STRIP_TAGS = ["script", "style", "noscript", "iframe", "nav", "footer", "header", "aside"]

# 常见正文选择器（按顺序尝试）
ARTICLE_SELECTORS = [
    "article",
    ".article",
    ".content",
    ".article-content",
    ".detail-content",
    ".news_content",
    ".v_news_content",
    "#content",
    ".entry-content",
]


@dataclass
class Page:
    url: str
    title: str
    text: str


def _clean_text(node) -> str:
    for tag in STRIP_TAGS:
        for el in node.find_all(tag):
            el.decompose()
    text = node.get_text("\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _http_get(url: str, timeout: float) -> bytes:
    """urllib GET 请求，自动跟随重定向，返回响应体字节。"""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _decode(raw: bytes, resp_charset: str | None = None) -> str:
    """按响应头 charset → utf-8 → gb18030 顺序解码。"""
    for enc in ([resp_charset] if resp_charset else []) + ["utf-8", "gb18030"]:
        if not enc:
            continue
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="ignore")


def fetch_page(url: str, timeout: float = 20.0) -> Page | None:
    """抓取单个页面并提取正文。失败返回 None。"""
    raw = None
    try:
        raw = _http_get(url, timeout)
    except Exception as exc:  # noqa: BLE001
        logger.warning("抓取失败 %s: %s", url, exc)
        return None

    html = _decode(raw)
    soup = BeautifulSoup(html, "lxml")

    # 标题
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        title = h1.get_text(strip=True)

    # 正文
    body = None
    for sel in ARTICLE_SELECTORS:
        node = soup.select_one(sel)
        if node and _clean_text(node):
            body = _clean_text(node)
            break
    if body is None:
        # 退化为整页正文
        body = _clean_text(soup.body) if soup.body else ""

    if not body:
        logger.warning("页面无正文: %s", url)
        return None

    return Page(url=url, title=title or url, text=body)


def sleep_between() -> None:
    """礼貌抓取：间隔 1 秒，降低对目标站点压力。"""
    time.sleep(1.0)

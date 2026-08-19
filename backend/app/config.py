"""环境变量配置。"""
from __future__ import annotations
import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录（backend/ 的上一级）
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


class Settings:
    # DeepSeek
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # 服务
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = _get_int("APP_PORT", 8000)
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")

    # 知识库
    KB_DIR: Path = ROOT_DIR / os.getenv("KB_DIR", "data/kb")
    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "BAAI/bge-small-zh-v1.5")
    EMBED_DEVICE: str = os.getenv("EMBED_DEVICE", "cpu")
    TOP_K: int = _get_int("TOP_K", 4)

    # 对话参数
    TEMPERATURE: float = 0.3
    MAX_TOKENS: int = 1200

    # 日志
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

"""请求/响应数据模型。"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    session_id: Optional[str] = Field(None, max_length=64, description="会话标识（可选）")


class Source(BaseModel):
    title: str = ""
    url: str = ""


class ChatResponse(BaseModel):
    reply: str = Field(..., description="助手回复")
    sources: List[Source] = Field(default_factory=list, description="参考来源")
    boundary: bool = Field(False, description="是否命中了安全/边界拦截（如隐私警告）")


class HealthResponse(BaseModel):
    status: str = "ok"
    kb_chunks: int = 0
    kb_ready: bool = False

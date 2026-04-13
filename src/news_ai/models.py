"""Data models for News AI Summary"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Feed:
    """RSS Feed"""
    id: int
    title: str
    category: str = ""
    enabled: bool = True
    url: str = ""


@dataclass
class Entry:
    """新闻条目"""
    id: int
    title: str
    url: str
    published_at: datetime
    summary: str
    content: Optional[str] = None
    feed_id: int = 0
    feed_title: str = ""


@dataclass
class Highlight:
    """重点新闻"""
    title: str
    source: str
    summary: str
    importance: str = "medium"  # high, medium, low


@dataclass
class SummarizeResult:
    """总结结果"""
    summary: str
    highlights: list[Highlight]
    keywords: list[str]
    sentiment: str  # positive, neutral, negative
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SummaryReport:
    """总结报告"""
    result: SummarizeResult
    feeds: list[Feed]
    entries: list[Entry]
    total_count: int

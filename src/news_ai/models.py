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
class Ticker:
    """股票/投资标的"""
    code: str  # 股票代码，如 SH600519
    name: str  # 公司名称，如 贵州茅台


@dataclass
class Highlight:
    """重点新闻"""
    title: str
    source: str
    summary: str
    importance: str = "medium"  # high, medium, low
    tickers: list[str] = field(default_factory=list)  # 相关股票代码列表
    url: str = ""  # 原文链接


@dataclass
class SummarizeResult:
    """总结结果"""
    summary: str
    highlights: list[Highlight]
    keywords: list[str]
    sentiment: str  # positive, neutral, negative
    tickers: list[Ticker] = field(default_factory=list)  # 标的一览
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SummaryReport:
    """总结报告"""
    result: SummarizeResult
    feeds: list[Feed]
    entries: list[Entry]
    total_count: int

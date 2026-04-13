"""News summarizer for News AI Summary"""

from datetime import datetime
from typing import Optional

from loguru import logger

from news_ai.models import Entry, Feed, SummarizeResult, SummaryReport
from news_ai.ai_client import AIClient


# Default prompt template
DEFAULT_PROMPT_TEMPLATE = """你是一个专业的财经新闻分析师。请分析以下新闻列表，提取关键信息。

## 要求
1. 识别最重要的3-5条新闻
2. 每条新闻提供50-100字的中文摘要
3. 识别新闻中的关键人物、公司、事件
4. 判断新闻的时效性和重要性

## 输出格式
请用以下 JSON 格式输出：
```json
{{
  "summary": "总体摘要，100-200字",
  "highlights": [
    {{
      "title": "新闻标题",
      "source": "来源",
      "summary": "摘要，50-100字",
      "importance": "high/medium/low"
    }}
  ],
  "keywords": ["关键词1", "关键词2", "..."],
  "sentiment": "positive/neutral/negative"
}}
```

## 新闻列表
{news_content}
"""


class NewsSummarizer:
    """News summarizer using AI"""

    def __init__(
        self,
        ai_client: AIClient,
        prompt_template: Optional[str] = None,
        max_entries: int = 100,
    ) -> None:
        """
        Initialize news summarizer.

        Args:
            ai_client: AI client instance
            prompt_template: Custom prompt template with {news_content} placeholder
            max_entries: Maximum number of entries to summarize
        """
        self.ai_client = ai_client
        self.prompt_template = prompt_template or DEFAULT_PROMPT_TEMPLATE
        self.max_entries = max_entries

    def summarize(
        self,
        entries: list[Entry],
        feeds: list[Feed],
    ) -> SummaryReport:
        """
        Generate summary for news entries.

        Args:
            entries: List of Entry objects
            feeds: List of Feed objects

        Returns:
            SummaryReport object
        """
        original_count = len(entries)
        if len(entries) > self.max_entries:
            logger.warning(
                f"Entry count ({len(entries)}) exceeds max ({self.max_entries}), truncating"
            )
            entries = entries[:self.max_entries]
            logger.info(f"Truncated entries from {original_count} to {len(entries)}")

        news_content = self._format_entries(entries)
        result = self.ai_client.summarize(news_content, self.prompt_template)

        report = SummaryReport(
            result=result,
            feeds=feeds,
            entries=entries,
            total_count=len(entries),
        )

        logger.info(f"Generated summary: {len(result.highlights)} highlights, sentiment: {result.sentiment}")
        return report

    @staticmethod
    def _format_entries(entries: list[Entry]) -> str:
        """
        Format entries for AI consumption.

        Args:
            entries: List of Entry objects

        Returns:
            Formatted string
        """
        lines = []
        for i, entry in enumerate(entries, 1):
            lines.append(f"{i}. [{entry.feed_title}] {entry.title}")
            lines.append(f"   时间: {entry.published_at.strftime('%Y-%m-%d %H:%M')}")
            if entry.summary:
                summary_text = entry.summary[:200] + "..." if len(entry.summary) > 200 else entry.summary
                lines.append(f"   摘要: {summary_text}")
            lines.append("")
        return "\n".join(lines)

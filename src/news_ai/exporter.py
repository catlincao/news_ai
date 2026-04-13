"""Markdown exporter for News AI Summary"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

from news_ai.models import SummaryReport


class MarkdownExporter:
    """Export summary reports as Markdown files"""

    TEMPLATE = """# {feeds_title} - 新闻总结报告

**生成时间**: {generated_at}
**数据来源**: Miniflux RSS
**Feeds 数量**: {feeds_count}
**新闻总数**: {total_count}

---

## 摘要

{summary}

---

## 重要新闻

{highlights}

---

## 标的一览

{tickers_section}

---

## 分类统计

|category|数量|
|--------|-----|
{category_stats}

---

## 关键词

{keywords}

---

## 情感分析

{sentiment}

---

*由 News AI Summary 生成*
"""

    def __init__(self, output_dir: str = ".") -> None:
        """
        Initialize Markdown exporter.

        Args:
            output_dir: Directory to write output files
        """
        self.output_dir = Path(output_dir)

    def _build_feeds_title(self, report: SummaryReport) -> str:
        """
        Build a short title from feed names.

        Args:
            report: SummaryReport object

        Returns:
            Comma-separated feed names
        """
        if not report.feeds:
            return "未指定"
        # Use first 3 feed titles, if more truncate with "等"
        feed_titles = [f.title for f in report.feeds]
        if len(feed_titles) <= 3:
            return "_".join(feed_titles)
        return "_".join(feed_titles[:3]) + "_等"

    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize string for use in filename.

        Args:
            name: String to sanitize

        Returns:
            Sanitized string safe for filename
        """
        # Remove or replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, "_")
        # Truncate if too long
        if len(name) > 50:
            name = name[:50]
        return name

    def export(self, report: SummaryReport) -> Path:
        """
        Export summary report to Markdown file.

        Args:
            report: SummaryReport object

        Returns:
            Path to created file

        Raises:
            PermissionError: If output directory is not writable
        """
        # Create output directory if it doesn't exist
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            logger.error(f"Permission denied creating output directory: {self.output_dir}")
            raise PermissionError(
                f"Cannot create output directory: {self.output_dir}. "
                "Please check directory permissions."
            ) from e

        # Build category statistics
        category_stats: dict[str, int] = {}
        for feed in report.feeds:
            if feed.category:
                category_stats[feed.category] = category_stats.get(feed.category, 0) + 1

        # Build highlights section
        highlights_lines = []
        for i, h in enumerate(report.result.highlights, 1):
            highlights_lines.append(f"### {i}. {h.title}")
            highlights_lines.append(f"- **来源**: {h.source}")
            if h.url:
                highlights_lines.append(f"- **链接**: [{h.url}]({h.url})")
            highlights_lines.append(f"- **摘要**: {h.summary}")
            if h.importance != "medium":
                highlights_lines.append(f"- **重要性**: {h.importance}")
            if h.tickers:
                highlights_lines.append(f"- **标的**: {', '.join(h.tickers)}")
            highlights_lines.append("")

        highlights_text = "\n".join(highlights_lines)

        # Build tickers section
        if report.result.tickers:
            tickers_lines = []
            # Sort by code
            sorted_tickers = sorted(report.result.tickers, key=lambda t: t.code)
            tickers_lines.append("| 代码 | 名称 |")
            tickers_lines.append("|------|------|")
            for ticker in sorted_tickers:
                tickers_lines.append(f"| {ticker.code} | {ticker.name} |")
            tickers_text = "\n".join(tickers_lines)
        else:
            tickers_text = "未识别到相关标的"

        # Build category stats table
        category_stats_lines = []
        for cat, count in sorted(category_stats.items()):
            category_stats_lines.append(f"| {cat} | {count} |")
        category_stats_text = "\n".join(category_stats_lines)

        # Format sentiment
        sentiment_emoji = {
            "positive": "📈",
            "neutral": "➡️",
            "negative": "📉",
        }
        sentiment_labels = {
            "positive": "偏正面",
            "neutral": "中性",
            "negative": "偏负面",
        }
        emoji = sentiment_emoji.get(report.result.sentiment, "➡️")
        label = sentiment_labels.get(report.result.sentiment, "中性")
        sentiment_text = f"{emoji} {label}"

        # Build feeds title string
        feeds_title = self._build_feeds_title(report)

        # Render template
        content = self.TEMPLATE.format(
            feeds_title=feeds_title,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            feeds_count=len(report.feeds),
            total_count=report.total_count,
            summary=report.result.summary,
            highlights=highlights_text,
            tickers_section=tickers_text,
            category_stats=category_stats_text,
            keywords=", ".join(report.result.keywords),
            sentiment=sentiment_text,
        )

        # Generate filename with feeds and date
        safe_feeds_title = self._sanitize_filename(feeds_title)
        filename = f"{safe_feeds_title}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        filepath = self.output_dir / filename

        # Write file
        try:
            filepath.write_text(content, encoding="utf-8")
            logger.info(f"Exported report to {filepath}")
        except PermissionError as e:
            logger.error(f"Permission denied writing file: {filepath}")
            raise PermissionError(
                f"Cannot write file: {filepath}. "
                "Please check directory permissions."
            ) from e

        return filepath

    def export_to_path(self, report: SummaryReport, filepath: str) -> Path:
        """
        Export summary report to a specific file path.

        Args:
            report: SummaryReport object
            filepath: Specific file path to save to

        Returns:
            Path to created file

        Raises:
            PermissionError: If file cannot be written
        """
        # Render the report content
        content = self.render_report(report)

        # Write to specified path
        path = Path(filepath)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            logger.info(f"Exported report to {path}")
        except PermissionError as e:
            logger.error(f"Permission denied writing file: {path}")
            raise PermissionError(
                f"Cannot write file: {path}. "
                "Please check directory permissions."
            ) from e

        return path

    def render_report(self, report: SummaryReport) -> str:
        """
        Render summary report to Markdown string without saving.

        Args:
            report: SummaryReport object

        Returns:
            Markdown content as string
        """
        # Build category statistics
        category_stats: dict[str, int] = {}
        for feed in report.feeds:
            if feed.category:
                category_stats[feed.category] = category_stats.get(feed.category, 0) + 1

        # Build highlights section
        highlights_lines = []
        for i, h in enumerate(report.result.highlights, 1):
            highlights_lines.append(f"### {i}. {h.title}")
            highlights_lines.append(f"- **来源**: {h.source}")
            if h.url:
                highlights_lines.append(f"- **链接**: [{h.url}]({h.url})")
            highlights_lines.append(f"- **摘要**: {h.summary}")
            if h.importance != "medium":
                highlights_lines.append(f"- **重要性**: {h.importance}")
            if h.tickers:
                highlights_lines.append(f"- **标的**: {', '.join(h.tickers)}")
            highlights_lines.append("")

        highlights_text = "\n".join(highlights_lines)

        # Build tickers section
        if report.result.tickers:
            tickers_lines = []
            # Sort by code
            sorted_tickers = sorted(report.result.tickers, key=lambda t: t.code)
            tickers_lines.append("| 代码 | 名称 |")
            tickers_lines.append("|------|------|")
            for ticker in sorted_tickers:
                tickers_lines.append(f"| {ticker.code} | {ticker.name} |")
            tickers_text = "\n".join(tickers_lines)
        else:
            tickers_text = "未识别到相关标的"

        # Build category stats table
        category_stats_lines = []
        for cat, count in sorted(category_stats.items()):
            category_stats_lines.append(f"| {cat} | {count} |")
        category_stats_text = "\n".join(category_stats_lines)

        # Format sentiment
        sentiment_emoji = {
            "positive": "📈",
            "neutral": "➡️",
            "negative": "📉",
        }
        sentiment_labels = {
            "positive": "偏正面",
            "neutral": "中性",
            "negative": "偏负面",
        }
        emoji = sentiment_emoji.get(report.result.sentiment, "➡️")
        label = sentiment_labels.get(report.result.sentiment, "中性")
        sentiment_text = f"{emoji} {label}"

        # Build feeds title string
        feeds_title = self._build_feeds_title(report)

        # Render template
        content = self.TEMPLATE.format(
            feeds_title=feeds_title,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            feeds_count=len(report.feeds),
            total_count=report.total_count,
            summary=report.result.summary,
            highlights=highlights_text,
            tickers_section=tickers_text,
            category_stats=category_stats_text,
            keywords=", ".join(report.result.keywords),
            sentiment=sentiment_text,
        )

        return content

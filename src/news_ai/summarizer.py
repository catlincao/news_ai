"""News summarizer for News AI Summary"""

from datetime import datetime
from typing import Optional

from loguru import logger

from news_ai.models import Entry, Feed, SummarizeResult, SummaryReport
from news_ai.ai_client import AIClient


# Default prompt template
DEFAULT_PROMPT_TEMPLATE = """你是一个专业的财经新闻分析师。请分析以下新闻列表，提取关键信息。

## 要求
1. 识别最重要的8-12条新闻，对同主题新闻进行合并
2. 每条新闻提供150-300字的详细中文摘要，包含背景、分析和影响
3. 识别新闻中的标的信息（股票代码如SH600519、公司名称等）
4. 识别新闻中的关键人物、公司、事件
5. 判断新闻的时效性和重要性

## 输出格式
请用以下 JSON 格式输出：
```json
{{
  "summary": "总体摘要，200-400字",
  "highlights": [
    {{
      "title": "新闻标题",
      "source": "来源",
      "url": "原文URL链接",
      "summary": "详细摘要，150-300字，包含背景、分析和影响",
      "importance": "high/medium/low",
      "tickers": ["股票代码1", "股票代码2"]
    }}
  ],
  "tickers": [
    {{"code": "SH600519", "name": "贵州茅台"}},
    {{"code": "SZ000858", "name": "五粮液"}}
  ],
  "keywords": ["关键词1", "关键词2", "..."],
  "sentiment": "positive/neutral/negative"
}}
```

## 新闻列表
{news_content}
"""

# Threshold for short summary (characters) - entries below this will get full content fetched
SHORT_SUMMARY_THRESHOLD = 100


class NewsSummarizer:
    """News summarizer using AI"""

    def __init__(
        self,
        ai_client: AIClient,
        prompt_template: Optional[str] = None,
        max_entries: int = 100,
        miniflux_client: Optional["MinifluxClient"] = None,  # type: ignore[name-defined]
        feeds_to_fetch_full_content: Optional[set[int]] = None,
    ) -> None:
        """
        Initialize news summarizer.

        Args:
            ai_client: AI client instance
            prompt_template: Custom prompt template with {news_content} placeholder
            max_entries: Maximum number of entries to summarize
            miniflux_client: Miniflux client for fetching full content (optional)
            feeds_to_fetch_full_content: Set of feed IDs for which to fetch full content from links
        """
        self.ai_client = ai_client
        self.prompt_template = prompt_template or DEFAULT_PROMPT_TEMPLATE
        self.max_entries = max_entries
        self.miniflux_client = miniflux_client
        self.feeds_to_fetch_full_content = feeds_to_fetch_full_content or set()

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

        # Fetch full content for entries with short summaries
        entries = self._enrich_short_entries(entries)

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

    def _enrich_short_entries(self, entries: list[Entry]) -> list[Entry]:
        """
        Fetch full content for entries with short summaries.

        Args:
            entries: List of Entry objects

        Returns:
            List of Entry objects with enriched content
        """
        if not self.miniflux_client:
            return entries

        enriched_count = 0
        for entry in entries:
            # Only fetch full content if:
            # 1. Entry's feed_id is in feeds_to_fetch_full_content set
            # 2. Summary is too short
            # 3. URL is available
            if (entry.feed_id in self.feeds_to_fetch_full_content and
                len(entry.summary) < SHORT_SUMMARY_THRESHOLD and entry.url):
                logger.info(f"[BEFORE ENRICH] Entry id={entry.id}, url={entry.url}, title={entry.title}, summary={entry.summary}")
                full_content = self._fetch_full_content(entry)
                if full_content:
                    entry.content = full_content
                    enriched_count += 1

        if enriched_count > 0:
            logger.info(f"[ENRICH] Enriched {enriched_count} entries with full content")

        return entries

    def _fetch_full_content(self, entry: Entry) -> str:
        """
        Fetch and extract full content from entry URL.

        Args:
            entry: Entry object with URL

        Returns:
            Extracted text content or empty string on failure
        """
        if not self.miniflux_client:
            return ""

        try:
            logger.info(f"[FETCH] Fetching content for entry id={entry.id}, url={entry.url}")

            # User has selected to fetch full content via checkbox
            # Combine both Miniflux API and direct URL content

            # Get Miniflux content
            miniflux_content = self.miniflux_client.get_entry_content(entry.id)
            miniflux_text = ""
            if miniflux_content:
                miniflux_text = self._extract_readable_content(miniflux_content)
                logger.info(f"[FULL CONTENT] Miniflux extracted {len(miniflux_text)} chars")

            # Get direct URL content
            direct_content = self._fetch_direct_url(entry.url)
            direct_text = ""
            if direct_content:
                direct_text = self._extract_readable_content(direct_content)
                logger.info(f"[FULL CONTENT] Direct URL extracted {len(direct_text)} chars")

            # Combine both - prefer direct URL content as it's usually more complete
            if direct_text and miniflux_text:
                # Both have content - combine them, direct URL first (more complete)
                combined_text = direct_text + "\n\n---\n\n补充信息（来自Miniflux摘要）:\n" + miniflux_text
                logger.info(f"[FULL CONTENT] Combined content length: {len(combined_text)}")
                logger.info(f"[FULL CONTENT] First 2000 chars:\n{combined_text[:2000]}")
                logger.info(f"[FULL CONTENT] Last 1000 chars:\n{combined_text[-1000:]}")
                return combined_text
            elif direct_text:
                logger.info(f"[FULL CONTENT] Length: {len(direct_text)}, First 2000:\n{direct_text[:2000]}")
                logger.info(f"[FULL CONTENT] Last 1000:\n{direct_text[-1000:]}")
                return direct_text
            elif miniflux_text:
                logger.info(f"[FULL CONTENT] Length: {len(miniflux_text)}, Content:\n{miniflux_text}")
                return miniflux_text
            else:
                logger.warning(f"No content found for entry {entry.id}")
                return ""

        except Exception as e:
            logger.warning(f"Failed to fetch full content for entry {entry.id}: {e}")
            return ""

    def _fetch_direct_url(self, url: str) -> str:
        """
        Fetch content directly from URL using httpx.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string
        """
        try:
            import httpx
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
            response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
            response.raise_for_status()
            logger.info(f"[DIRECT URL] Fetched {len(response.text)} chars from {url}")
            return response.text
        except Exception as e:
            logger.warning(f"Failed to fetch direct URL {url}: {e}")
            return ""

    def _extract_readable_content(self, html_content: str) -> str:
        """
        Extract readable text content from HTML.

        Handles multiple formats:
        - wallstreetcn.com: __SSR__ JavaScript variable
        - 韭研公社 (Nuxt.js): window.__NUXT__ JavaScript variable
        - Regular HTML pages

        Args:
            html_content: Raw HTML content

        Returns:
            Extracted text content
        """
        try:
            import re
            from html import unescape

            # Check for wallstreetcn __SSR__ format
            if '__SSR__' in html_content:
                return self._extract_ssr_content(html_content)

            # Check for Nuxt.js __NUXT__ format (e.g., 韭研公社)
            if 'window.__NUXT__' in html_content:
                return self._extract_nuxt_content(html_content)

            # Try readability-lxml first for regular pages
            try:
                from readability import Document
                doc = Document(html_content)
                text = unescape(doc.summary())
                text = re.sub(r'\s+', ' ', text)
                return text.strip()
            except ImportError:
                pass

            # Fallback: strip HTML tags
            text = re.sub(r'<[^>]+>', '', html_content)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        except Exception as e:
            logger.warning(f"Failed to extract readable content: {e}")
            return ""

    def _extract_nuxt_content(self, html_content: str) -> str:
        """
        Extract content from Nuxt.js pages where content is in window.__NUXT__.

        Args:
            html_content: Raw HTML content from Nuxt.js page

        Returns:
            Extracted text content
        """
        import re
        from html import unescape

        # Find the NUXT script tag
        nuxt_match = re.search(r'<script>window\.__NUXT__=.+?</script>', html_content, re.DOTALL)
        if not nuxt_match:
            logger.warning("Nuxt NUXT data not found in page")
            return ""

        script = nuxt_match.group(0)

        # Extract content field - find content:" and extract until next ",url
        content_start = script.find('content:"')
        if content_start < 0:
            logger.warning("content field not found in NUXT data")
            return ""

        content_start += 9  # len('content:"')
        rest = script[content_start:]

        # Find the ending marker
        end_pos = rest.find('",url')
        if end_pos < 0:
            end_pos = rest.find('",type')
        if end_pos < 0:
            end_pos = rest.find('",image')
        if end_pos < 0:
            end_pos = len(rest)

        raw = rest[:end_pos]

        # Decode \uXXXX Unicode escape sequences
        def unescape_unicode(s):
            def repl(m):
                return chr(int(m.group(1), 16))
            return re.sub(r'\\u([0-9a-fA-F]{4})', repl, s)

        content = unescape_unicode(raw)
        content = unescape(content)

        # Strip HTML tags but keep structure for readability
        content = re.sub(r'<div[^>]*>', '\n', content)
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r' +\n', '\n', content)
        content = re.sub(r'\n +', '\n', content)
        content = content.strip()

        return content

    def _extract_ssr_content(self, html_content: str) -> str:
        """
        Extract content from wallstreetcn.com __SSR__ format.

        The content is embedded in a __SSR__ JavaScript variable as JSON.
        Path: __SSR__.state.default.children.default.data.article.content
        Content is URL-encoded HTML (\\u003Cp\\u003E = <p>)

        Args:
            html_content: Raw HTML content from wallstreetcn.com page

        Returns:
            Extracted text content
        """
        import re
        from html import unescape

        # Find the __SSR__ script tag
        ssr_match = re.search(r'<script>__SSR__\s*=\s*(.+?)</script>', html_content, re.DOTALL)
        if not ssr_match:
            logger.warning("__SSR__ data not found in wallstreetcn page")
            return ""

        try:
            import json
            ssr_data = json.loads(ssr_match.group(1))
            # Navigate to content: __SSR__ -> state -> default -> children -> default -> data -> article -> content
            article = (ssr_data.get("state", {})
                       .get("default", {})
                       .get("children", {})
                       .get("default", {})
                       .get("data", {})
                       .get("article", {}))
            content = article.get("content", "")
            # Decode URL-encoded HTML
            content = unescape(content)

            # Strip HTML tags but keep structure for readability
            content = re.sub(r'<div[^>]*>', '\n', content)
            content = re.sub(r'<br\s*/?>', '\n', content)
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\n\s*\n', '\n\n', content)
            content = re.sub(r' +\n', '\n', content)
            content = re.sub(r'\n +', '\n', content)
            content = content.strip()

            return content
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to parse __SSR__ data: {e}")
            return ""

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
            # Add original article URL as hyperlink
            lines.append(f"   原文: [{entry.title}]({entry.url})")
            # Prefer full content over summary if available
            content = entry.content or entry.summary
            if content:
                # For detailed summaries, use more content (up to 10000 chars to allow AI to identify 8-12 highlights)
                content_text = content[:10000] + "..." if len(content) > 10000 else content
                lines.append(f"   内容: {content_text}")
                logger.info(f"[FORMAT] Entry {i} id={entry.id}, content_len={len(content)}, using_content_field={bool(entry.content)}")
            lines.append("")
        return "\n".join(lines)

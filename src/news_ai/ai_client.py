"""AI client implementations for News AI Summary"""

import json
import re
import time
from typing import Protocol, Any

import anthropic
import openai
from loguru import logger

from news_ai.models import SummarizeResult, Highlight, Ticker


class AIClient(Protocol):
    """Protocol for AI clients"""

    def summarize(self, news_content: str, prompt_template: str) -> SummarizeResult:
        """Generate news summary"""
        ...


class OpenAIClient:
    """OpenAI-compatible API client (supports MiniMax, custom endpoints, etc.)"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        base_url: str = "https://api.openai.com/v1",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: int = 60,
    ) -> None:
        """
        Initialize OpenAI-compatible client.

        Args:
            api_key: API key
            model: Model name
            base_url: Custom API endpoint (for MiniMax, custom deployments, etc.)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

    def summarize(self, news_content: str, prompt_template: str) -> SummarizeResult:
        """
        Generate summary using OpenAI-compatible API.

        Args:
            news_content: Formatted news content
            prompt_template: Prompt template with {news_content} placeholder

        Returns:
            SummarizeResult object
        """
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                prompt = prompt_template.format(news_content=news_content)

                client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    timeout=self.timeout,
                )
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的财经新闻分析师。"},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )

                result_text = response.choices[0].message.content
                json_str = self._extract_json(result_text)
                json_str = self._repair_json(json_str)
                data = self._parse_json_with_fallback(json_str)

                return SummarizeResult(
                    summary=data.get("summary", ""),
                    highlights=[
                        Highlight(
                            title=h["title"],
                            source=h.get("source", ""),
                            url=h.get("url", ""),
                            summary=h.get("summary", ""),
                            importance=h.get("importance", "medium"),
                            tickers=h.get("tickers", []),
                        )
                        for h in data.get("highlights", [])
                    ],
                    keywords=data.get("keywords", []),
                    sentiment=data.get("sentiment", "neutral"),
                    tickers=[
                        Ticker(code=t.get("code", ""), name=t.get("name", ""))
                        for t in data.get("tickers", [])
                    ],
                )

            except openai.APIError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"OpenAI API error (attempt {attempt + 1}): {e}")
                    time.sleep(retry_delay * (2 ** attempt))
                    retry_delay *= 2
                else:
                    logger.error(f"OpenAI API error after {max_retries} attempts: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error in OpenAI summarize: {e}")
                raise

        raise RuntimeError("Should not reach here")

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from response text"""
        # Try to find JSON block
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Try to find JSON object directly
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return match.group(0).strip()

        return text.strip()

    @staticmethod
    def _repair_json(json_str: str) -> str:
        """Repair common JSON formatting issues like missing commas and unescaped quotes."""
        # Fix missing commas between object fields (when newline separates fields)
        # This handles cases like: "field": value\n  "next_field": value
        json_str = re.sub(
            r'("\s*\n\s*")([^}\[\],])',
            r'",\2',
            json_str
        )
        # Fix missing commas before arrays/objects
        json_str = re.sub(
            r'([}\]])"([^"\[\]{}])',
            r'\1,"\2',
            json_str
        )
        # Fix unescaped quotes inside string values
        # Match field values that contain unescaped quotes
        def fix_unescaped_in_value(m):
            prefix = m.group(1)  # "fieldname": "
            content = m.group(2)  # the value content
            suffix = m.group(3)  # closing "
            # Escape all unescaped quotes within the content
            result = ""
            i = 0
            while i < len(content):
                c = content[i]
                if c == '\\' and i + 1 < len(content):
                    # Already escaped sequence, keep as-is
                    result += content[i:i+2]
                    i += 2
                elif c == '"':
                    # Unescaped quote - escape it
                    result += '\\"'
                    i += 1
                else:
                    result += c
                    i += 1
            return prefix + result + suffix
        # Match string values that might have unescaped inner quotes
        json_str = re.sub(
            r'("(?:summary|title|source|url|tickers?|keywords?|sentiment|code|name|importance|highlights?|tickers)":\s*")((?:[^"\\]|\\.)*)(")',
            fix_unescaped_in_value,
            json_str
        )
        return json_str

    @staticmethod
    def _parse_json_with_fallback(json_str: str) -> dict:
        """Parse JSON with multiple fallback repair strategies."""
        # Strategy 1: Try standard JSON parsing first
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Try to fix common issues
        repaired = json_str

        # Find all string values and escape inner quotes
        def escape_inner_quotes(m):
            prefix = m.group(1)
            content = m.group(2)
            suffix = m.group(3)
            result = ""
            i = 0
            while i < len(content):
                c = content[i]
                if c == '\\':
                    result += content[i:i+2]
                    i += 2
                elif c == '"':
                    result += '\\"'
                    i += 1
                elif c == '\n':
                    result += '\\n'
                    i += 1
                else:
                    result += c
                    i += 1
            return prefix + result + suffix

        # Match pattern: "field": "content"
        repaired = re.sub(
            r'("(?:[^"\\]|\\.)*"):\s*(")((?:[^"\\]|\\.)*)(")',
            escape_inner_quotes,
            repaired
        )

        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

        # Strategy 3: Replace smart quotes
        repaired = json_str
        repaired = repaired.replace('"', '"').replace('"', '"')
        repaired = repaired.replace(''', "'").replace(''', "'")

        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

        # Strategy 4: Extract fields using regex as last resort
        result = {
            "summary": "",
            "highlights": [],
            "keywords": [],
            "sentiment": "neutral",
            "tickers": []
        }

        summary_match = re.search(r'"summary":\s*"([^"]*)"', repaired)
        if summary_match:
            result["summary"] = summary_match.group(1)

        sentiment_match = re.search(r'"sentiment":\s*"(positive|neutral|negative)"', repaired)
        if sentiment_match:
            result["sentiment"] = sentiment_match.group(1)

        keywords_match = re.search(r'"keywords":\s*\[(.*?)\]', repaired, re.DOTALL)
        if keywords_match:
            result["keywords"] = re.findall(r'"([^"]*)"', keywords_match.group(1))

        return result


class AnthropicClient:
    """Anthropic-compatible API client (supports Anthropic and MiniMax)"""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        base_url: str = "https://api.anthropic.com",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: int = 60,
    ) -> None:
        """
        Initialize Anthropic-compatible client.

        Args:
            api_key: API key
            model: Model name
            base_url: Custom API endpoint (for MiniMax, custom deployments, etc.)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

    def summarize(self, news_content: str, prompt_template: str) -> SummarizeResult:
        """
        Generate summary using Anthropic-compatible API.

        Args:
            news_content: Formatted news content
            prompt_template: Prompt template with {news_content} placeholder

        Returns:
            SummarizeResult object
        """
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                prompt = prompt_template.format(news_content=news_content)

                client = anthropic.Anthropic(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    timeout=self.timeout,
                )
                response = client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                )

                # Find the text content in the response (skip ThinkingBlock if present)
                result_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        result_text = block.text
                        break
                    elif hasattr(block, "thinking"):
                        # Skip thinking blocks, continue to next block
                        continue

                if not result_text:
                    raise ValueError("No text content found in response")

                json_str = self._extract_json(result_text)
                json_str = self._repair_json(json_str)
                data = self._parse_json_with_fallback(json_str)

                return SummarizeResult(
                    summary=data.get("summary", ""),
                    highlights=[
                        Highlight(
                            title=h["title"],
                            source=h.get("source", ""),
                            url=h.get("url", ""),
                            summary=h.get("summary", ""),
                            importance=h.get("importance", "medium"),
                            tickers=h.get("tickers", []),
                        )
                        for h in data.get("highlights", [])
                    ],
                    keywords=data.get("keywords", []),
                    sentiment=data.get("sentiment", "neutral"),
                    tickers=[
                        Ticker(code=t.get("code", ""), name=t.get("name", ""))
                        for t in data.get("tickers", [])
                    ],
                )

            except anthropic.APIError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Anthropic API error (attempt {attempt + 1}): {e}")
                    time.sleep(retry_delay * (2 ** attempt))
                    retry_delay *= 2
                else:
                    logger.error(f"Anthropic API error after {max_retries} attempts: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error in Anthropic summarize: {e}")
                raise

        raise RuntimeError("Should not reach here")

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from response text"""
        # Try to find JSON block
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Try to find JSON object directly
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return match.group(0).strip()

        return text.strip()

    @staticmethod
    def _repair_json(json_str: str) -> str:
        """Repair common JSON formatting issues like missing commas and unescaped quotes."""
        # Fix missing commas between object fields (when newline separates fields)
        # This handles cases like: "field": value\n  "next_field": value
        json_str = re.sub(
            r'("\s*\n\s*")([^}\[\],])',
            r'",\2',
            json_str
        )
        # Fix missing commas before arrays/objects
        json_str = re.sub(
            r'([}\]])"([^"\[\]{}])',
            r'\1,"\2',
            json_str
        )
        # Fix unescaped quotes inside string values
        # Match field values that contain unescaped quotes
        def fix_unescaped_in_value(m):
            prefix = m.group(1)  # "fieldname": "
            content = m.group(2)  # the value content
            suffix = m.group(3)  # closing "
            # Escape all unescaped quotes within the content
            result = ""
            i = 0
            while i < len(content):
                c = content[i]
                if c == '\\' and i + 1 < len(content):
                    # Already escaped sequence, keep as-is
                    result += content[i:i+2]
                    i += 2
                elif c == '"':
                    # Unescaped quote - escape it
                    result += '\\"'
                    i += 1
                else:
                    result += c
                    i += 1
            return prefix + result + suffix
        # Match string values that might have unescaped inner quotes
        json_str = re.sub(
            r'("(?:summary|title|source|url|tickers?|keywords?|sentiment|code|name|importance|highlights?|tickers)":\s*")((?:[^"\\]|\\.)*)(")',
            fix_unescaped_in_value,
            json_str
        )
        return json_str

    @staticmethod
    def _parse_json_with_fallback(json_str: str) -> dict:
        """Parse JSON with multiple fallback repair strategies."""
        # Strategy 1: Try standard JSON parsing first
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Try to fix common issues
        repaired = json_str

        # Find all string values and escape inner quotes
        def escape_inner_quotes(m):
            prefix = m.group(1)
            content = m.group(2)
            suffix = m.group(3)
            result = ""
            i = 0
            while i < len(content):
                c = content[i]
                if c == '\\':
                    result += content[i:i+2]
                    i += 2
                elif c == '"':
                    result += '\\"'
                    i += 1
                elif c == '\n':
                    result += '\\n'
                    i += 1
                else:
                    result += c
                    i += 1
            return prefix + result + suffix

        # Match pattern: "field": "content"
        repaired = re.sub(
            r'("(?:[^"\\]|\\.)*"):\s*(")((?:[^"\\]|\\.)*)(")',
            escape_inner_quotes,
            repaired
        )

        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

        # Strategy 3: Replace smart quotes
        repaired = json_str
        repaired = repaired.replace('"', '"').replace('"', '"')
        repaired = repaired.replace(''', "'").replace(''', "'")

        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

        # Strategy 4: Extract fields using regex as last resort
        result = {
            "summary": "",
            "highlights": [],
            "keywords": [],
            "sentiment": "neutral",
            "tickers": []
        }

        summary_match = re.search(r'"summary":\s*"([^"]*)"', repaired)
        if summary_match:
            result["summary"] = summary_match.group(1)

        sentiment_match = re.search(r'"sentiment":\s*"(positive|neutral|negative)"', repaired)
        if sentiment_match:
            result["sentiment"] = sentiment_match.group(1)

        keywords_match = re.search(r'"keywords":\s*\[(.*?)\]', repaired, re.DOTALL)
        if keywords_match:
            result["keywords"] = re.findall(r'"([^"]*)"', keywords_match.group(1))

        return result


class AIClientFactory:
    """Factory for creating AI clients"""

    @staticmethod
    def create(provider: str, config: dict) -> AIClient:
        """
        Create an AI client based on provider.

        Args:
            provider: "openai", "anthropic", or "minimax"
            config: Configuration dictionary

        Returns:
            AIClient instance

        Raises:
            ValueError: If provider is unknown
        """
        if provider == "openai":
            return OpenAIClient(
                api_key=config.get("api_key", ""),
                model=config.get("model", "gpt-3.5-turbo"),
                base_url=config.get("base_url", "https://api.openai.com/v1"),
                max_tokens=config.get("max_tokens", 4096),
                temperature=config.get("temperature", 0.7),
                timeout=config.get("timeout", 60),
            )
        elif provider in ("anthropic", "minimax"):
            return AnthropicClient(
                api_key=config.get("api_key", ""),
                model=config.get("model", "claude-3-haiku-20240307"),
                base_url=config.get("base_url", "https://api.anthropic.com"),
                max_tokens=config.get("max_tokens", 4096),
                temperature=config.get("temperature", 0.7),
                timeout=config.get("timeout", 60),
            )
        else:
            raise ValueError(f"Unknown AI provider: {provider}. Use 'openai', 'anthropic', or 'minimax'.")

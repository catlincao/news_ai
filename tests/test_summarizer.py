"""Tests for summarizer module."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock

from news_ai.summarizer import NewsSummarizer, DEFAULT_PROMPT_TEMPLATE
from news_ai.models import Entry, Feed, SummarizeResult, Highlight


class TestNewsSummarizer:
    """Test cases for NewsSummarizer."""

    @pytest.fixture
    def mock_ai_client(self):
        """Create a mock AI client."""
        client = MagicMock()
        client.summarize.return_value = SummarizeResult(
            summary="Test summary",
            highlights=[
                Highlight(
                    title="Test News",
                    source="Test Source",
                    summary="Test description",
                    importance="high",
                )
            ],
            keywords=["test"],
            sentiment="positive",
        )
        return client

    @pytest.fixture
    def sample_entries(self):
        """Create sample entries for testing."""
        return [
            Entry(
                id=1,
                title="Entry 1",
                url="http://example.com/1",
                published_at=datetime(2024, 1, 1, 12, 0),
                summary="Summary 1",
                feed_id=1,
                feed_title="Feed 1",
            ),
            Entry(
                id=2,
                title="Entry 2",
                url="http://example.com/2",
                published_at=datetime(2024, 1, 1, 13, 0),
                summary="Summary 2",
                feed_id=2,
                feed_title="Feed 2",
            ),
        ]

    def test_initialization(self, mock_ai_client):
        """Test summarizer initializes correctly."""
        summarizer = NewsSummarizer(
            ai_client=mock_ai_client,
            prompt_template="Custom template",
            max_entries=50,
        )
        assert summarizer.ai_client == mock_ai_client
        assert summarizer.prompt_template == "Custom template"
        assert summarizer.max_entries == 50

    def test_initialization_with_defaults(self, mock_ai_client):
        """Test summarizer uses default values."""
        summarizer = NewsSummarizer(ai_client=mock_ai_client)
        assert summarizer.prompt_template == DEFAULT_PROMPT_TEMPLATE
        assert summarizer.max_entries == 100

    def test_summarize_calls_ai_client(self, mock_ai_client, sample_entries):
        """Test summarize calls AI client with formatted content."""
        summarizer = NewsSummarizer(ai_client=mock_ai_client)

        result = summarizer.summarize(sample_entries, [])

        mock_ai_client.summarize.assert_called_once()
        call_args = mock_ai_client.summarize.call_args
        assert "Entry 1" in call_args[0][0]
        assert "Entry 2" in call_args[0][0]

    def test_summarize_truncates_entries(self, mock_ai_client):
        """Test summarize truncates entries exceeding max_entries."""
        entries = [
            Entry(
                id=i,
                title=f"Entry {i}",
                url=f"http://example.com/{i}",
                published_at=datetime(2024, 1, 1, i, 0),
                summary=f"Summary {i}",
                feed_id=1,
                feed_title="Feed 1",
            )
            for i in range(150)
        ]
        summarizer = NewsSummarizer(ai_client=mock_ai_client, max_entries=100)

        result = summarizer.summarize(entries, [])

        assert mock_ai_client.summarize.call_count == 1
        call_args = mock_ai_client.summarize.call_args
        content = call_args[0][0]
        assert "Entry 1" in content
        assert "Entry 99" in content
        assert "Entry 100" not in content

    def test_summarize_returns_report(self, mock_ai_client, sample_entries):
        """Test summarize returns SummaryReport with correct data."""
        summarizer = NewsSummarizer(ai_client=mock_ai_client)
        feeds = [Feed(id=1, title="Feed 1")]

        report = summarizer.summarize(sample_entries, feeds)

        assert report.total_count == 2
        assert len(report.feeds) == 1
        assert report.result.summary == "Test summary"

    def test_format_entries(self, sample_entries):
        """Test _format_entries produces correct output."""
        output = NewsSummarizer._format_entries(sample_entries)

        assert "1. [Feed 1] Entry 1" in output
        assert "2. [Feed 2] Entry 2" in output
        assert "2024-01-01 12:00" in output
        assert "Summary 1" in output

    def test_format_entries_truncates_long_summary(self):
        """Test long summaries are truncated."""
        long_summary = "A" * 300
        entries = [
            Entry(
                id=1,
                title="Entry",
                url="http://example.com",
                published_at=datetime(2024, 1, 1),
                summary=long_summary,
                feed_id=1,
                feed_title="Feed",
            )
        ]

        output = NewsSummarizer._format_entries(entries)

        assert "..." in output
        assert ("A" * 200) in output
        assert ("A" * 300) not in output

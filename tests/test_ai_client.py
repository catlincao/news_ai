"""Tests for ai_client module."""

import json
import pytest
from unittest.mock import MagicMock, patch

from news_ai.ai_client import OpenAIClient, AnthropicClient, AIClientFactory
from news_ai.models import SummarizeResult, Highlight


class TestOpenAIClient:
    """Test cases for OpenAIClient."""

    @pytest.fixture
    def client(self):
        """Create an OpenAI client for testing."""
        return OpenAIClient(
            api_key="test_key",
            model="gpt-3.5-turbo",
            max_tokens=100,
            timeout=60,
        )

    def test_client_initialization(self, client):
        """Test client initializes with correct parameters."""
        assert client.api_key == "test_key"
        assert client.model == "gpt-5-turbo"
        assert client.max_tokens == 100

    def test_extract_json_with_code_block(self):
        """Test JSON extraction from markdown code block."""
        text = '```json\n{"summary": "Test", "highlights": []}\n```'
        result = OpenAIClient._extract_json(text)
        data = json.loads(result)
        assert data["summary"] == "Test"

    def test_extract_json_direct(self):
        """Test JSON extraction from raw text."""
        text = '{"summary": "Test", "highlights": []}'
        result = OpenAIClient._extract_json(text)
        data = json.loads(result)
        assert data["summary"] == "Test"

    @patch("news_ai.ai_client.openai.chat.completions.create")
    def test_summarize_success(self, mock_create, client):
        """Test successful summarization."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"summary": "Test Summary", "highlights": [{"title": "News 1", "source": "Source 1", "summary": "Desc 1", "importance": "high"}], "keywords": ["test"], "sentiment": "positive"}'
        mock_create.return_value = mock_response

        result = client.summarize("News content here", "Prompt template")

        assert isinstance(result, SummarizeResult)
        assert result.summary == "Test Summary"
        assert len(result.highlights) == 1
        assert result.highlights[0].title == "News 1"
        assert result.sentiment == "positive"

    @patch("news_ai.ai_client.openai.chat.completions.create")
    def test_summarize_retry_on_error(self, mock_create, client):
        """Test retry logic on API error."""
        mock_create.side_effect = [
            Exception("Rate limit"),
            Exception("Rate limit"),
            MagicMock(choices=[MagicMock(message=MagicMock(content='{"summary": "Retry success", "highlights": [], "keywords": [], "sentiment": "neutral"}'))]),
        ]

        result = client.summarize("News content", "Template")

        assert result.summary == "Retry success"
        assert mock_create.call_count == 3


class TestAnthropicClient:
    """Test cases for AnthropicClient."""

    @pytest.fixture
    def client(self):
        """Create an Anthropic client for testing."""
        return AnthropicClient(
            api_key="test_key",
            model="claude-3-haiku-20240307",
            max_tokens=100,
            timeout=60,
        )

    def test_client_initialization(self, client):
        """Test client initializes with correct parameters."""
        assert client.api_key == "test_key"
        assert client.model == "claude-3-haiku-20240307"

    @patch("news_ai.ai_client.anthropic.Anthropic")
    def test_summarize_success(self, mock_anthropic, client):
        """Test successful summarization."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = '{"summary": "Anthropic Summary", "highlights": [], "keywords": ["ai"], "sentiment": "neutral"}'
        mock_anthropic.return_value.messages.create.return_value = mock_response

        result = client.summarize("News content", "Prompt template")

        assert isinstance(result, SummarizeResult)
        assert result.summary == "Anthropic Summary"


class TestAIClientFactory:
    """Test cases for AIClientFactory."""

    def test_create_openai(self):
        """Test factory creates OpenAI client."""
        client = AIClientFactory.create("openai", {"api_key": "key"})
        assert isinstance(client, OpenAIClient)

    def test_create_anthropic(self):
        """Test factory creates Anthropic client."""
        client = AIClientFactory.create("anthropic", {"api_key": "key"})
        assert isinstance(client, AnthropicClient)

    def test_create_unknown_provider(self):
        """Test factory raises error for unknown provider."""
        with pytest.raises(ValueError) as exc_info:
            AIClientFactory.create("unknown", {})
        assert "Unknown AI provider" in str(exc_info.value)

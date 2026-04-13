"""Tests for miniflux_client module."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from news_ai.miniflux_client import MinifluxClient
from news_ai.models import Feed, Entry


class TestMinifluxClient:
    """Test cases for MinifluxClient."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Miniflux client."""
        with patch("news_ai.miniflux_client.miniflux.Client") as mock:
            yield mock

    @pytest.fixture
    def client(self, mock_client):
        """Create a MinifluxClient with mocked connection."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        return MinifluxClient(url="http://localhost:8080", api_key="test_key")

    def test_client_initialization(self, mock_client):
        """Test client initializes with correct parameters."""
        client = MinifluxClient(url="http://localhost:8080", api_key="test_key")
        mock_client.assert_called_once_with("http://localhost:8080", api_key="test_key")

    def test_list_feeds_returns_list(self, client, mock_client):
        """Test list_feeds returns a list of Feed objects."""
        mock_feed = MagicMock()
        mock_feed.id = 1
        mock_feed.title = "Test Feed"
        mock_feed.category = MagicMock()
        mock_feed.category.title.return_value = "News"
        mock_feed.url = "http://example.com"
        mock_client.return_value.get_feeds.return_value = [mock_feed]

        feeds = client.list_feeds()

        assert isinstance(feeds, list)
        assert len(feeds) == 1
        assert feeds[0].id == 1
        assert feeds[0].title == "Test Feed"

    def test_list_feeds_empty(self, client, mock_client):
        """Test list_feeds returns empty list when no feeds."""
        mock_client.return_value.get_feeds.return_value = []

        feeds = client.list_feeds()

        assert feeds == []

    def test_get_entries_returns_list(self, client, mock_client):
        """Test get_entries returns list of Entry objects."""
        mock_feed = MagicMock()
        mock_feed.id = 1
        mock_feed.title = "Test Feed"
        mock_client.return_value.get_feeds.return_value = [mock_feed]

        mock_entry = MagicMock()
        mock_entry.id = 100
        mock_entry.title = "Test Entry"
        mock_entry.url = "http://example.com/entry"
        mock_entry.updated = datetime(2024, 1, 1, 12, 0)
        mock_entry.created = datetime(2024, 1, 1, 11, 0)
        mock_entry.summary = "Test summary"
        mock_client.return_value.get_feed_entries.return_value = [mock_entry]

        entries = client.get_entries([1], limit=20)

        assert isinstance(entries, list)
        assert len(entries) == 1
        assert entries[0].id == 100
        assert entries[0].title == "Test Entry"

    def test_get_entries_sorts_by_time(self, client, mock_client):
        """Test entries are sorted by published_at descending."""
        mock_feed = MagicMock()
        mock_feed.id = 1
        mock_feed.title = "Test Feed"
        mock_client.return_value.get_feeds.return_value = [mock_feed]

        older = datetime(2024, 1, 1, 10, 0)
        newer = datetime(2024, 1, 1, 12, 0)

        mock_entry1 = MagicMock()
        mock_entry1.id = 1
        mock_entry1.title = "Older Entry"
        mock_entry1.url = "http://example.com/1"
        mock_entry1.updated = older
        mock_entry1.created = older
        mock_entry1.summary = ""

        mock_entry2 = MagicMock()
        mock_entry2.id = 2
        mock_entry2.title = "Newer Entry"
        mock_entry2.url = "http://example.com/2"
        mock_entry2.updated = newer
        mock_entry2.created = newer
        mock_entry2.summary = ""

        mock_client.return_value.get_feed_entries.side_effect = [
            [mock_entry1, mock_entry2],
            [mock_entry1, mock_entry2],
        ]

        entries = client.get_entries([1, 2], limit=20)

        assert entries[0].id == 2
        assert entries[1].id == 1

    def test_get_entries_handles_error(self, client, mock_client):
        """Test get_entries continues on individual feed error."""
        mock_feed = MagicMock()
        mock_feed.id = 1
        mock_feed.title = "Test Feed"
        mock_client.return_value.get_feeds.return_value = [mock_feed]

        mock_entry = MagicMock()
        mock_entry.id = 100
        mock_entry.title = "Test Entry"
        mock_entry.url = "http://example.com/entry"
        mock_entry.updated = datetime(2024, 1, 1, 12, 0)
        mock_entry.created = datetime(2024, 1, 1, 11, 0)
        mock_entry.summary = "Test summary"

        mock_client.return_value.get_feed_entries.side_effect = [
            Exception("Network error"),
            [mock_entry],
        ]

        entries = client.get_entries([1, 2], limit=20)

        assert len(entries) == 1
        assert entries[0].id == 100

    def test_test_connection_success(self, client, mock_client):
        """Test test_connection returns success tuple."""
        mock_client.return_value.get_feeds.return_value = []

        success, message = client.test_connection()

        assert success is True
        assert "0 feeds" in message

    def test_test_connection_failure(self, client, mock_client):
        """Test test_connection returns failure tuple on error."""
        mock_client.return_value.get_feeds.side_effect = Exception("Connection refused")

        success, message = client.test_connection()

        assert success is False
        assert "Connection refused" in message

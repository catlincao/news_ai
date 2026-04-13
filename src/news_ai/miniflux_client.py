"""Miniflux API client for News AI Summary"""

from datetime import datetime
from typing import Optional

import miniflux
from loguru import logger

from news_ai.models import Feed, Entry


class MinifluxClient:
    """Miniflux API wrapper with error handling and retry logic"""

    def __init__(self, url: str, api_key: str, timeout: int = 30) -> None:
        """
        Initialize Miniflux client.

        Args:
            url: Miniflux server URL
            api_key: Miniflux API key
            timeout: Request timeout in seconds
        """
        self.url = url
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[miniflux.Client] = None
        self._connect()

    def _connect(self) -> None:
        """Establish connection to Miniflux server"""
        try:
            self._client = miniflux.Client(self.url, api_key=self.api_key)
            logger.info(f"Connected to Miniflux at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to Miniflux: {e}")
            raise

    def list_feeds(self) -> list[Feed]:
        """
        Get all feeds from Miniflux.

        Returns:
            List of Feed objects
        """
        try:
            feeds = self._client.get_feeds()
            result = []
            for f in feeds:
                if isinstance(f, dict):
                    category = f.get("category", "") or {}
                    category_name = category.get("title", "未分类") if isinstance(category, dict) else str(category) if category else "未分类"
                    result.append(Feed(
                        id=f.get("id", 0),
                        title=f.get("title", ""),
                        category=category_name,
                        enabled=True,
                        url=f.get("site_url", ""),
                    ))
                else:
                    category_name = f.category.title() if f.category else "未分类"
                    result.append(Feed(
                        id=f.id,
                        title=f.title,
                        category=category_name,
                        enabled=True,
                        url=f.url if hasattr(f, 'url') else "",
                    ))
            logger.info(f"Retrieved {len(result)} feeds from Miniflux")
            return result
        except Exception as e:
            logger.error(f"Failed to list feeds: {e}")
            raise

    def get_entries(
        self,
        feed_ids: list[int],
        limit: int = 20
    ) -> list[Entry]:
        """
        Get entries from specified feeds.

        Args:
            feed_ids: List of feed IDs to fetch
            limit: Maximum entries per feed

        Returns:
            List of Entry objects sorted by published_at descending
        """
        entries: list[Entry] = []
        feed_titles: dict[int, str] = {}

        # First get feed titles
        try:
            feeds = self._client.get_feeds()
            for f in feeds:
                if isinstance(f, dict):
                    feed_titles[f.get("id", 0)] = f.get("title", "")
                else:
                    feed_titles[f.id] = f.title
        except Exception as e:
            logger.warning(f"Could not fetch feed titles: {e}")

        for feed_id in feed_ids:
            try:
                # Get only unread entries, sorted by created_at descending (newest first)
                feed_entries = self._client.get_feed_entries(
                    feed_id,
                    status="unread",
                    order="created_at",
                    direction="desc",
                    limit=limit,
                )
                logger.debug(f"get_feed_entries returned type: {type(feed_entries)}, keys: {feed_entries.keys() if isinstance(feed_entries, dict) else 'N/A'}")
                if isinstance(feed_entries, dict):
                    # 尝试从字典中提取条目列表
                    entries_list = feed_entries.get("entries", feed_entries.get("items", feed_entries.get("data", [])))
                    if isinstance(entries_list, list):
                        feed_entries = entries_list
                    else:
                        logger.warning(f"Could not extract entries list from dict, keys: {feed_entries.keys()}")
                        continue
                if not isinstance(feed_entries, list):
                    logger.warning(f"Unexpected feed_entries type: {type(feed_entries)}")
                    continue
                for e in feed_entries:
                    if isinstance(e, dict):
                        updated_str = e.get("updated")
                        created_str = e.get("created")
                        entry_time = datetime.now()
                        if updated_str:
                            try:
                                entry_time = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
                            except (ValueError, AttributeError):
                                pass
                        elif created_str:
                            try:
                                entry_time = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                            except (ValueError, AttributeError):
                                pass
                        entries.append(Entry(
                            id=e.get("id", 0),
                            title=e.get("title", ""),
                            url=e.get("url", ""),
                            published_at=entry_time,
                            summary=e.get("summary") or "",
                            feed_id=feed_id,
                            feed_title=feed_titles.get(feed_id, ""),
                        ))
                    elif hasattr(e, 'id'):
                        entry_time = getattr(e, "updated", None) or getattr(e, "created", None) or datetime.now()
                        entries.append(Entry(
                            id=e.id,
                            title=e.title,
                            url=e.url,
                            published_at=entry_time,
                            summary=getattr(e, 'summary', '') or '',
                            feed_id=feed_id,
                            feed_title=feed_titles.get(feed_id, ""),
                        ))
                    else:
                        logger.warning(f"Skipping invalid entry type: {type(e)}")
                logger.debug(f"Fetched {len(feed_entries)} entries from feed {feed_id}")
            except Exception as e:
                logger.warning(f"Failed to fetch entries for feed {feed_id}: {e}")
                continue

        # Sort by time descending
        entries.sort(key=lambda x: x.published_at, reverse=True)
        logger.info(f"Retrieved {len(entries)} total entries from {len(feed_ids)} feeds")
        return entries

    def get_entry_content(self, entry_id: int) -> str:
        """
        Get full content for an entry.

        Args:
            entry_id: Entry ID

        Returns:
            Full content as string
        """
        try:
            content = self._client.fetch_entry_content(entry_id)
            logger.debug(f"Fetched content for entry {entry_id}")
            return content
        except Exception as e:
            logger.warning(f"Failed to fetch content for entry {entry_id}: {e}")
            return ""

    def update_entries(self, entry_ids: list[int], status: str = "read") -> bool:
        """
        Update entry status (e.g., mark as read).

        Args:
            entry_ids: List of entry IDs to update.
            status: New status ("read" or "unread").

        Returns:
            True if successful, False otherwise.
        """
        try:
            for entry_id in entry_ids:
                self._client.update_entry(entry_id, status=status)
            logger.info(f"Updated {len(entry_ids)} entries to status: {status}")
            return True
        except Exception as e:
            logger.warning(f"Failed to update entries: {e}")
            return False

    def test_connection(self) -> tuple[bool, str]:
        """
        Test the connection to Miniflux.

        Returns:
            Tuple of (success, message)
        """
        try:
            feeds = self._client.get_feeds()
            return True, f"Connected successfully ({len(feeds)} feeds)"
        except Exception as e:
            return False, str(e)

"""Feed list widget for desktop application."""

from dataclasses import dataclass
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QCheckBox,
)
from PyQt6.QtCore import Qt
from loguru import logger

from ..config import AppConfig
from ..miniflux_client import MinifluxClient
from ..models import Feed


@dataclass
class FeedSelection:
    """Represents a feed with its selection state."""
    feed: Feed
    fetch_full_content: bool = True  # Default: fetch full content from link


class FeedListWidget(QWidget):
    """Widget for displaying and selecting feeds."""

    def __init__(self) -> None:
        """Initialize the feed list widget."""
        super().__init__()
        self._config: Optional[AppConfig] = None
        self._client: Optional[MinifluxClient] = None
        self._feeds: list[FeedSelection] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Feeds")
        self.refresh_button.clicked.connect(self._on_refresh_clicked)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Status", "补充链接信息"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def set_config(self, config: AppConfig) -> None:
        """Set the application configuration."""
        self._config = config
        try:
            self._client = MinifluxClient(
                url=config.miniflux.url,
                api_key=config.miniflux.api_key,
            )
            logger.info("FeedListWidget configured successfully")
        except Exception as e:
            logger.exception("Failed to initialize MinifluxClient in FeedListWidget")

    def _on_refresh_clicked(self) -> None:
        """Handle refresh button click."""
        logger.info("Refresh feeds button clicked")
        if self._client is None:
            logger.warning("MinifluxClient not initialized")
            return
        try:
            feeds = self._client.list_feeds()
            self._feeds = [FeedSelection(feed=f) for f in feeds]
            self.table.setRowCount(len(self._feeds))
            for row, fs in enumerate(self._feeds):
                self.table.setItem(row, 0, QTableWidgetItem(str(fs.feed.id)))
                self.table.setItem(row, 1, QTableWidgetItem(fs.feed.title))
                self.table.setItem(row, 2, QTableWidgetItem(fs.feed.category))
                status = "Enabled" if fs.feed.enabled else "Disabled"
                self.table.setItem(row, 3, QTableWidgetItem(status))

                # Add checkbox for "补充链接信息"
                checkbox = QCheckBox()
                checkbox.setChecked(fs.fetch_full_content)
                checkbox.stateChanged.connect(lambda state, r=row: self._on_checkbox_changed(r, state))
                self.table.setCellWidget(row, 4, checkbox)

            logger.info(f"Loaded {len(feeds)} feeds")
        except Exception as e:
            logger.exception("Failed to refresh feeds")

    def _on_checkbox_changed(self, row: int, state: int) -> None:
        """Handle checkbox state change."""
        if 0 <= row < len(self._feeds):
            self._feeds[row].fetch_full_content = (state == Qt.CheckState.Checked.value)
            logger.debug(f"Feed {self._feeds[row].feed.id} fetch_full_content = {self._feeds[row].fetch_full_content}")

    def get_selected_feed_selections(self) -> list[FeedSelection]:
        """Get the selected feeds with their settings.

        Returns:
            List of FeedSelection objects for selected feeds.
        """
        selections = []
        for index in self.table.selectionModel().selectedRows():
            row = index.row()
            if 0 <= row < len(self._feeds):
                selections.append(self._feeds[row])
        return selections

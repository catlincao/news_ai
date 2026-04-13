"""Feed list widget for desktop application."""

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
)
from PyQt6.QtCore import Qt
from loguru import logger

from ..config import AppConfig
from ..miniflux_client import MinifluxClient


class FeedListWidget(QWidget):
    """Widget for displaying and selecting feeds."""

    def __init__(self) -> None:
        """Initialize the feed list widget."""
        super().__init__()
        self._config: Optional[AppConfig] = None
        self._client: Optional[MinifluxClient] = None
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
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Status"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
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
            self.table.setRowCount(len(feeds))
            for row, feed in enumerate(feeds):
                self.table.setItem(row, 0, QTableWidgetItem(str(feed.id)))
                self.table.setItem(row, 1, QTableWidgetItem(feed.title))
                self.table.setItem(row, 2, QTableWidgetItem(feed.category))
                status = "Enabled" if feed.enabled else "Disabled"
                self.table.setItem(row, 3, QTableWidgetItem(status))
            logger.info(f"Loaded {len(feeds)} feeds")
        except Exception as e:
            logger.exception("Failed to refresh feeds")

    def get_selected_feed_ids(self) -> list[int]:
        """Get the IDs of selected feeds.

        Returns:
            List of selected feed IDs.
        """
        selected_ids = []
        for index in self.table.selectionModel().selectedRows():
            row = index.row()
            item = self.table.item(row, 0)
            if item is not None:
                try:
                    selected_ids.append(int(item.text()))
                except ValueError:
                    pass
        return selected_ids

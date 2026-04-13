"""History view widget for desktop application."""

from typing import Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QTextEdit,
    QPushButton,
)
from loguru import logger


class HistoryViewWidget(QWidget):
    """Widget for viewing historical summary reports."""

    def __init__(self) -> None:
        """Initialize the history view widget."""
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QHBoxLayout(self)

        self.list_widget = QListWidget()
        self.list_widget.setMaximumWidth(250)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

        right_layout = QVBoxLayout()

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        right_layout.addWidget(self.detail_text)

        button_layout = QHBoxLayout()
        self.reexport_button = QPushButton("Re-export")
        self.reexport_button.setEnabled(False)
        self.reexport_button.clicked.connect(self._on_reexport_clicked)
        button_layout.addWidget(self.reexport_button)
        button_layout.addStretch()

        right_layout.addLayout(button_layout)

        layout.addLayout(right_layout)

        self._load_history()

    def _load_history(self) -> None:
        """Load history list from disk."""
        try:
            from pathlib import Path
            import re

            history_dir = Path(".")
            md_files = sorted(
                history_dir.glob("news_summary_*.md"),
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )
            for f in md_files[:50]:
                self.list_widget.addItem(f.name)
            logger.info(f"Loaded {len(md_files)} history entries")
        except Exception as e:
            logger.exception("Failed to load history")

    def _on_item_clicked(self, item) -> None:
        """Handle list item click.

        Args:
            item: Clicked list item.
        """
        filename = item.text()
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            self.detail_text.setPlainText(content)
            self.reexport_button.setEnabled(True)
            logger.info(f"Loaded history item: {filename}")
        except Exception as e:
            logger.exception(f"Failed to load history item: {filename}")

    def _on_reexport_clicked(self) -> None:
        """Handle re-export button click."""
        current_item = self.list_widget.currentItem()
        if current_item is None:
            return

        filename = current_item.text()
        logger.info(f"Re-exporting: {filename}")

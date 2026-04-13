"""Summary view widget for desktop application."""

from typing import Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QLabel,
    QSpinBox,
)
from PyQt6.QtCore import QThread, pyqtSignal
from loguru import logger

from ..config import AppConfig
from ..miniflux_client import MinifluxClient
from ..ai_client import AIClientFactory
from ..summarizer import NewsSummarizer
from ..exporter import MarkdownExporter


class SummaryWorker(QThread):
    """Worker thread for generating summaries asynchronously."""

    finished = pyqtSignal(str, str)  # filepath, summary_content
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    empty_warning = pyqtSignal(str)

    def __init__(
        self,
        feed_ids: list[int],
        config: AppConfig,
        limit: int = 20,
        parent: Optional["SummaryViewWidget"] = None,
    ) -> None:
        """Initialize the summary worker.

        Args:
            feed_ids: List of feed IDs to summarize.
            config: Application configuration.
            limit: Maximum entries per feed.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._feed_ids = feed_ids
        self._config = config
        self._limit = limit

    def run(self) -> None:
        """Generate the summary in a background thread."""
        try:
            self.progress.emit(10)
            client = MinifluxClient(
                url=self._config.miniflux.url,
                api_key=self._config.miniflux.api_key,
            )
            entries = client.get_entries(self._feed_ids, limit=self._limit)

            if not entries:
                msg = "警告: 所有选定的 Feeds 暂无新闻"
                logger.warning(msg)
                self.empty_warning.emit(msg)
                self.finished.emit("", "无新闻可总结")
                return

            self.progress.emit(40)

            ai_client = AIClientFactory.create(
                self._config.ai.provider,
                {
                    "api_key": self._config.ai.api_key,
                    "model": self._config.ai.model,
                    "base_url": self._config.ai.base_url,
                    "max_tokens": self._config.ai.max_tokens,
                },
            )
            self.progress.emit(60)

            summarizer = NewsSummarizer(ai_client=ai_client)
            feeds = []
            result = summarizer.summarize(entries, feeds)
            self.progress.emit(80)

            # Mark entries as read
            try:
                client._client.update_entries(
                    [e.id for e in entries],
                    status="read"
                )
                logger.info(f"Marked {len(entries)} entries as read")
            except Exception as e:
                logger.warning(f"Failed to mark entries as read: {e}")

            # Generate markdown content
            exporter = MarkdownExporter(output_dir=".")
            filepath = exporter.export(result)
            summary_content = exporter.render_report(result)

            self.progress.emit(100)
            self.finished.emit(str(filepath), summary_content)
        except Exception as e:
            logger.exception("Summary generation failed")
            self.error.emit(str(e))


class SummaryViewWidget(QWidget):
    """Widget for generating and displaying news summaries."""

    def __init__(self) -> None:
        """Initialize the summary view widget."""
        super().__init__()
        self._config: Optional[AppConfig] = None
        self._worker: Optional[SummaryWorker] = None
        self._feed_list_widget: Optional["FeedListWidget"] = None
        self._current_summary: str = ""
        self._current_filepath: str = ""
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # Limit row
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("每 Feed 文章数量:"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setMinimum(1)
        self.limit_spin.setMaximum(100)
        self.limit_spin.setValue(20)
        limit_layout.addWidget(self.limit_spin)
        limit_layout.addStretch()
        layout.addLayout(limit_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Text edit for summary display
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        # Buttons
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Summary")
        self.generate_button.clicked.connect(self._on_generate_clicked)
        button_layout.addWidget(self.generate_button)

        self.export_button = QPushButton("Export Markdown")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._on_export_clicked)
        button_layout.addWidget(self.export_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def set_config(self, config: AppConfig) -> None:
        """Set the application configuration."""
        self._config = config
        logger.info("SummaryViewWidget configured")

    def set_feed_list_widget(self, feed_list_widget: "FeedListWidget") -> None:
        """Set the feed list widget to get selected feeds from."""
        self._feed_list_widget = feed_list_widget

    def _on_generate_clicked(self) -> None:
        """Handle generate button click."""
        if self._config is None:
            logger.warning("Configuration not set")
            return

        if self._feed_list_widget is None:
            logger.warning("Feed list widget not set")
            return

        feed_ids = self._feed_list_widget.get_selected_feed_ids()
        if not feed_ids:
            self.status_label.setText("请先在 Feeds 标签页选择要分析的 feeds")
            return

        limit = self.limit_spin.value()
        logger.info(f"Generate summary for feeds: {feed_ids}, limit: {limit}")
        self.generate_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.text_edit.clear()
        self.status_label.setText("Generating summary...")
        self.export_button.setEnabled(False)

        self._worker = SummaryWorker(
            feed_ids=feed_ids,
            config=self._config,
            limit=limit,
            parent=self,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.empty_warning.connect(self._on_empty_warning)
        self._worker.start()

    def _on_export_clicked(self) -> None:
        """Handle export button click."""
        if self._current_filepath:
            self.status_label.setText(f"已导出到: {self._current_filepath}")
            logger.info(f"Exported to: {self._current_filepath}")

    def _on_cancel_clicked(self) -> None:
        """Handle cancel button click."""
        if self._worker is not None and self._worker.isRunning():
            logger.info("Cancelling summary generation")
            self._worker.terminate()
            self._worker.wait()
            self.status_label.setText("Cancelled")
            self._reset_buttons()

    def _on_progress(self, value: int) -> None:
        """Handle progress updates."""
        self.progress_bar.setValue(value)

    def _on_finished(self, filepath: str, summary_content: str) -> None:
        """Handle summary generation completion."""
        logger.info(f"Summary generated: {filepath}")
        self._current_filepath = filepath
        self._current_summary = summary_content

        # Display summary in text edit
        self.text_edit.setPlainText(summary_content)
        self.status_label.setText(f"总结生成完成！点击「Export Markdown」导出，或直接在右侧查看")
        self.export_button.setEnabled(True)
        self._reset_buttons()

    def _on_error(self, error_message: str) -> None:
        """Handle errors during summary generation."""
        logger.error(f"Summary generation error: {error_message}")
        self.status_label.setText(f"Error: {error_message}")
        self._reset_buttons()

    def _reset_buttons(self) -> None:
        """Reset button states after operation completes."""
        self.generate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def _on_empty_warning(self, message: str) -> None:
        """Handle empty feed warning."""
        self.text_edit.setPlainText(message)
        self.status_label.setText("Warning: No news available")
        self._reset_buttons()

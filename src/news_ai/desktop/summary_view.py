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
    QFileDialog,
)
from PyQt6.QtCore import QThread, pyqtSignal
from loguru import logger

from ..config import AppConfig, get_user_preferences, save_user_preferences, UserPreferences
from ..miniflux_client import MinifluxClient
from ..ai_client import AIClientFactory
from ..summarizer import NewsSummarizer
from ..exporter import MarkdownExporter
from ..models import SummaryReport
from .feed_list import FeedSelection


class SummaryWorker(QThread):
    """Worker thread for generating summaries asynchronously."""

    finished = pyqtSignal(SummaryReport)  # report object
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    empty_warning = pyqtSignal(str)

    def __init__(
        self,
        feed_selections: list[FeedSelection],
        config: AppConfig,
        limit: int = 20,
        parent: Optional["SummaryViewWidget"] = None,
    ) -> None:
        """Initialize the summary worker.

        Args:
            feed_selections: List of FeedSelection objects with fetch_full_content settings.
            config: Application configuration.
            limit: Maximum entries per feed.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._feed_selections = feed_selections
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

            feed_ids = [fs.feed.id for fs in self._feed_selections]
            entries = client.get_entries(feed_ids, limit=self._limit)

            if not entries:
                msg = "警告: 所有选定的 Feeds 暂无新闻"
                logger.warning(msg)
                self.empty_warning.emit(msg)
                return

            self.progress.emit(40)

            # Build set of feed IDs that need full content fetching
            feeds_to_fetch = {
                fs.feed.id for fs in self._feed_selections if fs.fetch_full_content
            }
            logger.info(f"Feeds to fetch full content: {feeds_to_fetch}")

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

            summarizer = NewsSummarizer(
                ai_client=ai_client,
                miniflux_client=client,
                feeds_to_fetch_full_content=feeds_to_fetch,
            )
            feeds = [fs.feed for fs in self._feed_selections]
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

            self.progress.emit(100)
            self.finished.emit(result)
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
        self._current_report: Optional[SummaryReport] = None
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

        feed_selections = self._feed_list_widget.get_selected_feed_selections()
        if not feed_selections:
            self.status_label.setText("请先在 Feeds 标签页选择要分析的 feeds")
            return

        limit = self.limit_spin.value()
        logger.info(f"Generate summary for {len(feed_selections)} feeds, limit: {limit}")
        self.generate_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.text_edit.clear()
        self.status_label.setText("Generating summary...")
        self.export_button.setEnabled(False)

        self._worker = SummaryWorker(
            feed_selections=feed_selections,
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
        if self._current_report is None:
            self.status_label.setText("没有可导出的总结内容")
            return

        # Generate default filename from feeds
        feed_titles = [f.title for f in self._current_report.feeds]
        if len(feed_titles) <= 3:
            feeds_str = "_".join(feed_titles)
        else:
            feeds_str = "_".join(feed_titles[:3]) + "_等"
        default_filename = f"{feeds_str}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"

        # Get remembered export directory
        from pathlib import Path
        prefs = get_user_preferences()
        if prefs.last_export_dir:
            default_dir = prefs.last_export_dir
        else:
            default_dir = str(Path.home())

        # Show save dialog
        filepath, selected_filter = QFileDialog.getSaveFileName(
            self,
            "导出 Markdown 文件",
            str(Path(default_dir) / default_filename),
            "Markdown Files (*.md);;All Files (*)",
        )

        if not filepath:
            # User cancelled
            return

        # Remember the directory for next time
        selected_path = Path(filepath)
        export_dir = str(selected_path.parent)
        prefs.last_export_dir = export_dir
        save_user_preferences(prefs)
        logger.info(f"Remembered export directory: {export_dir}")

        # Export to selected path
        try:
            exporter = MarkdownExporter(output_dir=".")
            exporter.export_to_path(self._current_report, filepath)
            self._current_filepath = filepath
            self.status_label.setText(f"已导出到: {filepath}")
            logger.info(f"Exported to: {filepath}")
        except Exception as e:
            self.status_label.setText(f"导出失败: {e}")
            logger.error(f"Export failed: {e}")

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

    def _on_finished(self, report: SummaryReport) -> None:
        """Handle summary generation completion."""
        logger.info(f"Summary generated with {len(report.result.highlights)} highlights")
        self._current_report = report

        # Display summary in text edit
        exporter = MarkdownExporter(output_dir=".")
        summary_content = exporter.render_report(report)
        self.text_edit.setPlainText(summary_content)
        self.status_label.setText("总结生成完成！点击「Export Markdown」选择保存路径")
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

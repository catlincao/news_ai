"""Main window for the desktop application."""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMenuBar,
    QMenu,
    QStatusBar,
    QLabel,
    QTabWidget,
)
from PyQt6.QtCore import Qt
from loguru import logger

from ..config import get_config
from .feed_list import FeedListWidget
from .summary_view import SummaryViewWidget
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """Main application window with menu bar, status bar, and central widget."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        self._setup_ui()
        self._create_menu_bar()
        self._create_status_bar()
        logger.info("MainWindow initialized")

    def _setup_ui(self) -> None:
        """Set up the central widget and layout."""
        self.setWindowTitle("News AI Summary")
        self.setMinimumSize(900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()

        config = get_config()

        self.feed_list_widget = FeedListWidget()
        self.feed_list_widget.set_config(config)
        self.tab_widget.addTab(self.feed_list_widget, "Feeds")

        self.summary_view_widget = SummaryViewWidget()
        self.summary_view_widget.set_config(config)
        self.summary_view_widget.set_feed_list_widget(self.feed_list_widget)
        self.tab_widget.addTab(self.summary_view_widget, "Summary")

        layout.addWidget(self.tab_widget)

    def _create_menu_bar(self) -> None:
        """Create the application menu bar."""
        menu_bar = self.menuBar()

        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        settings_menu = QMenu("&Settings", self)
        menu_bar.addMenu(settings_menu)

        help_menu = QMenu("&Help", self)
        menu_bar.addMenu(help_menu)

    def _create_status_bar(self) -> None:
        """Create the application status bar."""
        self.statusBar()
        self.statusBar().showMessage("Ready")

    def closeEvent(self, event: "QCloseEvent") -> None:
        """Handle window close event."""
        logger.info("MainWindow closing")
        event.accept()

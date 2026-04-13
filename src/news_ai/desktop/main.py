"""Desktop application entry point."""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from loguru import logger

from .main_window import MainWindow


def _setup_app_metadata(app: QApplication) -> None:
    """Set up application metadata.

    Args:
        app: QApplication instance.
    """
    app.setApplicationName("News AI Summary")
    app.setApplicationDisplayName("News AI Summary")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("NewsAI")
    app.setOrganizationDomain("newsai.example.com")
    app.setDesktopFileName("news-ai-summary.desktop")
    app.setWindowIcon(QIcon.fromTheme("news", QIcon()))


def main() -> int:
    """Launch the desktop application.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    logger.info("Starting News AI Summary Desktop Application")

    app = QApplication(sys.argv)
    _setup_app_metadata(app)

    try:
        window = MainWindow()
        window.show()
        logger.info("Main window displayed successfully")
        return app.exec()
    except Exception as e:
        logger.exception("Failed to start desktop application")
        return 1


if __name__ == "__main__":
    sys.exit(main())

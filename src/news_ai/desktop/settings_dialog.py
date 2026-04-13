"""Settings dialog for desktop application."""

from typing import Optional

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QLabel,
)
from PyQt6.QtCore import Qt
from loguru import logger

from ..config import AppConfig


class SettingsDialog(QDialog):
    """Dialog for managing API configuration."""

    def __init__(self, config: Optional[AppConfig] = None, parent=None) -> None:
        """Initialize the settings dialog.

        Args:
            config: Current application configuration.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._config = config
        self._setup_ui()
        self._load_current_config()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.miniflux_url_input = QLineEdit()
        self.miniflux_url_input.setPlaceholderText("http://47.112.115.122:14545/")
        form_layout.addRow("Miniflux URL:", self.miniflux_url_input)

        self.miniflux_key_input = QLineEdit()
        self.miniflux_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.miniflux_key_input.setPlaceholderText("Your Miniflux API Key")
        form_layout.addRow("Miniflux API Key:", self.miniflux_key_input)

        self.openai_key_input = QLineEdit()
        self.openai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_input.setPlaceholderText("sk-...")
        form_layout.addRow("OpenAI API Key:", self.openai_key_input)

        self.anthropic_key_input = QLineEdit()
        self.anthropic_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.anthropic_key_input.setPlaceholderText("sk-ant-...")
        form_layout.addRow("Anthropic API Key:", self.anthropic_key_input)

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["openai", "anthropic"])
        form_layout.addRow("AI Provider:", self.provider_combo)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save_clicked)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _load_current_config(self) -> None:
        """Load current configuration values into the form."""
        if self._config is None:
            return

        self.miniflux_url_input.setText(self._config.miniflux.url)
        self.miniflux_key_input.setText(self._config.miniflux.api_key)

        if hasattr(self._config.ai, "openai_api_key"):
            self.openai_key_input.setText(self._config.ai.openai_api_key)
        if hasattr(self._config.ai, "anthropic_api_key"):
            self.anthropic_key_input.setText(self._config.ai.anthropic_api_key)

        self.provider_combo.setCurrentText(self._config.ai.provider)

    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        logger.info("Settings save clicked")
        self.accept()

    def get_config_values(self) -> dict:
        """Get the configuration values from the form.

        Returns:
            Dictionary of configuration values.
        """
        return {
            "miniflux_url": self.miniflux_url_input.text(),
            "miniflux_api_key": self.miniflux_key_input.text(),
            "openai_api_key": self.openai_key_input.text(),
            "anthropic_api_key": self.anthropic_key_input.text(),
            "ai_provider": self.provider_combo.currentText(),
        }

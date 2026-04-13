"""Configuration management for News AI Summary"""

import os
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MinifluxConfig(BaseModel):
    """Miniflux API configuration"""
    url: str = "http://47.112.115.122:14545/"
    api_key: str = ""


class AIConfig(BaseModel):
    """AI API configuration"""
    provider: str = "openai"  # openai, anthropic, or minimax
    model: str = "gpt-3.5-turbo"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"  # Custom API endpoint for compatible providers
    max_tokens: int = 4096
    temperature: float = 0.7


class AppConfig(BaseSettings):
    """Application configuration loaded from environment variables"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )

    miniflux: MinifluxConfig = Field(default_factory=MinifluxConfig)
    ai: AIConfig = Field(default_factory=AIConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables"""
        provider = os.getenv("AI_PROVIDER", "openai")
        api_key = ""
        base_url = "https://api.openai.com/v1"

        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY", "")
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            base_url = "https://api.anthropic.com"
        elif provider == "minimax":
            api_key = os.getenv("MINIMAX_API_KEY", "")
            base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")

        return cls(
            miniflux=MinifluxConfig(
                url=os.getenv("MINIFLUX_URL", "http://47.112.115.122:14545/"),
                api_key=os.getenv("MINIFLUX_API_KEY", ""),
            ),
            ai=AIConfig(
                provider=provider,
                model=os.getenv("AI_MODEL", "gpt-3.5-turbo"),
                api_key=api_key,
                base_url=base_url,
            ),
        )


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config


def reload_config() -> AppConfig:
    """Reload configuration from environment"""
    global _config
    _config = AppConfig.from_env()
    return _config

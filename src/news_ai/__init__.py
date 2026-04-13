"""News AI Summary - 基于 Miniflux 的新闻 AI 总结工具"""

__version__ = "0.1.0"

from loguru import logger

# Configure Loguru logging
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
)

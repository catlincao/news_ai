# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a dual-project repository:
- **Python CLI/GUI** (root directory) - News AI summarization tool with command-line and PyQt6 desktop interface
- **Flutter Android App** (apk/ directory) - Mobile application for AI-powered news summarization

Both projects connect to Miniflux RSS and use AI (OpenAI/Anthropic/MiniMax) to generate financial news summaries.

## Architecture

### Python Project (root)

Uses Clean Architecture with modular structure:
- `src/news_ai/cli.py` - Typer CLI commands
- `src/news_ai/miniflux_client.py` - Miniflux API client
- `src/news_ai/ai_client.py` - AI provider abstraction (OpenAI/Anthropic/MiniMax)
- `src/news_ai/summarizer.py` - Summary generation logic
- `src/news_ai/exporter.py` - Markdown report generation
- `src/news_ai/desktop/` - PyQt6 GUI components

### Flutter Project (apk/)

Uses Clean Architecture with BLoC pattern:
- `apk/lib/core/` - Config, constants, theme
- `apk/lib/data/models/` - Data models (freezed)
- `apk/lib/data/services/` - API clients (Miniflux, AI, storage)
- `apk/lib/presentation/blocs/` - BLoC state management (feed, summary, saved_summary)
- `apk/lib/presentation/screens/` - UI screens
- `apk/lib/utils/content_extractor.dart` - Special site content extraction (wallstreetcn, 韭研公社)

## Common Commands

### Python Project

```bash
# Install dependencies
uv sync

# Install with GUI support
uv sync --extra gui

# Run CLI
news-ai --help
news-ai list
news-ai summary --feeds 46,39 --limit 10

# Run desktop GUI
news-ai-gui

# Run tests
uv run pytest

# Lint and type check
uv run ruff check src/
uv run mypy src/
```

### Flutter Project

```bash
cd apk

# Install dependencies
flutter pub get

# Run tests
flutter test

# Analyze code
flutter analyze

# Build APK
flutter build apk --debug
flutter build apk --release

# Run on device
flutter run
```

## Configuration

Both projects use environment variables. Key variables:
- `MINIFLUX_URL`, `MINIFLUX_API_KEY` - Miniflux connection
- `AI_PROVIDER` - openai / anthropic / minimax
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `MINIMAX_API_KEY` - AI API keys

## Build Artifacts

Flutter and Gradle build outputs are gitignored. Do not commit:
- `apk/.dart_tool/` (regenerated on build)
- `apk/build/`
- `apk/android/.gradle/`

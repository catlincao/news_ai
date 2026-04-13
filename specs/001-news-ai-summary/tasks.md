# Tasks: 新闻AI总结系统

**Input**: Design documents from `/specs/001-news-ai-summary/`
**Prerequisites**: plan.md (required), spec.md (required)
**Updated**: 2026-04-12 - Added Desktop GUI phases (US5-US9)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure

## Phase 1: Setup (Day 1)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure: `src/`, `tests/`, `configs/`, `scripts/`, `src/desktop/`
- [ ] T002 [P] Create `pyproject.toml` with CLI dependencies: typer>=0.12.0, rich>=13.7.0, miniflux>=0.1.0, openai>=1.12.0, anthropic>=0.18.0, pyyaml>=6.0.1, pydantic>=2.6.0, python-dotenv>=1.0.0, loguru>=0.7.0, httpx>=0.27.0
- [ ] T003 [P] Create `pyproject.toml` with PyQt6 dependency: PyQt6>=6.6.0
- [ ] T004 [P] Create `pyproject.toml` dev dependencies: ruff>=0.3.0, mypy>=1.8.0, pytest>=8.0.0, pytest-asyncio>=0.23.0
- [ ] T005 [P] Create `src/__init__.py` with package initialization
- [ ] T006 [P] Create `src/__main__.py` for `python -m news_ai` entry point
- [ ] T007 [P] Create `tests/__init__.py`
- [ ] T008 [P] Create `src/models.py` with Feed, Entry, Highlight, SummarizeResult dataclasses with type annotations
- [ ] T009 [P] Create `src/config.py` with Pydantic models for MinifluxConfig, AIConfig, AppConfig using pydantic_settings
- [ ] T010 [P] Setup Loguru logging configuration in `src/__init__.py` or `src/logging.py`
- [ ] T011 Create `configs/feeds.yaml` with 8 feeds (IDs: 46, 45, 39, 41, 38, 40, 42, 47)
- [ ] T012 Create `configs/prompts.yaml` with summary prompt template

---

## Phase 2: Foundational (Day 1-2)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T013 [P] Implement MinifluxClient class in `src/miniflux_client.py` with __init__(url, api_key), list_feeds(), get_entries(feed_ids, limit), get_entry_content(entry_id) methods - all with type annotations
- [ ] T014 [P] Add retry logic with try-except and contextual error logging in `src/miniflux_client.py`
- [ ] T015 [P] Define AIClient Protocol in `src/ai_client.py` with summarize(news_content, prompt_template) method signature
- [ ] T016 [P] Implement OpenAIClient class in `src/ai_client.py` with __init__(api_key, model, max_tokens) and summarize() method with JSON parsing
- [ ] T017 [P] Implement AnthropicClient class in `src/ai_client.py` with __init__(api_key, model, max_tokens) and summarize() method
- [ ] T018 [P] Implement AIClientFactory in `src/ai_client.py` with create(provider, config) static method
- [ ] T019 [P] Implement NewsSummarizer class in `src/summarizer.py` with __init__(ai_client, prompt_template, max_entries), summarize(entries, feeds) methods
- [ ] T020 [P] Implement MarkdownExporter class in `src/exporter.py` with __init__(output_dir), export(report) methods, render to `news_summary_YYYYMMDD_HHMM.md` format

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 快速新闻总结 (Priority: P1) 🎯 MVP

**Goal**: 普通用户使用 `news-ai summary --feeds 46,39` 快速获取指定新闻源的摘要

**Independent Test**: `news-ai summary --feeds 46,39` → Markdown file generated at current directory with summary content

### Implementation for User Story 1

- [ ] T021 [P] [US1] Create Typer app structure in `src/cli.py` with @app typer.Typer()
- [ ] T022 [P] [US1] Create summary command in `src/cli.py` with @app.command("summary")
- [ ] T023 [P] [US1] Add --feeds parameter (Optional[str]) to summary command in `src/cli.py`
- [ ] T024 [P] [US1] Add --limit parameter (int = 20) to summary command in `src/cli.py`
- [ ] T025 [P] [US1] Add --output parameter (Optional[Path]) to summary command in `src/cli.py`
- [ ] T026 [US1] Implement feed ID parsing from comma-separated --feeds string in `src/cli.py`
- [ ] T027 [US1] Implement MinifluxClient initialization and list_feeds() call in `src/cli.py`
- [ ] T028 [US1] Implement get_entries() call for selected feeds in `src/cli.py`
- [ ] T029 [US1] Implement AIClientFactory.create() and NewsSummarizer.summarize() call in `src/cli.py`
- [ ] T030 [US1] Implement MarkdownExporter.export() call in `src/cli.py`
- [ ] T031 [US1] Add console.print progress messages with Rich in `src/cli.py`

**Checkpoint**: At this point, `news-ai summary --feeds 46,39` should work end-to-end

---

## Phase 4: User Story 2 - 交互式 Feed 选择 (Priority: P2)

**Goal**: 用户通过 `news-ai summary --interactive` 交互式界面选择要分析的 Feeds

**Independent Test**: `news-ai summary --interactive` → displays feed table → user types "1 3" → proceeds to summary

### Implementation for User Story 2

- [ ] T032 [P] [US2] Implement display_feeds_table() function in `src/cli.py` using Rich Table
- [ ] T033 [P] [US2] Implement get_category_color() function in `src/cli.py`
- [ ] T034 [P] [US2] Implement display_header() function in `src/cli.py` using Rich Panel
- [ ] T035 [P] [US2] Implement interactive_select_feeds() function in `src/cli.py` with console.input() for multi-select
- [ ] T036 [US2] Add --interactive flag (bool = False) to summary command in `src/cli.py`
- [ ] T037 [US2] Add 'a' for select-all handling in interactive_select_feeds() in `src/cli.py`
- [ ] T038 [US2] Add input validation with error message for invalid feed numbers in `src/cli.py`

**Checkpoint**: At this point, `news-ai summary --interactive` should work with feed selection

---

## Phase 5: User Story 3 - 配置文件管理 (Priority: P2)

**Goal**: 用户通过 `news-ai config-check` 和 `news-ai list` 查看和管理系统配置

**Independent Test**: `news-ai config-check` → shows Miniflux connection status and AI API Key status; `news-ai list` → shows feed table

### Implementation for User Story 3

- [ ] T039 [P] [US3] Create config_check command in `src/cli.py` with @app.command("config-check")
- [ ] T040 [P] [US3] Create list command in `src/cli.py` with @app.command("list")
- [ ] T041 [US3] Implement Miniflux connection test in config_check command in `src/cli.py`
- [ ] T042 [US3] Implement AI API Key presence check in config_check command in `src/cli.py`
- [ ] T043 [US3] Implement error display with solution hints in config_check command in `src/cli.py`

**Checkpoint**: At this point, `news-ai config-check` and `news-ai list` should work

---

## Phase 6: User Story 4 - 自定义输出 (Priority: P3)

**Goal**: 进阶用户通过 `--output` 参数自定义报告输出路径

**Independent Test**: `news-ai summary --feeds 46 --output /tmp/my_report.md` → file saved at `/tmp/my_report.md`

### Implementation for User Story 4

- [ ] T044 [US4] Implement output directory creation if not exists in `src/exporter.py`
- [ ] T045 [US4] Add permission error handling with user-friendly message in `src/exporter.py`
- [ ] T046 [US4] End-to-end verification: run `news-ai summary --feeds 46 --output /tmp/verify.md` and confirm file exists

**Checkpoint**: At this point, `--output` parameter should work correctly

---

## Phase 7: User Story 5 - 桌面应用启动 (Priority: P1) 🎯

**Goal**: 普通用户通过桌面应用图形界面使用新闻总结功能

**Independent Test**: Launch `news-ai-gui` or `python -m news_ai.desktop.main` → window displays → can interact with UI

### Desktop Foundation

- [X] T047 [P] [US5] Create `src/desktop/__init__.py`
- [X] T048 [P] [US5] Create `src/desktop/main.py` with QApplication initialization and main entry point
- [X] T049 [P] [US5] Create `src/desktop/main_window.py` with QMainWindow subclass
- [X] T050 [US5] Implement menu bar (File, Settings, Help) in `src/desktop/main_window.py`
- [X] T051 [US5] Implement status bar in `src/desktop/main_window.py`
- [X] T052 [US5] Implement central widget layout in `src/desktop/main_window.py`

**Checkpoint**: Desktop app launches and displays main window

---

## Phase 8: User Story 6 - 桌面 Feed 管理 (Priority: P1)

**Goal**: 桌面应用用户通过图形界面管理 Feeds

**Independent Test**: In desktop app, refresh feeds → see table → select feeds → verify selection

### Implementation for User Story 6

- [X] T053 [P] [US6] Create `src/desktop/feed_list.py` with FeedListWidget class (QWidget)
- [X] T054 [US6] Implement QTableWidget for feed display in `src/desktop/feed_list.py`
- [X] T055 [US6] Implement feed selection (checkbox column) in `src/desktop/feed_list.py`
- [X] T056 [US6] Implement refresh button to fetch feeds from MinifluxClient in `src/desktop/feed_list.py`
- [X] T057 [US6] Connect FeedListWidget to main window in `src/desktop/main_window.py`

**Checkpoint**: Desktop app shows feed list and allows selection

---

## Phase 9: User Story 7 - 桌面总结生成 (Priority: P1)

**Goal**: 桌面应用用户通过 GUI 一键生成新闻总结

**Independent Test**: Select feeds → click "Generate" → see progress → see summary results

### Implementation for User Story 7

- [X] T058 [P] [US7] Create `src/desktop/summary_view.py` with SummaryViewWidget class (QWidget)
- [X] T059 [US7] Implement QProgressBar for progress indication in `src/desktop/summary_view.py`
- [X] T060 [US7] Implement QTextEdit for summary display in `src/desktop/summary_view.py`
- [X] T061 [US7] Implement "Generate Summary" button in `src/desktop/summary_view.py`
- [X] T062 [US7] Implement "Export Markdown" button in `src/desktop/summary_view.py`
- [X] T063 [US7] Implement cancel button with QThread for async processing in `src/desktop/summary_view.py`
- [X] T064 [US7] Connect summary generation to core modules (MinifluxClient, AIClientFactory, NewsSummarizer) in `src/desktop/summary_view.py`
- [X] T065 [US7] Connect export to MarkdownExporter in `src/desktop/summary_view.py`
- [X] T066 [US7] Connect SummaryViewWidget to main window in `src/desktop/main_window.py`

**Checkpoint**: Desktop app can generate and export summaries

---

## Phase 10: User Story 8 - 桌面设置管理 (Priority: P2)

**Goal**: 桌面应用用户通过设置对话框管理 API 配置

**Independent Test**: Open Settings → change API key → save → verify new key works

### Implementation for User Story 8

- [X] T067 [P] [US8] Create `src/desktop/settings_dialog.py` with SettingsDialog class (QDialog)
- [X] T068 [US8] Implement QLineEdit for Miniflux URL in `src/desktop/settings_dialog.py`
- [X] T069 [US8] Implement QLineEdit for Miniflux API Key (password mode) in `src/desktop/settings_dialog.py`
- [X] T070 [US8] Implement QLineEdit for OpenAI API Key (password mode) in `src/desktop/settings_dialog.py`
- [X] T071 [US8] Implement QComboBox for AI Provider selection in `src/desktop/settings_dialog.py`
- [X] T072 [US8] Implement save/cancel buttons with validation in `src/desktop/settings_dialog.py`
- [X] T073 [US8] Implement settings dialog launch from menu in `src/desktop/main_window.py`

**Checkpoint**: Desktop app settings can be modified and saved

---

## Phase 11: User Story 9 - 桌面历史记录 (Priority: P3)

**Goal**: 桌面应用用户查看历史生成的总结报告

**Independent Test**: Open History → see list of past reports → click to view details

### Implementation for User Story 9

- [X] T074 [P] [US9] Create `src/desktop/history_view.py` with HistoryViewWidget class (QWidget)
- [X] T075 [US9] Implement QListWidget for report list in `src/desktop/history_view.py`
- [X] T076 [US9] Implement report detail view (QTextEdit read-only) in `src/desktop/history_view.py`
- [X] T077 [US9] Implement re-export functionality in `src/desktop/history_view.py`
- [X] T078 [US9] Connect HistoryViewWidget to main window in `src/desktop/main_window.py`

**Checkpoint**: Desktop app can view and re-export historical reports

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T079 [P] Add network timeout handling (30s) with retry logic in `src/miniflux_client.py`
- [X] T080 [P] Add AI API timeout handling with 3 retries and exponential backoff in `src/ai_client.py`
- [X] T081 [P] Add news count cap at 100 items with truncation message in `src/summarizer.py`
- [X] T082 [P] Add edge case handling: empty feed shows warning but continues in `src/miniflux_client.py`
- [X] T083 [P] Add edge case handling: all feeds empty generates warning report in `src/desktop/summary_view.py`
- [X] T084 [P] Add application icon and metadata in `src/desktop/main.py`
- [X] T085 [P] Update `pyproject.toml` with desktop entry point: `news-ai-gui = "news_ai.desktop.main:main"`
- [X] T086 Write unit tests for `src/miniflux_client.py` (mock Miniflux API) - 80% coverage target
- [X] T087 Write unit tests for `src/ai_client.py` (mock OpenAI/Anthropic API) - 70% coverage target
- [X] T088 Write unit tests for `src/summarizer.py` - 80% coverage target
- [X] T089 Write unit tests for `src/exporter.py` - 90% coverage target
- [X] T090 [P] Update `README.md` with desktop GUI installation and usage instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup** - No dependencies - can start immediately
- **Phase 2: Foundational** - Depends on Setup completion - BLOCKS all user stories
- **Phase 3-6: CLI Stories** - Depend on Foundational - can proceed in parallel
- **Phase 7-11: Desktop Stories** - Depend on Foundational - US5 must start first (desktop foundation)
- **Phase 12: Polish** - Depends on all stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - CLI MVP
- **User Story 2 (P2)**: Can start after Foundational - CLI (parallel with US1)
- **User Story 3 (P2)**: Can start after Foundational - CLI (parallel with US1)
- **User Story 4 (P3)**: Can start after Foundational - CLI (parallel)
- **User Story 5 (P1)**: Desktop foundation - MUST start before US6, US7
- **User Story 6 (P1)**: Depends on US5 (desktop foundation) - can parallel with US7
- **User Story 7 (P1)**: Depends on US5, US6 - core workflow
- **User Story 8 (P2)**: Can start after US5 - settings
- **User Story 9 (P3)**: Can start after US5 - history (parallel with US7, US8)

### Parallel Execution Strategy

1. Complete Phase 1 + Phase 2 (Setup + Foundational)
2. CLI team: Phase 3-6 (US1-US4) in parallel
3. Desktop team: Phase 7 (US5) first, then US6, US7 in sequence
4. Settings + History (US8, US9) can parallel with US7

---

## MVP Scope

**CLI MVP**: Phase 1 + Phase 2 + Phase 3 (US1) = T001-T031
**Desktop MVP**: Phase 5 (US5) + Phase 6 (US6) + Phase 7 (US7)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Desktop UI uses shared core modules (MinifluxClient, AIClientFactory, NewsSummarizer, MarkdownExporter)
- Tests are NOT included as separate tasks (plan.md specifies testing but spec.md did not explicitly request TDD)

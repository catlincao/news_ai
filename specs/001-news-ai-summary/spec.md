# Feature Specification: 新闻AI总结系统

**Feature Branch**: `001-news-ai-summary`
**Created**: 2026-04-12
**Status**: Draft
**Input**: User description: "新闻AI总结系统 - 规范说明书"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 快速新闻总结 (Priority: P1)

普通用户使用新闻AI总结系统快速获取指定新闻源的摘要。

**Why this priority**: 这是系统的核心功能，用户的主要价值所在，必须首先实现。

**Independent Test**: 可以通过指定 feed IDs 运行总结命令，验证是否生成正确的 Markdown 报告，并检查报告内容包含关键摘要和新闻列表。

**Acceptance Scenarios**:

1. **Given** 用户已配置 Miniflux API 和 AI API Key，**When** 执行 `news-ai summary --feeds 46,39`，**Then** 系统从 Miniflux 拉取 feed 46 和 39 的新闻，AI 分析后生成 Markdown 报告
2. **Given** 用户未配置 AI API Key，**When** 执行任何需要 AI 的命令，**Then** 系统显示清晰错误提示，指导用户配置环境变量
3. **Given** 指定了不存在的 Feed ID，**When** 执行 `news-ai summary --feeds 999`，**Then** 系统显示错误并列出所有可用 Feeds

---

### User Story 2 - 交互式 Feed 选择 (Priority: P2)

用户通过交互式界面选择要分析的 Feeds。

**Why this priority**: 提供更好的用户体验，降低命令行使用门槛，适合不熟悉 Feed ID 的用户。

**Independent Test**: 可以通过 `news-ai summary --interactive` 启动交互模式，验证系统是否显示 Feed 列表表格，用户输入选择后系统是否正确处理。

**Acceptance Scenarios**:

1. **Given** 用户执行 `news-ai summary --interactive`，**When** 系统显示 Feed 列表，**Then** 用户输入 "1 3" 选择第1和第3个 Feed，系统记录选择并继续执行总结
2. **Given** 用户执行 `news-ai summary --interactive`，**When** 用户输入 'a'，**Then** 系统选择所有启用的 Feeds
3. **Given** 用户在交互式选择中输入无效编号，**When** 系统验证输入，**Then** 显示错误提示并要求重新输入

---

### User Story 3 - 配置文件管理 (Priority: P2)

用户查看和管理系统配置，确保所有依赖正确配置。

**Why this priority**: 配置错误是用户最常遇到的问题，提前检查可以避免运行时失败。

**Independent Test**: 可以通过 `news-ai config-check` 验证系统配置，检查命令是否正确识别连接状态和环境变量配置。

**Acceptance Scenarios**:

1. **Given** 用户执行 `news-ai config-check`，**When** 所有配置正确，**Then** 显示 Miniflux 连接成功和 AI API Key 已配置的状态
2. **Given** 用户执行 `news-ai config-check`，**When** Miniflux 连接失败，**Then** 显示具体连接错误和可能原因
3. **Given** 用户执行 `news-ai list`，**Then** 系统以表格形式显示所有配置的 Feeds，包含 ID、名称、分类、状态列

---

### User Story 4 - 自定义输出 (Priority: P3)

进阶用户自定义输出路径和格式。

**Why this priority**: 技术用户可能需要将报告输出到特定位置或集成到自动化流程。

**Independent Test**: 可以通过 `--output` 参数指定输出路径，验证报告是否保存到指定位置。

**Acceptance Scenarios**:

1. **Given** 用户执行 `news-ai summary --feeds 46 --output /tmp/my_report.md`，**Then** 报告保存到 `/tmp/my_report.md` 而非默认位置
2. **Given** 用户指定输出到只读目录，**Then** 系统显示权限错误并提示替代方案

---

### User Story 5 - 桌面应用启动 (Priority: P1)

普通用户通过桌面应用图形界面使用新闻总结功能。

**Why this priority**: GUI 桌面应用是本次新增的核心功能，降低用户使用门槛。

**Independent Test**: 可以通过启动桌面应用窗口，验证窗口正常显示且可以与界面交互。

**Acceptance Scenarios**:

1. **Given** 用户启动 `news-ai-gui` 或 `python -m news_ai.desktop.main`，**Then** 桌面应用窗口正常显示主界面
2. **Given** 桌面应用启动时，**When** 检测到配置缺失，**Then** 显示设置对话框引导用户配置
3. **Given** 用户关闭窗口，**Then** 应用正常退出，不产生后台进程

---

### User Story 6 - 桌面 Feed 管理 (Priority: P1)

桌面应用用户通过图形界面管理 Feeds。

**Why this priority**: GUI 界面必须提供 Feed 管理功能，与 CLI 等效。

**Independent Test**: 在桌面应用中查看 Feed 列表，选择 Feeds 后验证是否正确获取新闻。

**Acceptance Scenarios**:

1. **Given** 用户在桌面应用中点击"刷新 Feeds"，**Then** 系统从 Miniflux 获取并显示所有 Feeds 列表
2. **Given** Feed 列表显示，**When** 用户勾选多个 Feeds，**Then** 系统记录选择的 Feeds
3. **Given** 用户点击某个 Feed，**Then** 显示该 Feed 的基本信息（名称、分类、新闻数量）

---

### User Story 7 - 桌面总结生成 (Priority: P1)

桌面应用用户通过 GUI 一键生成新闻总结。

**Why this priority**: GUI 核心功能，用户的主要操作流程。

**Independent Test**: 在桌面应用中勾选 Feeds，点击"生成总结"，验证是否显示进度并生成报告。

**Acceptance Scenarios**:

1. **Given** 用户勾选了 Feeds，**When** 点击"生成总结"按钮，**Then** 显示进度条表示正在处理
2. **Given** 总结生成中，**When** 用户可以取消操作，**Then** 系统停止并恢复界面
3. **Given** 总结完成，**Then** 在界面中显示摘要内容，并提供导出选项
4. **Given** 用户点击"导出 Markdown"，**Then** 保存报告到用户指定位置
5. **Given** 用户在生成前调整每 Feed 文章数量，**When** 使用 QSpinBox 设置 limit，**Then** 系统获取指定数量的未读文章（最新优先）
6. **Given** 总结生成完成，**When** 系统自动将已处理的文章标记为已读，**Then** Miniflux 中这些文章状态变为"已读"
7. **Given** 总结完成，**Then** 先在 GUI 文本框中显示 Markdown 内容，用户可预览后再决定是否导出
8. **Given** 总结完成，**When** 生成文件名和标题，**Then** 文件名和报告标题包含所选 Feeds 名称（或 ID）和生成日期（如 `华尔街见闻-资讯-最新_东方财富网-行业研报_20260413.md`）

---

### User Story 8 - 桌面设置管理 (Priority: P2)

桌面应用用户通过设置对话框管理 API 配置。

**Why this priority**: 配置管理是桌面应用的重要功能，影响所有操作。

**Independent Test**: 在桌面应用中打开设置，修改 API 配置后验证是否生效。

**Acceptance Scenarios**:

1. **Given** 用户点击"设置"菜单或按钮，**Then** 弹出设置对话框
2. **Given** 设置对话框显示当前配置，**When** 用户修改 API Key 并点击保存，**Then** 配置保存并生效
3. **Given** 用户输入无效配置，**When** 点击保存，**Then** 显示错误提示，不保存无效配置

---

### User Story 9 - 桌面历史记录 (Priority: P3)

桌面应用用户查看历史生成的总结报告。

**Why this priority**: 提供历史追溯功能，方便用户回顾以往总结。

**Independent Test**: 在桌面应用中打开历史记录，验证是否能查看之前的报告。

**Acceptance Scenarios**:

1. **Given** 用户点击"历史记录"菜单，**Then** 显示历史报告列表
2. **Given** 用户选择某条历史记录，**Then** 显示该报告的详细内容
3. **Given** 用户可以重新导出历史报告，**Then** 报告内容与生成时一致

---

### Edge Cases

- 当指定 Feed 没有新闻时：显示提示"该 Feed 暂无新闻"，继续处理其他 Feeds
- 当所有指定 Feeds 都无新闻时：显示警告并生成空报告（包含表头但无内容）
- 当 AI API 超时：自动重试 3 次，仍失败则提示用户并建议稍后重试
- 当单次新闻数超过 100 条时：截断为 100 条并提示用户
- 当网络中断时：捕获异常，显示错误，提示用户检查网络
- 当 AI 返回格式错误的 JSON 时：系统自动修复常见的 JSON 格式问题（如缺少逗号），提高鲁棒性

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统 MUST 支持通过 `--feeds` 参数指定单个或多个 Feed ID（逗号分隔）
- **FR-002**: 系统 MUST 支持 `--interactive` 交互式选择模式，显示 Feed 表格并允许多选
- **FR-003**: 系统 MUST 支持 `--limit` 参数控制每 Feed 获取的新闻数量（默认 20）
- **FR-004**: 系统 MUST 支持 `--output` 参数指定 Markdown 报告输出路径
- **FR-005**: 系统 MUST 提供 `list` 命令以表格形式列出所有配置的 Feeds
- **FR-006**: 系统 MUST 提供 `config-check` 命令检查并显示配置状态
- **FR-007**: 系统 MUST 从 Miniflux API 获取新闻数据，支持批量获取多个 Feeds
- **FR-008**: 系统 MUST 调用 AI API 生成新闻总结，支持 OpenAI 和 Anthropic 兼容 API
- **FR-009**: 系统 MUST 将总结结果导出为 Markdown 格式报告
- **FR-010**: 系统 MUST 在所有外部调用中使用 try-except 错误处理，日志包含上下文
- **FR-011**: 系统 MUST 支持按分类筛选 Feeds
- **FR-012**: 系统 MUST 对新闻列表进行去重和按时间排序
- **FR-013**: 系统 MUST 提供桌面 GUI 应用（PyQt6/PySide6）
- **FR-014**: 桌面应用 MUST 支持主窗口显示 Feed 列表和总结结果
- **FR-015**: 桌面应用 MUST 支持设置对话框管理 API 配置
- **FR-016**: 桌面应用 MUST 支持进度条显示处理状态
- **FR-017**: 桌面应用 MUST 支持导出 Markdown 报告到指定路径
- **FR-018**: 系统 MUST 仅获取未读文章（status="unread"），并按时间倒序排列（最新优先）
- **FR-019**: 系统 MUST 在生成总结后将处理的文章在 Miniflux 中标记为已读
- **FR-020**: 桌面应用 MUST 支持通过 QSpinBox 调整每 Feed 获取的文章数量（1-100）

---

### Key Entities *(include if feature involves data)*

- **Feed**: 代表一个新闻源，包含 id、title、category、enabled 属性
- **Entry**: 代表一条新闻条目，包含 id、title、url、published_at、summary、feed_id 属性
- **SummarizeResult**: 代表 AI 总结结果，包含 summary、highlights、keywords、sentiment 属性

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 用户可以在 2 分钟内完成从启动命令到生成报告的完整流程
- **SC-002**: 系统能够在 5 秒内完成 Feed 列表获取，30 秒内完成 AI 总结生成
- **SC-003**: 系统支持至少 8 个不同的 Feeds 配置
- **SC-004**: 生成的 Markdown 报告包含：生成时间、数据来源、Feeds 数量、新闻总数、摘要、重要新闻列表、分类统计
- **SC-005**: 用户可以通过环境变量配置 Miniflux URL、Miniflux API Key、AI API Keys，系统不硬编码任何密钥
- **SC-006**: 错误消息提供清晰的解决建议，用户可以根据错误提示自行解决问题
- **SC-007**: 系统限制单次处理新闻数不超过 100 条，避免 token 超限

---

## Assumptions

- 用户具备基本的命令行操作能力（CLI 模式）
- 用户可以访问互联网以下载新闻和调用 AI API
- Miniflux 服务地址（http://47.112.115.122:14545/）可访问
- AI API（OpenAI 或 Anthropic）服务可访问
- 用户具备有效的 Miniflux API Key 和至少一个 AI API Key
- 系统运行环境为 macOS 或 Linux，Python 3.11+
- 用户的主要需求是获取中文财经新闻的 AI 总结
- 桌面应用支持 Windows/macOS/Linux（PyQt6 跨平台）
- 桌面应用用户可能不具备命令行操作能力

---

## Changelog

### 2026-04-13

**新增功能**:

- **未读文章优先**: 获取 Feed 时仅拉取未读文章（status="unread"），并按创建时间倒序排列（最新文章在前）
- **自动标记已读**: 生成总结后，系统自动将已处理的文章在 Miniflux 中标记为已读
- **GUI 先展示后导出**: 桌面应用生成总结后，先在 GUI 文本框中显示 Markdown 内容，用户预览后再决定是否导出
- **可调整文章数量**: 桌面应用提供 QSpinBox 控件，允许用户调整每 Feed 获取的文章数量（范围 1-100）
- **JSON 格式容错**: AI 返回格式错误的 JSON 时，系统自动修复常见的格式问题（如缺少逗号），提高鲁棒性
- **Feeds 名称文件名**: 导出的 Markdown 文件名和报告标题包含所选 Feeds 名称和生成日期，便于识别（如 `华尔街见闻-资讯-最新_东方财富网-行业研报_20260413.md`）

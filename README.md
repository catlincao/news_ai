# News AI Summary

基于 Miniflux 的新闻 AI 总结工具。通过 AI 分析财经新闻并生成 Markdown 格式的总结报告。

## 项目组成

| 项目 | 路径 | 技术栈 | 说明 |
|------|------|--------|------|
| Python CLI/GUI | 根目录 | Python + PyQt6 | 命令行工具 + 桌面应用 |
| Flutter Android App | `apk/` | Flutter + BLoC | Android 移动应用 |

---

## 功能特性

### Python CLI/GUI

- 多 Feed 选择：支持指定单个或多个新闻源
- 交互式界面：友好的命令行交互体验
- 双 AI 支持：同时支持 OpenAI、Anthropic 和 MiniMax API
- 进度可视化：实时显示处理状态
- Markdown 导出：生成格式化的总结报告
- 桌面 GUI：PyQt6 桌面应用，图形界面操作

### Flutter Android App

- 连接 Miniflux 服务器获取 RSS 订阅源
- 支持多个订阅源选择
- 使用 AI (OpenAI/Anthropic/MiniMax) 生成新闻摘要
- 支持 wallstreetcn.com 和韭研公社等特殊页面内容提取
- 深色/浅色主题支持
- 配置管理（Miniflux URL、API Key、AI 配置）

---

## 环境要求

### Python 项目

- Python 3.11+
- Miniflux RSS 服务
- OpenAI API Key / Anthropic API Key / MiniMax API Key

### Flutter 项目

- Flutter SDK 3.0+
- Android SDK
- Miniflux RSS 服务
- OpenAI API Key / Anthropic API Key / MiniMax API Key

---

## 安装

### Python 项目

```bash
# 克隆项目
git clone git@github.com:catlincao/news_ai.git
cd news_ai

# 使用 uv 安装依赖
uv sync
```

### Flutter 项目

```bash
cd apk

# 获取依赖
flutter pub get
```

---

## 配置

### 环境变量

在 `.env` 文件或 shell 中设置：

```bash
# Miniflux 配置
export MINIFLUX_URL="https://xxx"
export MINIFLUX_API_KEY="your_miniflux_api_key"

# AI 配置（选择其一）
export AI_PROVIDER="openai"  # openai / anthropic / minimax

# OpenAI 配置
export OPENAI_API_KEY="your_openai_api_key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选

# Anthropic 配置
export ANTHROPIC_API_KEY="your_anthropic_api_key"

# MiniMax 配置
export MINIMAX_API_KEY="your_minimax_api_key"
export MINIMAX_BASE_URL="https://api.minimax.chat/v1"  # 可选

# 可选配置
export AI_MODEL="gpt-3.5-turbo"  # 根据提供商选择合适的模型
```

---

## 使用方法

### Python CLI/GUI

#### 配置检查

```bash
news-ai config-check
```

#### 列出所有 Feeds

```bash
news-ai list
```

#### 快速总结

```bash
# 指定 Feed IDs（逗号分隔）
news-ai summary --feeds 46,39

# 指定每 Feed 获取的新闻数
news-ai summary --feeds 46,39 --limit 10

# 指定输出目录
news-ai summary --feeds 46,39 --output /tmp/reports
```

#### 交互式选择

```bash
news-ai summary --interactive
```

### 桌面 GUI 应用

#### 安装桌面依赖

```bash
uv sync --extra gui
```

#### 启动桌面应用

```bash
# 方式一：使用命令行工具
news-ai-gui

# 方式二：使用 Python 模块
python -m news_ai.desktop.main
```

#### 桌面应用功能

- **Feeds 标签页**：查看和选择要分析的新闻源
- **Summary 标签页**：生成新闻总结并导出 Markdown
- **设置对话框**：配置 Miniflux 和 AI API
- **历史记录**：查看和重新导出之前的报告

### Flutter Android App

#### 构建 APK

```bash
cd apk

# Debug 版本
flutter build apk --debug

# Release 版本
flutter build apk --release
```

构建产物位于 `apk/build/app/outputs/flutter-apk/`

#### 运行调试

```bash
cd apk
flutter run
```

#### 配置说明

首次使用需要在设置页面配置：

- **Miniflux 服务器地址**: Miniflux 服务器的 URL
- **Miniflux API Key**: Miniflux 的 API 密钥
- **AI 提供商**: OpenAI / Anthropic / MiniMax
- **AI API Key**: 对应 AI 服务的 API 密钥
- **模型名称**: 如 gpt-3.5-turbo

---

## 项目结构

```
news_ai/
├── src/                        # Python CLI 核心代码
│   ├── __init__.py
│   ├── __main__.py            # 入口点
│   ├── cli.py                 # CLI 命令
│   ├── config.py              # 配置管理
│   ├── models.py              # 数据模型
│   ├── miniflux_client.py    # Miniflux API 客户端
│   ├── ai_client.py           # AI 客户端
│   ├── summarizer.py          # 总结生成器
│   ├── exporter.py            # Markdown 导出器
│   └── desktop/               # 桌面 GUI 应用
│       ├── main.py            # 桌面应用入口
│       ├── main_window.py     # 主窗口
│       ├── feed_list.py       # Feed 列表组件
│       ├── summary_view.py    # 总结视图组件
│       ├── settings_dialog.py # 设置对话框
│       └── history_view.py    # 历史记录组件
│
├── apk/                       # Flutter Android App
│   └── lib/
│       ├── main.dart          # 应用入口
│       ├── app.dart           # MaterialApp 配置
│       ├── core/              # 核心配置层
│       │   ├── config/        # 配置管理
│       │   ├── constants/     # 全局常量
│       │   └── theme/         # 主题定义
│       ├── data/              # 数据层
│       │   ├── models/        # 数据模型
│       │   ├── repositories/  # 数据仓库
│       │   └── services/      # 服务层
│       ├── presentation/       # 表现层
│       │   ├── blocs/         # BLoC 状态管理
│       │   ├── screens/       # 页面
│       │   └── widgets/       # 通用组件
│       └── utils/             # 工具函数
│
├── configs/                   # Feed 配置
├── tests/                    # 测试
├── pyproject.toml           # Python 项目配置
└── README.md                 # 本文档
```

---

## 开发

### Python 项目

#### 运行测试

```bash
uv run pytest
```

#### 代码检查

```bash
uv run ruff check src/
uv run mypy src/
```

#### 安装为命令行工具

```bash
uv pip install -e .
news-ai --help
```

### Flutter 项目

```bash
cd apk

# 获取依赖
flutter pub get

# 代码检查
flutter analyze

# 构建 Debug APK
flutter build apk --debug

# 构建 Release APK
flutter build apk --release
```

---

## 输出示例

生成的 Markdown 报告包含：

- **生成时间**
- **数据来源**
- **Feeds 数量**
- **新闻总数**
- **AI 生成的摘要**
- **重要新闻列表**（带来源、时间、摘要）
- **分类统计**
- **关键词**
- **情感分析**

---

## License

MIT

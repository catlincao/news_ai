# 新闻 AI 摘要 Android App

基于 Flutter 的新闻 AI 摘要应用，连接 Miniflux RSS 阅读器，使用 AI 生成财经新闻摘要。

> **注意：** `apk` 是 Flutter 项目目录（项目名恰好叫 `apk`），并非已编译的 APK 文件。

## 功能特性

- 连接 Miniflux 服务器获取 RSS 订阅源
- 支持多个订阅源选择
- 使用 AI (OpenAI/Anthropic/MiniMax) 生成新闻摘要
- 支持 wallstreetcn.com 和韭研公社等特殊页面内容提取
- 深色/浅色主题支持
- 配置管理（Miniflux URL、API Key、AI 配置）

---

## 项目结构详解

```
apk/
├── lib/                          # Flutter 核心代码
│   ├── main.dart                  # 应用入口，初始化 SharedPreferences
│   ├── app.dart                  # MaterialApp 配置，支持 light/dark 主题
│   │
│   ├── core/                     # 核心配置层
│   │   ├── config/
│   │   │   └── app_config.dart  # AppConfig 配置管理类
│   │   ├── constants/
│   │   │   └── app_constants.dart # 全局常量
│   │   └── theme/
│   │       └── app_theme.dart    # 主题定义（Material 3）
│   │
│   ├── data/                     # 数据层
│   │   ├── models/               # 数据模型（freezed）
│   │   │   ├── entry.dart        # Miniflux 条目模型
│   │   │   ├── feed.dart         # RSS 订阅源模型
│   │   │   ├── saved_summary.dart # 已保存摘要模型
│   │   │   └── summary_result.dart # AI 摘要结果模型
│   │   ├── repositories/         # 数据仓库（空目录，待填充）
│   │   └── services/             # 服务层
│   │       ├── ai_service.dart       # AI 服务（OpenAI/Anthropic/MiniMax）
│   │       ├── miniflux_service.dart # Miniflux RSS 阅读器 API 客户端
│   │       └── saved_summary_service.dart # 本地保存摘要服务
│   │
│   ├── presentation/              # 表现层
│   │   ├── blocs/                # BLoC 状态管理
│   │   │   ├── feed/              # 订阅源 BLoC
│   │   │   │   ├── feed_bloc.dart
│   │   │   │   ├── feed_event.dart
│   │   │   │   └── feed_state.dart
│   │   │   ├── summary/           # 摘要生成 BLoC
│   │   │   │   ├── summary_bloc.dart
│   │   │   │   ├── summary_event.dart
│   │   │   │   └── summary_state.dart
│   │   │   └── saved_summary/     # 已保存摘要 BLoC
│   │   │       ├── saved_summary_bloc.dart
│   │   │       ├── saved_summary_event.dart
│   │   │       └── saved_summary_state.dart
│   │   ├── screens/              # 页面
│   │   │   ├── home_screen.dart              # 首页
│   │   │   ├── feed_list_screen.dart         # 订阅源列表
│   │   │   ├── summary_screen.dart           # 摘要生成页
│   │   │   ├── summary_result_screen.dart    # 摘要结果页
│   │   │   ├── saved_summaries_screen.dart  # 已保存摘要列表
│   │   │   └── settings_screen.dart          # 设置页
│   │   └── widgets/             # 通用组件（空目录）
│   │
│   └── utils/                    # 工具函数
│       └── content_extractor.dart # 特殊页面内容提取（wallstreetcn/韭研公社）
│
├── android/                      # Android 原生配置
│   ├── app/
│   │   ├── build.gradle         # App 级构建配置（compileSdk 36, minSdk 26）
│   │   └── src/main/
│   │       ├── AndroidManifest.xml # 应用清单（权限、Activity、图标）
│   │       ├── kotlin/
│   │       │   └── com/newsai/apk/
│   │       │       └── MainActivity.kt # Kotlin 主入口
│   │       ├── java/
│   │       │   └── io/flutter/plugins/
│   │       │       └── GeneratedPluginRegistrant.java # Flutter 插件注册
│   │       └── res/
│   │           ├── drawable/
│   │           │   ├── ic_launcher_foreground.xml
│   │           │   └── launch_background.xml
│   │           ├── mipmap-anydpi-v26/
│   │           │   └── ic_launcher.xml  # 自适应图标
│   │           └── values/
│   │               ├── colors.xml   # 颜色定义
│   │               └── styles.xml   # 样式/主题
│   │
│   ├── build.gradle             # 项目级构建配置
│   ├── settings.gradle          # 项目设置
│   ├── gradle.properties        # Gradle 属性
│   ├── local.properties         # 本地 SDK 路径
│   ├── gradlew / gradlew.bat   # Gradle 包装脚本
│   └── gradle/wrapper/          # Gradle 包装器
│
├── pubspec.yaml                  # Flutter 依赖声明
├── pubspec.lock                  # 依赖锁定文件
├── .flutter-plugins-dependencies # Flutter 插件依赖
├── README.md                     # 项目文档
│
├── .dart_tool/                   # Dart 工具缓存
└── build/                        # 构建产物输出目录
```

---

### lib/ 目录文件说明

| 文件 | 作用 |
|---|---|
| `main.dart` | 应用入口，`WidgetsFlutterBinding.ensureInitialized()` 初始化 SharedPreferences |
| `app.dart` | `NewsAIApp` 根组件，配置 Material 3 主题（light/dark） |
| `core/config/app_config.dart` | `AppConfig` 配置管理类，存储/读取 Miniflux、AI 等配置 |
| `core/constants/app_constants.dart` | 全局常量定义 |
| `core/theme/app_theme.dart` | Flutter ThemeData 定义 |
| `data/models/entry.dart` | Miniflux 条目（新闻条目）数据模型 |
| `data/models/feed.dart` | RSS 订阅源数据模型 |
| `data/models/saved_summary.dart` | 已保存摘要数据模型 |
| `data/models/summary_result.dart` | AI 生成的摘要结果数据模型 |
| `data/services/ai_service.dart` | AI 服务客户端，封装 OpenAI/Anthropic/MiniMax API 调用 |
| `data/services/miniflux_service.dart` | Miniflux API 客户端，获取订阅源和条目 |
| `data/services/saved_summary_service.dart` | 本地摘要存储服务 |
| `utils/content_extractor.dart` | 特殊页面内容提取器（wallstreetcn.com、韭研公社） |
| `presentation/blocs/feed/` | 订阅源 BLoC：获取和管理 RSS 订阅源列表 |
| `presentation/blocs/summary/` | 摘要 BLoC：调用 AI 服务生成新闻摘要 |
| `presentation/blocs/saved_summary/` | 已保存摘要 BLoC：管理本地保存的摘要 |
| `presentation/screens/home_screen.dart` | 首页 |
| `presentation/screens/feed_list_screen.dart` | 订阅源列表页 |
| `presentation/screens/summary_screen.dart` | 摘要生成页 |
| `presentation/screens/summary_result_screen.dart` | 摘要结果展示页 |
| `presentation/screens/saved_summaries_screen.dart` | 已保存摘要列表页 |
| `presentation/screens/settings_screen.dart` | 设置页（Miniflux、AI 配置） |

---

### android/ 目录文件说明

| 文件 | 作用 |
|---|---|
| `AndroidManifest.xml` | 应用清单：声明网络权限、Activity、图标、支持明文流量 |
| `app/build.gradle` | App 模块构建配置（compileSdk 36, minSdk 26, targetSdk 34）|
| `app/src/main/kotlin/.../MainActivity.kt` | Kotlin 主入口Activity |
| `GeneratedPluginRegistrant.java` | Flutter 插件自动注册文件 |
| `build.gradle` | 项目级 Gradle 配置 |
| `settings.gradle` | 项目设置 |
| `gradle.properties` | Gradle 属性（AndroidX 配置等）|
| `local.properties` | 本地 SDK/NDK 路径 |
| `gradlew / gradlew.bat` | Gradle 包装脚本（Unix/Windows）|
| `gradle/wrapper/` | Gradle 包装器 jar 和配置 |

---

## 架构总结

采用 **Clean Architecture + BLoC** 模式：

```
presentation (UI/Bloc) → data (Services/Models) → core (Config/Theme/Utils)
```

- **Miniflux** 作为 RSS 后端获取订阅源
- **AI 服务**（OpenAI/Anthropic/MiniMax）生成新闻摘要
- 支持 **wallstreetcn.com** 和 **韭研公社** 等特殊站点的内容提取

---

## 构建步骤

### 1. 安装 Flutter SDK

确保已安装 Flutter SDK (>=3.0.0)

### 2. 获取依赖

```bash
cd apk
flutter pub get
```

### 3. 构建 APK

```bash
flutter build apk --debug
# 或 release 版本
flutter build apk --release
```

构建产物位于 `build/app/outputs/flutter-apk/`

### 4. 运行调试

```bash
flutter run
```

---

## 配置说明

首次使用需要配置以下信息：

- **Miniflux 服务器地址**: Miniflux 服务器的 URL
- **Miniflux API Key**: Miniflux 的 API 密钥
- **AI 提供商**: OpenAI / Anthropic / MiniMax
- **AI API Key**: 对应 AI 服务的 API 密钥
- **模型名称**: 如 gpt-3.5-turbo

---

## 核心依赖

| 依赖 | 版本 | 用途 |
|---|---|---|
| flutter_bloc | ^8.1.6 | BLoC 状态管理 |
| dio | ^5.4.3+1 | HTTP 客户端（调用 AI/Miniflux API）|
| freezed_annotation | ^2.4.1 | 不可变数据类 |
| json_annotation | ^4.9.0 | JSON 序列化注解 |
| shared_preferences | ^2.2.3 | 本地配置存储 |
| equatable | ^2.0.5 | 值相等比较 |
| url_launcher | ^6.3.0 | 外部链接打开 |
| flutter_linkify | ^6.0.0 | 文本链接识别 |

---

## 技术栈

- **Flutter 3.x** - UI 框架
- **flutter_bloc** - 状态管理
- **dio** - HTTP 客户端
- **shared_preferences** - 本地存储
- **freezed** - 不可变数据类

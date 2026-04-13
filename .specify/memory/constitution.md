<!--
Sync Impact Report
================================================================================
Version Change: 1.0.0 → 2.0.0 (MAJOR - Architecture Change)

Modified Principles: N/A
  - None

Added Sections:
  - 桌面应用层 (Desktop Application Layer) - PyQt6/PySide6
  - 双模式支持 (Dual-Mode Support) - CLI + Desktop

Removed Sections:
  - None

Module Boundary Changes:
  - CLI层 → CLI / Desktop UI 层
  - 新增桌面应用模块 (src/desktop/)

Version Change Reason:
  添加 PyQt6/PySide6 桌面应用，重大架构变更

Templates Status:
  ✅ All templates compatible

Deferred Items:
  - None

Follow-up Actions:
  - Update spec.md with desktop UI user stories
  - Update plan.md with desktop architecture
  - Generate new tasks for desktop UI
================================================================================
-->

# 新闻AI总结系统 宪法 (Constitution)

> 本文件定义了项目的不可妥协原则和技术要求。所有开发决策必须遵守本文件。
> 更新时需经过充分讨论，单一 AI 不可单方面修改核心原则。

---

## 一、核心价值观

### 1.1 简洁高效原则

```
专注于新闻总结核心功能
不引入无关的复杂特性
保持工具的轻量化和快速响应
```

### 1.2 数据隐私原则

```
所有API密钥必须通过环境变量注入
不将敏感信息硬编码到代码中
不支持将用户数据上传到第三方服务
```

### 1.3 AI 辅助原则

```
AI 负责分析和总结，人类保留最终决策权
总结结果必须可追溯、可解释
不依赖 AI 生成的内容作为唯一事实来源
```

---

## 二、技术红线 (不可逾越)

### 2.1 代码质量

| 规则 | 要求 |
|------|------|
| Type Hint | **所有函数必须有类型注解**，包括返回值 |
| 错误处理 | 所有外部调用必须 try-except，错误日志必须包含上下文 |
| 测试覆盖 | 核心模块测试覆盖率 > 50% |
| 依赖管理 | 使用 `uv` 管理，版本锁定 |

### 2.2 API 兼容性

```
必须同时支持 OpenAI 和 Anthropic 兼容 API
API 配置通过环境变量注入，不硬编码
支持 API Key 轮换和降级策略
```

### 2.3 数据源约束

| 数据源 | 接口 | 说明 |
|--------|------|------|
| Miniflux | http://47.112.115.122:14545/ | 新闻数据来源 |
| AI API | OpenAI / Anthropic | 新闻分析总结 |

### 2.4 配置管理

```
配置文件格式：YAML
敏感信息：仅支持环境变量
本地存储：SQLite（轻量）
```

---

## 三、模块边界 (强制隔离)

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI / Desktop UI                        │
│                        (Typer / PyQt6)                     │
├─────────────────────────────────────────────────────────────┤
│                        新闻获取层                            │
│                    (Miniflux Client)                        │
├─────────────────────────────────────────────────────────────┤
│                        AI 分析层                            │
│                   (AI Client Abstract)                     │
├─────────────────────────────────────────────────────────────┤
│                        导出层                                │
│                   (Markdown Exporter)                       │
└─────────────────────────────────────────────────────────────┘
```

**规则**：
- 模块间通信通过定义好的接口
- 每个模块独立可测试
- 模块替换不影响其他模块
- CLI 和 Desktop UI 共用底层核心模块
- Desktop UI 不得直接调用 API，均通过核心模块

---

## 四、命名规范

### 4.1 项目结构

```
news-ai-summary/
├── constitution.md
├── specify.md
├── plan.md
├── src/
│   ├── __init__.py
│   ├── cli.py              # 命令行入口 (Typer)
│   ├── config.py           # 配置管理
│   ├── miniflux_client.py  # Miniflux API 封装
│   ├── ai_client.py        # AI 客户端抽象
│   ├── summarizer.py       # 总结生成器
│   ├── exporter.py         # 导出器
│   └── desktop/            # 桌面应用 (PyQt6/PySide6)
│       ├── __init__.py
│       ├── main_window.py   # 主窗口
│       ├── feed_list.py    # Feed 列表视图
│       ├── summary_view.py # 总结结果视图
│       └── settings.py     # 设置对话框
├── tests/
│   ├── test_miniflux.py
│   ├── test_ai_client.py
│   └── test_summarizer.py
└── configs/
    └── feeds.yaml          # Feed 配置
```

### 4.2 配置项

```yaml
# feeds.yaml
feeds:
  - id: 46
    name: "华尔街见闻-最新"
    category: "资讯"
    enabled: true
  - id: 39
    name: "东方财富-行业研报"
    category: "研报"
    enabled: true
```

---

## 五、输出规范

### 5.1 Markdown 导出格式

```markdown
# 新闻总结报告

**生成时间**: YYYY-MM-DD HH:mm
**数据来源**: Miniflux RSS
**Feeds 数量**: N
**新闻总数**: M

---

## 摘要

[AI 生成的总体摘要，100-300 字]

---

## 重要新闻

### 1. [新闻标题]
- **来源**: [Feed 名称]
- **时间**: [发布时间]
- **摘要**: [AI 总结]

### 2. [新闻标题]
...

---

## 分类统计

| 分类 | 数量 |
|------|------|
| 资讯 | 10 |
| 研报 | 5 |
| 策略 | 3 |

---

*由 News AI Summary 生成*
```

### 5.2 文件命名

```
news_summary_YYYYMMDD_HHMM.md
```

---

## 六、AI 提示词规范

### 6.1 总结提示词模板

```
你是一个专业的财经新闻分析师。请分析以下新闻列表，提取关键信息。

## 要求
1. 识别最重要的3-5条新闻
2. 每条新闻提供50-100字的中文摘要
3. 识别新闻中的关键人物、公司、事件
4. 判断新闻的时效性和重要性

## 输出格式
请用以下 JSON 格式输出：
{
  "summary": "总体摘要，100-200字",
  "highlights": [
    {
      "title": "新闻标题",
      "source": "来源",
      "summary": "摘要，50-100字",
      "importance": "high/medium/low"
    }
  ],
  "keywords": ["关键词1", "关键词2", "..."],
  "sentiment": "positive/neutral/negative"
}

## 新闻列表
{news_content}
```

---

## 七、安全与合规

### 7.1 敏感信息

```
- Miniflux 服务: http://47.112.115.122:14545/
- Miniflux API Key: 仅环境变量 MINIFLUX_API_KEY
- AI API Key: 仅环境变量 OPENAI_API_KEY / ANTHROPIC_API_KEY
- 数据库: 本地 SQLite
```

**环境变量配置示例**：
```bash
export MINIFLUX_URL="http://47.112.115.122:14545/"
export MINIFLUX_API_KEY="your_api_key_here"
```

### 7.2 日志规范

```
禁止记录：完整新闻内容（只记录标题和来源）
必须记录：操作时间戳、模块名、日志级别
保留周期：7天滚动
```

---

## 八、变更管理

### 8.1 版本管理

```
Constitution: v1.0.0
发布: 2026-04-12
```

---

## Governance

**Constitution 宪法**: 本文件是项目的最高准则，所有其他实践和文档都必须服从本文件。

**变更管理**: 对本宪法的修订需要：
1. 在变更前进行充分讨论
2. 明确标注变更的类型（MAJOR/MINOR/PATCH）
3. 更新版本号并记录变更日期
4. 保持向后兼容性（除非是 MAJOR 变更）

**合规检查**: 所有 PR 和代码审查必须验证对本宪法的遵守情况。

**版本语义**:
- MAJOR: 向后不兼容的原则移除或重新定义
- MINOR: 新增原则/章节或实质性扩展指导
- PATCH: 澄清、措辞、错别字修复、非语义性改进

---

**Version**: 2.0.0 | **Ratified**: 2026-04-12 | **Last Amended**: 2026-04-12

*本宪法版本：v2.0.0 | 发布日期：2026-04-12 | 重大变更：添加 PyQt6 桌面应用*

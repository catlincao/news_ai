import 'dart:convert';
import 'package:dio/dio.dart';
import '../models/entry.dart';
import '../models/summary_result.dart';

enum AIProvider { openai, anthropic, minimax }

class AIConfig {
  final AIProvider provider;
  final String apiKey;
  final String model;
  final String? baseUrl;

  const AIConfig({
    required this.provider,
    required this.apiKey,
    required this.model,
    this.baseUrl,
  });
}

class AIService {
  final Dio _dio = Dio();
  final AIConfig config;

  static const String _promptTemplate = '''你是一个专业的财经新闻分析师。请分析以下新闻列表，提取关键信息。

## 要求
1. 识别最重要的8-12条新闻，对同主题新闻进行合并
2. 每条新闻提供150-300字的详细中文摘要，包含背景、分析和影响
3. 识别新闻中的标的信息（股票代码如SH600519、公司名称等）
4. 识别新闻中的关键人物、公司、事件
5. 判断新闻的时效性和重要性

## 输出格式
请用以下 JSON 格式输出：
```json
{
  "summary": "总体摘要，200-400字",
  "highlights": [
    {
      "title": "新闻标题",
      "source": "来源",
      "url": "原文URL链接",
      "summary": "详细摘要，150-300字，包含背景、分析和影响",
      "importance": "high/medium/low",
      "tickers": ["股票代码1", "股票代码2"]
    }
  ],
  "tickers": [
    {"code": "SH600519", "name": "贵州茅台"},
    {"code": "SZ000858", "name": "五粮液"}
  ],
  "keywords": ["关键词1", "关键词2", "..."],
  "sentiment": "positive/neutral/negative"
}
```

## 新闻列表
{news_content}
''';

  AIService({required this.config});

  String _buildPrompt(String newsContent) {
    return _promptTemplate.replaceAll('{news_content}', newsContent);
  }

  String _formatEntries(List<Entry> entries) {
    final lines = <String>[];

    // Limit to 20 entries to avoid token limit (MiniMax has ~8K token limit)
    final limitedEntries = entries.length > 20 ? entries.sublist(0, 20) : entries;

    for (var i = 0; i < limitedEntries.length; i++) {
      final entry = limitedEntries[i];
      lines.add('${i + 1}. [${entry.feedTitle}] ${entry.title}');
      lines.add('   时间: ${entry.publishedAt.toString().substring(0, 16)}');
      lines.add('   原文: ${entry.url}');
      final content = entry.content ?? entry.summary;
      if (content.isNotEmpty) {
        // Limit each content to 10000 characters (same as Mac version)
        final contentText = content.length > 10000
            ? '${content.substring(0, 10000)}...'
            : content;
        lines.add('   内容: $contentText');
      }
      lines.add('');
    }
    return lines.join('\n');
  }

  Future<SummaryResult> generateSummary(List<Entry> entries) async {
    if (entries.isEmpty) {
      throw Exception('No entries to summarize');
    }

    // Limit entries to 20 to avoid token limit
    final limitedEntries = entries.length > 20 ? entries.sublist(0, 20) : entries;

    // Debug: log entries being sent
    print('[AI] Sending ${limitedEntries.length} entries to AI:');
    for (final e in limitedEntries) {
      print('  - [${e.feedTitle}] ${e.title} (feedId=${e.feedId})');
    }

    final newsContent = _formatEntries(limitedEntries);
    final prompt = _buildPrompt(newsContent);

    switch (config.provider) {
      case AIProvider.openai:
        return _callOpenAI(prompt);
      case AIProvider.anthropic:
        return _callAnthropic(prompt);
      case AIProvider.minimax:
        return _callMinimax(prompt);
    }
  }

  Future<SummaryResult> _callOpenAI(String prompt) async {
    final baseUrl = config.baseUrl ?? 'https://api.openai.com/v1';

    try {
      final response = await _dio.post(
        '$baseUrl/chat/completions',
        options: Options(headers: {
          'Authorization': 'Bearer ${config.apiKey}',
          'Content-Type': 'application/json',
        }),
        data: {
          'model': config.model,
          'messages': [
            {'role': 'system', 'content': '你是一个专业的财经新闻分析师。'},
            {'role': 'user', 'content': prompt},
          ],
          'temperature': 0.7,
          'max_tokens': 4096,
        },
      );

      final data = response.data as Map<String, dynamic>;
      final content = data['choices']?[0]?['message']?['content'] as String? ?? '';
      return _parseAIResponse(content);
    } on DioException catch (e) {
      throw Exception('OpenAI API error: ${e.message}');
    }
  }

  Future<SummaryResult> _callAnthropic(String prompt) async {
    try {
      final response = await _dio.post(
        'https://api.anthropic.com/v1/messages',
        options: Options(headers: {
          'x-api-key': config.apiKey,
          'anthropic-version': '2023-06-01',
          'Content-Type': 'application/json',
        }),
        data: {
          'model': config.model,
          'max_tokens': 4096,
          'messages': [
            {'role': 'user', 'content': prompt},
          ],
        },
      );

      final data = response.data as Map<String, dynamic>;
      final content = data['content']?[0]?['text'] as String? ?? '';
      return _parseAIResponse(content);
    } on DioException catch (e) {
      throw Exception('Anthropic API error: ${e.message}');
    }
  }

  Future<SummaryResult> _callMinimax(String prompt) async {
    // MiniMax uses Anthropic-compatible API format
    final baseUrl = config.baseUrl ?? 'https://api.minimaxi.com';

    try {
      final response = await _dio.post(
        '$baseUrl/v1/messages',
        options: Options(headers: {
          'x-api-key': config.apiKey,
          'anthropic-version': '2023-06-01',
          'Content-Type': 'application/json',
        }),
        data: {
          'model': config.model,
          'max_tokens': 4096,
          'temperature': 0.7,
          'messages': [
            {'role': 'user', 'content': prompt},
          ],
        },
      );

      final data = response.data as Map<String, dynamic>;
      // Anthropic returns: {"content": [{"type": "text", "text": "..."}]}
      final content = (data['content'] as List<dynamic>?)
              ?.firstWhere(
                (e) => (e as Map<String, dynamic>)['type'] == 'text',
                orElse: () => {'text': ''},
              )?['text'] as String? ??
          '';
      return _parseAIResponse(content);
    } on DioException catch (e) {
      throw Exception('MiniMax API error: ${e.message}');
    }
  }

  SummaryResult _parseAIResponse(String content) {
    // Extract JSON from markdown code block if present
    String jsonStr = content;
    final codeBlockMatch = RegExp(r'```json\s*([\s\S]*?)\s*```').firstMatch(content);
    if (codeBlockMatch != null) {
      jsonStr = codeBlockMatch.group(1) ?? content;
    }

    // Try to find JSON object in the content
    final jsonMatch = RegExp(r'\{[\s\S]*\}').firstMatch(jsonStr);
    if (jsonMatch != null) {
      jsonStr = jsonMatch.group(0) ?? content;
    }

    try {
      final json = jsonDecode(jsonStr) as Map<String, dynamic>;
      return SummaryResult.fromJson(json);
    } catch (e) {
      throw Exception('Failed to parse AI response: $e');
    }
  }
}

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/config/app_config.dart';
import '../blocs/summary/summary_bloc.dart';
import '../blocs/summary/summary_event.dart';
import '../blocs/summary/summary_state.dart';
import '../blocs/saved_summary/saved_summary_bloc.dart';
import '../blocs/saved_summary/saved_summary_event.dart';
import '../blocs/saved_summary/saved_summary_state.dart';
import '../../data/models/entry.dart';
import '../../data/models/summary_result.dart';

class SummaryScreen extends StatefulWidget {
  final List<int> selectedFeedIds;
  final AppConfig config;

  const SummaryScreen({super.key, required this.selectedFeedIds, required this.config});

  @override
  State<SummaryScreen> createState() => _SummaryScreenState();
}

class _SummaryScreenState extends State<SummaryScreen> {
  @override
  void initState() {
    super.initState();
    context.read<SummaryBloc>().add(LoadEntries(
          feedIds: widget.selectedFeedIds,
          limit: widget.config.perFeedLimit,
        ));
  }

  void _generateSummary() {
    final state = context.read<SummaryBloc>().state;
    if (state.entries.isNotEmpty) {
      context.read<SummaryBloc>().add(GenerateSummary(entries: state.entries));
    }
  }

  void _copyToClipboard(String text) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('已复制到剪贴板')),
    );
  }

  Future<void> _openUrl(String url) async {
    print('[SummaryScreen] _openUrl called with: $url');
    try {
      // Clean the URL - remove any whitespace or newlines
      final cleanUrl = url.trim();
      final uri = Uri.parse(cleanUrl);
      print('[SummaryScreen] Parsed URI: $uri');
      if (await canLaunchUrl(uri)) {
        print('[SummaryScreen] canLaunchUrl true, launching...');
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        print('[SummaryScreen] canLaunchUrl false');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('无法打开链接: $cleanUrl')),
          );
        }
      }
    } catch (e) {
      print('[SummaryScreen] Error opening URL: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('打开链接失败: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return MultiBlocListener(
      listeners: [
        BlocListener<SummaryBloc, SummaryState>(
          listener: (context, state) {
            if (state.status == SummaryStatus.failure) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(state.errorMessage ?? '发生错误'),
                  backgroundColor: Colors.red,
                ),
              );
            }
          },
        ),
        BlocListener<SavedSummaryBloc, SavedSummaryState>(
          listener: (context, state) {
            if (state.status == SavedSummaryStatus.failure) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(state.errorMessage ?? '收藏失败'),
                  backgroundColor: Colors.red,
                ),
              );
            }
          },
        ),
      ],
      child: Scaffold(
        appBar: AppBar(
          title: const Text('生成摘要'),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () {
                context.read<SummaryBloc>().add(LoadEntries(
                      feedIds: widget.selectedFeedIds,
                      limit: widget.config.perFeedLimit,
                    ));
              },
            ),
          ],
        ),
        body: BlocBuilder<SummaryBloc, SummaryState>(
          builder: (context, state) {
            if (state.status == SummaryStatus.loading) {
              return const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('正在加载文章...'),
                  ],
                ),
              );
            }

            if (state.status == SummaryStatus.generating) {
              return const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('正在生成 AI 摘要...'),
                  ],
                ),
              );
            }

          if (state.result == null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('已加载 ${state.entries.length} 篇文章'),
                  const SizedBox(height: 8),
                  Text(
                    '每源限制: ${widget.config.perFeedLimit} 篇',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _generateSummary,
                    child: const Text('生成 AI 摘要'),
                  ),
                ],
              ),
            );
          }

          return _buildSummaryResult(state.result!, state.entries);
        },
      ),
    ),
    );
  }

  Widget _buildSummaryResult(SummaryResult result, List<Entry> entries) {
    return Column(
      children: [
        // Toolbar with regenerate and save buttons
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '已加载 ${entries.length} 篇文章',
                style: TextStyle(color: Colors.grey[600]),
              ),
              Row(
                children: [
                  ElevatedButton.icon(
                    onPressed: () {
                      context.read<SummaryBloc>().add(GenerateSummary(entries: entries));
                    },
                    icon: const Icon(Icons.refresh),
                    label: const Text('重新生成'),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    onPressed: () {
                      context.read<SavedSummaryBloc>().add(SaveSummary(
                        result: result,
                        feedIds: widget.selectedFeedIds,
                      ));
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('已收藏')),
                      );
                    },
                    icon: const Icon(Icons.bookmark_add),
                    label: const Text('收藏'),
                  ),
                ],
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Summary section
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            '总体摘要',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                          IconButton(
                            icon: const Icon(Icons.copy),
                            onPressed: () => _copyToClipboard(result.summary),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(result.summary),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Metadata
              Row(
                children: [
                  Chip(
                    avatar: const Icon(Icons.sentiment_neutral, size: 18),
                    label: Text(result.sentiment),
                  ),
                  const SizedBox(width: 8),
                  if (result.keywords.isNotEmpty)
                    Expanded(
                      child: Wrap(
                        spacing: 4,
                        children: result.keywords.take(5).map((k) {
                          return Chip(label: Text(k, style: const TextStyle(fontSize: 12)));
                        }).toList(),
                      ),
                    ),
                ],
              ),

              // 投资标
              if (result.tickers.isNotEmpty) ...[
                const SizedBox(height: 16),
                const Text(
                  '投资标',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: result.tickers.map((t) {
                    final label = t.name.isNotEmpty ? '${t.name}（${t.code}）' : t.code;
                    return Chip(
                      avatar: const Icon(Icons.show_chart, size: 16),
                      label: Text(label),
                      backgroundColor: Colors.blue.withValues(alpha: 0.1),
                    );
                  }).toList(),
                ),
              ],
              const SizedBox(height: 16),

              // Highlights
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    '重点新闻',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  TextButton.icon(
                    onPressed: () {
                      // Copy all highlights as formatted text
                      final allText = result.highlights.map((h) {
                        final tickersText = h.tickers.map((t) => t.name.isNotEmpty ? '${t.name}（${t.code}）' : t.code).join(', ');
                        return '【${h.title}】\n来源: ${h.source}\n'
                            '${h.url != null ? '链接: ${h.url}\n' : ''}'
                            '\n${h.summary}'
                            '${tickersText.isNotEmpty ? '\n\n标的信息: $tickersText' : ''}';
                      }).join('\n\n---\n\n');
                      _copyToClipboard(allText);
                    },
                    icon: const Icon(Icons.copy_all, size: 18),
                    label: const Text('复制全部'),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              ...result.highlights.map((h) => _buildHighlightCard(h)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildHighlightCard(Highlight highlight) {
    final tickersText = highlight.tickers.map((t) => t.name.isNotEmpty ? '${t.name}（${t.code}）' : t.code).join(', ');
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    highlight.title,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.copy, size: 20),
                  onPressed: () => _copyToClipboard(
                    '【${highlight.title}】\n来源: ${highlight.source}\n'
                    '${highlight.url != null ? '链接: ${highlight.url}\n' : ''}'
                    '\n${highlight.summary}'
                    '${tickersText.isNotEmpty ? '\n\n标的信息: $tickersText' : ''}'
                  ),
                  tooltip: '复制此条新闻',
                ),
                _buildImportanceChip(highlight.importance),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              highlight.source,
              style: TextStyle(color: Colors.grey[600], fontSize: 12),
            ),
            if (highlight.url != null && highlight.url!.isNotEmpty) ...[
              const SizedBox(height: 4),
              GestureDetector(
                onTap: () => _openUrl(highlight.url!),
                child: Text(
                  highlight.url!,
                  style: const TextStyle(color: Colors.blue, fontSize: 12, decoration: TextDecoration.underline),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
            const SizedBox(height: 8),
            Text(highlight.summary),
            if (highlight.tickers.isNotEmpty) ...[
              const SizedBox(height: 8),
              Wrap(
                spacing: 4,
                children: highlight.tickers.map((t) {
                  final label = t.name.isNotEmpty ? '${t.name}（${t.code}）' : t.code;
                  return Chip(
                    label: Text(label, style: const TextStyle(fontSize: 11)),
                    padding: EdgeInsets.zero,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  );
                }).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildImportanceChip(String importance) {
    Color color;
    switch (importance) {
      case 'high':
        color = Colors.red;
        break;
      case 'medium':
        color = Colors.orange;
        break;
      default:
        color = Colors.green;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        importance,
        style: TextStyle(color: color, fontSize: 12),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../data/models/saved_summary.dart';
import '../../data/models/summary_result.dart';

class SummaryResultScreen extends StatelessWidget {
  final SavedSummary savedSummary;

  const SummaryResultScreen({super.key, required this.savedSummary});

  void _copyToClipboard(BuildContext context, String text) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('已复制到剪贴板')),
    );
  }

  Future<void> _openUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final result = savedSummary.result;

    return Scaffold(
      appBar: AppBar(
        title: Text(savedSummary.title),
      ),
      body: ListView(
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
                        onPressed: () => _copyToClipboard(context, result.summary),
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
                  final allText = result.highlights.map((h) {
                    final tickersText = h.tickers.map((t) => t.name.isNotEmpty ? '${t.name}（${t.code}）' : t.code).join(', ');
                    return '【${h.title}】\n来源: ${h.source}\n'
                        '${h.url != null ? '链接: ${h.url}\n' : ''}'
                        '\n${h.summary}'
                        '${tickersText.isNotEmpty ? '\n\n标的信息: $tickersText' : ''}';
                  }).join('\n\n---\n\n');
                  _copyToClipboard(context, allText);
                },
                icon: const Icon(Icons.copy_all, size: 18),
                label: const Text('复制全部'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ...result.highlights.map((h) => _buildHighlightCard(context, h)),
        ],
      ),
    );
  }

  Widget _buildHighlightCard(BuildContext context, Highlight highlight) {
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
                  onPressed: () {
                    final tickersText = highlight.tickers.map((t) => t.name.isNotEmpty ? '${t.name}（${t.code}）' : t.code).join(', ');
                    _copyToClipboard(
                      context,
                      '【${highlight.title}】\n来源: ${highlight.source}\n'
                      '${highlight.url != null ? '链接: ${highlight.url}\n' : ''}'
                      '\n${highlight.summary}'
                      '${tickersText.isNotEmpty ? '\n\n标的信息: $tickersText' : ''}',
                    );
                  },
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

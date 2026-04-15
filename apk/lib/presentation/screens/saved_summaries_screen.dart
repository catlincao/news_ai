import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/models/saved_summary.dart';
import '../blocs/saved_summary/saved_summary_bloc.dart';
import '../blocs/saved_summary/saved_summary_event.dart';
import '../blocs/saved_summary/saved_summary_state.dart';
import 'summary_result_screen.dart';

class SavedSummariesScreen extends StatelessWidget {
  const SavedSummariesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('收藏摘要'),
      ),
      body: BlocBuilder<SavedSummaryBloc, SavedSummaryState>(
        builder: (context, state) {
          if (state.status == SavedSummaryStatus.loading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (state.summaries.isEmpty) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.bookmark_border, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text('暂无收藏', style: TextStyle(color: Colors.grey)),
                  SizedBox(height: 8),
                  Text(
                    '生成摘要后点击收藏按钮保存',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: state.summaries.length,
            itemBuilder: (context, index) {
              final summary = state.summaries[index];
              return _SavedSummaryCard(
                summary: summary,
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => SummaryResultScreen(savedSummary: summary),
                    ),
                  );
                },
                onDelete: () {
                  showDialog(
                    context: context,
                    builder: (ctx) => AlertDialog(
                      title: const Text('确认删除'),
                      content: const Text('确定要删除这条收藏吗？'),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(ctx),
                          child: const Text('取消'),
                        ),
                        TextButton(
                          onPressed: () {
                            Navigator.pop(ctx);
                            context.read<SavedSummaryBloc>().add(DeleteSavedSummary(summary.id));
                          },
                          child: const Text('删除', style: TextStyle(color: Colors.red)),
                        ),
                      ],
                    ),
                  );
                },
              );
            },
          );
        },
      ),
    );
  }
}

class _SavedSummaryCard extends StatelessWidget {
  final SavedSummary summary;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const _SavedSummaryCard({
    required this.summary,
    required this.onTap,
    required this.onDelete,
  });

  String _formatDate(DateTime dt) {
    return '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')} '
        '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }

  void _copyToClipboard(BuildContext context, String text) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('已复制到剪贴板')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final result = summary.result;
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      summary.title,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete_outline, size: 20),
                    onPressed: onDelete,
                    color: Colors.grey,
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                '收藏时间: ${_formatDate(summary.savedAt)}',
                style: TextStyle(color: Colors.grey[600], fontSize: 12),
              ),
              const SizedBox(height: 8),
              Text(
                result.summary,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 13),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Chip(
                    label: Text('${result.highlights.length}条重点'),
                    padding: EdgeInsets.zero,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  const SizedBox(width: 8),
                  Chip(
                    label: Text(result.sentiment),
                    padding: EdgeInsets.zero,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.copy, size: 18),
                    onPressed: () => _copyToClipboard(context, result.summary),
                    tooltip: '复制摘要',
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

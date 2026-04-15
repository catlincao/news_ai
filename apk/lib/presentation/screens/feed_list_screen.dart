import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../blocs/feed/feed_bloc.dart';
import '../blocs/feed/feed_event.dart';
import '../blocs/feed/feed_state.dart';
import '../../data/models/feed.dart';

class FeedListScreen extends StatelessWidget {
  final VoidCallback onFeedsSelected;

  const FeedListScreen({super.key, required this.onFeedsSelected});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('选择订阅源'),
        actions: [
          TextButton(
            onPressed: () {
              context.read<FeedBloc>().add(const SelectAllFeeds());
            },
            child: const Text('全选'),
          ),
          TextButton(
            onPressed: () {
              context.read<FeedBloc>().add(const DeselectAllFeeds());
            },
            child: const Text('取消'),
          ),
        ],
      ),
      body: BlocBuilder<FeedBloc, FeedState>(
        builder: (context, state) {
          if (state.status == FeedStatus.loading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (state.status == FeedStatus.failure) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    '加载失败',
                    style: TextStyle(color: Colors.red[700]),
                  ),
                  const SizedBox(height: 8),
                  Text(state.errorMessage ?? '未知错误'),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      context.read<FeedBloc>().add(const LoadFeeds());
                    },
                    child: const Text('重试'),
                  ),
                ],
              ),
            );
          }

          if (state.feeds.isEmpty) {
            return const Center(
              child: Text('没有订阅源，请先在 Miniflux 中添加订阅'),
            );
          }

          return RefreshIndicator(
            onRefresh: () async {
              final bloc = context.read<FeedBloc>();
              bloc.add(const RefreshFeeds());
              // Wait for the refresh to complete (status changes from loading to success/failure)
              await bloc.stream.firstWhere((s) => s.status != FeedStatus.loading);
            },
            child: ListView.builder(
              itemCount: state.feeds.length,
              itemBuilder: (context, index) {
                final feed = state.feeds[index];
                final isSelected = state.selectedFeedIds.contains(feed.id);
                final hasFullContent = state.feedsWithFullContent.contains(feed.id);

                return FeedTile(
                  feed: feed,
                  isSelected: isSelected,
                  hasFullContent: hasFullContent,
                  onTap: () {
                    context.read<FeedBloc>().add(ToggleFeedSelection(feed.id));
                  },
                  onFullContentToggle: () {
                    context.read<FeedBloc>().add(ToggleFeedFullContent(feed.id));
                  },
                );
              },
            ),
          );
        },
      ),
      bottomNavigationBar: BlocBuilder<FeedBloc, FeedState>(
        builder: (context, state) {
          return SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (state.feedsWithFullContent.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text(
                        '将扩展 ${state.feedsWithFullContent.length} 个订阅源的全文',
                        style: TextStyle(color: Colors.grey[600], fontSize: 12),
                      ),
                    ),
                  ElevatedButton(
                    onPressed: state.selectedFeedIds.isEmpty
                        ? null
                        : () {
                            onFeedsSelected();
                          },
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: Text(
                      '生成摘要 (${state.selectedFeedIds.length} 个订阅源)',
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class FeedTile extends StatelessWidget {
  final Feed feed;
  final bool isSelected;
  final bool hasFullContent;
  final VoidCallback onTap;
  final VoidCallback onFullContentToggle;

  const FeedTile({
    super.key,
    required this.feed,
    required this.isSelected,
    required this.hasFullContent,
    required this.onTap,
    required this.onFullContentToggle,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ListTile(
          leading: Icon(
            isSelected ? Icons.check_circle : Icons.circle_outlined,
            color: isSelected ? Colors.green : Colors.grey,
          ),
          title: Text(feed.title),
          subtitle: feed.category.isNotEmpty
              ? Text('${feed.category}  •  ${feed.unreadCount}篇未读')
              : Text('${feed.unreadCount}篇未读'),
          trailing: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (feed.unreadCount > 0)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.red.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${feed.unreadCount}',
                    style: const TextStyle(
                      color: Colors.red,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              const SizedBox(width: 8),
              Tooltip(
                message: '通过源链接扩展内容',
                child: Checkbox(
                  value: hasFullContent,
                  onChanged: (_) => onFullContentToggle(),
                ),
              ),
            ],
          ),
          onTap: onTap,
        ),
        if (hasFullContent && isSelected)
          Padding(
            padding: const EdgeInsets.only(left: 56, right: 16, bottom: 8),
            child: Row(
              children: [
                Icon(Icons.link, size: 14, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(
                  '将从源URL获取全文',
                  style: TextStyle(color: Colors.grey[600], fontSize: 12),
                ),
              ],
            ),
          ),
      ],
    );
  }
}

import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../core/config/app_config.dart';
import '../../../data/models/feed.dart';
import '../../../data/services/miniflux_service.dart';
import 'feed_event.dart';
import 'feed_state.dart';

class FeedBloc extends Bloc<FeedEvent, FeedState> {
  final MinifluxService _minifluxService;
  final AppConfig _config;

  FeedBloc({
    required MinifluxService minifluxService,
    required AppConfig config,
  })  : _minifluxService = minifluxService,
        _config = config,
        super(FeedState(feedsWithFullContent: config.feedsWithFullContent)) {
    on<LoadFeeds>(_onLoadFeeds);
    on<RefreshFeeds>(_onRefreshFeeds);
    on<ToggleFeedSelection>(_onToggleFeedSelection);
    on<SelectAllFeeds>(_onSelectAllFeeds);
    on<DeselectAllFeeds>(_onDeselectAllFeeds);
    on<ToggleFeedFullContent>(_onToggleFeedFullContent);
  }

  Future<void> _onLoadFeeds(LoadFeeds event, Emitter<FeedState> emit) async {
    print('[FeedBloc] _onLoadFeeds started');
    emit(state.copyWith(status: FeedStatus.loading));
    try {
      print('[FeedBloc] Fetching feeds from Miniflux...');
      final feeds = await _minifluxService.getFeeds();
      print('[FeedBloc] Got ${feeds.length} feeds');

      // Try to fetch unread counts
      List<Feed> feedsWithCounts = feeds;
      try {
        final feedIds = feeds.map((f) => f.id).toList();
        final counts = await _minifluxService.getAllFeedsUnreadCounts(feedIds);
        feedsWithCounts = feeds.map((feed) {
          return feed.copyWith(unreadCount: counts[feed.id] ?? 0);
        }).toList();
        print('[FeedBloc] Got unread counts for ${counts.length} feeds');
      } catch (e) {
        print('[FeedBloc] Failed to fetch unread counts: $e');
        // Continue without counts
      }

      print('[FeedBloc] Emitting success with ${feedsWithCounts.length} feeds');
      emit(state.copyWith(
        status: FeedStatus.success,
        feeds: feedsWithCounts,
      ));
    } catch (e) {
      print('[FeedBloc] Error loading feeds: $e');
      emit(state.copyWith(
        status: FeedStatus.failure,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onRefreshFeeds(RefreshFeeds event, Emitter<FeedState> emit) async {
    emit(state.copyWith(status: FeedStatus.loading));
    try {
      final feeds = await _minifluxService.getFeeds();
      // Fetch unread counts
      final feedIds = feeds.map((f) => f.id).toList();
      try {
        final counts = await _minifluxService.getAllFeedsUnreadCounts(feedIds);
        final feedsWithCounts = feeds.map((feed) {
          return feed.copyWith(unreadCount: counts[feed.id] ?? 0);
        }).toList();
        emit(state.copyWith(
          status: FeedStatus.success,
          feeds: feedsWithCounts,
        ));
      } catch (_) {
        // If fetching counts fails, just show feeds without counts
        emit(state.copyWith(
          status: FeedStatus.success,
          feeds: feeds,
        ));
      }
    } catch (e) {
      emit(state.copyWith(
        status: FeedStatus.failure,
        errorMessage: e.toString(),
      ));
    }
  }

  void _onToggleFeedSelection(ToggleFeedSelection event, Emitter<FeedState> emit) {
    final newSelected = Set<int>.from(state.selectedFeedIds);
    if (newSelected.contains(event.feedId)) {
      newSelected.remove(event.feedId);
    } else {
      newSelected.add(event.feedId);
    }
    emit(state.copyWith(selectedFeedIds: newSelected));
  }

  void _onSelectAllFeeds(SelectAllFeeds event, Emitter<FeedState> emit) {
    final allIds = state.feeds.map((f) => f.id).toSet();
    emit(state.copyWith(selectedFeedIds: allIds));
  }

  void _onDeselectAllFeeds(DeselectAllFeeds event, Emitter<FeedState> emit) {
    emit(state.copyWith(selectedFeedIds: {}));
  }

  void _onToggleFeedFullContent(ToggleFeedFullContent event, Emitter<FeedState> emit) {
    final newFullContent = Set<int>.from(state.feedsWithFullContent);
    if (newFullContent.contains(event.feedId)) {
      newFullContent.remove(event.feedId);
    } else {
      newFullContent.add(event.feedId);
    }
    // Save to persistent storage
    _config.setFeedsWithFullContent(newFullContent);
    emit(state.copyWith(feedsWithFullContent: newFullContent));
  }
}

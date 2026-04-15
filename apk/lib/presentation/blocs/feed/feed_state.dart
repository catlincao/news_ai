import 'package:equatable/equatable.dart';
import '../../../data/models/feed.dart';

enum FeedStatus { initial, loading, success, failure }

class FeedState extends Equatable {
  final FeedStatus status;
  final List<Feed> feeds;
  final Set<int> selectedFeedIds;
  final Set<int> feedsWithFullContent;  // Feeds where full content fetching is enabled
  final String? errorMessage;

  const FeedState({
    this.status = FeedStatus.initial,
    this.feeds = const [],
    this.selectedFeedIds = const {},
    this.feedsWithFullContent = const {},
    this.errorMessage,
  });

  FeedState copyWith({
    FeedStatus? status,
    List<Feed>? feeds,
    Set<int>? selectedFeedIds,
    Set<int>? feedsWithFullContent,
    String? errorMessage,
  }) {
    return FeedState(
      status: status ?? this.status,
      feeds: feeds ?? this.feeds,
      selectedFeedIds: selectedFeedIds ?? this.selectedFeedIds,
      feedsWithFullContent: feedsWithFullContent ?? this.feedsWithFullContent,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [status, feeds, selectedFeedIds, feedsWithFullContent, errorMessage];
}

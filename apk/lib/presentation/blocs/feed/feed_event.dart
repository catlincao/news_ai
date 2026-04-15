import 'package:equatable/equatable.dart';

abstract class FeedEvent extends Equatable {
  const FeedEvent();

  @override
  List<Object?> get props => [];
}

class LoadFeeds extends FeedEvent {
  const LoadFeeds();
}

class RefreshFeeds extends FeedEvent {
  const RefreshFeeds();
}

class ToggleFeedSelection extends FeedEvent {
  final int feedId;

  const ToggleFeedSelection(this.feedId);

  @override
  List<Object?> get props => [feedId];
}

class SelectAllFeeds extends FeedEvent {
  const SelectAllFeeds();
}

class DeselectAllFeeds extends FeedEvent {
  const DeselectAllFeeds();
}

class ToggleFeedFullContent extends FeedEvent {
  final int feedId;

  const ToggleFeedFullContent(this.feedId);

  @override
  List<Object?> get props => [feedId];
}

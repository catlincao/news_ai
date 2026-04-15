import 'package:equatable/equatable.dart';
import '../../../data/models/entry.dart';

abstract class SummaryEvent extends Equatable {
  const SummaryEvent();

  @override
  List<Object?> get props => [];
}

class LoadEntries extends SummaryEvent {
  final List<int> feedIds;
  final int limit;

  const LoadEntries({required this.feedIds, this.limit = 20});

  @override
  List<Object?> get props => [feedIds, limit];
}

class GenerateSummary extends SummaryEvent {
  final List<Entry> entries;

  const GenerateSummary({required this.entries});

  @override
  List<Object?> get props => [entries];
}

class FetchFullContent extends SummaryEvent {
  final List<Entry> entries;
  final Set<int> feedsToFetchFullContent;

  const FetchFullContent({
    required this.entries,
    required this.feedsToFetchFullContent,
  });

  @override
  List<Object?> get props => [entries, feedsToFetchFullContent];
}

class ClearSummary extends SummaryEvent {
  const ClearSummary();
}

class MarkEntriesRead extends SummaryEvent {
  final List<int> entryIds;

  const MarkEntriesRead({required this.entryIds});

  @override
  List<Object?> get props => [entryIds];
}

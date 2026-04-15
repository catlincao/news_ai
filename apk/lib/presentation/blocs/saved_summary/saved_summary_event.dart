import 'package:equatable/equatable.dart';
import '../../../data/models/summary_result.dart';

abstract class SavedSummaryEvent extends Equatable {
  const SavedSummaryEvent();

  @override
  List<Object?> get props => [];
}

class LoadSavedSummaries extends SavedSummaryEvent {
  const LoadSavedSummaries();
}

class SaveSummary extends SavedSummaryEvent {
  final SummaryResult result;
  final List<int> feedIds;

  const SaveSummary({required this.result, required this.feedIds});

  @override
  List<Object?> get props => [result, feedIds];
}

class DeleteSavedSummary extends SavedSummaryEvent {
  final String id;

  const DeleteSavedSummary(this.id);

  @override
  List<Object?> get props => [id];
}

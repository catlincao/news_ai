import 'package:equatable/equatable.dart';
import '../../../data/models/saved_summary.dart';

enum SavedSummaryStatus { initial, loading, success, failure }

class SavedSummaryState extends Equatable {
  final SavedSummaryStatus status;
  final List<SavedSummary> summaries;
  final String? errorMessage;

  const SavedSummaryState({
    this.status = SavedSummaryStatus.initial,
    this.summaries = const [],
    this.errorMessage,
  });

  SavedSummaryState copyWith({
    SavedSummaryStatus? status,
    List<SavedSummary>? summaries,
    String? errorMessage,
  }) {
    return SavedSummaryState(
      status: status ?? this.status,
      summaries: summaries ?? this.summaries,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [status, summaries, errorMessage];
}

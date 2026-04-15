import 'package:equatable/equatable.dart';
import '../../../data/models/entry.dart';
import '../../../data/models/summary_result.dart';

enum SummaryStatus { initial, loading, generating, success, failure }

class SummaryState extends Equatable {
  final SummaryStatus status;
  final List<Entry> entries;
  final SummaryResult? result;
  final String? errorMessage;
  final double progress;

  const SummaryState({
    this.status = SummaryStatus.initial,
    this.entries = const [],
    this.result,
    this.errorMessage,
    this.progress = 0.0,
  });

  SummaryState copyWith({
    SummaryStatus? status,
    List<Entry>? entries,
    SummaryResult? result,
    String? errorMessage,
    double? progress,
  }) {
    return SummaryState(
      status: status ?? this.status,
      entries: entries ?? this.entries,
      result: result ?? this.result,
      errorMessage: errorMessage,
      progress: progress ?? this.progress,
    );
  }

  @override
  List<Object?> get props => [status, entries, result, errorMessage, progress];
}

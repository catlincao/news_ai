import 'package:equatable/equatable.dart';
import 'summary_result.dart';

class SavedSummary extends Equatable {
  final String id;
  final String title;
  final SummaryResult result;
  final List<int> feedIds;
  final DateTime savedAt;

  const SavedSummary({
    required this.id,
    required this.title,
    required this.result,
    required this.feedIds,
    required this.savedAt,
  });

  factory SavedSummary.fromJson(Map<String, dynamic> json) {
    return SavedSummary(
      id: json['id'] as String,
      title: json['title'] as String,
      result: SummaryResult.fromJson(json['result'] as Map<String, dynamic>),
      feedIds: (json['feed_ids'] as List<dynamic>).cast<int>(),
      savedAt: DateTime.parse(json['saved_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'result': result.toJson(),
      'feed_ids': feedIds,
      'saved_at': savedAt.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [id, title, result, feedIds, savedAt];
}

import 'package:equatable/equatable.dart';

class Entry extends Equatable {
  final int id;
  final String title;
  final String url;
  final DateTime publishedAt;
  final String summary;
  final String? content;
  final int feedId;
  final String feedTitle;

  const Entry({
    required this.id,
    required this.title,
    required this.url,
    required this.publishedAt,
    required this.summary,
    this.content,
    this.feedId = 0,
    this.feedTitle = '',
  });

  factory Entry.fromJson(Map<String, dynamic> json) {
    return Entry(
      id: json['id'] as int,
      title: json['title'] as String? ?? '',
      url: json['url'] as String? ?? '',
      publishedAt: DateTime.tryParse(json['published_at'] as String? ?? '') ?? DateTime.now(),
      summary: json['summary'] as String? ?? '',
      content: json['content'] as String?,
      feedId: json['feed_id'] as int? ?? 0,
      feedTitle: (json['feed'] as Map<String, dynamic>?)?['title'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'url': url,
      'published_at': publishedAt.toIso8601String(),
      'summary': summary,
      'content': content,
      'feed_id': feedId,
      'feed_title': feedTitle,
    };
  }

  Entry copyWith({
    int? id,
    String? title,
    String? url,
    DateTime? publishedAt,
    String? summary,
    String? content,
    int? feedId,
    String? feedTitle,
  }) {
    return Entry(
      id: id ?? this.id,
      title: title ?? this.title,
      url: url ?? this.url,
      publishedAt: publishedAt ?? this.publishedAt,
      summary: summary ?? this.summary,
      content: content ?? this.content,
      feedId: feedId ?? this.feedId,
      feedTitle: feedTitle ?? this.feedTitle,
    );
  }

  @override
  List<Object?> get props => [id, title, url, publishedAt, summary, content, feedId, feedTitle];
}

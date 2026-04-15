import 'package:equatable/equatable.dart';

class Feed extends Equatable {
  final int id;
  final String title;
  final String category;
  final String url;
  final bool enabled;
  final int unreadCount;

  const Feed({
    required this.id,
    required this.title,
    this.category = '',
    this.url = '',
    this.enabled = true,
    this.unreadCount = 0,
  });

  factory Feed.fromJson(Map<String, dynamic> json) {
    return Feed(
      id: json['id'] as int,
      title: json['title'] as String? ?? '',
      category: (json['category'] as Map<String, dynamic>?)?['title'] as String? ?? '',
      url: json['url'] as String? ?? '',
      enabled: json['enabled'] as bool? ?? true,
      unreadCount: json['unread_count'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'category': category,
      'url': url,
      'enabled': enabled,
      'unread_count': unreadCount,
    };
  }

  @override
  List<Object?> get props => [id, title, category, url, enabled, unreadCount];

  Feed copyWith({
    int? id,
    String? title,
    String? category,
    String? url,
    bool? enabled,
    int? unreadCount,
  }) {
    return Feed(
      id: id ?? this.id,
      title: title ?? this.title,
      category: category ?? this.category,
      url: url ?? this.url,
      enabled: enabled ?? this.enabled,
      unreadCount: unreadCount ?? this.unreadCount,
    );
  }
}

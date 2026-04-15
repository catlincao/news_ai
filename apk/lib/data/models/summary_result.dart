import 'package:equatable/equatable.dart';

class Ticker extends Equatable {
  final String code;
  final String name;

  const Ticker({required this.code, required this.name});

  factory Ticker.fromJson(Map<String, dynamic> json) {
    return Ticker(
      code: json['code'] as String? ?? '',
      name: json['name'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() => {'code': code, 'name': name};

  @override
  List<Object?> get props => [code, name];
}

class Highlight extends Equatable {
  final String title;
  final String source;
  final String? url;
  final String summary;
  final String importance;
  final List<Ticker> tickers;

  const Highlight({
    required this.title,
    required this.source,
    this.url,
    required this.summary,
    required this.importance,
    this.tickers = const [],
  });

  factory Highlight.fromJson(Map<String, dynamic> json) {
    List<Ticker> tickers = [];
    final tickersData = json['tickers'] as List<dynamic>?;
    if (tickersData != null) {
      for (final t in tickersData) {
        if (t is Map<String, dynamic>) {
          tickers.add(Ticker.fromJson(t));
        } else if (t is String) {
          // Handle case where ticker is just a string code
          tickers.add(Ticker(code: t, name: ''));
        }
      }
    }
    return Highlight(
      title: json['title'] as String? ?? '',
      source: json['source'] as String? ?? '',
      url: json['url'] as String?,
      summary: json['summary'] as String? ?? '',
      importance: json['importance'] as String? ?? 'medium',
      tickers: tickers,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'source': source,
      'url': url,
      'summary': summary,
      'importance': importance,
      'tickers': tickers.map((e) => e.toJson()).toList(),
    };
  }

  @override
  List<Object?> get props => [title, source, url, summary, importance, tickers];
}

class SummaryResult extends Equatable {
  final String summary;
  final List<Highlight> highlights;
  final List<Ticker> tickers;
  final List<String> keywords;
  final String sentiment;
  final DateTime generatedAt;

  const SummaryResult({
    required this.summary,
    required this.highlights,
    this.tickers = const [],
    this.keywords = const [],
    required this.sentiment,
    required this.generatedAt,
  });

  factory SummaryResult.fromJson(Map<String, dynamic> json) {
    List<Ticker> tickers = [];
    final tickersData = json['tickers'] as List<dynamic>?;
    if (tickersData != null) {
      for (final t in tickersData) {
        if (t is Map<String, dynamic>) {
          tickers.add(Ticker.fromJson(t));
        } else if (t is String) {
          tickers.add(Ticker(code: t, name: ''));
        }
      }
    }
    return SummaryResult(
      summary: json['summary'] as String? ?? '',
      highlights: (json['highlights'] as List<dynamic>?)
              ?.map((e) => Highlight.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      tickers: tickers,
      keywords:
          (json['keywords'] as List<dynamic>?)?.cast<String>() ?? [],
      sentiment: json['sentiment'] as String? ?? 'neutral',
      generatedAt: DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'summary': summary,
      'highlights': highlights.map((e) => e.toJson()).toList(),
      'tickers': tickers.map((e) => e.toJson()).toList(),
      'keywords': keywords,
      'sentiment': sentiment,
      'generated_at': generatedAt.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [summary, highlights, tickers, keywords, sentiment, generatedAt];
}

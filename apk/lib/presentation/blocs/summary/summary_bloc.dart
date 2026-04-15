import 'package:dio/dio.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../core/config/app_config.dart';
import '../../../data/models/entry.dart';
import '../../../data/services/miniflux_service.dart';
import '../../../data/services/ai_service.dart';
import '../../../utils/content_extractor.dart';
import 'summary_event.dart';
import 'summary_state.dart';

class SummaryBloc extends Bloc<SummaryEvent, SummaryState> {
  final MinifluxService _minifluxService;
  final AIService _aiService;
  final AppConfig _config;

  SummaryBloc({
    required MinifluxService minifluxService,
    required AIService aiService,
    required AppConfig config,
  })  : _minifluxService = minifluxService,
        _aiService = aiService,
        _config = config,
        super(const SummaryState()) {
    on<LoadEntries>(_onLoadEntries);
    on<GenerateSummary>(_onGenerateSummary);
    on<ClearSummary>(_onClearSummary);
    on<MarkEntriesRead>(_onMarkEntriesRead);
  }

  Future<void> _onLoadEntries(LoadEntries event, Emitter<SummaryState> emit) async {
    print('[SummaryBloc] _onLoadEntries called with feedIds: ${event.feedIds}, limit: ${event.limit}');
    emit(state.copyWith(status: SummaryStatus.loading, progress: 0.0));
    try {
      print('[SummaryBloc] Fetching entries from Miniflux...');
      final entries = await _minifluxService.getEntries(
        feedIds: event.feedIds,
        limit: event.limit,
      );
      print('[SummaryBloc] Got ${entries.length} entries');
      final feedIds = entries.map((e) => e.feedId).toSet();
      print('[SummaryBloc] Entry feedIds: $feedIds');

      // Check which feeds need full content fetching
      final feedsWithFullContent = _config.feedsWithFullContent;
      final entriesNeedingFullContent = <Entry>[];
      final entriesWithMinifluxContent = <Entry>[];

      for (final entry in entries) {
        if (feedsWithFullContent.contains(entry.feedId) &&
            entry.summary.length < 100 &&
            entry.url.isNotEmpty) {
          entriesNeedingFullContent.add(entry);
        } else {
          entriesWithMinifluxContent.add(entry);
        }
      }

      // Fetch full content for entries that need it
      if (entriesNeedingFullContent.isNotEmpty) {
        final enrichedEntries = await _enrichEntriesWithFullContent(entriesNeedingFullContent);
        entriesWithMinifluxContent.addAll(enrichedEntries);
      }

      // Sort by published date descending
      entriesWithMinifluxContent.sort((a, b) => b.publishedAt.compareTo(a.publishedAt));

      emit(state.copyWith(
        status: SummaryStatus.success,
        entries: entriesWithMinifluxContent,
        progress: 0.5,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: SummaryStatus.failure,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<List<Entry>> _enrichEntriesWithFullContent(List<Entry> entries) async {
    final updatedEntries = <Entry>[];

    for (final entry in entries) {
      String? fullContent;

      // Try direct URL fetch first
      if (entry.url.isNotEmpty) {
        try {
          fullContent = await _fetchFullContent(entry.url);
        } catch (_) {}
      }

      // Fall back to Miniflux content
      if (fullContent == null || fullContent.isEmpty) {
        try {
          final minifluxContent = await _minifluxService.getEntryContent(entry.id);
          if (minifluxContent.isNotEmpty) {
            fullContent = ContentExtractor.extractReadableContent(minifluxContent);
          }
        } catch (_) {}
      }

      if (fullContent != null && fullContent.isNotEmpty) {
        updatedEntries.add(entry.copyWith(content: fullContent));
      } else {
        updatedEntries.add(entry);
      }
    }

    return updatedEntries;
  }

  Future<String> _fetchFullContent(String url) async {
    try {
      final dio = Dio();
      final response = await dio.get(
        url,
        options: Options(
          headers: {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          },
          responseType: ResponseType.plain,
          followRedirects: true,
        ),
      );
      if (response.statusCode == 200) {
        return ContentExtractor.extractReadableContent(response.data as String);
      }
    } catch (_) {}
    return '';
  }

  Future<void> _onGenerateSummary(GenerateSummary event, Emitter<SummaryState> emit) async {
    emit(state.copyWith(status: SummaryStatus.generating, progress: 0.6));
    try {
      final result = await _aiService.generateSummary(event.entries);

      // Mark entries as read after successfully generating summary
      final entryIds = event.entries.map((e) => e.id).toList();
      try {
        await _minifluxService.markEntriesAsRead(entryIds);
      } catch (_) {
        // Ignore errors in marking as read
      }

      emit(state.copyWith(
        status: SummaryStatus.success,
        result: result,
        progress: 1.0,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: SummaryStatus.failure,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onMarkEntriesRead(MarkEntriesRead event, Emitter<SummaryState> emit) async {
    try {
      await _minifluxService.markEntriesAsRead(event.entryIds);
    } catch (_) {
      // Ignore errors
    }
  }

  void _onClearSummary(ClearSummary event, Emitter<SummaryState> emit) {
    emit(const SummaryState());
  }
}

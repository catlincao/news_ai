import 'package:dio/dio.dart';
import '../models/feed.dart';
import '../models/entry.dart';

class MinifluxService {
  final Dio _dio;
  final String baseUrl;
  final String apiKey;

  MinifluxService({
    required this.baseUrl,
    required this.apiKey,
  }) : _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          headers: {
            'X-Auth-Token': apiKey,
            'Content-Type': 'application/json',
          },
          connectTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 30),
        ));

  Future<List<Feed>> getFeeds() async {
    try {
      final response = await _dio.get('/v1/feeds');
      final List<dynamic> data = response.data as List<dynamic>;
      return data.map((e) => Feed.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw Exception('Failed to fetch feeds: ${e.message}');
    }
  }

  Future<int> getFeedUnreadCount(int feedId) async {
    try {
      final response = await _dio.get(
        '/v1/feeds/$feedId/entries',
        queryParameters: {
          'status': 'unread',
          'limit': 1,
        },
      );
      final data = response.data as Map<String, dynamic>;
      return data['total'] as int? ?? 0;
    } catch (_) {
      return 0;
    }
  }

  Future<Map<int, int>> getAllFeedsUnreadCounts(List<int> feedIds) async {
    final counts = <int, int>{};
    // Fetch counts in parallel for performance
    final futures = feedIds.map((id) async {
      counts[id] = await getFeedUnreadCount(id);
    });
    await Future.wait(futures);
    return counts;
  }

  Future<List<Entry>> getEntries({
    List<int>? feedIds,
    int limit = 100,
    String status = 'unread',
  }) async {
    print('[MinifluxService] getEntries called with feedIds=$feedIds, limit=$limit, status=$status');
    try {
      List<Entry> allEntries = [];

      if (feedIds == null || feedIds.isEmpty) {
        // Get all feeds first
        print('[MinifluxService] feedIds is empty, fetching all feeds');
        final feeds = await getFeeds();
        feedIds = feeds.map((f) => f.id).toList();
        print('[MinifluxService] Fetched all feeds, feedIds now = $feedIds');
      }

      for (final feedId in feedIds) {
        try {
          print('[MinifluxService] Fetching entries for feed $feedId...');
          final response = await _dio.get(
            '/v1/feeds/$feedId/entries',
            queryParameters: {
              'status': status,
              'order': 'created_at',
              'direction': 'desc',
              'limit': limit,
            },
          );

          // Response is {"total": xx, "entries": [...]}
          final data = response.data as Map<String, dynamic>;
          final entriesList = data['entries'] as List<dynamic>? ?? [];
          final entries = entriesList.map((e) {
            final entry = Entry.fromJson(e as Map<String, dynamic>);
            return entry.copyWith(feedId: feedId);
          }).toList();
          print('[MinifluxService] Got ${entries.length} entries for feed $feedId');
          allEntries.addAll(entries);
        } on DioException catch (e) {
          print('[MinifluxService] Failed to fetch entries for feed $feedId: ${e.message}');
          // Skip feeds that fail
          continue;
        }
      }

      // Sort by published date descending
      allEntries.sort((a, b) => b.publishedAt.compareTo(a.publishedAt));
      print('[MinifluxService] getEntries returning ${allEntries.length} total entries');
      return allEntries;
    } on DioException catch (e) {
      throw Exception('Failed to fetch entries: ${e.message}');
    }
  }

  Future<String> getEntryContent(int entryId) async {
    try {
      final response = await _dio.get('/v1/entries/$entryId/content');
      return response.data as String? ?? '';
    } on DioException catch (e) {
      throw Exception('Failed to fetch entry content: ${e.message}');
    }
  }

  Future<void> markEntriesAsRead(List<int> entryIds) async {
    try {
      await _dio.put(
        '/v1/entries',
        data: {
          'entry_ids': entryIds,
          'status': 'read',
        },
      );
    } on DioException catch (e) {
      throw Exception('Failed to mark entries as read: ${e.message}');
    }
  }

  Future<bool> testConnection() async {
    try {
      print('Testing Miniflux connection...');
      print('Using X-Auth-Token header');
      final response = await _dio.get('/v1/feeds');
      print('Response status: ${response.statusCode}');
      return response.statusCode == 200;
    } on DioException catch (e) {
      print('DioException type: ${e.type}');
      print('DioException message: ${e.message}');
      print('DioException response: ${e.response}');
      return false;
    } catch (e) {
      print('Miniflux connection test failed: $e');
      return false;
    }
  }
}

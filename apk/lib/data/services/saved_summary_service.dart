import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/saved_summary.dart';

class SavedSummaryService {
  static const String _key = 'saved_summaries';
  final SharedPreferences _prefs;

  SavedSummaryService(this._prefs);

  List<SavedSummary> getAll() {
    final str = _prefs.getString(_key);
    if (str == null || str.isEmpty) return [];

    try {
      final list = jsonDecode(str) as List<dynamic>;
      return list.map((e) => SavedSummary.fromJson(e as Map<String, dynamic>)).toList()
        ..sort((a, b) => b.savedAt.compareTo(a.savedAt));
    } catch (_) {
      return [];
    }
  }

  bool exists(List<int> feedIds, DateTime dateTime) {
    final title = generateTitle(feedIds, dateTime);
    final list = getAll();
    return list.any((s) => s.title == title);
  }

  Future<void> save(SavedSummary summary) async {
    final list = getAll();
    // Check for duplicate
    if (list.any((s) => s.title == summary.title)) {
      throw Exception('该摘要已收藏');
    }
    list.insert(0, summary);
    await _saveList(list);
  }

  Future<void> delete(String id) async {
    final list = getAll();
    list.removeWhere((s) => s.id == id);
    await _saveList(list);
  }

  Future<void> _saveList(List<SavedSummary> list) async {
    final str = jsonEncode(list.map((e) => e.toJson()).toList());
    await _prefs.setString(_key, str);
  }

  String generateTitle(List<int> feedIds, DateTime dateTime) {
    final feedIdsStr = feedIds.join(',');
    final dt = '${dateTime.year}${_pad(dateTime.month)}${_pad(dateTime.day)}-${_pad(dateTime.hour)}${_pad(dateTime.minute)}';
    return '$feedIdsStr-$dt';
  }

  String _pad(int n) => n.toString().padLeft(2, '0');
}

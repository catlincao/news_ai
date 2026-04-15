import 'package:shared_preferences/shared_preferences.dart';
import '../../data/services/ai_service.dart';

class AppConfig {
  static const String _keyMinifluxUrl = 'miniflux_url';
  static const String _keyMinifluxApiKey = 'miniflux_api_key';
  static const String _keyAiProvider = 'ai_provider';
  static const String _keyAiApiKey = 'ai_api_key';
  static const String _keyAiModel = 'ai_model';
  static const String _keyAiBaseUrl = 'ai_base_url';
  static const String _keyFeedsFullContent = 'feeds_full_content';
  static const String _keyPerFeedLimit = 'per_feed_limit';

  final SharedPreferences _prefs;

  AppConfig(this._prefs);

  String get minifluxUrl => _prefs.getString(_keyMinifluxUrl) ?? 'http://47.112.115.122:14545';
  set minifluxUrl(String value) => _prefs.setString(_keyMinifluxUrl, value);

  String get minifluxApiKey => _prefs.getString(_keyMinifluxApiKey) ?? '';
  set minifluxApiKey(String value) => _prefs.setString(_keyMinifluxApiKey, value);

  String get aiProvider => _prefs.getString(_keyAiProvider) ?? 'openai';
  set aiProvider(String value) => _prefs.setString(_keyAiProvider, value);

  String get aiApiKey => _prefs.getString(_keyAiApiKey) ?? '';
  set aiApiKey(String value) => _prefs.setString(_keyAiApiKey, value);

  String get aiModel => _prefs.getString(_keyAiModel) ?? 'gpt-3.5-turbo';
  set aiModel(String value) => _prefs.setString(_keyAiModel, value);

  String get aiBaseUrl => _prefs.getString(_keyAiBaseUrl) ?? '';
  set aiBaseUrl(String value) => _prefs.setString(_keyAiBaseUrl, value);

  int get perFeedLimit => _prefs.getInt(_keyPerFeedLimit) ?? 20;
  set perFeedLimit(int value) => _prefs.setInt(_keyPerFeedLimit, value);

  Set<int> get feedsWithFullContent {
    final str = _prefs.getString(_keyFeedsFullContent) ?? '';
    if (str.isEmpty) return {};
    return str.split(',').map((s) => int.tryParse(s) ?? 0).where((i) => i > 0).toSet();
  }

  void setFeedsWithFullContent(Set<int> feedIds) {
    _prefs.setString(_keyFeedsFullContent, feedIds.join(','));
  }

  AIConfig get aiConfig {
    AIProvider provider;
    switch (aiProvider) {
      case 'anthropic':
        provider = AIProvider.anthropic;
        break;
      case 'minimax':
        provider = AIProvider.minimax;
        break;
      default:
        provider = AIProvider.openai;
    }
    return AIConfig(
      provider: provider,
      apiKey: aiApiKey,
      model: aiModel,
      baseUrl: aiBaseUrl.isEmpty ? null : aiBaseUrl,
    );
  }

  bool get isConfigured =>
      minifluxUrl.isNotEmpty &&
      minifluxApiKey.isNotEmpty &&
      aiApiKey.isNotEmpty;

  Future<void> clear() async {
    await _prefs.clear();
  }
}

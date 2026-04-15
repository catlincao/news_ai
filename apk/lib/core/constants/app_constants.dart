class AppConstants {
  static const String appName = '新闻 AI 摘要';
  static const String appVersion = '1.0.0';

  // Miniflux default settings
  static const String defaultMinifluxUrl = 'http://47.112.115.122:14545';

  // AI providers
  static const String providerOpenAI = 'openai';
  static const String providerAnthropic = 'anthropic';
  static const String providerMiniMax = 'minimax';

  // Default AI models
  static const String defaultOpenAIModel = 'gpt-3.5-turbo';
  static const String defaultAnthropicModel = 'claude-3-sonnet-20240229';
  static const String defaultMiniMaxModel = 'abab6-chat';

  // Content extraction
  static const int shortSummaryThreshold = 100;
  static const int maxContentLength = 10000;
}

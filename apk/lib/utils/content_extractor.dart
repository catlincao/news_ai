import 'dart:convert';

/// Content extractor for various news websites
class ContentExtractor {
  /// Extract content from wallstreetcn.com __SSR__ format
  static String extractSSRContent(String htmlContent) {
    // Find __SSR__ script tag
    final ssrMatch = RegExp(r'<script>__SSR__\s*=\s*({.+?})</script>', dotAll: true)
        .firstMatch(htmlContent);
    if (ssrMatch == null) {
      return '';
    }

    try {
      final ssrJson = jsonDecode(ssrMatch.group(1)!) as Map<String, dynamic>;
      final article = (ssrJson['state'] as Map<String, dynamic>?)?['default']
          ?['children']?['default']?['data']?['article'] as Map<String, dynamic>?;
      if (article == null) return '';

      var content = article['content'] as String? ?? '';
      // Decode URL-encoded HTML
      content = _decodeHtmlEntities(content);
      // Strip HTML tags but keep structure
      content = _stripHtmlTags(content);
      return content.trim();
    } catch (_) {
      return '';
    }
  }

  /// Extract content from Nuxt.js __NUXT__ format (韭研公社)
  static String extractNUXTContent(String htmlContent) {
    final nuxtMatch = RegExp(
      r'<script>window\.__NUXT__=.+?</script>',
      dotAll: true,
    ).firstMatch(htmlContent);
    if (nuxtMatch == null) return '';

    final script = nuxtMatch.group(0) ?? '';
    final contentStart = script.indexOf('content:"');
    if (contentStart < 0) return '';

    var rest = script.substring(contentStart + 9);
    var endPos = rest.indexOf('",url');
    if (endPos < 0) endPos = rest.indexOf('",type');
    if (endPos < 0) endPos = rest.indexOf('",image');
    if (endPos < 0) endPos = rest.length;

    var raw = rest.substring(0, endPos);
    // Decode Unicode escapes
    raw = _decodeUnicodeEscapes(raw);
    // Decode HTML entities
    raw = _decodeHtmlEntities(raw);
    // Strip HTML tags
    raw = _stripHtmlTags(raw);
    return raw.trim();
  }

  /// Extract content from regular HTML pages
  static String extractReadableContent(String htmlContent) {
    // First check for special formats
    if (htmlContent.contains('__SSR__')) {
      final content = extractSSRContent(htmlContent);
      if (content.isNotEmpty) return content;
    }
    if (htmlContent.contains('window.__NUXT__')) {
      final content = extractNUXTContent(htmlContent);
      if (content.isNotEmpty) return content;
    }

    // Fallback: simple HTML tag stripping
    return _stripHtmlTags(htmlContent).trim();
  }

  static String _decodeHtmlEntities(String text) {
    return text
        .replaceAll('&lt;', '<')
        .replaceAll('&gt;', '>')
        .replaceAll('&amp;', '&')
        .replaceAll('&quot;', '"')
        .replaceAll('&#39;', "'")
        .replaceAll('&nbsp;', ' ');
  }

  static String _decodeUnicodeEscapes(String text) {
    return text.replaceAllMapped(
      RegExp(r'\\u([0-9a-fA-F]{4})'),
      (m) => String.fromCharCode(int.parse(m.group(1)!, radix: 16)),
    );
  }

  static String _stripHtmlTags(String html) {
    // Replace div and br tags with newlines
    var text = html.replaceAll(RegExp(r'<div[^>]*>'), '\n');
    text = text.replaceAll(RegExp(r'<br\s*/?>'), '\n');
    // Remove all other HTML tags
    text = text.replaceAll(RegExp(r'<[^>]+>'), '');
    // Clean up whitespace
    text = text.replaceAll(RegExp(r'\n\s*\n'), '\n\n');
    text = text.replaceAll(RegExp(r' +\n'), '\n');
    text = text.replaceAll(RegExp(r'\n +'), '\n');
    return text;
  }
}

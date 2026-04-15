import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../core/config/app_config.dart';
import '../blocs/feed/feed_bloc.dart';
import '../blocs/feed/feed_event.dart';
import '../../data/services/miniflux_service.dart';
import '../../data/services/ai_service.dart';

class SettingsScreen extends StatefulWidget {
  final AppConfig config;

  const SettingsScreen({super.key, required this.config});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _minifluxUrlController;
  late TextEditingController _minifluxApiKeyController;
  late TextEditingController _aiApiKeyController;
  late TextEditingController _aiModelController;
  late TextEditingController _aiBaseUrlController;
  String _aiProvider = 'openai';
  bool _isTesting = false;
  String? _testResult;

  @override
  void initState() {
    super.initState();
    _minifluxUrlController = TextEditingController(text: widget.config.minifluxUrl);
    _minifluxApiKeyController = TextEditingController(text: widget.config.minifluxApiKey);
    _aiApiKeyController = TextEditingController(text: widget.config.aiApiKey);
    _aiModelController = TextEditingController(text: widget.config.aiModel);
    _aiBaseUrlController = TextEditingController(text: widget.config.aiBaseUrl);
    _aiProvider = widget.config.aiProvider;
  }

  @override
  void dispose() {
    _minifluxUrlController.dispose();
    _minifluxApiKeyController.dispose();
    _aiApiKeyController.dispose();
    _aiModelController.dispose();
    _aiBaseUrlController.dispose();
    super.dispose();
  }

  void _save() {
    widget.config.minifluxUrl = _minifluxUrlController.text.trim();
    widget.config.minifluxApiKey = _minifluxApiKeyController.text.trim();
    widget.config.aiApiKey = _aiApiKeyController.text.trim();
    widget.config.aiModel = _aiModelController.text.trim();
    widget.config.aiBaseUrl = _aiBaseUrlController.text.trim();
    widget.config.aiProvider = _aiProvider;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('设置已保存')),
    );
  }

  Future<void> _testConnection() async {
    setState(() {
      _isTesting = true;
      _testResult = null;
    });

    try {
      final url = _minifluxUrlController.text.trim();
      final apiKey = _minifluxApiKeyController.text.trim();

      print('Testing connection to: $url');
      print('API Key length: ${apiKey.length}');

      final service = MinifluxService(
        baseUrl: url,
        apiKey: apiKey,
      );
      final success = await service.testConnection();
      setState(() {
        _testResult = success ? '连接成功!' : '连接失败';
        _isTesting = false;
      });
    } catch (e) {
      print('Connection test exception: $e');
      setState(() {
        _testResult = '连接失败: $e';
        _isTesting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('设置'),
        actions: [
          TextButton(
            onPressed: _save,
            child: const Text('保存'),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Miniflux 配置',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _minifluxUrlController,
            decoration: const InputDecoration(
              labelText: 'Miniflux 服务器地址',
              hintText: 'http://47.112.115.122:14545',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _minifluxApiKeyController,
            decoration: const InputDecoration(
              labelText: 'Miniflux API Key',
              border: OutlineInputBorder(),
            ),
            obscureText: true,
          ),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: _isTesting ? null : _testConnection,
            child: _isTesting
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('测试连接'),
          ),
          if (_testResult != null) ...[
            const SizedBox(height: 8),
            Text(_testResult!,
                style: TextStyle(
                    color: _testResult!.contains('成功')
                        ? Colors.green
                        : Colors.red)),
          ],
          const SizedBox(height: 32),
          const Text(
            'AI 配置',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            value: _aiProvider,
            decoration: const InputDecoration(
              labelText: 'AI 提供商',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 'openai', child: Text('OpenAI')),
              DropdownMenuItem(value: 'anthropic', child: Text('Anthropic (Claude)')),
              DropdownMenuItem(value: 'minimax', child: Text('MiniMax')),
            ],
            onChanged: (value) {
              setState(() {
                _aiProvider = value ?? 'openai';
              });
            },
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _aiApiKeyController,
            decoration: const InputDecoration(
              labelText: 'AI API Key',
              border: OutlineInputBorder(),
            ),
            obscureText: true,
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _aiModelController,
            decoration: InputDecoration(
              labelText: '模型名称',
              hintText: _aiProvider == 'openai'
                  ? 'gpt-3.5-turbo, gpt-4'
                  : _aiProvider == 'anthropic'
                      ? 'claude-3-sonnet-20240229'
                      : 'abab6-chat',
              border: const OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _aiBaseUrlController,
            decoration: const InputDecoration(
              labelText: 'API Base URL (可选)',
              hintText: '如使用代理或自定义端点',
              border: OutlineInputBorder(),
            ),
          ),
        ],
      ),
    );
  }
}

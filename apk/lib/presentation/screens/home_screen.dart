import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/config/app_config.dart';
import '../../data/services/miniflux_service.dart';
import '../../data/services/ai_service.dart';
import '../../data/services/saved_summary_service.dart';
import '../blocs/feed/feed_bloc.dart';
import '../blocs/feed/feed_event.dart';
import '../blocs/summary/summary_bloc.dart';
import '../blocs/summary/summary_event.dart';
import '../blocs/saved_summary/saved_summary_bloc.dart';
import '../blocs/saved_summary/saved_summary_event.dart';
import 'feed_list_screen.dart';
import 'summary_screen.dart';
import 'saved_summaries_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  final AppConfig config;

  const HomeScreen({super.key, required this.config});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  MinifluxService? _minifluxService;
  AIService? _aiService;
  SavedSummaryService? _savedSummaryService;
  int _currentIndex = 0;
  List<int> _selectedFeedIds = [];
  late TextEditingController _limitController;

  @override
  void initState() {
    super.initState();
    _limitController = TextEditingController(text: widget.config.perFeedLimit.toString());
    _initServices();
  }

  @override
  void dispose() {
    _limitController.dispose();
    super.dispose();
  }

  void _saveLimit(String value) {
    final parsed = int.tryParse(value);
    if (parsed != null && parsed > 0) {
      widget.config.perFeedLimit = parsed;
    }
  }

  Future<void> _initServices() async {
    if (widget.config.isConfigured) {
      _minifluxService = MinifluxService(
        baseUrl: widget.config.minifluxUrl,
        apiKey: widget.config.minifluxApiKey,
      );
      _aiService = AIService(config: widget.config.aiConfig);
      if (widget.config.minifluxApiKey.isNotEmpty) {
        final prefs = await SharedPreferences.getInstance();
        _savedSummaryService = SavedSummaryService(prefs);
      }
      setState(() {});
    }
  }

  bool get _isConfigured => widget.config.isConfigured && _minifluxService != null && _aiService != null && _savedSummaryService != null;

  @override
  Widget build(BuildContext context) {
    if (!_isConfigured) {
      return _buildSetupScreen();
    }

    return MultiBlocProvider(
      providers: [
        BlocProvider(
          create: (_) => FeedBloc(
            minifluxService: _minifluxService!,
            config: widget.config,
          )..add(const LoadFeeds()),
        ),
        BlocProvider(
          create: (_) => SummaryBloc(
            minifluxService: _minifluxService!,
            aiService: _aiService!,
            config: widget.config,
          )..add(const ClearSummary()),
        ),
        BlocProvider(
          create: (_) => SavedSummaryBloc(service: _savedSummaryService!)
            ..add(const LoadSavedSummaries()),
        ),
      ],
      child: Builder(
        builder: (context) {
          return Scaffold(
            body: IndexedStack(
              index: _currentIndex,
              children: [
                _buildMainTab(context),
                FeedListScreen(
                  onFeedsSelected: () {
                    final feedState = context.read<FeedBloc>().state;
                    final newSelectedIds = feedState.selectedFeedIds.toList();
                    print('[HomeScreen] onFeedsSelected: selectedFeedIds = $newSelectedIds, limit = ${widget.config.perFeedLimit}');
                    // Clear previous summary and start loading immediately
                    context.read<SummaryBloc>()
                      ..add(const ClearSummary())
                      ..add(LoadEntries(feedIds: newSelectedIds, limit: widget.config.perFeedLimit));
                    setState(() {
                      _selectedFeedIds = newSelectedIds;
                      _currentIndex = 2;
                    });
                  },
                ),
                SummaryScreen(selectedFeedIds: _selectedFeedIds, config: widget.config),
                const SavedSummariesScreen(),
              ],
            ),
            bottomNavigationBar: NavigationBar(
              selectedIndex: _currentIndex,
              onDestinationSelected: (index) {
                setState(() {
                  _currentIndex = index;
                });
              },
              destinations: const [
                NavigationDestination(
                  icon: Icon(Icons.home_outlined),
                  selectedIcon: Icon(Icons.home),
                  label: '首页',
                ),
                NavigationDestination(
                  icon: Icon(Icons.rss_feed_outlined),
                  selectedIcon: Icon(Icons.rss_feed),
                  label: '订阅源',
                ),
                NavigationDestination(
                  icon: Icon(Icons.summarize_outlined),
                  selectedIcon: Icon(Icons.summarize),
                  label: '摘要',
                ),
                NavigationDestination(
                  icon: Icon(Icons.bookmark_outline),
                  selectedIcon: Icon(Icons.bookmark),
                  label: '收藏',
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildMainTab(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('新闻 AI 摘要'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => SettingsScreen(config: widget.config),
                ),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.newspaper,
                  size: 80,
                  color: Colors.blue,
                ),
                const SizedBox(height: 24),
                const Text(
                  '新闻 AI 摘要',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  '使用 AI 分析新闻',
                  style: TextStyle(color: Colors.grey[600]),
                ),
                const SizedBox(height: 32),
                // 每源限制输入
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text('每源限制：'),
                    SizedBox(
                      width: 60,
                      child: TextField(
                        keyboardType: TextInputType.number,
                        textAlign: TextAlign.center,
                        controller: _limitController,
                        decoration: const InputDecoration(
                          hintText: '20',
                          contentPadding: EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                          border: OutlineInputBorder(),
                        ),
                        onChanged: _saveLimit,
                      ),
                    ),
                    const Text(' 篇'),
                  ],
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () {
                    setState(() {
                      _currentIndex = 1;
                    });
                  },
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('选择订阅源'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  ),
                ),
                const SizedBox(height: 16),
                TextButton(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => SettingsScreen(config: widget.config),
                      ),
                    );
                  },
                  child: const Text('设置'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSetupScreen() {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.settings,
                size: 80,
                color: Colors.grey,
              ),
              const SizedBox(height: 24),
              const Text(
                '请先配置',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                '需要配置 Miniflux 和 AI API 才能使用',
                style: TextStyle(color: Colors.grey[600]),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => SettingsScreen(config: widget.config),
                    ),
                  );
                },
                child: const Text('前往设置'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

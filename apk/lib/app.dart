import 'package:flutter/material.dart';
import 'core/config/app_config.dart';
import 'presentation/screens/home_screen.dart';

class NewsAIApp extends StatelessWidget {
  final AppConfig config;

  const NewsAIApp({super.key, required this.config});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '新闻 AI 摘要',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: HomeScreen(config: config),
    );
  }
}

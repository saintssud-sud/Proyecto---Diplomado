import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'controllers/preferences_controller.dart';
import 'screens/splash_screen.dart';

class ProyectoFinalApp extends StatelessWidget {
  const ProyectoFinalApp({super.key});

  @override
  Widget build(BuildContext context) {
    final preferences = context.watch<PreferencesController>();

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'SIGVACH',
      themeMode: preferences.themeMode,
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.indigo),
      darkTheme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.indigo,
        brightness: Brightness.dark,
      ),
      home: const SplashScreen(),
    );
  }
}

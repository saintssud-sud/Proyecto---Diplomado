import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;

class AppConfig {
  const AppConfig({
    required this.supabaseUrl,
    required this.supabasePublishableKey,
  });

  final String supabaseUrl;
  final String supabasePublishableKey;

  factory AppConfig.fromEnvironment() {
    return const AppConfig(
      supabaseUrl: String.fromEnvironment('SUPABASE_URL'),
      supabasePublishableKey: String.fromEnvironment(
        'SUPABASE_PUBLISHABLE_KEY',
      ),
    );
  }

  factory AppConfig.fromJson(Map<String, dynamic> json) {
    return AppConfig(
      supabaseUrl: json['SUPABASE_URL'] as String? ?? '',
      supabasePublishableKey:
          json['SUPABASE_PUBLISHABLE_KEY'] as String? ?? '',
    );
  }

  /// Lee la configuración desde el asset empaquetado en la app
  /// (`assets/config/supabase.json`). Se usa como respaldo cuando se
  /// compila sin `--dart-define`, de modo que `flutter build apk --release`
  /// genere un APK funcional con Supabase.
  static Future<AppConfig> fromAsset() async {
    try {
      final raw = await rootBundle.loadString('assets/config/supabase.json');
      final decoded = jsonDecode(raw);
      if (decoded is Map<String, dynamic>) {
        return AppConfig.fromJson(decoded);
      }
    } catch (_) {
      // Asset ausente o inválido: se devuelve una configuración vacía.
    }
    return const AppConfig(supabaseUrl: '', supabasePublishableKey: '');
  }

  bool get hasSupabaseConfig =>
      supabaseUrl.trim().isNotEmpty && supabasePublishableKey.trim().isNotEmpty;

  bool get useSupabase => hasSupabaseConfig;

  String get modeLabel => 'SUPABASE';
}

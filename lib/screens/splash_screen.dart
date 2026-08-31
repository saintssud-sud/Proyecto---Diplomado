import 'dart:async';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../config/app_config.dart';
import 'auth_gate.dart';
import 'setup_required_screen.dart';

/// Pantalla de presentación (splash) con el logo SIGVACH.
///
/// Muestra el logo (assets/images/logo.png), el nombre del sistema y una
/// breve animación de aparición. Después de [minimumDuration] navega a la
/// pantalla principal según la configuración.
class SplashScreen extends StatefulWidget {
  const SplashScreen({
    super.key,
    this.minimumDuration = const Duration(milliseconds: 2800),
  });

  /// Tiempo mínimo que permanece visible el splash.
  final Duration minimumDuration;

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _fade;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    );
    _fade = CurvedAnimation(parent: _controller, curve: Curves.easeOut);
    _controller.forward();
    _timer = Timer(widget.minimumDuration, _goNext);
  }

  void _goNext() {
    if (!mounted) return;
    final config = context.read<AppConfig>();
    Navigator.of(context).pushReplacement(
      PageRouteBuilder<void>(
        transitionDuration: const Duration(milliseconds: 500),
        pageBuilder: (_, _, _) => config.hasSupabaseConfig
            ? const AuthGate()
            : const SetupRequiredScreen(),
        transitionsBuilder: (_, animation, _, child) =>
            FadeTransition(opacity: animation, child: child),
      ),
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF39B54A),
      body: SafeArea(
        child: Center(
          child: FadeTransition(
            opacity: _fade,
            child: Column(
              mainAxisSize: MainAxisSize.max,
              children: <Widget>[
                const SizedBox(height: 56),
                // Logo dentro de un recuadro blanco redondeado.
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(28),
                  ),
                  child: Image.asset(
                    'assets/images/logo.png',
                    width: 150,
                    height: 150,
                    fit: BoxFit.contain,
                  ),
                ),
                const SizedBox(height: 28),
                const Text(
                  'S.I.G.V.A.C.H.',
                  style: TextStyle(
                    fontSize: 30,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Sistema de Gestión de Variables para Cultivos',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 14, color: Colors.white),
                ),
                const Text(
                  'Hidropónicos',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 14, color: Colors.white),
                ),
                const Spacer(),
                const SizedBox(
                  width: 26,
                  height: 26,
                  child: CircularProgressIndicator(
                    strokeWidth: 3,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Cargando...',
                  style: TextStyle(fontSize: 13, color: Colors.white),
                ),
                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

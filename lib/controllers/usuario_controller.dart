import 'dart:async';

import 'package:flutter/foundation.dart';

import '../models/usuario_perfil.dart';
import '../repositories/usuario_repository.dart';

/// Controlador del perfil del usuario autenticado.
///
/// Expone el perfil actual (datos personales + rol) y permite saber si el
/// usuario es administrador para mostrar/ocultar el panel de gestión.
class UsuarioController extends ChangeNotifier {
  UsuarioController({UsuarioRepository? repository})
    : _repository = repository ?? UsuarioRepository();

  final UsuarioRepository _repository;

  UsuarioPerfil? _perfil;
  bool _cargando = false;
  bool _inicializado = false;
  StreamSubscription<void>? _authSub;

  UsuarioPerfil? get perfil => _perfil;

  bool get cargando => _cargando;

  bool get esAdmin => _perfil?.esAdmin ?? false;

  String? get nombre =>
      _perfil?.nombre.isNotEmpty == true ? _perfil!.nombre : null;

  /// Escucha los cambios de sesión y refresca el perfil.
  void iniciar() {
    if (_inicializado) return;
    _inicializado = true;

    _repository.auth.authStateChanges().listen((user) async {
      if (user == null) {
        _perfil = null;
        notifyListeners();
        return;
      }
      await recargar();
    });
  }

  /// Vuelve a leer el perfil del usuario actual desde Firestore.
  Future<void> recargar() async {
    _cargando = true;
    notifyListeners();
    try {
      _perfil = await _repository.obtenerUsuarioActual();
    } catch (e) {
      debugPrint('Error al cargar perfil: $e');
      _perfil = null;
    } finally {
      _cargando = false;
      notifyListeners();
    }
  }

  @override
  void dispose() {
    _authSub?.cancel();
    super.dispose();
  }
}

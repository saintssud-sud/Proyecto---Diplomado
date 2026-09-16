import 'package:flutter/foundation.dart';

import '../models/api/modelos_api.dart';
import '../repositories/api/usuarios_api_repository.dart';
import '../widgets/vista_con_estados.dart';
import 'estado_de_vista.dart';

/// Controlador del perfil de la cuenta con sesión iniciada.
///
/// El perfil no se guarda en el dispositivo: se consulta al servicio, que es
/// quien conoce el rol vigente y el estado de la cuenta. Así, si un
/// administrador cambia un permiso, la aplicación lo refleja en la siguiente
/// consulta en lugar de seguir mostrando un dato viejo.
class PerfilController extends ChangeNotifier {
  PerfilController({required UsuariosApiRepository usuarios}) : _usuarios = usuarios;

  final UsuariosApiRepository _usuarios;

  EstadoVista _estado = EstadoVista.cargando;
  String? _mensajeError;
  bool _errorDeConexion = false;
  PerfilUsuario? _perfil;

  EstadoVista get estado => _estado;
  String? get mensajeError => _mensajeError;
  bool get errorDeConexion => _errorDeConexion;
  PerfilUsuario? get perfil => _perfil;

  /// Nombre presentable: el del perfil o, si no lo tiene, el correo.
  String get nombrePresentable {
    final PerfilUsuario? actual = _perfil;
    if (actual == null) {
      return '';
    }
    return actual.nombre.isNotEmpty ? actual.nombre : actual.email;
  }

  /// Consulta el perfil del usuario autenticado.
  Future<void> cargar() async {
    _estado = EstadoVista.cargando;
    _mensajeError = null;
    _errorDeConexion = false;
    notifyListeners();

    try {
      _perfil = await _usuarios.obtenerPerfil();
      _estado = EstadoVista.conDatos;
    } catch (error) {
      final FalloDeVista fallo = FalloDeVista.desde(error);
      _perfil = null;
      _mensajeError = fallo.mensaje;
      _errorDeConexion = fallo.deConexion;
      _estado = EstadoVista.error;
    } finally {
      notifyListeners();
    }
  }

  /// Actualiza los datos personales y vuelve a consultar el perfil.
  Future<void> actualizar({
    String? nombre,
    String? telefono,
    String? cargo,
  }) async {
    _perfil = await _usuarios.actualizarPerfil(
      nombre: nombre,
      telefono: telefono,
      cargo: cargo,
    );
    _estado = EstadoVista.conDatos;
    _mensajeError = null;
    _errorDeConexion = false;
    notifyListeners();
  }
}

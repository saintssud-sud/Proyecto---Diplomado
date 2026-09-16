import '../../config/api_config.dart';
import '../../models/api/modelos_api.dart';
import '../../services/api_cliente.dart';

/// Operaciones sobre el perfil de la cuenta con sesión iniciada.
///
/// Corresponde al recurso `/api/v1/usuarios` del contrato. El perfil se crea al
/// registrarse y el servicio lo usa para autorizar cada petición; aquí la
/// aplicación lo consulta y mantiene los datos de contacto.
///
/// El **rol** y el estado de activación no se envían nunca desde aquí: no forman
/// parte del contrato de entrada, porque cambiarlos es una atribución de
/// administración y no del propio usuario.
class UsuariosApiRepository {
  UsuariosApiRepository(this._cliente);

  final ApiCliente _cliente;

  static const String _recurso = 'usuarios';

  /// Consulta el perfil del usuario autenticado.
  Future<PerfilUsuario> obtenerPerfil() async {
    final Map<String, dynamic> datos =
        await _cliente.obtenerMapa(ApiConfig.ruta('$_recurso/perfil'));
    return PerfilUsuario.fromJson(datos);
  }

  /// Actualiza los datos personales del usuario autenticado.
  Future<PerfilUsuario> actualizarPerfil({
    String? nombre,
    String? telefono,
    String? cargo,
  }) async {
    final Map<String, dynamic> cambios = <String, dynamic>{
      if (nombre != null) 'nombre': nombre,
      if (telefono != null) 'telefono': telefono,
      if (cargo != null) 'cargo': cargo,
    };
    if (cambios.isEmpty) {
      throw ArgumentError('No se indicó ningún dato para modificar.');
    }
    final Map<String, dynamic> datos = await _cliente.actualizar(
      ApiConfig.ruta('$_recurso/perfil'),
      cambios,
    );
    return PerfilUsuario.fromJson(datos);
  }
}

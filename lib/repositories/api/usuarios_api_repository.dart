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

  // --- Administración de cuentas -------------------------------------------
  //
  // Estas tres operaciones exigen el rol de administración: el servicio
  // responde 403 a cualquier otra cuenta, y esa comprobación se hace en el
  // servidor, no en la pantalla. Ocultar el botón no es autorización.
  //
  // Antes, el panel de usuarios leía la colección `usuarios` directamente desde
  // la aplicación. Esa vía dejó de funcionar cuando las reglas de seguridad de
  // Firestore cerraron el acceso directo, y además eludía dos protecciones que
  // el servicio sí aplica: que el rol pertenezca al catálogo y que la
  // administración no pueda quitarse a sí misma el rol ni desactivarse.

  /// Lista todas las cuentas registradas, con su rol y su estado.
  Future<List<PerfilUsuario>> listarCuentas() async {
    final List<Map<String, dynamic>> datos =
        await _cliente.obtenerLista(ApiConfig.ruta(_recurso));
    return datos.map(PerfilUsuario.fromJson).toList(growable: false);
  }

  /// Modifica los datos personales, el rol o el estado de una cuenta.
  ///
  /// Solo se envían los campos indicados. El servicio rechaza con 422 un rol
  /// que no exista en el sistema, y con 409 el intento de la propia
  /// administración de cambiarse el rol o desactivarse.
  Future<PerfilUsuario> modificarCuenta(
    String id, {
    String? nombre,
    String? telefono,
    String? cargo,
    String? rol,
    bool? activo,
  }) async {
    final Map<String, dynamic> cambios = <String, dynamic>{
      if (nombre != null) 'nombre': nombre,
      if (telefono != null) 'telefono': telefono,
      if (cargo != null) 'cargo': cargo,
      if (rol != null) 'rol': rol,
      if (activo != null) 'activo': activo,
    };
    if (cambios.isEmpty) {
      throw ArgumentError('No se indicó ningún dato para modificar.');
    }
    final Map<String, dynamic> datos = await _cliente.actualizar(
      ApiConfig.ruta('$_recurso/$id'),
      cambios,
    );
    return PerfilUsuario.fromJson(datos);
  }

  /// Elimina el perfil de una cuenta.
  ///
  /// La credencial de Firebase Authentication permanece: eliminarla exige
  /// privilegios de administración del proveedor, que no están en el alcance.
  Future<void> eliminarCuenta(String id) async {
    await _cliente.eliminar(ApiConfig.ruta('$_recurso/$id'));
  }
}

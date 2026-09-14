import '../../config/api_config.dart';
import '../../models/api/modelos_api.dart';
import '../../services/api_cliente.dart';

/// Operaciones sobre los módulos o zonas de cultivo.
///
/// Corresponde al recurso `/api/v1/modulos` del contrato. La escritura exige el
/// rol de administración y la lectura un rol habilitado para operar; la decisión
/// la toma el servidor, no esta capa.
class ModulosApiRepository {
  ModulosApiRepository(this._cliente);

  final ApiCliente _cliente;

  static const String _recurso = 'modulos';

  /// Lista los módulos, opcionalmente filtrando por estado de activación.
  Future<List<ModuloCultivo>> listar({bool? activo}) async {
    final List<Map<String, dynamic>> datos = await _cliente.obtenerLista(
      ApiConfig.ruta(_recurso),
      parametros: <String, String>{
        if (activo != null) 'activo': activo.toString(),
      },
    );
    return datos.map(ModuloCultivo.fromJson).toList(growable: false);
  }

  /// Consulta un módulo por su identificador.
  Future<ModuloCultivo> obtener(String id) async {
    final Map<String, dynamic> datos =
        await _cliente.obtenerMapa(ApiConfig.ruta('$_recurso/$id'));
    return ModuloCultivo.fromJson(datos);
  }

  /// Registra un módulo asociado a un tipo de cultivo y a un perfil.
  Future<ModuloCultivo> crear({
    required String nombre,
    required String tipoCultivo,
    required String perfilId,
    String? ubicacion,
  }) async {
    final Map<String, dynamic> datos =
        await _cliente.crear(ApiConfig.ruta(_recurso), <String, dynamic>{
      'nombre': nombre,
      'tipo_cultivo': tipoCultivo,
      'perfil_id': perfilId,
      if (ubicacion != null && ubicacion.trim().isNotEmpty) 'ubicacion': ubicacion.trim(),
    });
    return ModuloCultivo.fromJson(datos);
  }

  /// Modifica los campos indicados; los omitidos quedan como estaban.
  Future<ModuloCultivo> actualizar(
    String id, {
    String? nombre,
    String? tipoCultivo,
    String? perfilId,
    String? ubicacion,
    bool? activo,
  }) async {
    final Map<String, dynamic> cambios = <String, dynamic>{
      if (nombre != null) 'nombre': nombre,
      if (tipoCultivo != null) 'tipo_cultivo': tipoCultivo,
      if (perfilId != null) 'perfil_id': perfilId,
      if (ubicacion != null) 'ubicacion': ubicacion,
      if (activo != null) 'activo': activo,
    };
    if (cambios.isEmpty) {
      throw ArgumentError('No se indicó ningún campo para modificar.');
    }
    final Map<String, dynamic> datos =
        await _cliente.actualizar(ApiConfig.ruta('$_recurso/$id'), cambios);
    return ModuloCultivo.fromJson(datos);
  }

  /// Elimina un módulo; el servidor rechaza la operación si tiene lecturas.
  Future<void> eliminar(String id) => _cliente.eliminar(ApiConfig.ruta('$_recurso/$id'));
}

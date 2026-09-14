import '../../config/api_config.dart';
import '../../models/api/modelos_api.dart';
import '../../services/api_cliente.dart';

/// Operaciones sobre los rangos de referencia.
///
/// Corresponde al recurso `/api/v1/rangos` del contrato. Un rango pertenece a un
/// perfil de cultivo y a una variable, y es el valor contra el que el servidor
/// evalúa cada lectura recibida.
class RangosApiRepository {
  RangosApiRepository(this._cliente);

  final ApiCliente _cliente;

  static const String _recurso = 'rangos';

  /// Lista los rangos, opcionalmente filtrados por perfil y variable.
  Future<List<RangoReferencia>> listar({String? perfilId, String? variable}) async {
    final List<Map<String, dynamic>> datos = await _cliente.obtenerLista(
      ApiConfig.ruta(_recurso),
      parametros: <String, String>{
        if (perfilId != null) 'perfil_id': perfilId,
        if (variable != null) 'variable': variable,
      },
    );
    return datos.map(RangoReferencia.fromJson).toList(growable: false);
  }

  /// Define el rango de una variable en un perfil.
  ///
  /// El servidor rechaza el alta si el perfil ya tiene un rango para esa
  /// variable, y también si los valores no son coherentes.
  Future<RangoReferencia> crear({
    required String perfilId,
    required String variable,
    required double minimo,
    required double maximo,
  }) async {
    final Map<String, dynamic> datos =
        await _cliente.crear(ApiConfig.ruta(_recurso), <String, dynamic>{
      'perfil_id': perfilId,
      'variable': variable,
      'minimo': minimo,
      'maximo': maximo,
    });
    return RangoReferencia.fromJson(datos);
  }

  /// Modifica los límites del rango; los omitidos quedan como estaban.
  Future<RangoReferencia> actualizar(
    String id, {
    double? minimo,
    double? maximo,
  }) async {
    final Map<String, dynamic> cambios = <String, dynamic>{
      if (minimo != null) 'minimo': minimo,
      if (maximo != null) 'maximo': maximo,
    };
    if (cambios.isEmpty) {
      throw ArgumentError('No se indicó ningún límite para modificar.');
    }
    final Map<String, dynamic> datos =
        await _cliente.actualizar(ApiConfig.ruta('$_recurso/$id'), cambios);
    return RangoReferencia.fromJson(datos);
  }

  /// Elimina un rango de referencia.
  Future<void> eliminar(String id) => _cliente.eliminar(ApiConfig.ruta('$_recurso/$id'));
}

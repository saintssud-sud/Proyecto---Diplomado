import '../../config/api_config.dart';
import '../../models/api/modelos_api.dart';
import '../../services/api_cliente.dart';

/// Operaciones sobre las lecturas de las variables.
///
/// Corresponde al recurso `/api/v1/lecturas` del contrato. El envío automático
/// desde el módulo de adquisición se autentica con la clave del dispositivo y lo
/// realiza el propio dispositivo, no la aplicación; aquí solo se consultan
/// lecturas y se registran las que se miden a mano con instrumentos portátiles.
class LecturasApiRepository {
  LecturasApiRepository(this._cliente);

  final ApiCliente _cliente;

  static const String _recurso = 'lecturas';

  /// Consulta lecturas filtrando por módulo, variable y rango de fechas.
  Future<List<Lectura>> listar({
    String? moduloId,
    String? variable,
    DateTime? desde,
    DateTime? hasta,
    int? limite,
  }) async {
    final List<Map<String, dynamic>> datos = await _cliente.obtenerLista(
      ApiConfig.ruta(_recurso),
      parametros: _filtros(moduloId, variable, desde, hasta, limite),
    );
    return datos.map(Lectura.fromJson).toList(growable: false);
  }

  /// Devuelve el resumen por variable de la serie consultada.
  Future<List<ResumenVariable>> resumen({
    String? moduloId,
    String? variable,
    DateTime? desde,
    DateTime? hasta,
  }) async {
    final List<Map<String, dynamic>> datos = await _cliente.obtenerLista(
      ApiConfig.ruta('$_recurso/resumen'),
      parametros: _filtros(moduloId, variable, desde, hasta, null),
    );
    return datos.map(ResumenVariable.fromJson).toList(growable: false);
  }

  /// Consulta una lectura concreta.
  Future<Lectura> obtener(String id) async {
    final Map<String, dynamic> datos =
        await _cliente.obtenerMapa(ApiConfig.ruta('$_recurso/$id'));
    return Lectura.fromJson(datos);
  }

  /// Registra una lectura medida con instrumentos portátiles.
  ///
  /// El servidor fija el origen como manual: la aplicación no puede declarar que
  /// una lectura fue automática si no lo fue.
  Future<Lectura> registrarManual({
    required String moduloId,
    required String variable,
    required double valor,
    DateTime? timestamp,
    String? observacion,
  }) async {
    final Map<String, dynamic> datos =
        await _cliente.crear(ApiConfig.ruta('$_recurso/manual'), <String, dynamic>{
      'modulo_id': moduloId,
      'variable': variable,
      'valor': valor,
      if (timestamp != null) 'timestamp': timestamp.toUtc().toIso8601String(),
      if (observacion != null && observacion.trim().isNotEmpty)
        'observacion': observacion.trim(),
    });
    return Lectura.fromJson(datos);
  }

  /// Elimina una lectura; requiere rol de administración.
  Future<void> eliminar(String id) => _cliente.eliminar(ApiConfig.ruta('$_recurso/$id'));

  /// Descarga la exportación en CSV de la consulta indicada.
  Future<List<int>> exportarCsv({
    String? moduloId,
    String? variable,
    DateTime? desde,
    DateTime? hasta,
  }) {
    return _cliente.obtenerBytes(
      ApiConfig.ruta('exportaciones/lecturas.csv'),
      parametros: _filtros(moduloId, variable, desde, hasta, null),
    );
  }

  /// Arma la consulta omitiendo los filtros no indicados.
  ///
  /// El cliente descarta además los valores vacíos, de modo que un filtro sin
  /// valor no viaje como cadena vacía y el servidor no lo interprete como una
  /// búsqueda sin resultados.
  Map<String, String> _filtros(
    String? moduloId,
    String? variable,
    DateTime? desde,
    DateTime? hasta,
    int? limite,
  ) {
    return <String, String>{
      if (moduloId != null) 'modulo_id': moduloId,
      if (variable != null) 'variable': variable,
      if (desde != null) 'desde': desde.toUtc().toIso8601String(),
      if (hasta != null) 'hasta': hasta.toUtc().toIso8601String(),
      if (limite != null) 'limite': limite.toString(),
    };
  }
}

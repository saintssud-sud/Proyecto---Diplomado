import '../../config/api_config.dart';
import '../../models/api/modelos_api.dart';
import '../../services/api_cliente.dart';

/// Operaciones sobre las alertas.
///
/// Corresponde al recurso `/api/v1/alertas` del contrato. Las alertas no se
/// crean desde la aplicación: las genera el servidor cuando una lectura sale de
/// su rango de referencia. Aquí solo se consultan y se atienden.
class AlertasApiRepository {
  AlertasApiRepository(this._cliente);

  final ApiCliente _cliente;

  static const String _recurso = 'alertas';

  /// Lista las alertas activas, el historial o las de un módulo concreto.
  Future<List<AlertaServidor>> listar({
    String? estado,
    String? moduloId,
    int? limite,
  }) async {
    final List<Map<String, dynamic>> datos = await _cliente.obtenerLista(
      ApiConfig.ruta(_recurso),
      parametros: <String, String>{
        if (estado != null) 'estado': estado,
        if (moduloId != null) 'modulo_id': moduloId,
        if (limite != null) 'limite': limite.toString(),
      },
    );
    return datos.map(AlertaServidor.fromJson).toList(growable: false);
  }

  /// Consulta una alerta concreta, con la referencia a su lectura.
  Future<AlertaServidor> obtener(String id) async {
    final Map<String, dynamic> datos =
        await _cliente.obtenerMapa(ApiConfig.ruta('$_recurso/$id'));
    return AlertaServidor.fromJson(datos);
  }

  /// Marca la alerta como atendida, con una observación opcional.
  Future<AlertaServidor> marcarAtendida(String id, {String? observacion}) {
    return _cambiarEstado(id, 'atendida', observacion: observacion);
  }

  /// Devuelve la alerta al estado activo.
  Future<AlertaServidor> marcarActiva(String id) => _cambiarEstado(id, 'activa');

  Future<AlertaServidor> _cambiarEstado(
    String id,
    String estado, {
    String? observacion,
  }) async {
    final Map<String, dynamic> datos =
        await _cliente.actualizar(ApiConfig.ruta('$_recurso/$id'), <String, dynamic>{
      'estado': estado,
      if (observacion != null && observacion.trim().isNotEmpty)
        'observacion': observacion.trim(),
    });
    return AlertaServidor.fromJson(datos);
  }

  /// Elimina una alerta del historial; requiere rol de administración.
  Future<void> eliminar(String id) => _cliente.eliminar(ApiConfig.ruta('$_recurso/$id'));
}

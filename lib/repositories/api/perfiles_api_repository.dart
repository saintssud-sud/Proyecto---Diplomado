import '../../config/api_config.dart';
import '../../models/api/modelos_api.dart';
import '../../services/api_cliente.dart';

/// Operaciones sobre los perfiles de cultivo.
///
/// Corresponde al recurso `/api/v1/perfiles` del contrato. Un perfil agrupa los
/// rangos de referencia de un tipo de cultivo y es el que se asocia a cada
/// módulo, de modo que sus rangos son los que se aplican al evaluar las
/// lecturas.
class PerfilesApiRepository {
  PerfilesApiRepository(this._cliente);

  final ApiCliente _cliente;

  static const String _recurso = 'perfiles';

  /// Lista los perfiles de cultivo registrados.
  Future<List<PerfilCultivo>> listar() async {
    final List<Map<String, dynamic>> datos =
        await _cliente.obtenerLista(ApiConfig.ruta(_recurso));
    return datos.map(PerfilCultivo.fromJson).toList(growable: false);
  }

  /// Consulta un perfil concreto.
  Future<PerfilCultivo> obtener(String id) async {
    final Map<String, dynamic> datos =
        await _cliente.obtenerMapa(ApiConfig.ruta('$_recurso/$id'));
    return PerfilCultivo.fromJson(datos);
  }

  /// Registra un perfil de cultivo al que luego se le asocian sus rangos.
  Future<PerfilCultivo> crear({
    required String nombre,
    String? descripcion,
    bool predefinido = false,
  }) async {
    final Map<String, dynamic> datos =
        await _cliente.crear(ApiConfig.ruta(_recurso), <String, dynamic>{
      'nombre': nombre,
      if (descripcion != null && descripcion.trim().isNotEmpty)
        'descripcion': descripcion.trim(),
      'predefinido': predefinido,
    });
    return PerfilCultivo.fromJson(datos);
  }

  /// Elimina un perfil; el servidor rechaza la operación si tiene rangos.
  Future<void> eliminar(String id) => _cliente.eliminar(ApiConfig.ruta('$_recurso/$id'));
}

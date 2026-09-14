import 'package:flutter/foundation.dart';

import '../models/api/modelos_api.dart';
import '../repositories/api/lecturas_api_repository.dart';
import '../widgets/vista_con_estados.dart';
import 'estado_de_vista.dart';

/// Controlador de las lecturas que consume la API.
///
/// Mantiene el estado de la vista —cargando, con datos, vacío o con error— y
/// expone el mensaje que corresponde a cada fallo. La pantalla no interpreta
/// excepciones: solo dibuja el estado que este controlador publica.
class LecturasController extends ChangeNotifier {
  LecturasController(this._repositorio);

  final LecturasApiRepository _repositorio;

  EstadoVista _estado = EstadoVista.cargando;
  List<Lectura> _lecturas = const <Lectura>[];
  String? _mensajeError;
  bool _errorDeConexion = false;
  bool _cargando = false;

  // Filtros vigentes de la consulta.
  String? _moduloId;
  String? _variable;
  DateTime? _desde;
  DateTime? _hasta;

  EstadoVista get estado => _estado;
  List<Lectura> get lecturas => _lecturas;
  String? get mensajeError => _mensajeError;
  bool get errorDeConexion => _errorDeConexion;
  bool get cargando => _cargando;

  String? get moduloId => _moduloId;
  String? get variable => _variable;
  DateTime? get desde => _desde;
  DateTime? get hasta => _hasta;

  /// Lecturas fuera del rango de referencia, según el estado que asignó el servidor.
  List<Lectura> get fueraDeRango => _lecturas
      .where((Lectura lectura) =>
          lectura.estadoRango != null && EstadoRango.esFueraDeRango(lectura.estadoRango!))
      .toList(growable: false);

  /// Consulta las lecturas con los filtros vigentes.
  Future<void> cargar({
    String? moduloId,
    String? variable,
    DateTime? desde,
    DateTime? hasta,
    bool limpiarFiltros = false,
  }) async {
    if (limpiarFiltros) {
      _moduloId = null;
      _variable = null;
      _desde = null;
      _hasta = null;
    } else {
      if (moduloId != null) _moduloId = moduloId;
      if (variable != null) _variable = variable;
      if (desde != null) _desde = desde;
      if (hasta != null) _hasta = hasta;
    }

    _cargando = true;
    _estado = EstadoVista.cargando;
    _mensajeError = null;
    _errorDeConexion = false;
    notifyListeners();

    try {
      final List<Lectura> lecturas = await _repositorio.listar(
        moduloId: _moduloId,
        variable: _variable,
        desde: _desde,
        hasta: _hasta,
      );
      _lecturas = lecturas;
      _estado = lecturas.isEmpty ? EstadoVista.vacio : EstadoVista.conDatos;
    } catch (error) {
      // La traducción distingue el fallo de conexión del rechazo del servidor.
      final FalloDeVista fallo = FalloDeVista.desde(error);
      _lecturas = const <Lectura>[];
      _mensajeError = fallo.mensaje;
      _errorDeConexion = fallo.deConexion;
      _estado = EstadoVista.error;
    } finally {
      _cargando = false;
      notifyListeners();
    }
  }

  /// Vuelve a consultar con los filtros vigentes.
  Future<void> reintentar() => cargar();

  /// Registra una lectura medida a mano.
  ///
  /// Los errores se propagan a quien invoca —[ErrorApi] con el detalle por campo
  /// o [ErrorConexion]— porque el formulario debe señalar el dato rechazado en
  /// el propio campo, y eso el controlador no puede decidirlo.
  Future<Lectura> registrarManual({
    required String moduloId,
    required String variable,
    required double valor,
    DateTime? timestamp,
    String? observacion,
  }) async {
    final Lectura lectura = await _repositorio.registrarManual(
      moduloId: moduloId,
      variable: variable,
      valor: valor,
      timestamp: timestamp,
      observacion: observacion,
    );
    // La lectura nueva se incorpora al listado sin volver a consultar todo.
    _lecturas = <Lectura>[lectura, ..._lecturas];
    _estado = EstadoVista.conDatos;
    notifyListeners();
    return lectura;
  }

  /// Elimina una lectura y la retira del listado.
  Future<void> eliminar(String id) async {
    await _repositorio.eliminar(id);
    _lecturas = _lecturas.where((Lectura lectura) => lectura.id != id).toList(growable: false);
    _estado = _lecturas.isEmpty ? EstadoVista.vacio : EstadoVista.conDatos;
    notifyListeners();
  }
}

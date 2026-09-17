import 'package:flutter/foundation.dart';

import '../models/api/modelos_api.dart';
import '../repositories/api/alertas_api_repository.dart';
import '../widgets/vista_con_estados.dart';
import 'estado_de_vista.dart';

/// Controlador de las alertas del sistema.
///
/// Las alertas **no se crean desde la aplicación**: las genera el servidor
/// cuando una lectura sale del rango de referencia de su perfil. Aquí solo se
/// consultan —activas e historial— y se marcan como atendidas, siempre contra el
/// servicio, de modo que la pantalla y el aviso del panel cuenten lo mismo.
class AlertasController extends ChangeNotifier {
  AlertasController({required AlertasApiRepository alertas}) : _alertas = alertas;

  final AlertasApiRepository _alertas;

  EstadoVista _estado = EstadoVista.cargando;
  String? _mensajeError;
  bool _errorDeConexion = false;
  List<AlertaServidor> _activas = const <AlertaServidor>[];
  List<AlertaServidor> _atendidas = const <AlertaServidor>[];

  EstadoVista get estado => _estado;
  String? get mensajeError => _mensajeError;
  bool get errorDeConexion => _errorDeConexion;

  /// Alertas pendientes de atender.
  List<AlertaServidor> get activas => _activas;

  /// Alertas ya atendidas: el historial.
  List<AlertaServidor> get atendidas => _atendidas;

  /// Total de alertas consultadas, para decidir el estado vacío.
  int get total => _activas.length + _atendidas.length;

  /// Consulta las alertas activas y el historial.
  ///
  /// Se piden las dos listas en la misma operación lógica: si el servicio no
  /// responde, la pantalla lo informa como un fallo y no como un historial
  /// vacío, que el usuario leería como «no hay nada que atender».
  /// Consulta las alertas del módulo indicado.
  ///
  /// El filtro por módulo es el mismo que usa el panel principal: sin él, la
  /// pantalla mostraba alertas de todos los módulos juntas, aunque el resto de
  /// la aplicación trabaje sobre el módulo vigente.
  Future<void> cargar({String? moduloId}) async {
    _estado = EstadoVista.cargando;
    _mensajeError = null;
    _errorDeConexion = false;
    notifyListeners();

    try {
      final List<AlertaServidor> activas =
          await _alertas.listar(estado: 'activa', moduloId: moduloId);
      final List<AlertaServidor> atendidas =
          await _alertas.listar(estado: 'atendida', moduloId: moduloId);
      _activas = List<AlertaServidor>.unmodifiable(activas);
      _atendidas = List<AlertaServidor>.unmodifiable(atendidas);
      _estado = total == 0 ? EstadoVista.vacio : EstadoVista.conDatos;
    } catch (error) {
      final FalloDeVista fallo = FalloDeVista.desde(error);
      _activas = const <AlertaServidor>[];
      _atendidas = const <AlertaServidor>[];
      _mensajeError = fallo.mensaje;
      _errorDeConexion = fallo.deConexion;
      _estado = EstadoVista.error;
    } finally {
      notifyListeners();
    }
  }

  /// Marca una alerta como atendida y refresca las dos listas.
  Future<void> marcarAtendida(String id, {String? observacion}) async {
    await _alertas.marcarAtendida(id, observacion: observacion);
    await cargar();
  }

  /// Devuelve una alerta atendida al estado activo.
  Future<void> marcarActiva(String id) async {
    await _alertas.marcarActiva(id);
    await cargar();
  }
}

import 'package:flutter/foundation.dart';

import '../models/api/modelos_api.dart';
import '../repositories/api/perfiles_api_repository.dart';
import '../repositories/api/rangos_api_repository.dart';
import '../widgets/vista_con_estados.dart';
import 'estado_de_vista.dart';

/// Controlador de los rangos de referencia.
///
/// Un rango pertenece a un perfil de cultivo y a una variable, y es el valor
/// contra el que el **servidor** evalúa cada lectura. Por eso los cambios se
/// envían al servicio y después se vuelve a consultar: lo que se muestra es lo
/// que quedó guardado, no lo que la pantalla supone que se guardó.
class RangosController extends ChangeNotifier {
  RangosController({
    required RangosApiRepository rangos,
    required PerfilesApiRepository perfiles,
  })  : _rangos = rangos,
        _perfiles = perfiles;

  final RangosApiRepository _rangos;
  final PerfilesApiRepository _perfiles;

  EstadoVista _estado = EstadoVista.cargando;
  String? _mensajeError;
  bool _errorDeConexion = false;
  List<RangoReferencia> _rangosCargados = const <RangoReferencia>[];
  Map<String, String> _nombresDePerfil = const <String, String>{};

  EstadoVista get estado => _estado;
  String? get mensajeError => _mensajeError;
  bool get errorDeConexion => _errorDeConexion;
  List<RangoReferencia> get rangos => _rangosCargados;

  /// Nombre presentable del perfil; si no se pudo resolver, devuelve el id.
  String nombrePerfil(String perfilId) => _nombresDePerfil[perfilId] ?? perfilId;

  /// Consulta los rangos y los perfiles (para mostrar el nombre del perfil).
  Future<void> cargar() async {
    _estado = EstadoVista.cargando;
    _mensajeError = null;
    _errorDeConexion = false;
    notifyListeners();

    try {
      final List<PerfilCultivo> perfiles = await _perfiles.listar();
      final List<RangoReferencia> rangos = await _rangos.listar();

      _nombresDePerfil = <String, String>{
        for (final PerfilCultivo perfil in perfiles) perfil.id: perfil.nombre,
      };
      final List<RangoReferencia> ordenados = List<RangoReferencia>.of(rangos)
        ..sort((RangoReferencia a, RangoReferencia b) =>
            a.variable.compareTo(b.variable));
      _rangosCargados = List<RangoReferencia>.unmodifiable(ordenados);
      _estado = _rangosCargados.isEmpty ? EstadoVista.vacio : EstadoVista.conDatos;
    } catch (error) {
      final FalloDeVista fallo = FalloDeVista.desde(error);
      _rangosCargados = const <RangoReferencia>[];
      _mensajeError = fallo.mensaje;
      _errorDeConexion = fallo.deConexion;
      _estado = EstadoVista.error;
    } finally {
      notifyListeners();
    }
  }

  /// Actualiza los límites del rango y refresca la lista.
  Future<void> actualizar(
    RangoReferencia rango, {
    double? minimo,
    double? maximo,
  }) async {
    await _rangos.actualizar(rango.id, minimo: minimo, maximo: maximo);
    await cargar();
  }
}
